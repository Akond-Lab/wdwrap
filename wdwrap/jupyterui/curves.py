#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import functools
import logging
from collections import OrderedDict
from typing import Union

import numpy as np
import pandas as pd
from traitlets import HasTraits, Bool, Int, Float, Instance, validate, Unicode
from traittypes import DataFrame

from scipy.interpolate import BSpline, CubicSpline

from .wdtraits import WdParamTraitCollection
from ..bundle import Bundle
from ..param import ParFlag
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
    approx_method = Unicode(default_value='b-spline')
    approx_periodic = Bool(default_value=True)
    approx_indep_column = Unicode(default_value='ph')  # hjd
    approx_dep_columns = {'mag', 'rv1', 'rv2'}

    def __init__(self, *args, df=None, **kwargs):
        super().__init__(*args, **kwargs)
        if df is not None:
            self.dataframe = df
        self.observe(lambda change: self.approximators.cache_clear(),
                     ['approx_order', 'approx_method', 'approx_periodic', 'approx_indep_column'])

    def invalidate(self):
        self.approximators.cache_clear()
        self.df_version += 1

    @property
    def df(self):
        return self.dataframe

    def set_df(self, df):
        self.invalidate()
        self.dataframe = df

    @functools.lru_cache()
    def approximators(self):
        def nans(x):
            if np.isscalar(x):
                return np.nan
            else:
                return np.full_like(x, np.nan)
        ret = {col: nans for col in self.approx_dep_columns}
        if self.df is not None:
            for c in self.approx_dep_columns & set(self.df.columns):
                if self.approx_method == 'cubic-spline':
                    kwargs = {}
                    if self.approx_periodic:
                        kwargs['extrapolate'] = 'periodic'
                        ret[c] = CubicSpline(self.df[self.approx_indep_column], self.df[c], **kwargs)
                else:
                    logging.error(f'Unknown interpolation method "{self.approx_method}"')
        return ret

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
        self.invalidate()

    def transform(self, df):
        for trans in self.transformers.values():
            df = trans.transform(df)
        return df

    def invalidate(self):
        self.cached_df = None
        super().invalidate()

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
    pass

# ############ CURVES as observed/generated pair ####################### #

class Curve(HasTraits):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen_values = GeneratedValues()
        self.obs_values = ObserverdValues()

class WdCurve(Curve):
    wdparams = Instance(WdParamTraitCollection,
                        kw={'flags_any': ParFlag.curvedep})
    plot = Bool(default_value=True)
    fit = Bool(default_value=False)

    def __init__(self, *args, bundle: Bundle = None, **kwargs):
        super().__init__(*args, **kwargs)
        if bundle is not None:
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
