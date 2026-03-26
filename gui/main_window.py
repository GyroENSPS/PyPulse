import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from gui.ui_files.py_files.UI_PS_main import Ui_MainWindow
from gui.pulse_table_widget import PulseTableWidget
from logic.var_logic import VarLogic
from logic.sequence_logic import SequenceLogic
from gui.pulse_viewer import PulseViewer
from hardware.pulse_streamer import PulseStreamerDriver
from hardware.sequence_builder import SequenceBuilder
import configparser

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # dossier de main_window.py
CHANNEL_LABELS = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "A0", "A1"]


class SequenceWorker(QThread):
    """Worker thread pour le calcul complet de la séquence de mesure.
    Évite de bloquer le thread UI lors de séquences longues.
    """
    result_ready = pyqtSignal(list, int)
    error_occurred = pyqtSignal(str)

    def __init__(self, sequence_logic, params):
        super().__init__()
        self.sequence_logic = sequence_logic
        self.params = params

    def run(self):
        try:
            final_patterns, n_tuples = self.sequence_logic.build_measurement_sequence(**self.params)
            self.result_ready.emit(final_patterns, n_tuples)
        except Exception as e:
            self.error_occurred.emit(str(e))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Init UI
        self.ui.comboBox_trigger_per_point_channel.addItems(CHANNEL_LABELS)
        self.ui.comboBox_trigger_per_sequence_channel.addItems(CHANNEL_LABELS)
        self.ui.comboBox_trigger_per_sequence_channel.setCurrentIndex(3)
        self.ui.comboBox_trigger_per_point_channel.setCurrentIndex(2)

        # Init logic
        self.pulse_table = PulseTableWidget(self.ui.tableWidget, [], on_change_callback=self._plot_pulse)
        self.var_logic   = VarLogic(self.ui.tableWidget_var, self.pulse_table)
        self.sequence_logic = SequenceLogic(self.pulse_table, self.var_logic)
        self.pulse_viewer = PulseViewer(self.ui.pulse_view)
        self._sequence_worker = None

        # Init PulseStreamer
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        hw_cfg_path = os.path.join(BASE_DIR, "..", "config", "hardware.cfg")

        hw_config = configparser.ConfigParser()
        hw_config.read(hw_cfg_path)

        ps_ip = hw_config.get("pulse_streamer", "ip", fallback="169.254.8.2")
        ps_clock = hw_config.get("pulse_streamer", "clock", fallback="internal")

        self.ps_driver = PulseStreamerDriver(ip=ps_ip, clock=ps_clock)

        self.sequence_builder = SequenceBuilder(self.ps_driver)
        self.sequence_builder = SequenceBuilder(self.ps_driver)

        self.ui.pulse_sequence_view.setDownsampling(auto=True, mode="subsample")
        self.ui.pulse_sequence_view.setClipToView(True)

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
        # PulseStreamer
        self.ui.pushButton_PS_run_continuous.clicked.connect(self._run_continuous)
        self.ui.pushButton_PS_reset.clicked.connect(self._stop_stream)
        self.ui.pushButton_PS_run_N_times.clicked.connect(self._run_n_times)

    def _compute_sequence(self):
        # Empêcher un double-clic pendant le calcul
        if self._sequence_worker is not None and self._sequence_worker.isRunning():
            return

        p = self._get_sequence_params()
        self.ui.progressBar.setValue(0)
        self.ui.pushButton_compute_sequence.setEnabled(False)

        self._sequence_worker = SequenceWorker(self.sequence_logic, p)
        self._sequence_worker.result_ready.connect(lambda fp, nt: self._on_sequence_ready(fp, nt, p))
        self._sequence_worker.error_occurred.connect(self._on_sequence_error)
        self._sequence_worker.start()

    def _on_sequence_ready(self, final_patterns, n_tuples, p):
        self.ui.label_num_tupple.setText(str(n_tuples))
        self.ui.progressBar.setValue(100)
        self.ui.pushButton_compute_sequence.setEnabled(True)
        self.final_patterns = final_patterns

        # Affichage : toujours un preview à 10 points, jamais la séquence complète
        self._preview_sequence()

        # Export summary
        export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "..", "sequences")
        os.makedirs(export_dir, exist_ok=True)
        path = os.path.join(export_dir, "last_measurement_sequence.txt")
        self.sequence_logic.export_sequence_summary(
            final_patterns,
            num_points=p["num_points"],
            n_repeat=p["n_repeat"],
            min_val=p["min_val"],
            max_val=p["max_val"],
            path=path
        )

    def _on_sequence_error(self, error_msg):
        self.ui.pushButton_compute_sequence.setEnabled(True)
        self.ui.progressBar.setValue(0)
        QtWidgets.QMessageBox.critical(self, "Erreur de calcul", f"Échec du calcul de la séquence :\n{error_msg}")

    def _run_continuous(self):
        if not hasattr(self, "final_patterns") or self.final_patterns is None:
            print("No sequence computed yet.")
            return
        self.ps_driver.connect()
        if not self.ps_driver.is_connected():
            print("Cannot stream: PulseStreamer not connected.")
            return
        sequence = self.sequence_builder.build(self.final_patterns)
        self.ps_driver.stream_infinite(sequence)

    def _run_n_times(self):
        if not hasattr(self, "final_patterns") or self.final_patterns is None:
            print("No sequence computed yet.")
            return
        self.ps_driver.connect()
        if not self.ps_driver.is_connected():
            print("Cannot stream: PulseStreamer not connected.")
            return
        n = self.ui.spinBox_n_average.value()
        sequence = self.sequence_builder.build(self.final_patterns)
        self.ps_driver.stream_n_times(sequence, n)

    def _stop_stream(self):
        if self.ps_driver.is_connected():
            self.ps_driver.reset()

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
        final_patterns, n_tuples = self.sequence_logic.build_measurement_sequence(
            num_points=10,  # preview rapide avec seulement 10 points
            n_repeat=p["n_repeat"],
            min_val=p["min_val"], max_val=p["max_val"],
            point_trigger_channel=p["point_trigger_channel"],
            point_trigger_duration=p["point_trigger_duration"],
            sequence_trigger_channel=p["sequence_trigger_channel"],
            sequence_trigger_duration=p["sequence_trigger_duration"],
        )
        self.pulse_viewer.plot_sequence(final_patterns, self.ui.pulse_sequence_view)

    def _plot_pulse(self):
        if not hasattr(self, "sequence_logic") or not hasattr(self, "pulse_viewer"):
            return
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
