#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import os
from typing import Mapping

import PySide2
from PySide2.QtCore import QFile, Qt, QTextStream, QSettings, Slot
from PySide2.QtGui import QFont, QKeySequence
from PySide2.QtPrintSupport import QPrintDialog, QPrinter
from PySide2.QtWidgets import (QAction, QApplication, QLabel, QDialog, QFileDialog, QMainWindow, QMessageBox,
                               QDockWidget)

from wdwrap.bundle import Bundle
from wdwrap.exceptions import FileFormatNotSupportedError, FileFormatMultipleSetsError
from wdwrap.qtgui.container import ParentColumnContainer, Container
from wdwrap.qtgui.icons import IconFactory
from wdwrap.qtgui.model_connector import ConnectedCheckableAction, TraitletsModelConnector
from wdwrap.qtgui.model_curves import CurveContainer, CurvesModel
from wdwrap.qtgui.widget_info import InfoPanelWidget
from wdwrap.qtgui.widget_project import ProjectWidget
from wdwrap.version import __version__


# from . import console

_logger = None
def logger():
    global _logger
    if _logger is None:
        import logging
        _logger = logging.getLogger('qtui')
    return _logger


# noinspection PyPep8Naming
class MainWindow(QMainWindow):

    def __init__(self, parent=None, flags=None):
        super().__init__(parent)
        self.project_filename = None

        self.project_widget = ProjectWidget(self)
        self.setCentralWidget(self.project_widget)
        self.project_widget.project.curves_collection_changed.connect(self.curvesCollectionChanged)

        self.createActions()
        self.createToolBars()
        self.createStatusBar()
        self.createMenus()
        self.createDockWindows()

        self.setWindowTitle("WD Wrapper")

        self.readWindowSettings()
        self.readAppState()

        # open last fits
        # try:
        #     self.openLastFits()
        # except FileNotFoundError:
        #     print('Can not open last file')

    @Slot(Container)
    def currentItemChanged(self, item: Container):
        if isinstance(item, ParentColumnContainer):
            item = item.parent()
        self.delCurveAct.setEnabled(isinstance(item, CurveContainer))

    @Slot(CurveContainer)
    def curvesCollectionChanged(self, curves_model: CurvesModel):
        self.createPlotMenu(source=curves_model)
        # QMessageBox.information(self, 'collection changed', 'DEBUG: collection changed')

    @Slot(CurveContainer)
    def curvesPlotChanged(self, curves_model: CurvesModel):
        self.checkPlotInPlotMenu(source=curves_model)
        # QMessageBox.information(self, 'collection changed', 'DEBUG: collection changed')

    def closeEvent(self, event: PySide2.QtGui.QCloseEvent):
        self.writeAppState()
        self.writeWindowSettings()
        super().closeEvent(event)

    def keyPressEvent(self, e):
        # if e.key() == Qt.Key_Delete:
        #     self.deleteSelected()
        pass

    def print_(self):
        document = self.textEdit.document()
        printer = QPrinter()

        dlg = QPrintDialog(printer, self)
        if dlg.exec_() != QDialog.Accepted:
            return

        document.print_(printer)

        self.statusBar().showMessage("Ready", 2000)

    @Slot()
    def open_lcin(self):
        file_name, _ = QFileDialog.getOpenFileName(self.centralWidget(), "Open lc.in", "./", "lc.in (*)")
        if file_name:
            try:
                self.project_widget.project.load_bundle(file_name)
                logger().info(f'lc.in file opened, path: {file_name}')
            except (ValueError, FileFormatNotSupportedError, FileFormatMultipleSetsError) as e:
                logger().exception(f'lc.in file f{file_name} loading failed. Input file format error', exc_info=e)
                msg = QMessageBox()
                msg.setWindowTitle('File loading failed')
                msg.setText('Input file format error:')
                msg.setInformativeText(str(e))
                msg.exec_()

    @Slot()
    def save_lcin(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save lc.in", "lc.in", "lc.in (*)")
        if file_name:
            self.project_widget.project.save_bundle(file_name)
            logger().info(f'lc.in file saved, path: {file_name}')

    @Slot()
    def open_prj(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Project', './', 'WD Wrapper Project (*.wdw)')
        if filename:
            if self.open_prj_from_file(filename):
                self.setWindowTitle(os.path.basename(filename))
                self.project_filename = filename

    @Slot()
    def save_prj_as(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Project", './project.wdw', "WD Wrapper Project (*.wdw)")
        if filename:
            self.project_filename = filename
            self.setWindowTitle(os.path.basename(filename))
            self.save_prj_to_file(self.project_filename, mode='gui save as')

    @Slot()
    def save_prj(self):
        if self.project_filename is None:
            self.save_prj_as()
        else:
            self.save_prj_to_file(self.project_filename, mode='gui save')

    def save_prj_to_file(self, filename, mode):
        self.project_widget.project.save_project(filename, mode=mode)
        logger().info(f'Project saved, path: {filename}')

    def open_prj_from_file(self, filename):
        if self.project_widget.project.open_project(filename):
            logger().info(f'Project opened, path: {filename}')
            return True
        else:
            logger().error(f'Project opening failed, path: {filename}')
            return False

    def save(self):
        filename, _ = QFileDialog.getSaveFileName(self,
                                                  "Choose a file name", '.', "HTML (*.html *.htm)")
        if not filename:
            return

        file = QFile(filename)
        if not file.open(QFile.WriteOnly | QFile.Text):
            QMessageBox.warning(self, "Dock Widgets",
                                "Cannot write file %s:\n%s." % (filename, file.errorString()))
            return

        out = QTextStream(file)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        out << self.textEdit.toHtml()
        QApplication.restoreOverrideCursor()

        self.statusBar().showMessage("Saved '%s'" % filename, 2000)

    def readAppState(self):
        # if self.tedaCommandLine.ignoreSettings:
        #     return
        settings = QSettings()
        self.project_widget.restore_session(settings)
        # settings.beginGroup("WCS")
        # self.wcsSexAct.setChecked(bool(settings.value("sexagesimal", True)))
        # self.wcsGridAct.setChecked(bool(settings.value("grid", False)))
        # settings.endGroup()

    def writeAppState(self):
        # if self.tedaCommandLine.ignoreSettings:
        #     return
        settings = QSettings()
        self.project_widget.save_session(settings)
        # settings.beginGroup("WCS")
        # settings.setValue("sexagesimal", self.wcsSexAct.isChecked())
        # settings.setValue("grid", self.wcsGridAct.isChecked())
        # settings.endGroup()

    def undo(self):
        document = self.textEdit.document()
        document.undo()

    def about(self):
        QMessageBox.about(self, "WD Wrapper",
                          f"WD Wrapper  {__version__} <br/>"
                          "Authors: <ul> "
                          "<li>Mikołaj Kałuszyński</li>"
                          "</ul>"
                          "Created by <a href='https://akond.com'>Akond Lab</a> for The Araucaria Project")

    # def on_console_show(self):
    #     self.console.show(window=self, )

    def createActions(self):
        self.openlcinAct = QAction(IconFactory.getIcon('open_lc'), "&Open lc.in", self,
                                   shortcut=QKeySequence.Open, statusTip="Open lc.in file", triggered=self.open_lcin)
        self.savelcinAct = QAction(IconFactory.getIcon('save_lc'),  "&Save lc.in as", self,
                                   shortcut=QKeySequence.Save, statusTip="Save lc.in file", triggered=self.save_lcin)
        self.openProjectAct = QAction(IconFactory.getIcon('open_prj'), "Open &project", self,
                                      statusTip="Open project", triggered=self.open_prj)
        self.saveProjectAct = QAction(IconFactory.getIcon('save_prj'), "S&ave project", self,
                                      statusTip="Save project", triggered=self.save_prj)
        self.saveProjectAsAct = QAction(IconFactory.getIcon('save_prj'), "S&ave project as...", self,
                                        statusTip="Save project to new file", triggered=self.save_prj_as)
        self.autoSaveProjectAct = QAction(None, "Auto save project", self,
                                          statusTip="Automatically save project")
        self.autoSaveProjectAct.setCheckable(True)
        self.autoSaveProjectAct.setChecked(False)

        self.addLightCurveAct = QAction(IconFactory.getIcon('note_add'),
                               "Add &LC", self, statusTip="Add light curve", triggered=self.project_widget.add_lc)
        self.addRvCurveAct = QAction(IconFactory.getIcon('note_add'),
                               "Add &RV", self, statusTip="Add radial velocity curve",
                                     triggered=self.project_widget.add_rv)
        self.delCurveAct =   QAction(IconFactory.getIcon('note_del'),
                               "Delete Curve", self, statusTip="Delete selected curve",
                                     triggered=self.project_widget.del_curve)
        self.delCurveAct.setEnabled(False)

        self.quitAct = QAction("&Quit", self, shortcut="Ctrl+Q", statusTip="Quit the application", triggered=self.close)
        self.aboutAct = QAction("&About", self, statusTip="Show the application's About box", triggered=self.about)
        self.aboutQtAct = QAction("About &Qt", self, statusTip="Show the Qt library's About box", triggered=QApplication.instance().aboutQt)

        # self.qtConsoleAct = QAction('Python Console', self,
        #                             statusTip="Open IPython console window", triggered=self.on_console_show)

        # self.wcsSexAct = QAction('Sexagesimal', self,
        #                          statusTip="Format WCS coordinates as sexagesimal (RA in hour angle) instead of decimal deg")
        # self.wcsSexAct.toggled.connect(self.on_sex_toggle)
        # self.wcsSexAct.setCheckable(True)


    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openlcinAct)
        self.fileMenu.addAction(self.savelcinAct)

        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.openProjectAct)
        self.fileMenu.addAction(self.saveProjectAct)
        self.fileMenu.addAction(self.saveProjectAsAct)
        self.fileMenu.addAction(self.autoSaveProjectAct)

        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

        self.curvesMenu = self.menuBar().addMenu("&Curves")
        self.curvesMenu.addAction(self.addLightCurveAct)
        self.curvesMenu.addAction(self.addRvCurveAct)

        self.plotMenu = self.menuBar().addMenu("&Plot")

        self.viewMenu = self.menuBar().addMenu("&View")
        # self.viewMenu.addAction(self.qtConsoleAct)
        # self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fileToolBar.toggleViewAction())
        self.viewMenu.addAction(self.curvesToolBar.toggleViewAction())

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File Toolbar")
        self.fileToolBar.setObjectName("FILE TOOLBAR")
        self.fileToolBar.addAction(self.openProjectAct)
        self.fileToolBar.addAction(self.saveProjectAct)
        self.fileToolBar.addAction(self.openlcinAct)
        self.fileToolBar.addAction(self.savelcinAct)

        self.curvesToolBar = self.addToolBar("Curves Toolbar")
        self.curvesToolBar.setObjectName("CURVES TOOLBAR")
        self.curvesToolBar.addAction(self.addLightCurveAct)
        self.curvesToolBar.addAction(self.addRvCurveAct)
        self.curvesToolBar.addAction(self.delCurveAct)


    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createDockWindows(self):
        # Info
        dock = QDockWidget('Details', self)
        dock.setObjectName("DETAILS")
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.detailsWidget = InfoPanelWidget(self)
        self.project_widget.treeCurrentItemChanged.connect(self.detailsWidget.setItem)
        self.project_widget.treeCurrentItemChanged.connect(self.currentItemChanged)
        dock.setWidget(self.detailsWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        # dock.setFloating(True)
        # dock.hide()

        # Scale
        # dock = QDockWidget("Dynamic Scale", self)
        # dock.setObjectName("SCALE")
        # dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        # self.scaleWidget = ScaleWidget(self, scales_model=self.scales_model, cmap_model=self.cmaps)
        # dock.setWidget(self.scaleWidget)
        # self.addDockWidget(Qt.RightDockWidgetArea, dock)
        # self.viewMenu.addAction(dock.toggleViewAction())
        # dock.setFloating(True)
        # dock.hide()


        # #radial profiles
        # dock = QDockWidget("Radial Profile Fit", self)
        # dock.setObjectName("RADIAL_PROFILE_IRAF")
        # dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        # self.radial_profile_iraf_widget = IRAFRadialProfileWidget(self.fits_image.data)
        # dock.setWidget(self.radial_profile_iraf_widget)
        # self.addDockWidget(Qt.RightDockWidgetArea, dock)
        # self.viewMenu.addAction(dock.toggleViewAction())
        # self.dockRadialFit = dock


    def createPlotMenu(self, source: CurvesModel):
        self.plotMenu.clear()
        light_curves = []
        rv_curves = []
        for c in source.curves_iter():
            if c.is_rv():
                rv_curves.append(c)
            else:
                light_curves.append(c)
        for c in light_curves + [None] + rv_curves:
            if c is None:
                self.plotMenu.addSeparator()
            else:
                action = ConnectedCheckableAction(c.objectName())
                connector = TraitletsModelConnector('plot')
                action.model_connector = connector
                connector.connect_model(c.content)
                self.plotMenu.addAction(action)
                # a = self.plotMenu.addAction(c.objectName())
                # a.setData(id(c))
                # a.setCheckable(True)
                # c.content.observe(lambda change: self.curvesPlotChanged(source))
        # self.checkPlotInPlotMenu(source)

    # def _plotMenuCurvesActions(self) -> Mapping[int, QAction]:
    #     """plotMenu actions indexed by Data: CurveContainer's id """
    #     return {a.data(): a for a in  self.plotMenu.actions()}

    # def checkPlotInPlotMenu(self, source: CurvesModel):
    #     actions = self._plotMenuCurvesActions()
    #     for c in source.curves_iter():
    #         try:
    #             menu_action = actions[id(c)]
    #             menu_action.setChecked(c.plot)
    #         except KeyError:
    #             pass

    # noinspection PyTypeChecker
    def readWindowSettings(self):
        # if self.tedaCommandLine.ignoreSettings:
        #     return
        settings = QSettings()
        settings.beginGroup("MainWindow")
        size, pos = settings.value("size"), settings.value("pos")
        settings.endGroup()
        if size is not None and pos is not None:
            print('settings: resize to {} and move to {}', size, pos)
            self.move(pos)
            # self.resize(size)
            print('Size reported ', self.size())
            print('Size set ', size)
            self.resize(size)
            print('Size reported ', self.size())
        else:
            self.resize(800, 600)

        geometry = settings.value("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
            self.restoreState(settings.value("windowState"))


    def writeWindowSettings(self):
        # if self.tedaCommandLine.ignoreSettings:
        #     return
        settings = QSettings()
        settings.beginGroup("MainWindow")
        settings.setValue("size", self.size())
        settings.setValue("pos", self.pos())
        settings.endGroup()

        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())

