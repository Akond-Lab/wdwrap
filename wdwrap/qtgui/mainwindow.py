#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

import PySide2
from PySide2.QtCore import QFile, Qt, QTextStream, QSettings, Slot
from PySide2.QtGui import QFont, QKeySequence
from PySide2.QtPrintSupport import QPrintDialog, QPrinter
from PySide2.QtWidgets import (QAction, QApplication, QLabel, QDialog, QFileDialog, QMainWindow, QMessageBox,
                               QDockWidget)

from wdwrap.bundle import Bundle
from wdwrap.qtgui.container import ParentColumnContainer, Container
from wdwrap.qtgui.icons import IconFactory
from wdwrap.qtgui.model_curves import CurveContainer
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

        self.project_widget = ProjectWidget(self)
        self.setCentralWidget(self.project_widget)

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
        file_name, _ = QFileDialog.getOpenFileName(self, "Open lc.in", ".", "lc.in (*)")
        if file_name:
            try:
                self.project_widget.project.load_bundle(file_name)
                logger().info(f'lc.in file opened, path: {file_name}')
            except (ValueError, Bundle.FileFormatNotSupportedError, Bundle.FileFormatMultipleSetsError) as e:
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
        self.openlcinAct = QAction(IconFactory.getIcon('note_add'),
                               "&Open lc.in", self, shortcut=QKeySequence.Open, statusTip="Open lc.in file", triggered=self.open_lcin)
        self.savelcinAct = QAction(IconFactory.getIcon('note_add'),
                               "&Save lc.in as", self, shortcut=QKeySequence.Save, statusTip="Save lc.in file", triggered=self.save_lcin)
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
        self.fileMenu.addAction(self.quitAct)

        self.curvesMenu = self.menuBar().addMenu("&Curves")
        self.curvesMenu.addAction(self.addLightCurveAct)
        self.curvesMenu.addAction(self.addRvCurveAct)

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

