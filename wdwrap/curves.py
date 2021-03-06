#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import functools
import math
import random
import threading
from collections import OrderedDict
from concurrent.futures import CancelledError
from typing import Optional, List

import numpy as np
import pandas as pd
from dask.distributed import Future
from scipy.interpolate import CubicSpline
from traitlets import HasTraits, Bool, Int, Float, Instance, Unicode

from wdwrap.bundle import Bundle
from wdwrap.config import cfg
from wdwrap.drivers import MPAGE
from wdwrap.jobs import JobScheduler
from wdwrap.param import ParFlag
from wdwrap.parameters import ParameterSet

"""
Module contains three families of classes:
   * `CurveTransformer` : transformers od dataframe (binning/resampling)
   * `CurveValues` : represents Dataframe with independent variable and one or more values
   * `Curve` : The curve with metadata, observed CurveValues, model-generated CurveValues
"""

_logger = None
def logger():
    global _logger
    if _logger is None:
        import logging
        _logger = logging.getLogger('curves')
    return _logger


class CurveTransformer(HasTraits):
    """Transformers one dataframe into another"""

    def __init__(self, *args, col_independent='ph', col_values=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.col_independent = col_independent
        self.col_values = ['mag'] if col_values is None else col_values

    def transform(self, df):
        return df

    def to_dict(self):
        pass

    def from_dict(self, d):
        pass


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
        except KeyError:  # no hjd column, do not overwrite 'ph'
            return df
        except TypeError:  # period is None
            mi = df[self.col_hjd].min()
            ma = df[self.col_hjd].max()
            rng = ma - mi
            ph = ((df[self.col_hjd] - mi) / rng) % 1.0
        ndf = df.copy()
        ndf['ph'] = ph
        return ndf

class CurveLightWeigher(CurveTransformer):
    """Adds/Updates `weight*`  column(s) """
    intrinsic_weight = Float(1.0)
    sigma = Float(default_value=1.0)
    noise_scaling_exponent = Float(min=0.0, max=1.0)
    light_normalization_ratio = Float(default_value=1.0)

    def __init__(self, *args, col_magnitude='mag', **kwargs):
        self.col_magnitude = col_magnitude
        super().__init__(*args, **kwargs)

    def transform(self, df):
        try:
            normalized_light = self.light_normalization_ratio * 10.0**(-0.4*df[self.col_magnitude])
            # ph = ((df[self.col_hjd] - self.hjd0) / self.period + self.delta) % 1.0
            flux_weights = 1.0 / normalized_light**(2 * self.noise_scaling_exponent)
            sigma_weights = np.full_like(flux_weights, 1e-4 / self.sigma**2)
            intrinsic_weights = np.full_like(flux_weights, self.intrinsic_weight)
            weights = flux_weights * sigma_weights * intrinsic_weights
        except KeyError:  # no mag column
            return df
        ndf = df.copy()
        # TODO: save only result weight, get rid of constant sigma_weights and intrinsic_weights (performance)
        ndf['weight'] = weights
        ndf['normalized_light'] = normalized_light
        ndf['weight_intrinsic'] = intrinsic_weights
        ndf['weight_flux'] = flux_weights
        ndf['weight_sigma'] = sigma_weights
        return ndf



class CurveResampler(CurveTransformer):
    """Resamples original dataframe into `k` bins, from min to max

    `k == 0` means: no transformation.
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
    # TODO implement linear approximator
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
            self.dataframe = self._empty_dataframe()
        self.observe(lambda change: self.get_approximators.invalidate_caches(),
                     ['approx_order', 'approx_method', 'approx_periodic', 'indep_column'])

    def _empty_dataframe(self):
        return pd.DataFrame(columns=[self.indep_column, *self.dep_columns])

    def to_dict(self):
        return {
            'approximation': {
                'method': self.approx_method,
                'periodic': self.approx_periodic,
                'order': self.approx_order,
            },
            'indep_col': self.indep_column,
            'dep_cols': list(self.dep_columns),
        }


    def from_dict(self, d):
        apx = d['approximation']
        self.approx_method = apx['method']
        self.approx_periodic = apx['periodic']
        self.approx_order = apx['order']
        self.indep_column = d['indep_col']
        self.dep_columns = set(d['dep_cols'])

    def terminal_clean_up(self):
        self.dataframe = pd.DataFrame()

    def on_data_changed(self):
        self.get_approximators.cache_clear()
        self.df_version += 1

    @property
    def df(self):
        return self.dataframe

    def set_df(self, df):
        self.dataframe = df
        self.on_data_changed()

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
                        try:
                            ret[c] = CubicSpline(self.df[self.indep_column], self.df[c], **kwargs)
                        except ValueError:  # to little data rows
                            ret[c] = np.frompyfunc(lambda x: np.nan, 1, 1)  # returns nans of shape of x
                else:
                    logger().error(f'Unknown interpolation method "{self.approx_method}"')
        return ret

    def get_combined_values(self, indep_var_values=None):
        """
        Returns dataframe of actual values supplemented with approximated values at specified points.
        Used to ensure density of plots
        Parameters
        ----------
        indep_var_values: points to add

        Returns
        -------
        (x, df) corresponding independent variable values (phase) and combined dataframe
        """
        approx_df = self.get_values_at(indep_var_values)  # calc approx values
        approx_df = approx_df.append(self.df, ignore_index=True)  # combine with existing
        approx_df.sort_values(self.indep_column, inplace=True)
        return approx_df[self.indep_column], approx_df

    #@functools.lru_cache()
    def get_values_at(self, indep_var_values=None):
        """Curve values at specified points

        Uses approximation, returns DataFrame.
        If indep_var_values is None, returns values without approximation
        If `combine_with_generated` is true, include actual points as well as approximated in the result
        """
        if indep_var_values is None:
            return self.df

        approx = self.get_approximators()
        df = pd.DataFrame(indep_var_values, columns=[self.indep_column])
        indep_var_values = indep_var_values % 1.0  # dirty treating indep_column as phase (will fail for hjd)
        for col, a in approx.items():
            df[col] = a(indep_var_values)
        return df

    @property
    def n(self):
        return len(self.df)

    def empty(self):
        return self.n == 0

    def df_to_dict(self):
        return self.dataframe.to_dict(orient='split')

    def df_from_dict(self, d):
        df = pd.DataFrame(**d)
        self.set_df(df)


class ConvertedValues(CurveValues):
    """Keeps additional 'original' dataframe which is converted somehow into
    `CurveValues.dt` """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_df = None
        self.transformers = OrderedDict()
        self.add_transformers()
        self.scan_transformers()

    def to_dict(self):
        d = super().to_dict()
        d['transformers'] = {k: v.to_dict() for k, v in self.transformers.items()}
        return d

    def from_dict(self, d):
        super().from_dict(d)
        for k, v in d['transformers'].items():
            self.transformers[k].from_dict(v)

    def add_transformers(self):
        self.transformers['phaser'] = CurvePhaser()
        self.transformers['resampler'] = CurveResampler()

    def scan_transformers(self):
        for t in self.transformers.values():
            t.observe(lambda change: self.on_transformer_changed(change))

    def on_transformer_changed(self, change):
        self.on_data_changed()

    def transform(self, df):
        for trans in self.transformers.values():
            df = trans.transform(df)
        return df

    def on_data_changed(self):
        self.cached_df = None
        super().on_data_changed()

    @property
    def df(self):
        if self.cached_df is None:
            self.cached_df = self.transform(self.dataframe)
        return self.cached_df


class ObservedValues(ConvertedValues):
    _filename = Unicode(default_value='<none>')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_transformers(self):
        super().add_transformers()
        self.transformers['weigher'] = CurveLightWeigher()

    def to_dict(self):
        d = super().to_dict()
        d['file'] = self.filename
        d['dataframe'] = self.df_to_dict()
        return d

    def from_dict(self, d):
        super().from_dict(d)
        self.df_from_dict(d['dataframe'])
        self.filename = d['file']

    def load(self, fd):
        pass

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, val):
        # for some UI simplification, val can be just filename or [filename, dataframe] pair
        df = None
        if isinstance(val, tuple):
            val, df = val
        if df is not None:
            self.set_df(df)
        self._filename = val

    @property
    def phaser(self) -> CurvePhaser:
        return self.transformers['phaser']

    @property
    def resampler(self) -> CurveResampler:
        return self.transformers['resampler']

    @property
    def weigher(self) -> CurveLightWeigher:
        return self.transformers['weigher']


class GeneratedValues(CurveValues):
    class STATUS:
        Canceling = 3
        Invalid = 2
        Calculating = 1
        Ready = 0

        @classmethod
        def to_str(cls, status):
            if status == cls.Canceling: return 'CANCELING'
            if status == cls.Invalid: return 'INVALID'
            if status == cls.Calculating: return 'CALCULATING'
            if status == cls.Ready: return 'READY'

    status = Int(default_value=STATUS.Invalid)

    def __init__(self, *args, **kwargs):
        self.gen_timeout = kwargs.get('timeout', cfg().getfloat('timeouts', 'ui-curve-calc'))
        super().__init__(*args, **kwargs)

    def generate(self, wait=False, timeout=None):
        pass

    def refresh(self, wait=False):
        """Generate if needed"""
        if self.status == self.STATUS.Invalid:
            self.generate(wait=wait, timeout=self.gen_timeout)

    def invalidate(self):
        if self.status == self.STATUS.Calculating:  # cancel and re-generate
            self.generate(timeout=self.gen_timeout)
        else:
            self.status = self.STATUS.Invalid

    def cancel(self):
        pass

    @property
    def normalization_coefficient(self):
        try:
            return self.df['Lcombined'][0] / self.df['Lnorm'][0]
        except LookupError:
            return 1.0


class WdGeneratedValues(GeneratedValues):
    segment_dividers_version = Int()

    def __init__(self, *args, bundle: Bundle, rv: bool, **kwargs):
        super().__init__(*args, **kwargs)
        self.calculation_semaphore = threading.Lock()
        self.is_rv = rv
        self.bundle = bundle
        self.parameters = ParameterSet()
        self.parameters.update_filtered(self.bundle, ParameterSet.filter_curve)

        n = cfg().getint('curves', 'default-segments')
        assert 0 < n <= 20
        self.segment_dividers = [float(v) for v in np.linspace(0, 1, n + 1)]
        self.segment_data = [{'PHIN': bundle['PHIN'].val} for _ in range(n)]  # n identical (but not the same) dicts
        self.futures: List[Future] = []
        self.__handler_bundle_value_change = lambda change: self.on_bundle_value_change(change)
        self.__handler_invalidate = lambda change: self.invalidate()
        self.bundle.observe(self.__handler_bundle_value_change, names=['val'],
                            flags_not=ParFlag.curvedep | ParFlag.curvepriv)  # observe all but curve specific
        self.parameters.observe(self.__handler_bundle_value_change, names=['val'],
                                flags_all=ParFlag.curvedep)  # observe curve specific
        self.observe(self.__handler_invalidate, 'segment_dividers_version')

    def to_dict(self):
        d = super().to_dict()
        d['wd_parameters'] = self.parameters.to_dict()
        d['segments'] = {
            'boundaries': self.segment_dividers,
            'data': self.segment_data,
        }
        # do we  save generated values ?
        d['dataframe'] = self.df_to_dict()
        return d

    def from_dict(self, d):
        super().from_dict(d)
        self.parameters.from_dict(d['wd_parameters'])
        self.segment_dividers = d['segments']['boundaries']
        self.segment_data = d['segments']['data']


    def terminal_clean_up(self):
        self.bundle.unobserve(self.__handler_bundle_value_change, names=['val'])
        self.parameters.unobserve(self.__handler_bundle_value_change, names=['val'])
        self.unobserve_all()
        self.parameters = None
        self.bundle = None
        super().terminal_clean_up()


    def generate(self, wait=False, timeout=None):
        self.cancel()
        bundle = self.bundle.clone()
        bundle.update_parameters(self.parameters)
        bundle['MPAGE'] = MPAGE.VELOC if self.is_rv else MPAGE.LIGHT
        running = False
        for s in range(self.segments_count()):
            b = bundle.clone()
            lo, hi = self.segment_range(s)
            b['PHSTRT'] = lo
            b['PHSTOP'] = hi
            b['PHIN'] = self.segment_data[s]['PHIN']
            self.calculation_semaphore.acquire(blocking=False)
            f = JobScheduler.instance().schedule('lc', b, timeout=timeout)
            f.add_done_callback(lambda fut: self.on_segment_calculated(fut))
            running = True
            logger().info(f'Future scheduled: {f}')
            self.futures.append(f)
        if running:
            self.status = self.STATUS.Calculating
        if wait:
            self.wait()

    def wait(self, timeout=None) -> bool:
        if timeout is None:
            timeout = -1
        if self.calculation_semaphore.acquire(timeout=timeout):
            self._release_semaphore()
            return True
        else:  # timeout
            return False

    def on_segment_calculated(self, fut):
        logger().info(f'Future done: {fut}')
        if fut not in self.futures:  # ignore old futures
            return
        for f in self.futures:  # ignore if there are some futures still running
            if not f.done():
                return
        futures = self.futures
        self.futures = []
        logger().info(f'Futures all done, collecting')
        results = []
        for f in futures:
            try:
                result = f.result()
                df = result.get('veloc' if self.is_rv else 'light', None)
                if df is not None:
                    results.append(df)
            except CancelledError:
                pass

        # results = [f.result().get('veloc' if self.is_rv else 'light', None) for f in self.futures]
        # results = [r for r in results if r is not None]
        try:
            df = pd.concat(results)
        except ValueError:  # nothing to concatenate
            df = self._empty_dataframe()
        df = df[~df.duplicated([self.indep_column])]
        df.sort_values(self.indep_column)
        df.reindex()
        self.set_df(df)
        self._release_semaphore()

    def set_df(self, df):
        super().set_df(df)
        self.status = self.STATUS.Ready

    def _release_semaphore(self):
        try:
            self.calculation_semaphore.release()
        except RuntimeError:
            pass

    def cancel(self):
        for f in self.futures:
            if not f.done():
                self.status = self.STATUS.Canceling
                f.cancel()
        self.futures = []
        self._release_semaphore()

    def segments_count(self) -> int:
        return len(self.segment_data)

    def segment_split_at(self, divider: float) -> int:
        seg = self.segment_at(divider)
        self.segment_split(seg, divider)
        return seg

    def segment_at(self, pos: float) -> int:
        for s in range(self.segments_count()):
            if self.segment_dividers[s + 1] > pos:
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
        self.segment_dividers.insert(segment + 1, divider)
        self.segment_data.insert(segment + 1, data)
        self.segment_dividers_version += 1
        return divider

    def segment_delete(self, segment: int, update_version=True):
        del self.segment_data[segment]
        del self.segment_dividers[max(segment, 1)]  # delete left boundary if not first
        self.segment_dividers_version += 1

    def segment_delete_empty(self):
        raise NotImplementedError()

    def segment_range(self, segment: int) -> (float, float):
        return self.segment_dividers[segment], self.segment_dividers[segment + 1]

    def segment_set_range(self, segment: int, from_value: Optional[float] = None, to_value: Optional[float] = None):
        modified = False
        if from_value is not None \
                and segment > 0 \
                and not math.isclose(self.segment_dividers[segment], from_value)\
                and 0.0 <= from_value < 1.0:
            self.segment_dividers[segment] = from_value
            modified = True
            for s in range(segment - 1, 0, -1):
                if self.segment_dividers[s] > from_value:
                    self.segment_dividers[s] = from_value
                else:
                    break
            for s in range(segment + 1, len(self.segment_dividers) - 1):
                if self.segment_dividers[s] < from_value:
                    self.segment_dividers[s] = from_value
                else:
                    break
        if to_value is not None \
                and segment < len(self.segment_dividers) - 2 \
                and not math.isclose(self.segment_dividers[segment + 1], to_value)\
                and 0.0 < to_value <= 1.0:
            self.segment_dividers[segment + 1] = to_value
            modified = True
            for s in range(segment, 0, -1):
                if self.segment_dividers[s] > to_value:
                    self.segment_dividers[s] = to_value
                else:
                    break
            for s in range(segment + 2, len(self.segment_dividers) - 1):
                if self.segment_dividers[s] < to_value:
                    self.segment_dividers[s] = to_value
                else:
                    break
        if modified:
            self.segment_dividers_version += 1

    def segment_get_data(self, segment: int, key: str):
        return self.segment_data[segment][key]

    def segment_update_data(self, segment: int, data: dict):
        newdata = self.segment_data[segment].copy()
        newdata.update(data)
        self.segment_set_data(segment, newdata)

    def segment_set_data(self, segment: int, data: dict):
        if data != self.segment_data[segment]:
            self.segment_data[segment] = data
            self.segment_dividers_version += 1

    def segment_is_empty(self, segment: int) -> bool:
        lo, hi = self.segment_range(segment)
        return math.isclose(lo, hi)

    def on_bundle_value_change(self, change):
        if not change.owner.flags & ParFlag.curvepriv:
            self.invalidate()


# ############ CURVES as observed/generated pair ####################### #

class Curve(HasTraits):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen_values = GeneratedValues()
        self.obs_values = ObservedValues()

    def to_dict(self):
        return {
            'synthetic': self.gen_values.to_dict(),
            'observed': self.obs_values.to_dict(),
        }

    def from_dict(self, d):
        self.gen_values.from_dict(d['synthetic'])
        self.obs_values.from_dict(d['observed'])


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
    # wdparams = Instance(WdParamTraitCollection,
    #                     kw={'flags_any': ParFlag.curvedep | ParFlag.curvepriv})
    plot = Bool(default_value=True)
    fit = Bool(default_value=False)
    color = Unicode('#000000')
    color_obs = Unicode('#FF0000')

    def __init__(self, *args, bundle: Bundle = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.color_obs = f'#{random.randint(0, 0xffffff):06x}'
        if bundle is None:
            bundle = Bundle.default_binary()
        self.gen_values = WdGeneratedValues(bundle=bundle, rv=self.is_rv())
        self.gen_values.observe(lambda change: self.on_generated_status_change(change), 'status')
        self.read_bundle(bundle)

    def to_dict(self):
        ret = {
            'rv': self.is_rv(),
            'plot': self.plot,
            'color': self.color,
            'color obs': self.color_obs,
            'fit': self.fit,
        }
        ret.update(super().to_dict())
        return ret

    def from_dict(self, d):
        super().from_dict(d)
        self.plot = d['plot']
        self.fit = d['fit']
        self.color = d['color']
        try:
            self.color_obs = d['color obs']
        except KeyError:
            pass


    def read_bundle(self, bundle: ParameterSet, set_fit=False):
        # self.wdparams.read_bundle(bundle=bundle, set_fit=set_fit)
        self.obs_values.phaser.period = float(bundle['PERIOD'])
        self.obs_values.phaser.hjd0 = float(bundle['HJD0'])
        bundle['PERIOD'].observe(lambda change: self.on_period_change(change))
        bundle['HJD0'].observe(lambda change: self.on_hjd0_change(change))

    def on_period_change(self, change):
        self.obs_values.phaser.period = float(change.new)

    def on_hjd0_change(self, change):
        self.obs_values.phaser.hjd0 = float(change.new)

    def on_generated_status_change(self, change):
        if change.new == self.gen_values.STATUS.Ready:
            self._propagate_normalization_coefficient()

    @classmethod
    def is_rv(cls): return False

    def _propagate_normalization_coefficient(self):
        coeff = self.gen_values.normalization_coefficient
        self.obs_values.weigher.light_normalization_ratio = coeff

class LightCurve(WdCurve):
    @classmethod
    def is_rv(cls): return False


class VelocCurve(WdCurve):
    @classmethod
    def is_rv(cls): return True
