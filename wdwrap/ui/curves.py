#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

from collections import OrderedDict
import numpy as np
import pandas as pd
from traitlets import HasTraits, Bool, Int, Float, Instance
from traittypes import DataFrame

from .wdtraits import WdParamTraitCollection
from ..bundle import Bundle
from ..param import ParFlag

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
    k = Int(min=0)
    vmin = Float(allow_none=True)
    vmax = Float(allow_none=True)

    def __init__(self, *args, k=0, vmin=0.0, vmax=1.0, col_independent='ph', col_values=None, **kwargs):
        super().__init__(*args, col_independent=col_independent, col_values=col_values,
                         k=k, vmin=vmin, vmax=vmax, **kwargs)

    def transform(self, df):
        if self.k > 0:
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

#####################################################

class CurveValues(HasTraits):
    df = DataFrame()
    plot = Bool()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def n(self):
        return len(self.df)


class ConvertedValues(CurveValues):
    """Keeps additional 'original' dataframe which is converted somehow into
    `CurveValues.dt` """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_df = None
        self.transformers = OrderedDict([
            ('phaser', CurvePhaser()),
            ('resampler', CurveResampler())
        ])

    def transform(self):
        df = self.original_df
        for trans in self.transformers.values():
            df = trans.transform(df)
        self.df = df

    @property
    def orgN(self):
        return len(self.original_df)

class ObserverdValues(ConvertedValues):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = None

    def load(self, fd):
        pass

class GeneratedValues(CurveValues):
    pass

#####################################################

class Curve(HasTraits):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen_values = GeneratedValues()
        self.obs_values = ObserverdValues()

class WdCurve(Curve):
    wdparams = Instance(WdParamTraitCollection,
                        kw={'flags_any': ParFlag.curvedep})

    def __init__(self, *args, bundle: Bundle = None, **kwargs):
        super().__init__(*args, **kwargs)
        if bundle is not None:
            self.init_from_bundle(bundle)

    def init_from_bundle(self, bundle):
        self.wdparams



class LightCurve(WdCurve):
    pass

class VelocCurve(WdCurve):
    pass
