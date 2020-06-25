#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
from collections import OrderedDict
from typing import Mapping

from PySide2.QtCore import Slot
from matplotlib.artist import Artist
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from wdwrap.jupyterui.curves import WdCurve
from wdwrap.qtgui.curves_model import CurvesModel, CurveValuesContainer


class CurvesPlotWidget(FigureCanvas):

    def __init__(self, figsize=(14, 10)):
        self.figure = Figure(figsize=figsize)
        self.figure.tight_layout()
        # fig.subplots_adjust(left=0, bottom=0.001, right=1, top=1, wspace=None, hspace=None)
        super().__init__(self.figure)

    def curves_iter(self, **kwargs):
        yield from []

    def plot_curves(self):
        self.curves_artists = OrderedDict()
        for curve in self.curves_model.children_iter(plot=True):
            shapes: Mapping[Artist] = self.plot_curve(curve)
            self.curves_artists[curve] = shapes

    def plot_curve(self, curve_container: CurveValuesContainer):
        # TODO: Implement plotting curve here or in subclass
        return []

class WdCurvesPlotWidget(CurvesPlotWidget):
    def __init__(self, model: CurvesModel):
        self.curves_model = model
        self.curves_artists: OrderedDict[WdCurve, Mapping[Artist]] = OrderedDict()
        super().__init__()
        self.ax = self.figure.add_subplot()
        self.plot_curves()


    def curves_filter(self, curve: WdCurve, **kwargs) -> bool:
        for_plotting = kwargs.get('plot', False)
        return curve.plot or not for_plotting

    def curves_iter(self, **kwargs):
        for curve in self.curves_model.curves:
            if self.curves_filter(**kwargs):
                yield curve

class LightPlotWidget(WdCurvesPlotWidget):
    def __init__(self, model: CurvesModel):
        super().__init__(model)

    def curves_filter(self, curve, **kwargs):
        return not curve.is_rv() and super().curves_filter(curve, **kwargs)

    # def connect_curves(self):
    #     for c in
    #             curve.observe(lambda change: self.on_curve_changed(change))

    @Slot()
    def on_curve_changed(self, change):
        pass




class RvPlotWidget(WdCurvesPlotWidget):
    def curves_filter(self, curve, **kwargs):
        return curve.is_rv() and super().curves_filter(curve, **kwargs)
