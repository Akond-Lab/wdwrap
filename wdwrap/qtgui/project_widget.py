#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import typing

import PySide2
from PySide2.QtWidgets import QSplitter, QWidget, QTreeView
from PySide2.QtCore import Qt
from wdwrap.qtgui.parameters_delegate import ParametersTableDelegate
from wdwrap.qtgui.parameters_widget import ParametersWidget
from wdwrap.qtgui.project import Project


class ProjectWidget(QSplitter):

    def __init__(self, parent, f=...):
        super().__init__(parent, f)
        self.splitter = self  # inheritance from QSplitter may not be preserved
        self.splitter.setOrientation(Qt.Vertical)

        self.project = Project()
        self.w_parameters = ParametersWidget(self.project.bundle)
        self.w_parameters_tree = QTreeView()
        self.w_parameters_tree.setModel(self.project.parameters_model)
        delegate = ParametersTableDelegate()
        self.w_parameters_tree.setItemDelegate(delegate)
        self.splitter.addWidget(self.w_parameters_tree)
        self.splitter.addWidget(QWidget())

    def resizeEvent(self, arg__1: PySide2.QtGui.QResizeEvent):
        super().resizeEvent(arg__1)



