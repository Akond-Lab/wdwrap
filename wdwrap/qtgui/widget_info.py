#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import typing
from threading import Lock
from typing import Optional

import PySide2
from PySide2.QtCore import Slot, Signal, Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QGroupBox, QTableWidget, QTableWidgetItem, \
    QHBoxLayout, QToolButton, QCheckBox, QFormLayout, QLineEdit, QPushButton, QTextEdit, QStackedLayout, QComboBox, \
    QDoubleSpinBox

from wdwrap.curves import WdGeneratedValues
from wdwrap.param import Parameter
from wdwrap.qtgui.container import Container, ParentColumnContainer
from wdwrap.qtgui.dialog_dataopen import DataOpenDialog, ObservedCurveDataOpenDialog
from wdwrap.qtgui.model_connector import TraitletsModelConnector, connected_widget, QObjectModelConnector, \
    PythonPropertyConnector, PythonMethodConnector
from wdwrap.qtgui.model_curves import CurveValuesContainer, CurveGeneratedContainer, CurveContainer
from wdwrap.qtgui.widget_colorpicker import SelectColorButton
from wdwrap.qtgui.widget_curvekindlabel import CurveKindLabel
from wdwrap.qtgui.widget_pandas import WidgetPandas
from wdwrap.qtgui.widget_wdparameter import WdParameterMinEdit, WdParameterMaxEdit, WdParameterValueEdit
from wdwrap.qtgui.wpparameter_container import WdParameterContainer

_logger = None
def logger():
    global _logger
    if _logger is None:
        import logging
        _logger = logging.getLogger('details')
    return _logger

class DetailsPageBase(QWidget):
    def __init__(self, parent, label='details'):
        super().__init__(parent)
        self.item: Optional[Container] = None
        self.enabled = False
        self.label = label

    def is_active_for_item(self, item):
        """Should return item or None if not active"""
        return None

    @Slot(Container)
    def setItem(self, item: Container):
        self.item_is_going_to_change(new_item=item)
        old = self.item
        self.item = item
        self.item_changed(previous_item=old)

    def item_is_going_to_change(self, new_item: Container):
        pass

    def item_changed(self, previous_item: Container):
        pass


class NoItemPage(DetailsPageBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = 'details'
        layout = QVBoxLayout()
        self.label1 = QLabel('Select curve to see details')
        layout.addWidget(self.label1)
        self.setLayout(layout)

class WdParameterPage(DetailsPageBase):
    class NonexpandableStackedLayout(QStackedLayout):

        def __init__(self, expand=0, parent=None):
            self.expand = expand
            super().__init__(parent)

        def expandingDirections(self):
            return self.expand

    def __init__(self, parent=None):
        super().__init__(parent, 'wd parameter')
        self.wdparameter: Optional[Parameter] = None

        self.layout = QVBoxLayout()
        self.name: QLabel = connected_widget(QLabel, PythonMethodConnector('name'), 'setText', None)
        self.name.setTextFormat(Qt.RichText)
        self.name.setStyleSheet('font-weight: bold')
        self.help_str = connected_widget(QLabel, PythonPropertyConnector('help_str'), 'setText', None)
        self.doc = connected_widget(QTextEdit, PythonPropertyConnector('doc'), 'setText', None)

        self.grp = QGroupBox('Value')
        self.grp_layout1 = QHBoxLayout()
        self.grp_layout11 = QVBoxLayout()
        # self.slayout_val = self.NonexpandableStackedLayout(expand=Qt.Horizontal)
        self.val = WdParameterValueEdit()
        self.val.setStatusTip('Current value')
        # self.slayout_val.addWidget(self.val_number)
        self.grp_layout11.addWidget(self.val)
        # self.grp_layout11.addWidget(self.val_number)
        self.fit: QCheckBox = connected_widget(QCheckBox, TraitletsModelConnector('fix'), 'setChecked', 'toggled')
        self.fit.setText('fixed')
        self.fit.setStatusTip('Whether value of this parameter is excluded from adjustment when fitting')
        self.grp_layout11.addWidget(self.fit)
        # self.grp_layout11.addStretch()
        self.grp_layout1.addLayout(self.grp_layout11)
        self.grp_layout12 = QFormLayout()
        # self.val_min: QLineEdit = connected_widget(QLineEdit,
        #                                 TraitletsModelConnector('val_min', model_to_view=str, view_to_model=float),
        #                                 'setText', 'textEdited')
        self.val_min = WdParameterMinEdit()
        self.val_max = WdParameterMaxEdit()
        self.grp_layout12.addRow('min', self.val_min)
        self.grp_layout12.addRow('max', self.val_max)
        # self.grp_layout12.addWidget(QLabel('max, min are used as boundaries in fitting'))
        self.grp_layout1.addLayout(self.grp_layout12)
        self.grp.setLayout(self.grp_layout1)

        self.layout.addWidget(self.name)
        self.layout.addWidget(self.help_str)
        self.layout.addWidget(self.grp)
        self.layout.addWidget(self.doc)

        self.setLayout(self.layout)
        pass


    # @Slot(bool)
    # def _on_fit_view_change(self, fit: bool):
    #     self.property.fix = not fit
    #
    # def _on_fit_model_change(self, fit: bool):
    #     self.property.fix = not fit
    #

    def is_active_for_item(self, item):
        """Should return item or None if not active"""
        if isinstance(item, WdParameterContainer):
            return item
        else:
            return None

    def item_changed(self, previous_item: Container):
        super().item_changed(previous_item)
        if self.enabled:
            try:
                self.wdparameter: Parameter = self.item.content
                try:
                    self.wdparameter.unobserve(self._value_handler)
                except:
                    pass
                self.name.model_connector.connect_model(self.wdparameter)
                self.help_str.model_connector.connect_model(self.wdparameter)
                self.doc.model_connector.connect_model(self.wdparameter)
                self.fit.model_connector.connect_model(self.wdparameter)
                self.val.set_parameter(self.wdparameter)
                self.val_min.set_parameter(self.wdparameter)
                self.val_max.set_parameter(self.wdparameter)
                fittable = self.wdparameter.is_fitable()
                self.fit.setEnabled(fittable)
                self.val_min.setEnabled(fittable)
                self.val_max.setEnabled(fittable)

            except AttributeError:
                pass

class DataPage(DetailsPageBase):
    def __init__(self, parent=None):
        super().__init__(parent, 'data')
        layout = QVBoxLayout()
        self.pandas = WidgetPandas()
        layout.addWidget(self.pandas)
        self.setLayout(layout)

    def is_active_for_item(self, item):
        """Should return item or None if not active"""
        if isinstance(item, CurveValuesContainer):
            return item
        else:
            return None

    def item_changed(self, previous_item: Container):
        super().item_changed(previous_item)
        try:
            df = self.item.get_df()
        except AttributeError:
            df = None
        self.pandas.setDataFrame(df)

class CurveMainPage(DetailsPageBase):
    def __init__(self, parent=None):
        super().__init__(parent, 'curve details')
        self.curve = None

        layout = QVBoxLayout()

        group_0 = QGroupBox('Curve')
        grp_layout = QHBoxLayout()
        grp_layout1 = QFormLayout()
        self.curvename = connected_widget(QLineEdit, QObjectModelConnector(), 'setText', 'textEdited')
        self.filename  = connected_widget(QLineEdit, TraitletsModelConnector('filename'), 'setText', None)
        grp_layout1.addRow('Name', self.curvename)
        grp_layout1.addRow('File', self.filename)
        grp_layout.addLayout(grp_layout1)
        grp_layout2 = QVBoxLayout()
        self.kind_label = CurveKindLabel()
        self.kind_label.setStatusTip('Change band by setting IBAND curve specific parameter in synthetic curve tree')
        self.load_button = QPushButton('Load')
        self.load_button.clicked.connect(self.load_data_dialog)
        grp_layout2.addWidget(self.kind_label)
        grp_layout2.addWidget(self.load_button)
        grp_layout.addLayout(grp_layout2)
        group_0.setLayout(grp_layout)
        layout.addWidget(group_0)

        group_1 = QGroupBox('Plot')
        grp_layout = QHBoxLayout()
        self.plot_button = QCheckBox('Visible')
        self.color_button = SelectColorButton()
        self.color_button.model_connector = TraitletsModelConnector(property_name='color')
        # self.color_button.setText('Color')
        grp_layout.addWidget(self.plot_button)
        grp_layout.addStretch()
        grp_layout.addWidget(QLabel('Color'))
        grp_layout.addWidget(self.color_button)
        group_1.setLayout(grp_layout)
        layout.addWidget(group_1)

        layout.addStretch()
        self.setLayout(layout)

        # self.table_segments.itemActivated.connect(self._on_segment_activated)
        # self.table_segments.itemChanged.connect(self._on_segment_item_changed)
        # self.add_segment_button.clicked.connect(self._on_segment_add_clicked)
        # self.del_segment_button.clicked.connect(self._on_segment_del_clicked)


    @Slot(bool)
    def load_data_dialog(self, selected: bool):
        dialog = ObservedCurveDataOpenDialog(self.item.content, parent=self)
        dialog.open()

    def is_active_for_item(self, item):
        """Should return item or None if not active"""
        if isinstance(item, CurveContainer):
            return item
        else:
            return None

    def item_changed(self, previous_item: Container):
        """when curved item for which details are displayed hve been changed"""
        super().item_changed(previous_item)
        if self.enabled:
            try:
                if isinstance(self.item, CurveContainer):
                    self.curve = self.item.content
                    self.color_button.model_connector.connect_model(self.curve)
                    self.curvename.model_connector.connect_model(self.item, self.item.setObjectName,
                                                                 self.item.objectNameChanged, self.item.objectName())
                    self.filename.model_connector.connect_model(self.curve.obs_values)
                    self.kind_label.connect_model(self.item)
                else:
                    self.curve = None
            except AttributeError:
                self.curve = None


class GeneratedCurvePage(DetailsPageBase):
    def __init__(self, parent=None):
        super().__init__(parent, 'synthetic curve')
        self.gen_curve: Optional[WdGeneratedValues] = None
        self.segments_edit_semaphore = Lock()

        layout = QVBoxLayout()
        group_segments = QGroupBox('Segments')
        layout_segments = QVBoxLayout()
        layout_segments_hdr = QHBoxLayout()
        layout_segments_hdr_labels = QVBoxLayout()
        layout_segments_hdr_labels.addWidget(QLabel('Segments are calculated in parallel'))
        layout_segments_hdr_labels.addWidget(QLabel('and may have different density (PHIN)'))
        layout_segments_hdr.addLayout(layout_segments_hdr_labels)
        layout_segments_hdr.addStretch()
        self.add_segment_button = QToolButton()
        self.add_segment_button.setText('+')
        self.del_segment_button = QToolButton()
        self.del_segment_button.setText('-')
        layout_segments_hdr.addWidget(self.add_segment_button)
        layout_segments_hdr.addWidget(self.del_segment_button)
        layout_segments.addLayout(layout_segments_hdr)
        self.table_segments = QTableWidget(1, 3)
        self.table_segments.setHorizontalHeaderLabels(['phase from', 'phase to', 'PHIN phase incr'])
        layout_segments.addWidget(self.table_segments)
        group_segments.setLayout(layout_segments)
        layout.addWidget(group_segments)
        self.setLayout(layout)

        self.table_segments.itemActivated.connect(self._on_segment_activated)
        self.table_segments.itemChanged.connect(self._on_segment_item_changed)
        self.add_segment_button.clicked.connect(self._on_segment_add_clicked)
        self.del_segment_button.clicked.connect(self._on_segment_del_clicked)

    def is_active_for_item(self, item):
        """Should return item or None if not active"""
        if isinstance(item, CurveGeneratedContainer):
            return item
        else:
            return None


    @Slot(QTableWidgetItem)
    def _on_segment_activated(self, item: QTableWidgetItem):
        self.del_segment_button.setEnabled(self.table_segments.rowCount() > 1)
        self.add_segment_button.setEnabled(self.table_segments.rowCount() <= 20)

    @Slot(QTableWidgetItem)
    def _on_segment_item_changed(self, item: QTableWidgetItem):
        """when user enters new value to segments table"""

        if self.segments_edit_semaphore.locked():  # item is being updated from code rather than by user
            return

        val = float(item.text())
        logger().info(f'Segment value changed: {val}')
        if item.column() == 0:
            self.gen_curve.segment_set_range(segment=item.row(), from_value=val)
        elif item.column() == 1:
            self.gen_curve.segment_set_range(segment=item.row(), to_value=val)
        elif item.column() == 2:
            self.gen_curve.segment_update_data(segment=item.row(), data={'PHIN': val})
        self.populate_segments()

    @Slot(bool)
    def _on_segment_add_clicked(self, selected: bool):
        """on delete segment button"""
        row = self.table_segments.currentRow()
        if row is None:
            return
        self.gen_curve.segment_split(row)
        self.populate_segments()

    @Slot(bool)
    def _on_segment_del_clicked(self, selected: bool):
        """on add new segment button"""
        row = self.table_segments.currentRow()
        if self.table_segments.rowCount() < 2 or row is None:
            return
        self.gen_curve.segment_delete(row)
        self.populate_segments()

    def item_changed(self, previous_item: Container):
        """when curved item for which details are displayed hve been changed"""
        super().item_changed(previous_item)
        if self.enabled:
            try:
                if isinstance(self.item.content, WdGeneratedValues):
                    self.gen_curve = self.item.content
                else:
                    self.gen_curve = None
            except AttributeError:
                self.gen_curve = None
            self.populate_segments()
        # try:
        #     df = self.item.get_df()
        # except AttributeError:
        #     df = None
        # self.pandas.setDataFrame(df)

    def populate_segments(self):
        if self.gen_curve is None:
            self.table_segments.setRowCount(0)
            return
        self.table_segments.setRowCount(self.gen_curve.segments_count())
        for n in range(self.gen_curve.segments_count()):
            start, stop = self.gen_curve.segment_range(n)
            phin = self.gen_curve.segment_get_data(n, 'PHIN')
            self.set_segment_text(n, 0, start)
            self.set_segment_text(n, 1, stop)
            self.set_segment_text(n, 2, phin)
        self.table_segments.resizeRowsToContents()

    def set_segment_text(self, row, col, txt):
        with self.segments_edit_semaphore:
            item = self.table_segments.item(row, col)
            if item is None:
                item = QTableWidgetItem()
                self.table_segments.setItem(row, col, item)
            item.setText(str(txt))


class InfoPanelWidget(QWidget):

    itemChanged = Signal(Container)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.item: Optional[Container] = None
        self.all_tabs = []

        layout = QVBoxLayout()
        self.tabs_widget = QTabWidget()
        self.tabs_widget.setTabBarAutoHide(True)
        self.tabs_widget.setDocumentMode(True)
        layout.addWidget(self.tabs_widget)
        self._register_tabs()
        self._selectTabs()
        self.setLayout(layout)

    def _register_tabs(self):
        self.all_tabs.append(WdParameterPage())
        self.all_tabs.append(CurveMainPage())
        self.all_tabs.append(GeneratedCurvePage())
        self.all_tabs.append(DataPage())
        self.all_tabs.append(NoItemPage())
        for tab in self.all_tabs:
            self.tabs_widget.addTab(tab, tab.label)
            self.itemChanged.connect(tab.setItem)

    @Slot(Container)
    def setItem(self, item: Container):
        if isinstance(item, ParentColumnContainer):
            item = item.parent()
        if item != self.item:
            self.item = item
            self._selectTabs()
            self.itemChanged.emit(item)

    def _should_be_active(self, page: DetailsPageBase):
        if isinstance(page, NoItemPage):
            return self.item is None
        else:
            return page.is_active_for_item(self.item) is not None


    def _selectTabs(self):
        # remove
        for i in range(self.tabs_widget.count()):
            page: DetailsPageBase = self.tabs_widget.widget(i)
            active = self._should_be_active(page)
            page.enabled = active
            self.tabs_widget.setTabVisible(i, active)

