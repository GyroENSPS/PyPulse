import sys
from PyQt5 import QtWidgets
from gui.ui_files.py_files.UI_PS_main import Ui_MainWindow
from gui.pulse_table_widget import PulseTableWidget
from logic.var_logic import VarLogic
from logic.sequence_logic import SequenceLogic
from gui.pulse_viewer import PulseViewer
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # dossier de main_window.py
CHANNEL_LABELS = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "A0", "A1"]





class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Init UI
        self.ui.comboBox_trigger_per_point_channel.addItems(CHANNEL_LABELS)
        self.ui.comboBox_trigger_per_sequence_channel.addItems(CHANNEL_LABELS)
        self.ui.comboBox_trigger_per_sequence_channel.setCurrentIndex(9)
        self.ui.comboBox_trigger_per_point_channel.setCurrentIndex(2)

        # Init logic
        self.pulse_table = PulseTableWidget(self.ui.tableWidget, [])
        self.var_logic   = VarLogic(self.ui.tableWidget_var, self.pulse_table)
        self.sequence_logic = SequenceLogic(self.pulse_table, self.var_logic)
        self.pulse_viewer = PulseViewer(self.ui.pulse_view)
        self.pulse_table._on_change = self._plot_pulse

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
        self.ui.pushButton_plot_pulse.clicked.connect(self._plot_pulse)

        # Auto-sync var names → comboboxes on cell change
        self.ui.tableWidget_var.cellChanged.connect(lambda _: self._on_var_changed())
        # Update plot viewer after every changes
        self.ui.tableWidget_var.cellChanged.connect(self._plot_pulse)
        self.ui.tableWidget_var.itemChanged.connect(lambda: self._plot_pulse())
        # plot viewer for measurement sequences
        self.ui.pushButton_pulse_sequence.clicked.connect(self._preview_sequence)
        self.ui.pushButton_compute_sequence.clicked.connect(self._compute_sequence)

    def _on_var_changed(self):
        self.var_logic.update_param_names()
        self._plot_pulse()

    def _get_sequence_params(self) -> dict:
        point_trigger_enabled = self.ui.checkBox_trigger_per_point_check.isChecked()
        sequence_trigger_enabled = self.ui.checkBox_trigger_per_sequence_check.isChecked()
        return {
            "num_points": self.ui.spinBox_num_points.value(),
            "n_repeat": self.ui.spinBox_n_repeat.value(),
            "min_val": self.ui.spinBox_min.value(),
            "max_val": self.ui.spinBox_max.value(),
            "point_trigger_channel": self.ui.comboBox_trigger_per_point_channel.currentIndex()
            if point_trigger_enabled else -1,
            "point_trigger_duration": self.ui.spinBox_trigger_per_point_duration.value(),
            "sequence_trigger_channel": self.ui.comboBox_trigger_per_sequence_channel.currentIndex()
            if sequence_trigger_enabled else -1,
            "sequence_trigger_duration": self.ui.spinBox_trigger_per_sequence_duration.value(),
        }

    def _preview_sequence(self):
        p = self._get_sequence_params()
        final_patterns, n_tuples, total_time = self.sequence_logic.build_measurement_sequence(
            num_points=10,  # preview rapide avec seulement 10 points
            n_repeat=p["n_repeat"],
            min_val=p["min_val"], max_val=p["max_val"],
            point_trigger_channel=p["point_trigger_channel"],
            point_trigger_duration=p["point_trigger_duration"],
            sequence_trigger_channel=p["sequence_trigger_channel"],
            sequence_trigger_duration=p["sequence_trigger_duration"],
        )
        self.pulse_viewer.plot_sequence(final_patterns, self.ui.pulse_sequence_view)

    def _compute_sequence(self):
        p = self._get_sequence_params()
        self.ui.progressBar.setValue(0)
        final_patterns, n_tuples, total_time = self.sequence_logic.build_measurement_sequence(**p)
        self.ui.label_num_tupple.setText(str(n_tuples))
        self.ui.label_total_time.setText(f"{total_time} s")
        self.ui.progressBar.setValue(100)
        self.pulse_viewer.plot_sequence(final_patterns, self.ui.pulse_sequence_view)
        self.final_patterns = final_patterns  # garde en mémoire pour le streaming

    def _plot_pulse(self):
        pulse_durations, IO_matrix, variable_index = self.sequence_logic.export_for_viewer()
        min_val = self.ui.spinBox_min.value()
        max_val = self.ui.spinBox_max.value()
        self.pulse_viewer.plot_pattern(pulse_durations, IO_matrix, variable_index, min_val, max_val)

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
