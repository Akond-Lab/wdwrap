# #  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
# import typing
# import logging
# from _collections import OrderedDict
#
# import PySide2
# from PySide2.QtCore import QAbstractTableModel, QAbstractItemModel, Qt, QModelIndex, QObject, Property
# from wdwrap.bundle import Bundle
# from wdwrap.param import Parameter, ParFlag
#
# logging.getLogger().setLevel(logging.DEBUG)
#
# class Container(QObject):
#     def __init__(self, name, data, parent=None):
#         super().__init__(parent)
#         self.setObjectName(name)
#         self._content = data
#
#     def get_content(self):
#         return self._content
#
#     content = Property(str, get_content, constant=True)
#
#     def data(self, column: str, role: int):
#         if role == Qt.DisplayRole:
#             if column == 'name':
#                 return self.objectName()
#         return None
#
#     def set_data(self, column: str, role: int, data):
#         pass
#
#     # def editable(self, column: str):
#     #     return False
#
#     def flags(self, column: str, flags):
#         return flags
#
#     def values_choice(self, column):
#         return None, None
#
# class WdParameterContainer(Container):
#     @property
#     def wdpar(self) -> Parameter:
#         p = self.content
#         return p
#
#     def data(self, column: str, role: int):
#         # if role not in [Qt.DisplayRole, Qt.EditRole, Qt.CheckStateRole]:
#         #     return None
#         ret = super().data(column, role)
#         try:
#             if ret is None:
#                 if column == 'value' and role in [Qt.DisplayRole, Qt.EditRole]:
#                     try:
#                         ret = f'{self.wdpar}: {self.wdpar.help_val[self.wdpar.val]}'
#                     except (AttributeError, LookupError, TypeError):
#                         ret = str(self.wdpar)
#                 elif column == 'description' and role in [Qt.DisplayRole]:
#                     ret = self.wdpar.help_str
#                 elif column == 'description' and role in [Qt.ToolTipRole]:
#                     ret = self.wdpar.__doc__
#                 elif column == 'help' and role in [Qt.DisplayRole]:
#                     ret = self.wdpar.__doc__
#                 elif column == 'min' and role in [Qt.DisplayRole, Qt.EditRole]:
#                     ret = self.wdpar.min
#                 elif column == 'max' and role in [Qt.DisplayRole, Qt.EditRole]:
#                     ret = self.wdpar.max
#                 elif column == 'fit' and role in [Qt.CheckStateRole]:
#                     if self.wdpar.flags & ParFlag.fittable:
#                         ret = Qt.Unchecked if self.wdpar.fix else Qt.Checked
#                 # elif column == 'fit' and role in [Qt.DisplayRole, Qt.EditRole]:
#                 #     ret = not self.wdpar.fix
#
#         except AttributeError:
#             pass
#         return ret
#
#     def values_choice(self, column):
#         if column == 'value' and self.wdpar.help_val:
#             items = list(self.wdpar.help_val.items())
#             values = [k           for k, v in items]
#             labels = [f'{k}: {v}' for k, v in items]
#             return values, labels
#         else:
#             return None, None
#
#
#
#     def set_data(self, column: str, role: int, data):
#         if role not in [Qt.EditRole, Qt.CheckStateRole]:
#             return False
#
#         ret = False
#         try:
#             if column == 'value':
#                 self.content.from_str(data)
#                 ret = True
#             elif column == 'min':
#                 self.content.min = self.content.scan_str(data)
#                 ret = True
#             elif column == 'max':
#                 self.content.max = self.content.scan_str(data)
#                 ret = True
#             elif column == 'fit':
#                 self.content.fix = not bool(data)
#                 ret = True
#         except Exception as e:
#             raise e
#         return ret
#
#     # def editable(self, column: str):
#     #     if column in ['value', 'min', 'max', 'fit']:
#     #         return True
#     #     else:
#     #         return False
#
#     def flags(self, column: str, flags):
#         if column in ['value']:
#             if self.wdpar.flags & ParFlag.controlling:
#                 flags &= ~Qt.ItemIsEnabled
#             else:
#                 flags |= Qt.ItemIsEditable
#         elif column in ['min', 'max']:
#             if self.wdpar.flags & ParFlag.fittable:
#                 flags |= Qt.ItemIsEditable
#         elif column in ['fit']:
#             if self.wdpar.flags & ParFlag.fittable:
#                 flags |= Qt.ItemIsUserCheckable
#         return flags
#
#
# class ColumnsPreset(object):
#
#     def __init__(self, columns: list) -> None:
#         self.enabled = [True] * len(columns)
#         self.idx_to_name = columns
#         self.name_to_idx = OrderedDict([(v, k) for k, v in enumerate(self.idx_to_name)])
#         self.enabled_to_idx = []
#         self.idx_to_enabled = []
#         self.update_enabled_idx()
#
#     def update_enabled_idx(self):
#         self.enabled_to_idx = [idx for idx in range(len(self.idx_to_name)) if self.enabled[idx]]
#         self.idx_to_enabled = [self.enabled_to_idx.index(idx) if self.enabled[idx] else None
#                                for idx in range(len(self.idx_to_name))]
#
#     def enable_column(self, name, enable=True):
#         idx = self.name_to_idx[name]
#         if self.enabled[idx] != enable:
#             self.enabled[idx] = enable
#             self.update_enabled_idx()
#
#     def column_name_to_number(self, name):
#         """Returns enabled column number for given name"""
#         idx = self.name_to_idx[name]
#         return self.idx_to_enabled[idx]
#
#     def column_number_to_name(self, no):
#         """Returns name for given enabled column number"""
#         idx = self.enabled_to_idx[no]
#         return self.idx_to_name[idx]
#
#
#     def __len__(self):
#         return len(self.enabled_to_idx)
#
#
# class BundleModel(QAbstractItemModel):
#     def __init__(self, bundle: Bundle = None, parent=None):
#         self.bundle = bundle
#         super().__init__(parent)
#         self.qmodel = Container('root', self)
#         self.bundle_qmodel = Container('bundle', self.bundle, self.qmodel)
#         self.build_qmodel()
#         self.columns = ColumnsPreset(['name', 'value', 'fit', 'min', 'max', 'description'])
#         # self.columns = ColumnsPreset(['name', 'value'])
#
#     def build_qmodel(self):
#         for n, l in enumerate(self.bundle.lines):
#             line = Container(f'Line {n}', l, self.bundle_qmodel)
#             for key, item in l.items():
#                 WdParameterContainer(key, item, line)
#         # d1 = Container('dupa1', None, self.bundle_qmodel)
#         # d2 = Container('dupa2', None, d1)
#         # d3 = Container('dupa3', None, d2)
#
#     # overridden
#
#     def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
#         idx = QModelIndex()
#         if not parent.isValid(): #  Top level
#             try:
#                 idx = self.createIndex(row, column, self.bundle_qmodel.children()[row])
#             except IndexError:
#                 pass
#         else:
#             try:
#                 parent_container = parent.internalPointer()
#                 children = parent_container.children()
#                 child = children[row]
#                 idx = self.createIndex(row, column, child)
#             except IndexError:
#                 return QModelIndex()
#         logging.debug(f'Index ({row},{column}) of {parent} is {idx}')
#         return idx
#
#     def parent(self, index) -> PySide2.QtCore.QObject:
#         if not index.isValid():
#             return QModelIndex()
#
#         obj: Container = index.internalPointer()
#         parent: Container = obj.parent()
#         if parent.objectName() == 'bundle':  # top
#             return QModelIndex()
#         row = 0
#         try:
#             row = parent.parent().children().index(self)
#         except (AttributeError, ValueError) as e:  # parent is None or child not found
#             # raise e
#             pass
#         parent_idx = self.createIndex(row, 0, parent)
#         logging.debug(f'Parent ({parent_idx.row()},{parent_idx.column()}) of {index} is {parent_idx}')
#         return parent_idx
#
#     def rowCount(self, parent: PySide2.QtCore.QModelIndex = ...) -> int:
#         if not parent.isValid():
#             container: Container = self.bundle_qmodel
#         else:
#             container: Container = parent.internalPointer()
#         count = len(container.children())
#         return count
#
#     def columnCount(self, parent: PySide2.QtCore.QModelIndex = ...) -> int:
#         return len(self.columns)
#
#     def data(self, index: PySide2.QtCore.QModelIndex, role: int = ...) -> typing.Any:
#         if not index.isValid():
#             return None
#         container, colname = self.item_and_column(index)
#         data = container.data(colname, role)
#         return data
#
#     def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
#         container, colname = self.item_and_column(index)
#         change = container.set_data(colname, role, value)
#         if change:
#             self.dataChanged.emit(index, index)
#
#     def flags(self, index: PySide2.QtCore.QModelIndex) -> PySide2.QtCore.Qt.ItemFlags:
#         container, colname = self.item_and_column(index)
#         f = super().flags(index)
#         f = container.flags(colname, f)
#         return f
#
#     def headerData(self, section: int, orientation: PySide2.QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
#         if role != Qt.DisplayRole:
#             return None
#         if orientation == Qt.Horizontal:
#             return self.columns.column_number_to_name(section)
#         else:
#             return None
#
#
#
#     #  convenience methods
#
#     def item_and_column(self, index: QModelIndex) -> (Container, str):
#         """Returns pair (container, column_name)"""
#         if not index.isValid():
#             return None, None
#         container: Container = index.internalPointer()
#         col_name = self.columns.column_number_to_name(index.column())
#         return container, col_name
#
#
#
#
#
#
#
#
#
#
#
