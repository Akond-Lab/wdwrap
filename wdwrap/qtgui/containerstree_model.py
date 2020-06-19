#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

import logging
import typing
from abc import abstractmethod
from collections import OrderedDict

import PySide2
from PySide2.QtCore import QModelIndex, Qt, QAbstractItemModel
from wdwrap.qtgui.container import Container


class ContainesTreeModel(QAbstractItemModel):
    """Base class for Tree models"""

    def __init__(self, parent):
        super(ContainesTreeModel, self).__init__(parent)
        self.root = Container('root', self)
        self.display_root = self.root
        self.columns = ColumnsPreset()
        self.build_qmodel()

    @abstractmethod
    def build_qmodel(self):
        pass

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        idx = QModelIndex()
        if not parent.isValid():  # Top level
            try:
                idx = self.createIndex(row, column, self.display_root.children()[row])
            except IndexError:
                pass
        else:
            try:
                parent_container = parent.internalPointer()
                children = parent_container.children()
                child = children[row]
                idx = self.createIndex(row, column, child)
            except IndexError:
                return QModelIndex()
        logging.debug(f'Index ({row},{column}) of {parent} is {idx}')
        return idx

    def parent(self, index) -> PySide2.QtCore.QObject: # noqa
        if not index.isValid():
            return QModelIndex()

        obj: Container = index.internalPointer()
        parent: Container = obj.parent()
        if parent == self.display_root:  # top
            return QModelIndex()
        row = 0
        try:
            row = parent.parent().children().index(self)
        except (AttributeError, ValueError):  # parent is None or child not found
            pass
        parent_idx = self.createIndex(row, 0, parent)
        logging.debug(f'Parent ({parent_idx.row()},{parent_idx.column()}) of {index} is {parent_idx}')
        return parent_idx

    def rowCount(self, parent: PySide2.QtCore.QModelIndex = ...) -> int:
        if not parent.isValid():
            container: Container = self.display_root
        else:
            # noinspection PyTypeChecker
            container: Container = parent.internalPointer()
        count = len(container.children())
        return count

    def columnCount(self, parent: PySide2.QtCore.QModelIndex = ...) -> int:
        return len(self.columns)

    def data(self, index: PySide2.QtCore.QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None
        container, colname = self.item_and_column(index)
        data = container.data(colname, role)
        return data

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        container, colname = self.item_and_column(index)
        changed = container.set_data(colname, role, value)
        if changed:
            self.dataChanged.emit(index, index)
        return changed

    def flags(self, index: PySide2.QtCore.QModelIndex) -> PySide2.QtCore.Qt.ItemFlags:
        container, colname = self.item_and_column(index)
        f = super().flags(index)
        f = container.flags(colname, f)
        return f

    def headerData(self, section: int, orientation: PySide2.QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.columns.column_number_to_name(section)
        else:
            return None

    #  convenience methods

    def item_and_column(self, index: QModelIndex) -> (Container, str):
        """Returns pair (container, column_name)"""
        if not index.isValid():
            return None, None
        container: Container = index.internalPointer()
        col_name = self.columns.column_number_to_name(index.column())
        return container, col_name


class ColumnsPreset(object):

    def __init__(self, columns=None) -> None:
        if columns is None:
            columns = ['name']
        self.enabled = [True] * len(columns)
        self.idx_to_name = columns
        self.name_to_idx = OrderedDict([(v, k) for k, v in enumerate(self.idx_to_name)])
        self.enabled_to_idx = []
        self.idx_to_enabled = []
        self.update_enabled_idx()

    def update_enabled_idx(self):
        self.enabled_to_idx = [idx for idx in range(len(self.idx_to_name)) if self.enabled[idx]]
        self.idx_to_enabled = [self.enabled_to_idx.index(idx) if self.enabled[idx] else None
                               for idx in range(len(self.idx_to_name))]

    def enable_column(self, name, enable=True):
        idx = self.name_to_idx[name]
        if self.enabled[idx] != enable:
            self.enabled[idx] = enable
            self.update_enabled_idx()

    def column_name_to_number(self, name):
        """Returns enabled column number for given name"""
        idx = self.name_to_idx[name]
        return self.idx_to_enabled[idx]

    def column_number_to_name(self, no):
        """Returns name for given enabled column number"""
        idx = self.enabled_to_idx[no]
        return self.idx_to_name[idx]

    def __len__(self):
        return len(self.enabled_to_idx)
