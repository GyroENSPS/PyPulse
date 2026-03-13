import sys
from PyQt5 import QtWidgets
from gui.ui_files.py_files.UI_PS_main import Ui_MainWindow
from gui.pulse_table_widget import PulseTableWidget
from logic.var_logic import VarLogic
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # dossier de main_window.py


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Init logic
        self.pulse_table = PulseTableWidget(self.ui.tableWidget, [])
        self.var_logic   = VarLogic(self.ui.tableWidget_var, self.pulse_table)

        self._connect_signals()

    def _connect_signals(self):
        # Pulse table buttons
        self.ui.pushButton_add_col_left.clicked.connect(self.pulse_table.add_column_left)
        self.ui.pushButton_add_col_right.clicked.connect(self.pulse_table.add_column_right)
        self.ui.pushButton_del_col.clicked.connect(self.pulse_table.remove_column)
        self.ui.pushButton_move_left.clicked.connect(self.pulse_table.move_column_left)
        self.ui.pushButton_move_right.clicked.connect(self.pulse_table.move_column_right)
        self.ui.pushButton_invert.clicked.connect(self.pulse_table.invert_row)
        self.ui.pushButton_swap_rows.clicked.connect(self.pulse_table.swap_rows)
        self.ui.pushButton_load_config.clicked.connect(self._load_pulse_config)
        self.ui.pushButton_extrract_matrix.clicked.connect(self._save_pulse_config)

        # Var table buttons
        self.ui.pushButton_add_var_down.clicked.connect(self.var_logic.add_var_row)
        self.ui.pushButton_save_var.clicked.connect(self._save_var_config)
        self.ui.pushButton_load_var.clicked.connect(self._load_var_config)
        self.ui.pushButton_sort_py_vars.clicked.connect(
            lambda: self.var_logic.sort_and_resolve()
        )

        # Auto-sync var names → comboboxes on cell change
        self.ui.tableWidget_var.cellChanged.connect(
            lambda: self.var_logic.update_param_names()
        )

    def _save_pulse_config(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save pulse config", "config/pulse_config/", "Config files (*.cfg)"
        )
        if path:
            self.pulse_table.save_config(path)

    def _load_pulse_config(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Load pulse config",
            os.path.join(BASE_DIR, "..", "config", "pulse_config"),
            "Config files (*.cfg)"
        )
        if path:
            self.pulse_table.load_config(path)

    def _save_var_config(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save var config", "config/var_config/", "Config files (*.cfg)"
        )
        if path:
            self.var_logic.save_config(path)

    def _load_var_config(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load var config", "config/var_config/", "Config files (*.cfg)"
        )
        if path:
            self.var_logic.load_config(path)
