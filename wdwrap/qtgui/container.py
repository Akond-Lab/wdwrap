#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

from PySide2.QtCore import QObject, Property, Signal
from PySide2.QtCore import Qt


class Container(QObject):
    def __init__(self, name, data, parent=None):
        super().__init__(parent)
        self.setObjectName(name)
        self._content = data

    def get_content(self):
        return self._content

    def _get_content_property(self):
        return self.get_content()

    content = Property(str, _get_content_property, constant=True)

    def data(self, column: str, role: int):
        if role in [Qt.DisplayRole, Qt.EditRole]:
            if column == 'name':
                return self.objectName()
        return None

    def set_data(self, column: str, role: int, data):
        return False

    # def editable(self, column: str):
    #     return False

    def flags(self, column: str, flags):
        return flags

    def values_choice(self, column):
        return None, None

class PropertiesAccessContainer(Container):
    """Access data of content properties treated as columns

        Routes column `ParentPropertyContainer.data_column`
        to parent's content attribute `ParentPropertyContainer.parents_attr`
    """

    def __init__(self, name, data, parent=None, columns_mapper=lambda col: col, read_only=True):
        super().__init__(name, data=data, parent=parent)
        self.read_only = read_only
        self.mapper = columns_mapper

    def col_read_only(self, column):
        return self.read_only

    def roles(self, column):
        try:
            prop_name = self.mapper(column)
            v = getattr(self.content, prop_name)
        except (LookupError, AttributeError):
            return []
        if isinstance(v, bool):
            if self.col_read_only(column):
                return [Qt.CheckStateRole]  # 10
            else:
                return [Qt.CheckStateRole, Qt.EditRole]  # 10 2
        else:
            if self.col_read_only(column):
                return [Qt.DisplayRole]  # 0
            else:
                return [Qt.DisplayRole, Qt.EditRole]  # 0 2

    def data(self, column: str, role: int):
        ret = None
        if role in self.roles(column):
            try:
                prop_name = self.mapper(column)
                ret = getattr(self.content, prop_name)
                if isinstance(ret, bool):
                    ret = Qt.Checked if ret else Qt.Unchecked
            except (LookupError, AttributeError):
                pass
        if ret is None:
            ret = super().data(column=column, role=role)
        return ret

    def set_data(self, column: str, role: int, data):
        changed = False
        if role in self.roles(column):
            try:
                prop_name = self.mapper(column)
                old = getattr(self.content, prop_name)
                if isinstance(old, bool):
                    data = not data == Qt.Unchecked
                if data != old:
                    setattr(self.content, prop_name, data)
                    changed = True
            except (LookupError, AttributeError):
                pass
        return changed

    def flags(self, column: str, flags):
        if not self.col_read_only(column):
            v = None
            try:
                prop_name = self.mapper(column)
                v = getattr(self.content, prop_name)
            except (LookupError, AttributeError):
                pass
            if isinstance(v, bool):
                flags |= Qt.ItemIsUserCheckable
            elif v is not None:
                flags |= Qt.ItemIsEditable
        return flags


class ParentColumnContainer(Container):
    """Draws data from parent Container column

        Redirects column `ParentColumnContainer.data_column`
        to parent's `ParentColumnContainer.parents_column`
    """

    def __init__(self, name, parent=None, parents_column=None, data_column='data'):
        super().__init__(name, data=None, parent=parent)
        if parents_column is None:
            parents_column = name
        self.parents_column = parents_column
        self.data_column = data_column

    def get_content(self):
        return self.parent().get_content()

    def data(self, column: str, role: int):
        if column == self.data_column:  # ask parent
            return self.parent().data(column=self.parents_column, role=role)
        else:
            return super().data(column=column, role=role)

    def set_data(self, column: str, role: int, data):
        if column == self.data_column:  # ask parent
            return self.parent().set_data(column=self.parents_column, role=role, data=data)
        else:
            return super().set_data(column=column, role=role, data=data)

    def flags(self, column: str, flags):
        if column == self.data_column:  # ask parent
            return self.parent().flags(column=self.parents_column, flags=flags)
        else:
            return super().flags(column=column, flags=flags)

    def values_choice(self, column):
        if column == self.data_column:  # ask parent
            return self.parent().values_choice(column=self.parents_column)
        else:
            return super().values_choice(column=column)
