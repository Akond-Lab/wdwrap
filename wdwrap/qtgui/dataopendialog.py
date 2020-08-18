#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import typing
from functools import partial

import pandas as pd

import PySide2
from PySide2.QtCore import Signal, Slot
from PySide2.QtGui import QIntValidator
from PySide2.QtWidgets import QDialog, QFormLayout, QPushButton, QTableView, QFileDialog, QDialogButtonBox, \
    QVBoxLayout, QGroupBox, QLineEdit, QTextEdit, QHBoxLayout

from wdwrap.io import DataFrameReader
from wdwrap.qtgui.model_pandas import PandasDataFrameModel


class ColumnsGroupBox(QGroupBox):

    columns_changes = Signal()

    def __init__(self,
                 title,
                 expected_columns,
                 all_columns=None,
                 parent: typing.Optional[PySide2.QtWidgets.QWidget] = None):
        super().__init__(title, parent)

        self.allcolumns = all_columns if all_columns else expected_columns
        self.columns = expected_columns

        layout = QFormLayout()
        self.coledits = {}
        for col in self.allcolumns:
            e = QLineEdit()
            e.setValidator(QIntValidator(0,100))
            try:
                n = self.columns.index(col)
                e.setText(str(n))
            except ValueError:
                pass
            handler = partial(self.on_column_change, col=col)
            e.textEdited.connect(handler)
            self.coledits[col] = e
            layout.addRow(col, e)
        self.setLayout(layout)

    def on_column_change(self, val, col):
        if val != '':
            try:
                n = int(val)
                if not 0 <= n < 100:
                    return False
            except ValueError:
                return False
            for c, e in self.coledits.items():
                if c != col and val == e.text():
                    e.setText('')
        self.columns = []
        for c, e in self.coledits.items():
            try:
                n = int(e.text())
            except ValueError:
                continue
            self.columns.extend([''] * (n - len(self.columns) + 1))  # enlarge list to at lest n elemenets
            self.columns[n] = c
        print(self.columns)
        self.columns_changes.emit()


class DataOpenDialog(QDialog):

    def __init__(self,
                 expected_columns,
                 obligatory_columns,
                 all_columns = None,
                 parent: typing.Optional[PySide2.QtWidgets.QWidget] = None,
                 ):
        super().__init__(parent)
        self.file = None
        self.allcolumns = all_columns if all_columns else expected_columns
        self.columns = expected_columns
        self.obligatorycolumns = obligatory_columns
        self.setWindowTitle('Open Data File')
        self.filename = QLineEdit()
        self.filename.setReadOnly(True)
        self.filename.setMinimumWidth(150)
        self.loadbutton = QPushButton("Load...")
        self.loadbutton.clicked.connect(self.file_dialog)

        layout_left = QVBoxLayout()
        filebox = QGroupBox('File')
        layoutf = QFormLayout()
        layoutf.addRow('File', self.filename)
        layoutf.addRow('', self.loadbutton)
        filebox.setLayout(layoutf)
        layout_left.addWidget(filebox)
        self.columnsbox = ColumnsGroupBox('Columns order', expected_columns=expected_columns, all_columns=all_columns)
        self.columnsbox.columns_changes.connect(self.on_columns_order_changed)
        layout_left.addWidget(self.columnsbox)
        layout_left.addStretch()

        layout_right = QVBoxLayout()
        previewbox = QGroupBox('File 10 lines preview')
        previewboxlayout = QVBoxLayout()
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setLineWrapMode(QTextEdit.NoWrap)
        self.preview.setMinimumWidth(500)
        self.preview.setMinimumHeight(170)
        previewboxlayout.addWidget(self.preview)
        previewbox.setLayout(previewboxlayout)
        layout_right.addWidget(previewbox)

        self.tablemodel = PandasDataFrameModel(df=pd.DataFrame())
        self.tableview = QTableView()
        self.tableview.setModel(self.tablemodel)
        tablebox = QGroupBox('Data preview')
        tableboxlayout = QVBoxLayout()
        self.tableview.setMinimumWidth(500)
        self.tableview.setMinimumHeight(250)
        self.tableview.setWordWrap(False)
        self.tableview.setShowGrid(False)
        tableboxlayout.addWidget(self.tableview)
        tablebox.setLayout(tableboxlayout)
        layout_right.addWidget(tablebox)

        layout = QHBoxLayout()
        layout.addLayout(layout_left)
        layout.addLayout(layout_right)

        layoutmain = QVBoxLayout()
        layoutmain.addLayout(layout)

        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)
        layoutmain.addWidget(self.buttonbox)
        self.setLayout(layoutmain)
        self.update_ok()

    @property
    def df(self):
        return self.tablemodel.df

    def file_dialog(self):
        filedialog = QFileDialog(caption='Select Data File')
        filedialog.setFileMode(QFileDialog.ExistingFile)
        if filedialog.exec():
            self.file = filedialog.selectedFiles()[0]
            self.filename.setText(self.file)
            lines = []
            with open(self.file) as fd:
                for _ in range(10):
                    lines.append(fd.readline())
            self.preview.setText(''.join(lines))
            reader = DataFrameReader(self.file)
            self.tablemodel.set_df(reader.df)
            self.tablemodel.set_columns(self.columnsbox.columns)
            self.tableview.resizeRowsToContents()
        self.update_ok()

    @Slot()
    def on_columns_order_changed(self):
        self.tablemodel.set_columns(self.columnsbox.columns)
        self.update_ok()

    def is_ok(self):
        columns = set(self.tablemodel.df.columns)
        for c in self.obligatorycolumns:
            if not isinstance(c, tuple):
                c = (c,)
            c = set(c)
            if c.isdisjoint(columns):
                return False
        return True

    def update_ok(self):
        self.buttonbox.button(QDialogButtonBox.Ok).setEnabled(self.is_ok())



