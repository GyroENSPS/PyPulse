import configparser
from PyQt5.QtWidgets import QCheckBox, QTableWidgetItem, QFileDialog


class VarLogic:
    """
    Manages the variable table (tableWidget_var).
    Columns: name | value | description | variable (CheckBox sweep flag)
    """

    def __init__(self, var_table_widget, pulse_table_widget_ref):
        self.table = var_table_widget
        self.pulse_table = pulse_table_widget_ref  # PulseTableWidget instance
        self.python_var_flag = False
        self._init_first_row()
        try:
            self.load_config(r"config\var_config\default_var_config.cfg")
            self.pulse_table.load_config(r"config\pulse_config\default_pulse.cfg")

        except Exception as e:
            print("Error : ", e)

    def _init_first_row(self):
        """Add default first row on startup."""
        self.add_var_row()

    # --- Internal helpers ---

    def _create_var_row(self, row: int):
        self.table.setItem(row, 0, QTableWidgetItem(f"param_{row}"))
        self.table.setItem(row, 1, QTableWidgetItem("0"))
        btn = QCheckBox()
        btn.clicked.connect(lambda _, r=row: self._on_var_change(r))
        self.table.setCellWidget(row, 3, btn)

    def _fill_row(self, row: int, data: list):
        for col, value in enumerate(data):
            widget = self.table.cellWidget(row, col)
            if isinstance(widget, QCheckBox):
                widget.setChecked(value == "True")
            else:
                self.table.setItem(row, col, QTableWidgetItem(value))

    def _on_var_change(self, row: int):
        """Called when a variable checkbox changes."""
        pass

    # --- Public API ---

    def add_var_row(self):
        """Append a new variable row at the bottom."""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self._create_var_row(row)
        self.update_param_names()

    def read_var_table(self) -> tuple:
        """
        Returns (var_names, var_instructions, sweep_var_indices).
        var_names        : list of str
        var_instructions : list of str (Python expressions)
        sweep_var_indices: list of int (rows flagged as sweep variable)
        """
        var_names, var_instructions, sweep_indices = [], [], []
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            val_item  = self.table.item(row, 1)
            checkbox  = self.table.cellWidget(row, 3)
            var_names.append(name_item.text() if name_item else "")
            var_instructions.append(val_item.text() if val_item else "0")
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                sweep_indices.append(row)
        return var_names, var_instructions, sweep_indices

    def update_param_names(self):
        """Sync variable names into all ComboBoxes of the pulse table."""
        if self.python_var_flag:
            return
        names = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            names.append(item.text() if item else "")
        self.pulse_table.update_combobox_items(names)

    def create_python_var(self) -> list:
        row_count = self.table.rowCount()
        var_names = [None] * row_count
        var_values = [None] * row_count

        run_cond = True
        error_count = 0

        while run_cond and error_count < 100:
            run_cond = False
            for row in range(row_count):
                name_item = self.table.item(row, 0)
                val_item = self.table.item(row, 1)

                # Skip incomplete rows
                if name_item is None or val_item is None:
                    continue
                var_name_str = name_item.text().strip()
                var_value_str = val_item.text().strip()
                if not var_name_str or not var_value_str:
                    continue

                var_names[row] = var_name_str
                code_line = f"{var_name_str} = {var_value_str}"
                try:
                    exec(code_line)
                    exec(f"var_values[row] = {var_name_str}")
                except Exception as e:
                    run_cond = True
                    error_count += 1
                    print(f"Error n°{error_count} while resolving row {row}: {code_line} → {e}")

        return var_values

    def sort_and_resolve(self) -> list:
        """
        Sorts variable rows to resolve dependencies (bubbles unresolvable rows downward),
        then evaluates all expressions. Updates ComboBoxes after sorting.
        """
        row_count = self.table.rowCount()
        var_names = [None] * row_count
        var_values = [None] * row_count

        run_cond = True
        error_count = 0

        while run_cond and error_count < 100:
            run_cond = False
            for row in range(row_count):
                name_item = self.table.item(row, 0)
                val_item = self.table.item(row, 1)

                # Skip incomplete rows
                if name_item is None or val_item is None:
                    continue
                var_name_str = name_item.text().strip()
                var_value_str = val_item.text().strip()
                if not var_name_str or not var_value_str:
                    continue

                var_names[row] = var_name_str
                code_line = f"{var_name_str} = {var_value_str}"
                try:
                    exec(code_line)
                    exec(f"var_values[row] = {var_name_str}")
                except Exception as e:
                    run_cond = True
                    error_count += 1
                    print(f"Error n°{error_count} while resolving row {row}: {code_line} → {e}")
                    if row < row_count - 1:
                        self.swap_vars(row, row + 1)

        self.update_param_names()
        return var_values

    def swap_vars(self, row_a: int, row_b: int):
        """Swap two rows in the variable table."""
        self.python_var_flag = True
        cols = self.table.columnCount()
        row1, row2 = [], []
        for col in range(cols):
            w1 = self.table.cellWidget(row_a, col)
            w2 = self.table.cellWidget(row_b, col)
            if isinstance(w1, QCheckBox):
                row1.append(str(w1.isChecked()))
            else:
                item = self.table.item(row_a, col)
                row1.append(item.text() if item else "0")
            if isinstance(w2, QCheckBox):
                row2.append(str(w2.isChecked()))
            else:
                item = self.table.item(row_b, col)
                row2.append(item.text() if item else "0")
        self._fill_row(row_b, row1)
        self._fill_row(row_a, row2)
        self.python_var_flag = False
        self.update_param_names()

    def save_config(self, path: str):
        config = configparser.ConfigParser()
        rows = self.table.rowCount()
        row_keys = [str(r) for r in range(rows)]
        for col in range(self.table.columnCount()):
            header = self.table.horizontalHeaderItem(col)
            section = header.text() if header else str(col)
            config[section] = {}
            for row in range(rows):
                widget = self.table.cellWidget(row, col)
                if isinstance(widget, QCheckBox):
                    val = str(widget.isChecked())
                else:
                    item = self.table.item(row, col)
                    val = item.text() if item else "0"
                config[section][row_keys[row]] = val
        with open(path, "w", encoding="utf-8") as f:
            config.write(f)
        print(f"Var config saved to {path}")

    def load_config(self, path: str):
        config = configparser.ConfigParser()
        with open(path, "r", encoding="utf-8") as f:
            config.read_file(f)
        sections = config.sections()
        if not sections:
            print("Empty config file.")
            return
        keys = list(config[sections[0]].keys())
        self.table.clearContents()
        self.table.setRowCount(len(keys))
        self.table.setColumnCount(len(sections))
        self.table.setHorizontalHeaderLabels(sections)
        for row, key in enumerate(keys):
            row_data = [config.get(s, key, fallback="") for s in sections]
            self._create_var_row(row)
            self._fill_row(row, row_data)
        self.update_param_names()
