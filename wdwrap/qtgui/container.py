#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

from PySide2.QtCore import QObject, Property, Qt


class Container(QObject):
    def __init__(self, name, data, parent=None):
        super().__init__(parent)
        self.setObjectName(name)
        self._content = data

    def get_content(self):
        return self._content

    content = Property(str, get_content, constant=True)

    def data(self, column: str, role: int):
        if role == Qt.DisplayRole:
            if column == 'name':
                return self.objectName()
        return None

    def set_data(self, column: str, role: int, data):
        pass

    # def editable(self, column: str):
    #     return False

    def flags(self, column: str, flags):
        return flags

    def values_choice(self, column):
        return None, None