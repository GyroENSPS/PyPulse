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

    def build_measurement_sequence(self, num_points: int, n_repeat: int,
                                   min_val: int, max_val: int,
                                   point_trigger_channel: int,
                                   point_trigger_duration: int,
                                   sequence_trigger_channel: int,
                                   sequence_trigger_duration: int) -> tuple:
        """
        Génère la séquence complète de mesure (balayage du paramètre variable).
        Retourne (final_patterns, total_tuple_length, total_measurement_time).
        """
        pulse_durations, IO_matrix, variable_index, param_per_col = self.read_table()

        # Récupère noms et instructions des variables
        row_count = self.var_logic.table.rowCount()
        var_names = []
        var_instructions = []
        var_conds_idx = []
        for row in range(row_count):
            name_item = self.var_logic.table.item(row, 0)
            val_item = self.var_logic.table.item(row, 1)
            checkbox = self.var_logic.table.cellWidget(row, 3)
            if name_item and val_item:
                var_names.append(name_item.text().strip())
                var_instructions.append(val_item.text().strip())
            else:
                var_names.append("")
                var_instructions.append("0")
            from PyQt5.QtWidgets import QCheckBox
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                var_conds_idx.append(row)

        meas_points = np.linspace(min_val, max_val, num_points, dtype=int)

        all_pulse_durations = np.zeros(len(pulse_durations) * num_points * n_repeat)
        point_trigger_timings = np.zeros(2 * num_points)
        point_trigger_IO = np.zeros(2 * num_points)

        for idx, point in enumerate(meas_points):
            # Substitue le point de mesure dans les variables de balayage
            current_instructions = list(var_instructions)
            for i in var_conds_idx:
                current_instructions[i] = str(point)

            new_params = self.update_pulse_durations(var_names, current_instructions)
            new_durations = np.copy(pulse_durations)
            for col_idx, param_number in enumerate(param_per_col):
                if param_number is not None:
                    new_durations[col_idx] = new_params[param_number]

            point_trigger_timings[idx * 2: idx * 2 + 2] = [
                point_trigger_duration,
                sum(new_durations) * n_repeat - point_trigger_duration
            ]
            point_trigger_IO[idx * 2: idx * 2 + 2] = [1, 0]

            for repeat_idx in range(n_repeat):
                first = (idx * n_repeat + repeat_idx) * len(pulse_durations)
                last = first + len(pulse_durations)
                all_pulse_durations[first:last] = new_durations

        half = sequence_trigger_duration // 2

        # Préambule : toutes les voies à 0 sauf le trigger de séquence
        if sequence_trigger_channel != -1:
            preamble_duration = sequence_trigger_duration
        else:
            preamble_duration = 0
            # Le trigger séquence fait 0 pendant half, puis 1 pendant half
        sequence_trigger_preamble = [(half, 0), (half, 1)]
        # Les autres voies sont à 0 pendant tout le préambule
        silent_preamble = [(preamble_duration, 0)]

        # Séquence principale : trigger séquence reste à 0
        sequence_trigger_timings = [sum(all_pulse_durations)]
        sequence_trigger_IO = [0]

        all_IO_states = np.tile(IO_matrix, (1, num_points * n_repeat))

        final_patterns = [None] * len(all_IO_states)
        total_tuple_length = 0

        for i in range(len(all_IO_states)):
            # Partie principale
            if point_trigger_channel != -1 and i == point_trigger_channel:
                main_pattern = self.pattern_calculator(point_trigger_timings, point_trigger_IO)
            elif sequence_trigger_channel != -1 and i == sequence_trigger_channel:
                main_pattern = self.pattern_calculator(sequence_trigger_timings, sequence_trigger_IO)
            else:
                main_pattern = self.pattern_calculator(all_pulse_durations, all_IO_states[i])

            # Préambule
            if sequence_trigger_channel != -1 and i == sequence_trigger_channel:
                preamble = sequence_trigger_preamble
            else:
                preamble = [(preamble_duration, 0)]

            # Concaténation préambule + séquence principale
            final_patterns[i] = preamble + main_pattern
            total_tuple_length += len(final_patterns[i])

        return final_patterns, total_tuple_length

    def export_sequence_summary(self, final_patterns: list, num_points: int, n_repeat: int,
                                min_val: int, max_val: int, path: str):
        """
        Generates a .txt summary file with:
        - Measurement points list
        - Repetitions per point
        - ASCII waveform diagram for one measurement point
        - Variable table
        """
        from gui.pulse_viewer import CHANNEL_LABELS

        pulse_durations, IO_matrix, variable_index, param_per_col = self.read_table()
        meas_points = list(range(min_val, max_val + 1,
                                 max(1, (max_val - min_val) // max(1, num_points - 1))))[:num_points]

        lines = []

        # --- Header ---
        lines.append("=" * 60)
        lines.append("  PyPulse — Sequence Summary")
        lines.append("=" * 60)
        lines.append("")

        # --- Measurement points ---
        lines.append("[ Measurement Points ]")
        lines.append(f"  Min        : {min_val} ns")
        lines.append(f"  Max        : {max_val} ns")
        lines.append(f"  Num points : {num_points}")
        lines.append(f"  Points     : {meas_points}")
        lines.append("")

        # --- Repetitions ---
        lines.append("[ Repetitions ]")
        lines.append(f"  Repetitions per point : {n_repeat}")
        lines.append(f"  Total acquisitions    : {num_points * n_repeat}")
        lines.append("")

        # --- Variable table ---
        lines.append("[ Variables ]")
        lines.append(f"  {'Name':<15} {'Expression':<20} {'Sweep'}")
        lines.append(f"  {'-' * 15} {'-' * 20} {'-' * 5}")
        row_count = self.var_logic.table.rowCount()
        for row in range(row_count):
            name_item = self.var_logic.table.item(row, 0)
            val_item = self.var_logic.table.item(row, 1)
            checkbox = self.var_logic.table.cellWidget(row, 3)
            from PyQt5.QtWidgets import QCheckBox
            name = name_item.text() if name_item else ""
            expr = val_item.text() if val_item else ""
            sweep = "yes" if isinstance(checkbox, QCheckBox) and checkbox.isChecked() else "no"
            if name:
                lines.append(f"  {name:<15} {expr:<20} {sweep}")
        lines.append("")

        # --- ASCII waveform for one point ---
        lines.append("[ Pulse Diagram — one measurement point ]")
        lines.append("")

        cols = len(pulse_durations)
        # Normalize durations to ASCII widths (min 3, max 12 chars per segment)
        col_widths = []
        for col in range(cols):
            var_idx = param_per_col[col]
            var_name_item = self.var_logic.table.item(var_idx, 0) if var_idx is not None else None
            var_name = var_name_item.text() if var_name_item else str(int(pulse_durations[col]))
            col_widths.append(max(len(var_name) + 2, 5))

        # Header: duration row
        dur_row = "  Duration |"
        for col, d in enumerate(pulse_durations):
            w = col_widths[col]
            var_idx = param_per_col[col]
            var_name_item = self.var_logic.table.item(var_idx, 0) if var_idx is not None else None
            var_name = var_name_item.text() if var_name_item else str(int(d))
            txt = var_name[:w].center(w)
            dur_row += txt + "|"

        lines.append(dur_row)
        lines.append("  " + "-" * (len(dur_row) - 2))

        # One row per channel
        for ch in range(len(IO_matrix)):
            label = CHANNEL_LABELS[ch] if ch < len(CHANNEL_LABELS) else f"CH{ch}"
            row_str = f"  {label:<8} |"
            for col in range(cols):
                w = col_widths[col]
                val = IO_matrix[ch][col]
                if val == 1:
                    block = ("T" * (w - 2)).center(w)
                elif val == 0:
                    block = (" " * (w - 2)).center(w)
                else:
                    # Analog: show value
                    block = f"{val:.1f}".center(w)
                row_str += block + "|"
            # Mark variable columns
            if any(IO_matrix[ch][v] != IO_matrix[ch][0] for v in variable_index):
                row_str += "  ← sweep"
            lines.append(row_str)


        # Variable region marker
        if variable_index:
            marker = "  Sweep col |"
            for col in range(cols):
                w = col_widths[col]
                marker += ("^^^" if col in variable_index else " " * w).center(w) + "|"
            lines.append(marker)

        lines.append("")
        lines.append("=" * 60)

        # --- Write file ---
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"Summary exported to {path}")


