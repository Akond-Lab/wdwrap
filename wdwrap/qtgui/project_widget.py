#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

import PySide2
from PySide2.QtWidgets import QSplitter, QTreeView
from PySide2.QtCore import Qt, QSettings
from wdwrap.qtgui.curvesplot_widget import LightPlotWidget, RvPlotWidget
from wdwrap.qtgui.parameters_delegate import ParametersTableDelegate
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

        self.w_light_plot = LightPlotWidget(self.project.curves_model)
        self.w_rv_plot = RvPlotWidget(self.project.curves_model)

        self.left_splitter.addWidget(self.w_parameters_tree)
        self.left_splitter.addWidget(self.w_curves_tree)

        self.right_splitter.addWidget(self.w_light_plot)
        self.right_splitter.addWidget(self.w_rv_plot)

    def resizeEvent(self, arg__1: PySide2.QtGui.QResizeEvent):
        super().resizeEvent(arg__1)

    def save_session(self, settings: QSettings):
        settings.beginGroup('project_splitter')
        settings.setValue('horiz', self.main_splitter.saveState())
        settings.setValue('vert_trees', self.left_splitter.saveState())
        settings.setValue('vert_plots', self.right_splitter.saveState())
        settings.endGroup()
        settings.beginGroup('tree_columns')
        settings.setValue('params', self.w_parameters_tree.header().saveState())
        settings.setValue('curves', self.w_curves_tree.header().saveState())
        settings.endGroup()

    def restore_session(self, settings: QSettings):
        settings.beginGroup('project_splitter')
        try:
            self.main_splitter.restoreState(settings.value("horiz"))
            self.left_splitter.restoreState(settings.value("vert_trees"))
            self.right_splitter.restoreState(settings.value("vert_plots"))
        except AttributeError:
            pass
        settings.endGroup()
        settings.beginGroup('tree_columns')
        try:
            self.w_parameters_tree.header().restoreState(settings.value("params"))
            self.w_curves_tree.header().restoreState(settings.value("curves"))
        except AttributeError:
            pass
        settings.endGroup()





