import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QLocale

from gui.ui_files.py_files.UI_PS_main import Ui_MainWindow
import qdarkstyle

QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())