#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import pandas as pd
import numpy as np

class CurvesList(object):

    def __init__(self) -> None:
        super().__init__()

        dtypes = np.dtype(self.column_dtypes())
        self.df = pd.DataFrame(np.empty(0, dtypes))

    def _columns(self):
        raise NotImplementedError

    def columns(self, with_data=False):
        c = self._columns()
        if with_data:
            c.append(('data', object, None))
        return c

    def add(self, **kwargs):
        item = self._default_item()
        item.update(kwargs)
        try:
            size = len(kwargs['data'])
            item['size'] = size
        except (TypeError, LookupError):
            pass
        self.df.loc[len(self.df)] = item

    def column_dtypes(self):
        return [(n, t) for (n, t, _) in self.columns(with_data=True)]

    def column_names(self, with_data=False):
        return [v[0] for v in self.columns(with_data=with_data)]

    def headers_json(self):
        return [{'text': v, 'value': v} for v in self.column_names()]

    def items_json(self):
        cols = self.column_names()
        return [{c: r[c] for c in cols} for _, r in self.df.iterrows()]

    def _default_item(self):
        return {n: v for (n, _, v) in self.columns(with_data=True)}


class LcCurvesList(CurvesList):

    def _columns(self):
        return [('active', bool, True),
                ('plot', bool, True),
                ('band', str, 'V'),
                ('bin', int, 1),
                ('size', int, 0),
                ('file', str, ''),
                ]

class RvCurvesList(CurvesList):

    def _columns(self):
        return [('active', bool, True),
                ('plot', bool, True),
                ('bin', int, 1),
                ('size', int, 0),
                ('file', str, ''),
                ]
