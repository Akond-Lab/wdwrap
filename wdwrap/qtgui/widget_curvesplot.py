#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import logging
from collections import OrderedDict
from typing import Mapping, Any, Generator

import numpy as np
from PySide2.QtCore import Slot, Qt, QSize, QModelIndex
from PySide2.QtWidgets import QToolBar
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from wdwrap.curves import WdCurve, WdGeneratedValues, ObservedValues
from wdwrap.qtgui.model_curves import CurvesModel, CurveValuesContainer, CurveContainer
from wdwrap.qtgui.signal_delayed import SignalDelayedPermanentTimer

_logger = None
def logger():
    global _logger
    if _logger is None:
        import logging
        _logger = logging.getLogger('curvplot')
    return _logger

# constants for plotting
line_width = 1
line_alpha = 1.0
obs_points_size = 4
obs_points_alpha = 0.4
gen_points_size = 2
gen_points_alpha = 1.0
line_points = 500

class NavigationToolbar (NavigationToolbar2QT):
    toolitems = [t for t in NavigationToolbar2QT.toolitems
                 if t[0] in ('Home', 'Pan', 'Zoom', 'Save')]

class CurvesPlotWidget(FigureCanvas):

    def __init__(self, figsize=(14, 10)):
        self.figure = Figure(figsize=figsize)
        self.figure.tight_layout()
        self.logger = logging.getLogger('curvfig')
        self.curves_artists: OrderedDict[WdCurve, Mapping[str, Any]] = OrderedDict()

        # fig.subplots_adjust(left=0, bottom=0.001, right=1, top=1, wspace=None, hspace=None)
        super().__init__(self.figure)
        toolbar = NavigationToolbar(self, self)
        toolbar.setOrientation(Qt.Vertical)
        toolbar.setIconSize(QSize(15, 15))
        toolbar2 = QToolBar()
        toolbar2.setOrientation(Qt.Vertical)
        toolbar2.addAction("x")
        # toolbar2.setIconSize((10,10))

    def curves_iter(self, **kwargs) -> Generator[CurveContainer, None, None]:
        yield from []

    def plot_curves(self):
        self.curves_artists = OrderedDict()
        for curve in self.curves_iter(plot=True):
            shapes: Mapping[Artist] = self.plot_curve(curve)
            self.curves_artists[curve] = shapes


    def redraw_idle(self):
        self.draw_idle()

    def get_curve_container(self, curve: WdCurve):
        for c in self.curves_iter():
            try:
                if c.content == curve:
                    return c
            except AttributeError:
                pass
        return None

    @Slot(CurveValuesContainer)
    def on_observed_curve_changed(self, curve_values_container):
        self.logger.info(f'On observed curve change  {curve_values_container.content}: adjusting')
        try:
            self.update_observed_curve(curve_values_container)
            self.update_residuals_curve(curve_values_container)
        except KeyError:
            self.logger.info(f'Adjustment canceled curve  {curve_values_container.content} not found')

    @Slot(CurveValuesContainer)
    def on_generated_curve_changed(self, curve_values_container):
        self.logger.info(f'On generated curve change  {curve_values_container.content}: adjusting')
        try:
            self.update_generated_curve(curve_values_container)
            self.update_residuals_curve(curve_values_container)
        except KeyError:
            self.logger.info(f'Adjustment canceled curve  {curve_values_container.content} not found')

    @Slot(CurveValuesContainer)
    def on_generated_curve_invalidated(self, curve_values_container):
        curve_container: CurveContainer = curve_values_container.parent()
        if curve_container.plot:
            self.invalidate_curve(curve_values_container)
            curve: WdCurve = curve_container.content
            curve.gen_values.refresh()
            self.logger.info(f'Forced curve {curve_values_container} refresh')

    # Change: 'plot' is handled via traitletes observing
    # @Slot(CurveContainer)
    # def on_curve_plot_changed(self, curve_container: CurveContainer):
    #     curve: WdCurve = curve_container.content
    #     artists = self.curves_artists[curve_container]
    #     plot = curve_container.plot
    #     if plot and len(artists) == 0:
    #         self.plot_curve(curve_container)
    #     else:
    #         for a in artists.values():
    #             a.set_visible(plot)
    #     self.redraw_idle()

    @Slot(CurveContainer)
    def on_curve_color_changed(self, curve_container: CurveContainer):
        self.update_curve_color(curve_container)

    def update_curve_color(self, curve_container: CurveContainer):
        curve: WdCurve = curve_container.content
        if curve.is_rv():
            return
        artists = self.curves_artists[curve_container]
        for k, a in artists.items():
            try:
                if k.startswith('obs') or k.startswith('resid'):
                    a.set_color(curve.color_obs)
                else:
                    a.set_color(curve.color)
            except AttributeError:
                pass
        self.redraw_idle()

    def update_curve(self, curve_values_container: CurveValuesContainer):
        self.update_generated_curve(curve_values_container)
        self.update_observed_curve(curve_values_container)
        self.update_residuals_curve(curve_values_container)

    def update_generated_curve(self, curve_values_container: CurveValuesContainer):
        pass

    def update_observed_curve(self, curve_values_container: CurveValuesContainer):
        pass

    def update_residuals_curve(self, curve_values_container: CurveValuesContainer):
        pass

    def invalidate_curve(self, curve_values_container: CurveValuesContainer):
        pass

    def plot_curve(self, curve_container: CurveContainer):
        # curve_container.sig_plot_changed.connect(self.on_curve_plot_changed)
        if curve_container.plot:
            g: CurveValuesContainer = curve_container.findChild(CurveValuesContainer, 'synthetic')
            o: CurveValuesContainer = curve_container.findChild(CurveValuesContainer, 'observed')

            g.sig_curve_changed.connect(self.on_generated_curve_changed)
            g.sig_curve_invalidated.connect(self.on_generated_curve_invalidated)
            o.sig_curve_changed.connect(self.on_observed_curve_changed)
            curve = curve_container.content
            curve.observe(lambda change: self.update_curve_color(curve_container), ['color', 'color_obs'])
            curve.gen_values.refresh()
        return {}

    def _xy_for_generated_curve(self, generated: WdGeneratedValues, number_of_points=600):
        x = np.linspace(-0.1, 1.1, number_of_points)
        xx, yy = generated.get_combined_values(indep_var_values=x)
        return xx, yy


class WdCurvesPlotWidget(CurvesPlotWidget):
    def __init__(self, model: CurvesModel):
        self.refresh_delayed_signal = SignalDelayedPermanentTimer(connect=self.refresh_from_model)
        self.curves_model = model
        self.curves_model.rowsRemoved.connect(self._on_row_removed)
        self.curves_model.rowsInserted.connect(self._on_row_inserted)
        self.curves_model.modelReset.connect(self._on_model_reset)
        super().__init__()
        gs = self.figure.add_gridspec(3, 1)
        self.ax: Axes = self.figure.add_subplot(gs[0:2, 0])
        self.ax_resid: Axes = self.figure.add_subplot(gs[2, 0], sharex=self.ax)
        self._prepare_axis()
        self.figure.subplots_adjust(hspace=0.000)
        self.plot_curves()


    @Slot(QModelIndex, int, int)
    def _on_row_removed(self, parent_idx, first, last):
        logger().info(f'model curves removed: {first}:{last}')

    @Slot(QModelIndex, int, int)
    def _on_row_inserted(self, parent_idx, first, last):
        logger().info(f'model curves inserted: {first}:{last}')

    @Slot()
    def _on_model_reset(self):
        logger().info(f'model curves have been reset')
        self.refresh_from_model_delayed()

    def refresh_from_model_delayed(self):
        self.refresh_delayed_signal.emit(self)

    @Slot()
    def refresh_from_model(self):
        """Forgets everything, reads model and plots its curves"""
        self.clear_axies()
        self.plot_curves()

    def clear_axies(self):
        self.ax.clear()
        self.ax_resid.clear()
        self._prepare_axis()

    def curves_filter(self, curve: CurveContainer, **kwargs) -> bool:
        for_plotting = kwargs.get('plot', False)
        return curve.plot or not for_plotting  #  either always True or curve.plot if for plotting

    def curves_iter(self, **kwargs) -> Generator[CurveContainer, None, None]:
        for curve_container in self.curves_model.curves_iter():
            if self.curves_filter(curve_container, **kwargs):
                yield curve_container
        # for curve in self.curves_model.curves:
        #     if self.curves_filter(curve, **kwargs):
        #         yield curve

    def plot_curves(self):
        self.ax_resid.axhline(0.0, color='gray', lw=1)
        span_alpha = 0.1
        self.ax.axvspan(-100.0, 0.0, alpha=span_alpha, in_layout=False)
        self.ax.axvspan(1.0, 100.0, alpha=span_alpha, in_layout=False)
        self.ax_resid.axvspan(-100.0, 0.0, alpha=span_alpha, in_layout=False)
        self.ax_resid.axvspan(1.0, 100.0, alpha=span_alpha, in_layout=False)
        super().plot_curves()
        self.redraw_idle()
        # observe `plot' attribute of all (plotted and not) curves
        for curve in self.curves_iter():
            curve.content.observe(lambda change: self.refresh_from_model_delayed(), 'plot')


    def redraw_idle(self):
        self.ax.relim(visible_only=True)
        self.ax.autoscale()
        self.ax_resid.relim(visible_only=True)
        self.ax_resid.autoscale()
        self.ax.set_xlim(-0.1, 1.1, auto=False)
        super().redraw_idle()

    def _prepare_axis(self):
        pass


class LightPlotWidget(WdCurvesPlotWidget):
    def __init__(self, model: CurvesModel):
        super().__init__(model)

    def _prepare_axis(self):
        self.ax.invert_yaxis()
        self.ax_resid.invert_yaxis()

    def curves_filter(self, curve, **kwargs):
        return not curve.content.is_rv() and super().curves_filter(curve, **kwargs)

    # def connect_curves(self):
    #     for c in
    #             curve.observe(lambda change: self.on_curve_changed(change))

    def invalidate_curve(self, curve_values_container: CurveValuesContainer):
        super().invalidate_curve(curve_values_container)
        curve_container: CurveContainer = curve_values_container.parent()
        if curve_container.plot:
            try:
                artists = self.curves_artists[curve_container]
                line: Line2D = artists['gen']
                line.set_xdata([])
                line.set_ydata([])
                self.redraw_idle()
            except LookupError:
                logger().warning('Invalidating not existing curve. Remnant of removed curve still exists?')
                pass

    def update_generated_curve(self, curve_values_container: CurveValuesContainer):
        super().update_generated_curve(curve_values_container)
        curve_container: CurveContainer = curve_values_container.parent()
        if curve_container.plot:
            curve: WdCurve = curve_container.content
            generated: WdGeneratedValues = curve.gen_values
            gen_df = generated.get_values_at()
            artists = self.curves_artists[curve_container]
            line: Line2D = artists['gen']
            line.set_xdata(gen_df['ph'])
            line.set_ydata(gen_df['mag'])
            x, y = self._xy_for_generated_curve(generated, number_of_points=line_points)
            line: Line2D = artists['gen_approx']
            line.set_xdata(x)
            line.set_ydata(y['mag'])
            self.redraw_idle()

    def update_observed_curve(self, curve_values_container: CurveValuesContainer):
        super().update_observed_curve(curve_values_container)
        curve_container: CurveContainer = curve_values_container.parent()
        if curve_container.plot:
            curve: WdCurve = curve_container.content
            observed: ObservedValues = curve.obs_values
            obs_df = observed.get_values_at()
            artists = self.curves_artists[curve_container]
            line: Line2D = artists['obs']
            line.set_xdata(obs_df['ph'])
            line.set_ydata(obs_df['mag'])
            #TODO update error bars/caps
            self.redraw_idle()

    def update_residuals_curve(self, curve_values_container: CurveValuesContainer):
        super().update_residuals_curve(curve_values_container)
        curve_container: CurveContainer = curve_values_container.parent()
        if curve_container.plot:
            curve: WdCurve = curve_container.content
            observed: ObservedValues = curve.obs_values
            generated: WdGeneratedValues = curve.gen_values
            obs_df = observed.get_values_at()
            residuals = obs_df['mag'] - generated.get_values_at(obs_df['ph'])['mag']
            artists = self.curves_artists[curve_container]
            line: Line2D = artists['resid']
            line.set_xdata(obs_df['ph'])
            line.set_ydata(residuals)
            #TODO update error bars/caps
            self.redraw_idle()


    def plot_curve(self, curve_container: CurveContainer):
        ret = {}
        if curve_container.plot:
            curve: WdCurve = curve_container.content
            #  observed
            obs = curve.obs_values
            obs_df = obs.get_values_at()
            try:
                errors = obs_df['mag_e']
            except LookupError:
                errors = None
            obs_plot_result = self.ax.errorbar(
                obs_df['ph'], obs_df['mag'], yerr=errors,
                fmt='.', color=curve.color_obs, alpha=obs_points_alpha, markersize=obs_points_size,
            )
            ret['obs'], ret['obs_errcaps'], ret['obs_errbars'] = obs_plot_result
            #  synthetic
            gen = curve.gen_values
            gen_df = gen.get_values_at()
            x, y = self._xy_for_generated_curve(generated=gen, number_of_points=line_points)
            ret['gen_approx'] = self.ax.plot(
                x, y['mag'],
                '-', color=curve.color, alpha=line_alpha,  lw=line_width, zorder=4,
            )[0]
            ret['gen'] = self.ax.plot(
                gen_df['ph'], gen_df['mag'],
                '.', markersize=gen_points_size, alpha=gen_points_alpha, color=curve.color, zorder=5,
            )[0]
            #  residua
            gen_at_obs = gen.get_values_at(obs_df['ph'])
            resid_at_obs = obs_df['mag'] - gen_at_obs['mag']
            resid_plot_result = self.ax_resid.errorbar(
                obs_df['ph'], resid_at_obs, yerr=errors,
                fmt='.', color=curve.color_obs, alpha=obs_points_alpha, markersize=obs_points_size,
            )
            ret['resid'], ret['resid_errcaps'], ret['resid_errbars'] = resid_plot_result

        ret.update(super().plot_curve(curve_container))
        return ret


class RvPlotWidget(WdCurvesPlotWidget):
    def curves_filter(self, curve, **kwargs):
        return curve.content.is_rv() and super().curves_filter(curve, **kwargs)

    def invalidate_curve(self, curve_values_container: CurveValuesContainer):
        super().invalidate_curve(curve_values_container)
        curve_container: CurveContainer = curve_values_container.parent()
        if curve_container.plot:
            try:
                artists = self.curves_artists[curve_container]
                for rv in ['rv1', 'rv2']:
                    line: Line2D = artists['gen_'+rv]
                    line.set_xdata([])
                    line.set_ydata([])
                self.redraw_idle()
            except LookupError:
                pass  # no artists for container

    def update_generated_curve(self, curve_values_container: CurveValuesContainer):
        super().update_generated_curve(curve_values_container)
        curve_container: CurveContainer = curve_values_container.parent()
        if curve_container.plot:
            curve: WdCurve = curve_container.content
            generated: WdGeneratedValues = curve.gen_values
            gen_df = generated.get_values_at()
            artists = self.curves_artists[curve_container]
            x, y = self._xy_for_generated_curve(generated)
            for rv in ['rv1', 'rv2']:
                line: Line2D = artists['gen_'+rv]
                line.set_xdata(gen_df['ph'])
                line.set_ydata(gen_df[rv])
                line: Line2D = artists['gen_approx_'+rv]
                line.set_xdata(x)
                line.set_ydata(y[rv])
            self.redraw_idle()


    def update_observed_curve(self, curve_values_container: CurveValuesContainer):
        super().update_observed_curve(curve_values_container)
        curve_container: CurveContainer = curve_values_container.parent()
        if curve_container.plot:
            curve: WdCurve = curve_container.content
            observed: ObservedValues = curve.obs_values
            obs_df = observed.get_values_at()
            artists = self.curves_artists[curve_container]
            for rv in ['rv1', 'rv2']:
                line: Line2D = artists['obs_'+rv]
                line.set_xdata(obs_df['ph'])
                line.set_ydata(obs_df[rv])
            #TODO update error bars/caps
            self.redraw_idle()

    def update_residuals_curve(self, curve_values_container: CurveValuesContainer):
        super().update_residuals_curve(curve_values_container)
        curve_container: CurveContainer = curve_values_container.parent()
        if curve_container.plot:
            curve: WdCurve = curve_container.content
            observed: ObservedValues = curve.obs_values
            generated: WdGeneratedValues = curve.gen_values
            obs_df = observed.get_values_at()
            generated_at_observed = generated.get_values_at(obs_df['ph'])
            artists = self.curves_artists[curve_container]
            for rv in ['rv1', 'rv2']:
                residuals = obs_df[rv] - generated_at_observed[rv]
                line: Line2D = artists['resid_'+rv]
                line.set_xdata(obs_df['ph'])
                line.set_ydata(residuals)
            #TODO update error bars/caps
            self.redraw_idle()


    def plot_curve(self, curve_container: CurveContainer):
        ret = {}
        if curve_container.plot:
            curve: WdCurve = curve_container.content
            gen = curve.gen_values
            gen_df = gen.get_values_at()
            x_genline, y_genline = self._xy_for_generated_curve(gen)
            obs = curve.obs_values
            obs_df = obs.get_values_at()
            gen_at_obs = gen.get_values_at(obs_df['ph'])
            for rv, color in [('rv1', 'red'), ('rv2', 'blue')]:
                #  observed
                try:
                    errors = obs_df[rv+'_e']
                except LookupError:
                    errors = None
                obs_plot_result = self.ax.errorbar(
                    obs_df['ph'], obs_df[rv], yerr=errors,
                    fmt='.', color=color, alpha=0.8, markersize=4,
                )
                ret['obs_'+rv], ret['obs_errcaps_'+rv], ret['obs_errbars_'+rv] = obs_plot_result
                #  synthetic
                ret['gen_approx_'+rv] = self.ax.plot(
                    x_genline, y_genline[rv],
                    '-', color='black', alpha=0.5,
                )[0]
                ret['gen_'+rv] = self.ax.plot(
                    gen_df['ph'], gen_df[rv],
                    '.', markersize=2, color='black',
                )[0]
                #  residua
                resid_at_obs = obs_df[rv] - gen_at_obs[rv]
                resid_plot_result = self.ax_resid.errorbar(
                    obs_df['ph'], resid_at_obs, yerr=errors,
                    fmt='.', color=color, alpha=0.8, markersize=4,
                )
                ret['resid_'+rv], ret['resid_errcaps_'+rv], ret['resid_errbars_'+rv] = resid_plot_result

        ret.update(super().plot_curve(curve_container))
        return ret

    def plot_curves(self):
        self.ax.axhline(0.0, color='gray', lw=1)
        super().plot_curves()


