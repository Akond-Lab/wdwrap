#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import functools
import logging
import math
import threading
from collections import OrderedDict
from enum import Enum
import random
from typing import Union, Optional, List

import numpy as np
import pandas as pd
from traitlets import HasTraits, Bool, Int, Float, Instance, validate, Unicode
from traittypes import DataFrame

from scipy.interpolate import BSpline, CubicSpline
from dask.distributed import Future

from .wdtraits import WdParamTraitCollection
from ..bundle import Bundle
from ..jobs import JobScheduler
from ..param import ParFlag
from ..drivers import MPAGE
from ..parameters import ParameterSet

"""
Module contains three families of classes:
   * `CurveTransformer` : transformers od dataframe (binning/resampling)
   * `CurveValues` : represents Dataframe with indempendent variable and one or more values
   * `Curve` : The curve with metadata, observed CurveValues, model-generated CurveValues
"""

class CurveTransformer(HasTraits):
    """Transformes one dataframe into another"""
    def __init__(self, *args, col_independent='ph', col_values=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.col_independent = col_independent
        self.col_values = ['mag'] if col_values is None else col_values

    def transform(self, df):
        return df

class CurvePhaser(CurveTransformer):
    """Adds/Updates `ph` (phase) column """
    hjd0 = Float(min=0)
    period = Float(min=0, allow_none=True)
    delta = Float()

    def __init__(self, *args, col_hjd='hjd', hjd0=0.0, period=None, delta=0.0,
                 col_independent='ph', col_values=None, **kwargs):
        super().__init__(*args, hjd0=hjd0, period=period, delta=delta,
                         col_independent=col_independent, col_values=col_values, **kwargs)
        self.col_hjd = col_hjd

    def transform(self, df):
        try:
            ph = ((df[self.col_hjd] - self.hjd0) / self.period + self.delta) % 1.0
        except KeyError:  # no hjd column
            return df
        except TypeError:  #  period is None
            mi = df[self.col_hjd].min()
            ma = df[self.col_hjd].max()
            rng = ma - mi
            ph = ((df[self.col_hjd] - mi) / rng) % 1.0
        ndf = df.copy()
        ndf['ph'] = ph
        return ndf


class CurveResampler(CurveTransformer):
    """Resamples original dataframe into `k` bins, from min to max

    `k == 0` maens: no transformation.
    `min,max == None` means: take `min()` or `max()` from source dataframe
    """
    k = Int(min=5, default_value=20)
    active = Bool(default_value=False)
    vmin = Float(allow_none=True)
    vmax = Float(allow_none=True)

    def __init__(self, *args, k=20, vmin=0.0, vmax=1.0, col_independent='ph', col_values=None, **kwargs):
        super().__init__(*args, col_independent=col_independent, col_values=col_values,
                         k=k, vmin=vmin, vmax=vmax, **kwargs)

    def transform(self, df):
        if self.active and self.k > 0:
            mi = df[self.col_independent].min() if self.vmin is None else self.vmin
            ma = df[self.col_independent].max() if self.vmax is None else self.vmax
            binwidth = (ma - mi) / self.k
            boundaries = np.linspace(mi, ma, self.k + 1)
            # ph = boundaries[:-1] + (binwidth / 2)  # put independent values in the center of bins
            cut = pd.cut(df[self.col_independent], boundaries)
            # calc mean of all bins for all value columns and independent column also
            ret = df[self.col_values + [self.col_independent]].groupby(cut).mean()
            return ret
        else:
            return super().transform(df)

# ############ CURVES as single set of points ####################### #

class CurveValues(HasTraits):
    df_version = Int()  # observe for transformed data change
    dataframe = Instance(pd.DataFrame, ())  # observe for original dataframe change
    plot = Bool()
    approx_order = Int(default_value=0)
    approx_method = Unicode(default_value='cubic-spline')
    approx_periodic = Bool(default_value=True)
    indep_column = Unicode(default_value='ph')  # hjd
    dep_columns = {'mag', 'rv1', 'rv2'}

    def __init__(self, *args, df=None, **kwargs):
        super().__init__(*args, **kwargs)
        if df is not None:
            self.dataframe = df
        else:
            self.dataframe = pd.DataFrame(columns=[self.indep_column, *self.dep_columns])
        self.observe(lambda change: self.get_approximators.invalidate_caches(),
                     ['approx_order', 'approx_method', 'approx_periodic', 'indep_column'])

    def invalidate_caches(self):
        self.get_approximators.cache_clear()
        # self.get_values_at.cache_clear()

    @property
    def df(self):
        return self.dataframe

    def set_df(self, df):
        self.invalidate_caches()
        self.dataframe = df

    @functools.lru_cache()
    def get_approximators(self):
        def nans(x):
            if np.isscalar(x):
                return np.nan
            else:
                return np.full_like(x, np.nan)
        ret = {col: nans for col in self.dep_columns if col in self.df.columns}
        if self.df is not None:
            for c in self.dep_columns & set(self.df.columns):
                if self.approx_method == 'cubic-spline':
                    kwargs = {}
                    if self.approx_periodic:
                        kwargs['extrapolate'] = 'periodic'
                        ret[c] = CubicSpline(self.df[self.indep_column], self.df[c], **kwargs)
                else:
                    logging.error(f'Unknown interpolation method "{self.approx_method}"')
        return ret

    # @functools.lru_cache()
    def get_values_at(self, indep_var_values=None):
        """Curve values at specified points

        Uses approximation, returns DataFrame.
        If indep_var_values is None, returns values without approximation"""
        if indep_var_values is None:
            return self.df

        approx = self.get_approximators()
        df = pd.DataFrame(indep_var_values, columns=[self.indep_column])
        for col, a in approx.items():
            df[col] = a(indep_var_values)
        return df

    @property
    def n(self):
        return len(self.df)

    def empty(self):
        return self.n == 0

class ConvertedValues(CurveValues):
    """Keeps additional 'original' dataframe which is converted somehow into
    `CurveValues.dt` """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_df = None
        self.transformers = OrderedDict([
            ('phaser', CurvePhaser()),
            ('resampler', CurveResampler())
        ])
        self.scan_transformers()

    def scan_transformers(self):
        for t in self.transformers.values():
            t.observe(lambda change: self.on_transformer_changed(change))

    def on_transformer_changed(self, change):
        self.invalidate_caches()

    def transform(self, df):
        for trans in self.transformers.values():
            df = trans.transform(df)
        return df

    def invalidate_caches(self):
        self.cached_df = None
        super().invalidate_caches()

    @property
    def df(self):
        if self.cached_df is None:
            self.cached_df = self.transform(self.dataframe)
        return self.cached_df


class ObserverdValues(ConvertedValues):
    filename = Unicode()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(self, fd):
        pass

    @property
    def phaser(self) -> CurvePhaser:
        return self.transformers['phaser']

    @property
    def resampler(self) -> CurveResampler:
        return self.transformers['resampler']

class GeneratedValues(CurveValues):
    class STATUS:
        Canceling = 3
        Invalid = 2
        Calculating = 1
        Ready = 0

    status = Int(default_value=STATUS.Invalid)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def generate(self, wait=False):
        pass

    def refresh(self, wait=False):
        """Generate if needed"""
        if self.status == self.STATUS.Invalid:
            self.generate(wait=wait)

    def invalidate(self):
        if self.status == self.STATUS.Calculating: # cancel and re-generate
            self.generate()
        else:
            self.status = self.STATUS.Invalid

    def cancel(self):
        pass



class WdGeneratedValues(GeneratedValues):
    segment_dividers_version = Int()

    def __init__(self, *args, bundle: Bundle, rv: bool, **kwargs):
        super().__init__(*args, **kwargs)
        self.calculation_semaphore = threading.Semaphore()
        self.is_rv = rv
        self.bundle = bundle
        self.parameters = ParameterSet()
        self.segment_dividers = [0.0, 0.5, 1.0]
        self.segment_data = [{'PHIN': bundle['PHIN'].val}, {'PHIN': bundle['PHIN'].val}]
        self.futures: List[Future] = []

    def generate(self, wait=False):
        self.cancel()
        bundle = self.bundle.copy()
        bundle.update(self.parameters)
        bundle['MPAGE'] = MPAGE.VELOC if self.is_rv else MPAGE.LIGHT
        running = False
        for s in range(self.segments_count()):
            b = bundle.copy()
            lo, hi = self.segment_range(s)
            b['PHSTRT'] = lo
            b['PHSTOP'] = hi
            b['PHIN'] = self.segment_data[s]['PHIN']
            f = JobScheduler.instance().schedule('lc', b)
            f.add_done_callback(lambda fut: self.on_segment_calculated(fut))
            running = True
            logging.warning(f'Future scheduled: {f}')
            self.futures.append(f)
        if running:
            self.status = self.STATUS.Calculating
            self.calculation_semaphore.acquire()
        if wait:
            self.wait()

    def wait(self, timeout=None) -> bool:
        if self.calculation_semaphore.acquire(timeout=timeout):
            self.calculation_semaphore.release()
            return True
        else: #  timeout
            return False


    def on_segment_calculated(self, fut):
        logging.warning(f'Future done: {fut}')
        for f in self.futures:
            if not f.done():
                return
        logging.warning(f'Futures all done, collecting')
        results = []
        for f in self.futures:
            result = f.result()
            df = result.get('veloc' if self.is_rv else 'light', None)
            if df is not None:
                results.append(df)

        # results = [f.result().get('veloc' if self.is_rv else 'light', None) for f in self.futures]
        # results = [r for r in results if r is not None]
        df = pd.concat(results)
        df = df[~df.duplicated([self.indep_column])]
        df.sort_values(self.indep_column)
        df.reindex()
        self.set_df(df)
        self.calculation_semaphore.release()

    def set_df(self, df):
        super().set_df(df)
        self.status = self.STATUS.Ready

    def cancel(self):
        self.status = self.STATUS.Canceling
        for f in self.futures:
            f.cancel()
        self.futures = []

    def segments_count(self) -> int:
        return len(self.segment_data)

    def segment_split_at(self, divider: float) -> int:
        seg = self.segment_at(divider)
        self.segment_split(seg, divider)
        return seg

    def segment_at(self, pos: float) -> int:
        for s in range(self.segments_count()):
            if self.segment_dividers[s+1] > pos:
                return s
        if math.isclose(pos, 1.0):
            return self.segments_count() - 1
        else:
            raise ValueError('pos should be <= 1.0')

    def segment_split(self, segment: int, divider: Optional[float] = None) -> float:
        import copy
        lo, hi = self.segment_range(segment)
        if divider is None:
            if math.isclose(lo, hi):
                divider = lo
            else:
                divider = lo + (hi - lo) / 2.
        data = copy.copy(self.segment_data[segment])
        self.segment_dividers.insert(segment+1, divider)
        self.segment_data.insert(segment+1, data)
        self.segment_dividers_version += 1
        return divider

    def segment_delete(self, segment: int, update_version=True):
        del self.segment_data[segment]
        del self.segment_dividers[max(segment, 1)]  # delete left boundary if not first
        self.segment_dividers_version += 1

    def segment_delete_empty(self):
        raise NotImplementedError()

    def segment_range(self, segment: int) -> (float, float):
        return self.segment_dividers[segment], self.segment_dividers[segment+1]

    def segment_set_range(self, segment: int, from_value: Optional[float] = None, to_value: Optional[float] = None):
        modified = False
        if from_value is not None and segment > 0 and not math.isclose(self.segment_dividers[segment], from_value):
            self.segment_dividers[segment] = from_value
            modified = True
            for s in range(segment - 1, 0, -1):
                if self.segment_dividers[s] > from_value:
                    self.segment_dividers[s] = from_value
                else:
                    break
        if to_value is not None and segment < len(self.segment_dividers) - 2 and not math.isclose(
                self.segment_dividers[segment+1], to_value):
            self.segment_dividers[segment+1] = to_value
            modified = True
            for s in range(segment + 2, len(self.segment_dividers) - 1):
                if self.segment_dividers[s] < to_value:
                    self.segment_dividers[s] = to_value
                else:
                    break
        if modified:
            self.segment_dividers_version += 1

    def segment_is_empty(self, segment: int) -> bool:
        lo, hi = self.segment_range(segment)
        return math.isclose(lo, hi)


# ############ CURVES as observed/generated pair ####################### #

class Curve(HasTraits):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen_values = GeneratedValues()
        self.obs_values = ObserverdValues()

    # def get_points_generated(self, calc_at=None, generate=True):
    #     pass
    #
    # def get_points_generated_async(self, calc_at=None):
    #     pass
    #
    # def get_generated_interpolator(self, generate=True):
    #     pass
    #
    # def get_points_observed(self):
    #     pass
    #
    # def get_points_residuals(self):
    #     pass


class WdCurve(Curve):
    wdparams = Instance(WdParamTraitCollection,
                        kw={'flags_any': ParFlag.curvedep})
    plot = Bool(default_value=True)
    fit = Bool(default_value=False)
    color = Unicode('red')

    def __init__(self, *args, bundle: Bundle = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = f'#{random.randint(0, 0xffffff):06x}44'
        if bundle is None:
            bundle = Bundle.default_binary()
        self.gen_values = WdGeneratedValues(bundle=bundle, rv=self.is_rv())

        self.read_bundle(bundle)

    def read_bundle(self, bundle: ParameterSet, set_fit=False):
        self.wdparams.read_bundle(bundle=bundle, set_fit=set_fit)

    @classmethod
    def is_rv(cls): return False


class LightCurve(WdCurve):
    @classmethod
    def is_rv(cls): return False


class VelocCurve(WdCurve):
    @classmethod
    def is_rv(cls): return True
