#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import typing

import PySide2
from PySide2.QtWidgets import QSplitter, QFrame, QHBoxLayout, QVBoxLayout
from wdwrap.bundle import Bundle
from wdwrap.qtgui.project import Project
from wdwrap.qtgui.wdvalue_widget import WdValueWidget


class ParametersWidget(QFrame):

    def __init__(self, bundle: Bundle):
        self.bundle = bundle
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.create_children()

    def create_children(self):
        if self.bundle is not None:
            for row in self.bundle.lines:
                self.create_row(row)

    def create_row(self, row):
        layout = QHBoxLayout()
        for key, item in row.items():
            w = WdValueWidget.from_parameter(item)
            layout.addWidget(w)
        self.layout().addLayout(layout)


