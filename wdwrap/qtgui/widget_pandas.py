#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

import pandas as pd
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget, QTableView, QVBoxLayout

from wdwrap.qtgui.model_pandas import PandasDataFrameModel


class WidgetPandas(QWidget):
    def __init__(self, parent=None, df=None):
        super().__init__(parent)
        if df is None:
            df = pd.DataFrame()
        self.tablemodel = PandasDataFrameModel(df=df)
        self.tableview = QTableView()
        self.tableview.setModel(self.tablemodel)
        tableboxlayout = QVBoxLayout()
        self.tableview.setMinimumWidth(500)
        self.tableview.setMinimumHeight(250)
        self.tableview.setWordWrap(False)
        self.tableview.setShowGrid(False)
        tableboxlayout.addWidget(self.tableview)
        self.setLayout(tableboxlayout)

    @Slot(pd.DataFrame)
    def setDataFrame(self, df: pd.DataFrame):
        if df is None:
            df = pd.DataFrame()
        self.tablemodel.set_df(df)

    @Slot()
    def refreshTable(self):
        self.tablemodel.beginResetModel()
        self.tablemodel.endResetModel()