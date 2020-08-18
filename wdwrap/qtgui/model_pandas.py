#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

import typing

import PySide2
from PySide2.QtCore import QAbstractTableModel, Qt


class PandasDataFrameModel(QAbstractTableModel):
    def __init__(self, df, parent: typing.Optional[PySide2.QtCore.QObject] = None):
        super().__init__(parent)
        self.df = df

    def set_df(self, df):
        self.beginResetModel()
        self.df = df
        self.endResetModel()

    def set_columns(self, cols):
        # extend to size of dataframe
        cols.extend([''] * (self.columnCount() - len(cols)))  # enlarge list to at lest n elemenets
        # shrink to size of dataframe
        cols = cols[ : self.columnCount()]
        self.df.columns = cols
        self.headerDataChanged.emit(Qt.Horizontal, 0, len(cols))


    def headerData(self, section: int, orientation: PySide2.QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.df.columns[section]
        else:
            return super().headerData(section, orientation, role)

    def data(self, index: PySide2.QtCore.QModelIndex, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole:
            row, col = index.row(), index.column()
            ret = str(self.df.iloc[row, col])
        else:
            ret = None
        return ret

    def rowCount(self, parent: PySide2.QtCore.QModelIndex = ...) -> int:
        return len(self.df)

    def columnCount(self, parent: PySide2.QtCore.QModelIndex = ...) -> int:
        return self.df.shape[1]