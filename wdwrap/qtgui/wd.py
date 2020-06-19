#!/usr/bin/env python
"""
Wd GUI
"""
from sys import stderr

from PySide2.QtCore import QCommandLineParser, QCoreApplication
from PySide2.QtWidgets import QApplication

from wdwrap.qtgui.mainwindow import MainWindow
from wdwrap.version import __version__


def main():
    import sys

    app = QApplication(sys.argv)
    QApplication.setOrganizationName('Akond Lab')
    QApplication.setOrganizationDomain('akond.com')
    QApplication.setApplicationName('WD Wrapper')
    QApplication.setApplicationVersion(__version__)

    # tcl = TedaCommandLine()
    # parser = QCommandLineParser()
    #
    # result = tcl.parseCommandLine(parser)
    # if result.result == CommandLineParseResult.CommandLineError :
    #     print(result.errorMessage, "\n\n", parser.helpText(), file=sys.stderr)
    #     return 1
    # elif result.result == CommandLineParseResult.CommandLineVersionRequested :
    #     print(QCoreApplication.applicationName(), QCoreApplication.applicationVersion(), "\n")
    #     return 0
    # elif result.result == CommandLineParseResult.CommandLineHelpRequested :
    #     parser.showHelp()
    #     return 0


    mainWin = MainWindow()
    # mainWin.resize(800, 600)   # now in config, see: MainWindow.readWindowSettings
    mainWin.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
