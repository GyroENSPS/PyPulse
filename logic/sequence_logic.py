import numpy as np
from PyQt5.QtWidgets import QCheckBox, QComboBox


class SequenceLogic:

    def __init__(self, pulse_table, var_logic):
        """
        pulse_table : PulseTableWidget instance
        var_logic   : VarLogic instance
        """
        self.pulse_table = pulse_table
        self.var_logic   = var_logic

    # --- Read table ---

    def read_table(self) -> tuple:
        """
        Reads the pulse table and returns:
        - pulse_durations : np.array of float, one value per column
        - IO_matrix       : np.array (10, n_cols), rows = channels, cols = segments
        - variable_index  : list of column indices whose duration is a sweep variable
        - param_per_col   : list of var-table row index selected in each ComboBox
        """
        table = self.pulse_table.table
        cols  = table.columnCount()

        var_values   = self.var_logic.create_python_var()
        pulse_durations = np.zeros(cols)
        IO_matrix       = np.zeros((10, cols))
        variable_index  = []
        param_per_col   = [None] * cols

        for col in range(cols):
            combo = table.cellWidget(0, col)
            if combo is None:
                continue
            idx = combo.currentIndex()
            param_per_col[col] = idx
            if var_values[idx] is not None:
                pulse_durations[col] = var_values[idx]

            var_checkbox = self.var_logic.table.cellWidget(idx, 3)
            if isinstance(var_checkbox, QCheckBox) and var_checkbox.isChecked():
                variable_index.append(col)

            for row in range(1, 9):
                cb = table.cellWidget(row, col)
                IO_matrix[row - 1][col] = 1 if (cb and cb.isChecked()) else 0

            for row in range(9, 11):
                item = table.item(row, col)
                try:
                    IO_matrix[row - 1][col] = float(item.text())
                except:
                    pass

        return pulse_durations, IO_matrix, variable_index, param_per_col

    # --- Variable resolution ---

    def update_pulse_durations(self, var_names: list, var_instructions: list) -> np.ndarray:
        """
        Re-evaluates variable expressions (used during sweep — one instruction
        may have been replaced by the current sweep point value).
        Returns array of resolved values, one per variable row.
        """
        n = len(var_instructions)
        new_values = np.zeros(n)
        run_flag   = True
        error_count = 0

        while run_flag and error_count < 100:
            run_flag = False
            for idx, instruction in enumerate(var_instructions):
                try:
                    code_line = f"{var_names[idx]} = {instruction}"
                    exec(code_line)
                    exec(f"new_values[idx] = {var_names[idx]}")
                except:
                    run_flag = True
                    error_count += 1

        return new_values

    # --- Pattern calculator ---

    def pattern_calculator(self, pulse_durations: list, io_states: list) -> list:
        """
        Compresses (durations, states) into a list of (duration, value) tuples
        by merging consecutive segments with the same state.
        """
        pattern = [None] * (len(io_states) + 1)
        j, k = 0, 0
        stop_pattern = True

        while stop_pattern:
            pulse_len = pulse_durations[k]
            stop_roll = True
            i = k + 1
            while stop_roll:
                if i == len(pulse_durations):
                    pattern[j] = (pulse_len, io_states[i - 1])
                    stop_pattern = False
                    stop_roll    = False
                elif io_states[i] == io_states[i - 1]:
                    pulse_len += pulse_durations[i]
                    i += 1
                else:
                    pattern[j] = (pulse_len, io_states[i - 1])
                    pulse_len = 0
                    j += 1
                    k = i
                    stop_roll = False

        return pattern[:j + 1]

    # --- Export for viewer (single pattern preview) ---

    def export_for_viewer(self) -> tuple:
        """
        Builds the data needed by PulseViewer.plot_pattern():
        Returns (pulse_durations, IO_matrix, variable_index).
        """
        pulse_durations, IO_matrix, variable_index, _ = self.read_table()
        return pulse_durations, IO_matrix, variable_index
