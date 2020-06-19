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
        self.project = Project()

        self.main_splitter = self  # inheritance from QSplitter may not be preserved
        self.main_splitter.setOrientation(Qt.Horizontal)
        self.left_splitter = QSplitter(Qt.Vertical)
        self.right_splitter = QSplitter(Qt.Vertical)
        self.main_splitter.addWidget(self.left_splitter)
        self.main_splitter.addWidget(self.right_splitter)

        # self.w_parameters = ParametersWidget(self.project.bundle)
        self.w_parameters_tree = QTreeView()
        self.w_parameters_tree.setModel(self.project.parameters_model)
        delegate = ParametersTableDelegate()
        self.w_parameters_tree.setItemDelegate(delegate)

        self.w_curves_tree = QTreeView()
        self.w_curves_tree.setModel(self.project.curves_model)

        self.left_splitter.addWidget(self.w_parameters_tree)
        self.left_splitter.addWidget(self.w_curves_tree)

    def resizeEvent(self, arg__1: PySide2.QtGui.QResizeEvent):
        super().resizeEvent(arg__1)



