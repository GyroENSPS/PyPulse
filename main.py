import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QLocale

from gui.main_window import MainWindow
import qdarkstyle
from server.command_server import CommandServer


QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    window = MainWindow()
    window.show()

    server = CommandServer(window)
    server.start()

    sys.exit(app.exec_())