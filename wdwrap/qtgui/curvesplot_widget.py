#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import logging
from collections import OrderedDict
from typing import Mapping

import numpy as np
from PySide2.QtCore import Slot, Qt, QSize
from PySide2.QtWidgets import QToolBar
from matplotlib.artist import Artist
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from wdwrap.jupyterui.curves import WdCurve, WdGeneratedValues
from wdwrap.qtgui.curves_model import CurvesModel, CurveValuesContainer, CurveContainer

class NavigationToolbar (NavigationToolbar2QT):
    toolitems = [t for t in NavigationToolbar2QT.toolitems
                 if t[0] in ('Home', 'Pan', 'Zoom', 'Save')]

class CurvesPlotWidget(FigureCanvas):

    def __init__(self, figsize=(14, 10)):
        self.figure = Figure(figsize=figsize)
        self.figure.tight_layout()
        self.logger = logging.getLogger('curvfig')
        self.curves_artists: OrderedDict[WdCurve, Mapping[str, Artist]] = OrderedDict()

        # fig.subplots_adjust(left=0, bottom=0.001, right=1, top=1, wspace=None, hspace=None)
        super().__init__(self.figure)
        toolbar = NavigationToolbar(self, self)
        toolbar.setOrientation(Qt.Vertical)
        toolbar.setIconSize(QSize(15, 15))
        toolbar2 = QToolBar()
        toolbar2.setOrientation(Qt.Vertical)
        toolbar2.addAction("x")
        # toolbar2.setIconSize((10,10))

    def curves_iter(self, **kwargs):
        yield from []

    def plot_curves(self):
        self.curves_artists = OrderedDict()
        for curve in self.curves_iter(plot=True):
            shapes: Mapping[Artist] = self.plot_curve(curve)
            self.curves_artists[curve] = shapes

    @Slot(CurveValuesContainer)
    def on_curve_changed(self, curve_values_container):
        self.logger.info(f'On curve change  {curve_values_container.content}: adjusting')
        self.update_curve(curve_values_container)

    def update_curve(self, curve_values_container: CurveValuesContainer):
        pass

    def plot_curve(self, curve_container: CurveContainer):

        if curve_container.plot:
            g: CurveValuesContainer = curve_container.findChild(CurveValuesContainer, 'generated')
            o: CurveValuesContainer = curve_container.findChild(CurveValuesContainer, 'observed')

            g.sig_curve_changed.connect(self.on_curve_changed)
            o.sig_curve_changed.connect(self.on_curve_changed)
            curve = curve_container.content
            curve.gen_values.refresh()
        return {}

class WdCurvesPlotWidget(CurvesPlotWidget):
    def __init__(self, model: CurvesModel):
        self.curves_model = model
        super().__init__()
        gs = self.figure.add_gridspec(3, 1)
        self.ax = self.figure.add_subplot(gs[0:2, 0])
        self.ax.invert_yaxis()
        self.ax_resid = self.figure.add_subplot(gs[2, 0], sharex=self.ax)
        self.ax_resid.invert_yaxis()
        self.figure.subplots_adjust(hspace=0.000)
        self.plot_curves()


    def curves_filter(self, curve: WdCurve, **kwargs) -> bool:
        for_plotting = kwargs.get('plot', False)
        return curve.plot or not for_plotting

    def curves_iter(self, **kwargs):
        for curve_container in self.curves_model.curves_iter():
            if self.curves_filter(curve_container, **kwargs):
                yield curve_container
        # for curve in self.curves_model.curves:
        #     if self.curves_filter(curve, **kwargs):
        #         yield curve

class LightPlotWidget(WdCurvesPlotWidget):
    def __init__(self, model: CurvesModel):
        super().__init__(model)

    def curves_filter(self, curve, **kwargs):
        return not curve.content.is_rv() and super().curves_filter(curve, **kwargs)

    # def connect_curves(self):
    #     for c in
    #             curve.observe(lambda change: self.on_curve_changed(change))

    def update_curve(self, curve_values_container: CurveValuesContainer):
        super().update_curve(curve_values_container)
        curve_container: CurveContainer = curve_values_container.parent()
        if curve_container.plot:
            curve: WdCurve = curve_container.content
            generated: WdGeneratedValues = curve.gen_values
            gen_df = generated.get_values_at()
            artists = self.curves_artists[curve_container]
            line: Line2D = artists['gen']
            line.set_xdata(gen_df['ph'])
            line.set_ydata(gen_df['mag'])
            x = np.linspace(-0.1, 1.1, 600)
            y = generated.get_values_at(x % 1.0)['mag']
            line: Line2D = artists['gen_approx']
            line.set_xdata(x)
            line.set_ydata(y)

            self.ax.relim()
            self.ax.autoscale()

            self.draw_idle()

    def plot_curve(self, curve_container: CurveContainer):
        ret = {}
        if curve_container.plot:
            curve: WdCurve = curve_container.content
            gen = curve.gen_values
            # gen.refresh(wait=True)  # TODO: Temporary - delete later
            gen_df = gen.get_values_at()
            ret['gen_approx'] = self.ax.plot(
                gen_df['ph'], gen_df['mag'],
                '-', color=curve.color, alpha=0.4,
            )[0]
            ret['gen'] = self.ax.plot(
                gen_df['ph'], gen_df['mag'],
                '.', markersize=2, color=curve.color,
            )[0]
        ret.update(super().plot_curve(curve_container))
        return ret


class RvPlotWidget(WdCurvesPlotWidget):
    def curves_filter(self, curve, **kwargs):
        return curve.content.is_rv() and super().curves_filter(curve, **kwargs)
