#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import logging
from typing import Optional, List

from PySide2.QtCore import Signal, Property
from wdwrap.bundle import Bundle
from wdwrap.jupyterui.curves import WdCurve, GeneratedValues
from wdwrap.lazylogger import logger
from wdwrap.qtgui.container import Container, PropertiesAccessContainer, ParentColumnContainer
from wdwrap.qtgui.containerstree_model import ContainesTreeModel, ColumnsPreset
from wdwrap.qtgui.wpparameter_container import WdParameterContainer



class CurveContainer(PropertiesAccessContainer):

    def __init__(self, name, data:WdCurve, parent=None, columns_mapper=lambda col: col, read_only=True):
        super().__init__(name, data, parent, columns_mapper, read_only)
        data.observe(lambda change: self.on_plot_changed(change), ['plot'])
        data.observe(lambda change: self.on_fit_changed(change), ['fit'])

    def get_plot(self):
        return self.content.plot
    def set_plot(self, val):
        self.content.plot = val

    plot = Property(bool, get_plot, set_plot)
    sig_plot_changed = Signal(bool)

    def on_plot_changed(self, change):
        self.sig_plot_changed.emit(change.new)

    def get_fit(self):
        return self.content.fit
    def set_fit(self, val):
        self.content.fit = val

    fit = Property(bool, get_plot, set_plot)
    sig_fit_changed = Signal(bool)

    def on_fit_changed(self, change):
        self.sig_fit_changed.emit(change.new)

class CurveValuesContainer(PropertiesAccessContainer):
    def get_plot(self):
        return self.parent().plot

    plot = Property(bool, get_plot)
    sig_curve_changed = Signal(Container)
    sig_curve_invalidated = Signal(Container)


class CurveObservedContainer(CurveValuesContainer):
    pass

class CurveGeneratedContainer(CurveValuesContainer):

    def __init__(self, name, data, parent=None):
        super().__init__(name, data, parent)
        data.observe(lambda change: self.on_curve_status_change(change), 'status')

    def on_curve_status_change(self, change):
        logger().info('Curve {} status {} -> {}'.format(
            self,
            GeneratedValues.STATUS.to_str(change.old),
            GeneratedValues.STATUS.to_str(change.new),
        ))
        if change.new == GeneratedValues.STATUS.Ready:
            logging.info(f'Curve {self.content} ready - emitting signal')
            self.sig_curve_changed.emit(self)
        elif change.new == GeneratedValues.STATUS.Invalid:
            logging.info(f'Curve {self.content} invalid - emitting signal')
            self.sig_curve_invalidated.emit(self)


class CurvesModel(ContainesTreeModel):
    def __init__(self, curves: Optional[List[WdCurve]] = None, parent=None):
        self.curves = curves
        super().__init__(parent)
        self.columns = ColumnsPreset(['name', 'data'])

    def children_iter_filter(self, child: Container, **kwargs) -> bool:
        if kwargs.get('curves', False) and not isinstance(child, CurveContainer):
            return False
        if kwargs.get('curvevaluess', False) and not isinstance(child, CurveValuesContainer):
            return False
        return super().children_iter_filter(child, **kwargs)

    def curves_iter(self):
        yield from self.children_iter(depth=0, curves=True)

    def build_qmodel(self):
        for n, l in enumerate(self.curves):
            name = 'RV' if l.is_rv() else 'Light'
            try:
                name += f' {n} {l.obs_values.filename}'
            except AttributeError:
                name += f' {n}'
            c = CurveContainer(name, l, self.display_root)
            ParentColumnContainer('plot', c)
            ParentColumnContainer('fit', c)
            CurveGeneratedContainer('generated', l.gen_values, c)
            o = CurveObservedContainer('observed', l.obs_values, c)
            ParentColumnContainer('bins', o)
            ParentColumnContainer('min', o)
            ParentColumnContainer('max', o)