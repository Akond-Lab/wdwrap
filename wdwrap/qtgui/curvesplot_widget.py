#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from wdwrap.qtgui.curves_model import CurvesModel


class CurvesPlotWidget(FigureCanvas):

    def __init__(self, figsize=(14, 10)):
        self.figure = Figure(figsize=figsize)
        self.figure.tight_layout()
        # fig.subplots_adjust(left=0, bottom=0.001, right=1, top=1, wspace=None, hspace=None)
        super().__init__(self.figure)


class WdCurvesPlotWidget(CurvesPlotWidget):
    def __init__(self, model: CurvesModel):
        self.curves_model = model
        super().__init__()
        self.ax = self.figure.add_subplot()
        self.plot_curves()

    def plot_curves(self):
        pass


class LightPlotWidget(WdCurvesPlotWidget):
    def __init__(self, model: CurvesModel):
        super().__init__(model)

    def plot_curves(self):
        super().plot_curves()
        self.ax.plot([0], [0])


class RvPlotWidget(WdCurvesPlotWidget):
    def plot_curves(self):
        super().plot_curves()
        self.ax.plot([0], [0])
