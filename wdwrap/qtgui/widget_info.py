#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
from threading import Lock
from typing import Optional

from PySide2.QtCore import Slot, Signal
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QGroupBox, QTableWidget, QTableWidgetItem, \
    QHBoxLayout, QToolButton

from wdwrap.jupyterui.curves import WdGeneratedValues
from wdwrap.qtgui.container import Container, ParentColumnContainer
from wdwrap.qtgui.model_curves import CurveValuesContainer, CurveGeneratedContainer
from wdwrap.qtgui.widget_pandas import WidgetPandas

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


class DataPage(DetailsPageBase):
    def __init__(self, parent=None):
        super().__init__(parent, 'data')
        layout = QVBoxLayout()
        self.pandas = WidgetPandas()
        layout.addWidget(self.pandas)
        self.setLayout(layout)

    def item_changed(self, previous_item: Container):
        super().item_changed(previous_item)
        try:
            df = self.item.get_df()
        except AttributeError:
            df = None
        self.pandas.setDataFrame(df)

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

    def _should_be_active(self, page):
        if isinstance(page, NoItemPage):
            return self.item is None
        elif isinstance(page, DataPage):
            return isinstance(self.item, CurveValuesContainer)
        elif isinstance(page, GeneratedCurvePage):
            return isinstance(self.item, CurveGeneratedContainer)
        else:
            return False

    def _selectTabs(self):
        # remove
        for i in range(self.tabs_widget.count()):
            page: DetailsPageBase = self.tabs_widget.widget(i)
            active = self._should_be_active(page)
            page.enabled = active
            self.tabs_widget.setTabVisible(i, active)

