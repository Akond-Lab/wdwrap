#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import logging
from typing import Optional, List, Mapping, Generator

from PySide2.QtCore import Signal, Property, QObject
from wdwrap.curves import WdCurve, GeneratedValues, VelocCurve, LightCurve
from wdwrap.lazylogger import logger
from wdwrap.qtgui.container import Container, PropertiesAccessContainer, ParentColumnContainer
from wdwrap.qtgui.model_containerstree import ContainersTreeModel, ColumnsPreset
from wdwrap.qtgui.signal_delayed import SignalDelayedPermanentTimer
from wdwrap.qtgui.model_wpparameter import WdParameterContainer

_logger = None
def logger():
    global _logger
    if _logger is None:
        import logging
        _logger = logging.getLogger('curves model')
    return _logger


class CurveContainer(PropertiesAccessContainer):

    def __init__(self, name, data:WdCurve, parent=None, columns_mapper=lambda col: col, read_only=True):
        super().__init__(name, data, parent, columns_mapper, read_only)
        self.get_content().observe(lambda change: self.on_plot_changed(change), ['plot'])
        self.get_content().observe(lambda change: self.on_fit_changed(change), ['fit'])

    def terminal_clean_up(self):
        from traitlets import HasTraits
        content: HasTraits = self.get_content()
        if content:
            content.unobserve_all()
        super().terminal_clean_up()

    def get_plot(self):
        return self.content.plot
    def set_plot(self, val):
        if isinstance(val, int):
            val = (val != 0)
        self.content.plot = val

    plot = Property(bool, get_plot, set_plot)
    sig_plot_changed = Signal(bool)

    def on_plot_changed(self, change):
        self.sig_plot_changed.emit(change.new)

    def get_fit(self):
        return self.content.fit
    def set_fit(self, val):
        if isinstance(val, int):
            val = (val != 0)
        self.content.fit = val

    fit = Property(bool, get_fit, set_fit)
    sig_fit_changed = Signal(bool)

    def on_fit_changed(self, change):
        self.sig_fit_changed.emit(change.new)

    def is_rv(self) -> bool:
        return self.content.is_rv()

class CurveValuesContainer(PropertiesAccessContainer):
    def __init__(self, name, data, parent=None, columns_mapper=lambda col: col, read_only=True):
        super().__init__(name, data, parent, columns_mapper, read_only)
        self.sig_curve_changed = SignalDelayedPermanentTimer('curve_change')
        self.sig_curve_invalidated = SignalDelayedPermanentTimer('curve_invalidate')

    def terminal_clean_up(self):
        self.sig_curve_changed.enable(False)
        self.sig_curve_changed.disconnect()
        self.sig_curve_changed = None
        self.sig_curve_invalidated.enable(False)
        self.sig_curve_invalidated.disconnect()
        self.sig_curve_invalidated = None
        super().terminal_clean_up()

    def get_plot(self):
        return self.parent().plot

    plot = Property(bool, get_plot)
    # sig_curve_changed = Signal(Container)
    # sig_curve_invalidated = signal(Container)

    def get_df(self):
        return self.get_content().df


class CurveObservedContainer(CurveValuesContainer):
    def __init__(self, name, data, parent=None, columns_mapper=lambda col: col, read_only=True):
        super().__init__(name, data, parent, columns_mapper, read_only)
        self.__handler_on_curve_data_change = lambda change: self.on_curve_data_change(change)
        self.get_content().observe(self.__handler_on_curve_data_change, 'df_version')
        logger().info('Curve {} created'.format(self))

    def on_curve_data_change(self, change):
        logger().info('Curve {} data changed - emitting signal'.format(self))
        self.sig_curve_changed.emit(self)

    def terminal_clean_up(self):
        logger().info(f'Curve {type(self)} (id:{id(self)}) deleting')
        self.get_content().unobserve(self.__handler_on_curve_data_change, names='df_version')
        super().terminal_clean_up()

    # def get_file(self):
    #     return 'self.content.plot'
    # def set_file(self, val):
    #     self.content.plot = val
    #
    # file = Property(str, get_file, set_file)

class CurveGeneratedContainer(CurveValuesContainer):

    def __init__(self, name, data, parent=None, columns_mapper=lambda col: col, read_only=True):
        super().__init__(name, data, parent, columns_mapper, read_only)
        data.observe(lambda change: self.on_curve_status_change(change), 'status')

    def add_children_for_private_wd_parameters(self):
        parameters = self.content.parameters
        for key, item in parameters.items():
            WdParameterContainer(key, item, parent=self)

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


class CurvesModel(ContainersTreeModel):
    def __init__(self, curves: Optional[List[WdCurve]] = None, parent=None):
        self.curves = curves
        super().__init__(parent)
        self.columns = ColumnsPreset(['name', 'value'])

    def children_iter_filter(self, child: Container, **kwargs) -> bool:
        if kwargs.get('curves', False) and not isinstance(child, CurveContainer):
            return False
        if kwargs.get('curvevaluess', False) and not isinstance(child, CurveValuesContainer):
            return False
        return super().children_iter_filter(child, **kwargs)

    def curves_iter(self) -> Generator[CurveContainer, None, None]:
        yield from self.children_iter(depth=0, curves=True)

    def build_qmodel(self):
        for n, l in enumerate(self.curves):
            name = 'RV' if l.is_rv() else 'Light'
            try:
                name += f' {n} {l.obs_values.filename}'
            except AttributeError:
                name += f' {n}'
            self._add_curve(l, name=name)
        self.sort_curves()

    def delete_curve_container(self, to_delete: CurveContainer):
        if to_delete in self.display_root.children():
            self.beginResetModel()
            # to_delete.disconnect()
            to_delete.setParent(None)
            to_delete.deleteLater()
            # del to_delete
            self.endResetModel()

    def delete_all_curve_containers(self):
        to_del = [c for c in self.curves_iter()]
        for c in to_del:
            self.delete_curve_container(c)
        self.curves = []

    def add_curve(self, curve: WdCurve, name: str = None):
        """
        Adds single curve
        """
        self.beginResetModel()

        if name is None:
            if curve.is_rv():
                name = 'New RV'
            else:
                name = 'New Light'
        self._add_curve(curve, name)
        self.curves.append(curve)
        self.sort_curves()
        self.endResetModel()

    def add_curves(self, curves: Mapping[str, WdCurve], replace: bool):
        """
        Add several curves at once

        Parameters
        ----------
        replace: delete existing curves first?
        curves: dictionary - curve name to  `WdCurve` instance
        """
        try:
            self.beginResetModel()
            if replace:
                self.delete_all_curve_containers()
            for name, c in curves.items():
                self._add_curve(c, name=name)
            self.curves += curves
            self.sort_curves()
        finally:
            self.endResetModel()

    def _add_curve(self, curve: WdCurve, name: str):
        """Adds curve on the end of list, use sort_curves to restore proper order"""
        c = CurveContainer(name, curve, self.display_root, read_only=False)
        ParentColumnContainer('plot', c)
        ParentColumnContainer('fit', c)
        g = CurveGeneratedContainer('synthetic', curve.gen_values, c)
        g.add_children_for_private_wd_parameters()
        o = CurveObservedContainer('observed', curve.obs_values, c, read_only=False)
        ParentColumnContainer('file', o, parents_column='filename')
        ParentColumnContainer('bins', o)
        ParentColumnContainer('min', o)
        ParentColumnContainer('max', o)

    def sort_curves(self,
                    comp_function=lambda curve1, curve2: -1 if curve1.is_rv() and not curve2.is_rv() else
                                                          1 if not curve1.is_rv() and curve2.is_rv() else
                                                          0):
        """Sort curves list, default comparison just puts light curves overs RV curves"""
        to_sort = self.display_root.children()
        sorted = self._merge_sort_curves(to_sort, comp_function)
        ob = QObject()
        for o in sorted:
            o.setParent(ob)
        for o in sorted:
            o.setParent(self.display_root)

    def _merge_sort_curves(self, curves_list, comp_function):
        if len(curves_list) < 2:
            return curves_list
        divide_on = len(curves_list) // 2
        l1 = self._merge_sort_curves(curves_list[:divide_on], comp_function)
        l2 = self._merge_sort_curves(curves_list[divide_on:], comp_function)
        n1 = 0
        n2 = 0
        merged = []
        while n1 < len(l1) and n2 < len(l2):
            if comp_function(l1[n1], l2[n2]) >= 0:
                merged.append(l1[n1])
                n1 += 1
            else:
                merged.append(l2[n2])
                n2 += 1
        return merged + l1[n1:] + l2[n2:]


