#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab

import PySide2
from PySide2.QtCore import QFile, Qt, QTextStream, QSettings
from PySide2.QtGui import QFont, QKeySequence
from PySide2.QtPrintSupport import QPrintDialog, QPrinter
from PySide2.QtWidgets import (QAction, QApplication, QLabel, QDialog, QFileDialog, QMainWindow, QMessageBox)

from wdwrap.qtgui.icons import IconFactory
from wdwrap.qtgui.project_widget import ProjectWidget
from wdwrap.version import __version__


# from . import console


# noinspection PyPep8Naming
class MainWindow(QMainWindow):

    def __init__(self, parent=None, flags=None):
        super().__init__(parent)

        self.central_widget = ProjectWidget(self)
        self.setCentralWidget(self.central_widget)

        self.createActions()
        self.createToolBars()
        self.createStatusBar()
        self.createDockWindows()
        self.createMenus()

        self.setWindowTitle("WD Wrapper")

        self.readWindowSettings()
        self.readAppState()

        # open last fits
        # try:
        #     self.openLastFits()
        # except FileNotFoundError:
        #     print('Can not open last file')

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

    def open_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", ".", "Fits files (*.fits)")
        if file_name:
            self.open_fits(file_name)

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
        # settings.beginGroup("WCS")
        # self.wcsSexAct.setChecked(bool(settings.value("sexagesimal", True)))
        # self.wcsGridAct.setChecked(bool(settings.value("grid", False)))
        # settings.endGroup()

    def writeAppState(self):
        # if self.tedaCommandLine.ignoreSettings:
        #     return
        settings = QSettings()
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
        self.openAct = QAction(IconFactory.getIcon('note_add'),
                               "&Open", self, shortcut=QKeySequence.Open, statusTip="Open FITS file", triggered=self.open_dialog)
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
        self.fileMenu.addAction(self.openAct)

        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

        self.viewMenu = self.menuBar().addMenu("&View")
        # self.viewMenu.addAction(self.qtConsoleAct)
        # self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.mainToolBar.toggleViewAction())

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.mainToolBar = self.addToolBar("File Toolbar")
        self.mainToolBar.addAction(self.openAct)


    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createDockWindows(self):
        pass
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

