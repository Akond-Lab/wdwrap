#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

import numpy as np
from traitlets import HasTraits, Bool, Int, Float
from traittypes import DataFrame

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

    def transform(self, dt):
        return dt

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

    def transform(self, dt):
        if self.k > 0:
            mi = dt[self.col_independent].min() if self.vmin is None else self.vmin
            ma = dt[self.col_independent].max() if self.vmax is None else self.vmax
            binwidth = (ma - mi) / self.k
            ind = np.linspace(mi, ma, self.k)
            ind += binwidth / 2  # put independent values in the center of bins
        else:
            return super().transform(dt)


class CurveValues(HasTraits):
    dt = DataFrame()
    plot = Bool()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def n(self):
        return len(self.dt)


class ConvertedValues(CurveValues):
    """Keeps additional 'original' dataframe which is converted somehow into
    `CurveValues.dt` """


class Curve(HasTraits):
    pass
