import configparser
from PyQt5.QtWidgets import QCheckBox, QTableWidgetItem, QComboBox, QMessageBox, QFileDialog

CHANNEL_COLORS = [
                    "#1f77b4",  # bleu
                    "#ff7f0e",  # orange
                    "#2ca02c",  # vert
                    "#d62728",  # rouge
                    "#9467bd",  # violet
                    "#8c564b",  # brun
                    "#e377c2",  # rose
                    "#7f7f7f",  # gris
                    "#bcbd22",  # jaune-vert
                    "#17becf"   # cyan
                    ]
ROW_LABELS = ["Duration", "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "A0", "A1"]
NUM_DIGITAL_ROWS = 8   # rows 1–8
NUM_ANALOG_ROWS  = 2   # rows 9–10
TOTAL_ROWS       = 1  # row 0 (combobox) + 8 digital + 2 analog + 1 header = 11


class PulseTableWidget:
    """
    Manages the pulse sequence table (tableWidget).
    Row 0    : ComboBox — duration parameter selection
    Rows 1–8 : CheckBox — digital channels DO0–DO7
    Rows 9–10: QTableWidgetItem (float) — analog channels AO0–AO1
    """

    def __init__(self, table_widget, list_variable_names: list, on_change_callback=None):
        self.table = table_widget
        self.table.setVerticalHeaderLabels(ROW_LABELS)
        self._on_change_callback = on_change_callback  # callback externe
        self.list_variable_names = list_variable_names
        self._init_first_column()


    def _init_first_column(self):
        """Initialize the first column on startup."""
        self._create_column(0)

    # --- Internal helpers ---

    def _create_checkbox(self, row: int, col: int) -> QCheckBox:
        btn = QCheckBox()
        btn.setStyleSheet(f"""
            QCheckBox::indicator {{ width: 100px; height: 30px; }}
            QCheckBox::indicator:unchecked {{ background-color: black; }}
            QCheckBox::indicator:checked  {{ background-color: {CHANNEL_COLORS[row - 1]}; }}
        """)
        btn.stateChanged.connect(self._on_change)
        return btn

    def _create_combobox(self) -> QComboBox:
        combo = QComboBox()
        combo.addItems(self.list_variable_names)
        combo.activated.connect(self._on_change)
        return combo

    def _create_column(self, col: int):
        self.table.setCellWidget(0, col, self._create_combobox())
        for row in range(1, 9):
            self.table.setCellWidget(row, col, self._create_checkbox(row, col))
        for row in range(9, 11):
            self.table.setItem(row, col, QTableWidgetItem("0"))
        self.table.setHorizontalHeaderItem(col, QTableWidgetItem(str(col)))
        self.table.resizeColumnsToContents()

    def _copy_column(self, col: int) -> list:
        result = []
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, col)
            if isinstance(widget, QCheckBox):
                result.append(str(widget.isChecked()))
            elif isinstance(widget, QComboBox):
                result.append(str(widget.currentIndex()))
            else:
                item = self.table.item(row, col)
                result.append(item.text() if item else "0")
        return result

    def _fill_column(self, col: int, data: list):
        for row, value in enumerate(data):
            widget = self.table.cellWidget(row, col)
            if isinstance(widget, QCheckBox):
                widget.setChecked(value == "True")
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(int(value))
            else:
                self.table.setItem(row, col, QTableWidgetItem(value or "0"))

    def _copy_digital_row(self, row: int) -> list:
        return [str(self.table.cellWidget(row, col).isChecked())
                for col in range(self.table.columnCount())]

    def _paste_digital_row(self, row: int, data: list):
        for col, value in enumerate(data):
            self.table.cellWidget(row, col).setChecked(value.strip().lower() == "true")

    def _on_change(self):
        """Called whenever a cell value changes — hook for live preview."""
        if self._on_change_callback:
            self._on_change_callback()
        pass

    # --- Public API : columns ---

    def add_column_left(self):
        col = self.table.currentColumn()
        if col == -1:
            print("No column selected.")
            return
        self.table.insertColumn(col)
        self._create_column(col)

    def add_column_right(self):
        col = self.table.currentColumn()
        if col == -1:
            print("No column selected.")
            return
        self.table.insertColumn(col + 1)
        self._create_column(col + 1)

    def remove_column(self):
        col = self.table.currentColumn()
        if col == -1:
            print("No column selected.")
            return
        self.table.removeColumn(col)

    def move_column_left(self):
        col = self.table.currentColumn()
        if col <= 0:
            print("Cannot move column further left.")
            return
        data_cur, data_prev = self._copy_column(col), self._copy_column(col - 1)
        h_cur  = self.table.horizontalHeaderItem(col).text()
        h_prev = self.table.horizontalHeaderItem(col - 1).text()
        self._fill_column(col - 1, data_cur)
        self._fill_column(col,     data_prev)
        self.table.setHorizontalHeaderItem(col,     QTableWidgetItem(h_prev))
        self.table.setHorizontalHeaderItem(col - 1, QTableWidgetItem(h_cur))
        self.table.setCurrentCell(0, col - 1)

    def move_column_right(self):
        col = self.table.currentColumn()
        if col >= self.table.columnCount() - 1:
            print("Cannot move column further right.")
            return
        data_cur, data_next = self._copy_column(col), self._copy_column(col + 1)
        h_cur  = self.table.horizontalHeaderItem(col).text()
        h_next = self.table.horizontalHeaderItem(col + 1).text()
        self._fill_column(col + 1, data_cur)
        self._fill_column(col,     data_next)
        self.table.setHorizontalHeaderItem(col,     QTableWidgetItem(h_next))
        self.table.setHorizontalHeaderItem(col + 1, QTableWidgetItem(h_cur))
        self.table.setCurrentCell(0, col + 1)

    # --- Public API : rows ---

    def invert_row(self):
        row = self.table.currentRow()
        for col in range(self.table.columnCount()):
            widget = self.table.cellWidget(row, col)
            if isinstance(widget, QComboBox):
                print("Cannot invert ComboBox row.")
                return
            elif isinstance(widget, QCheckBox):
                widget.setChecked(not widget.isChecked())
            else:
                item = self.table.item(row, col)
                self.table.setItem(row, col, QTableWidgetItem(str(-float(item.text()))))

    def swap_rows(self):
        selected = sorted(set(idx.row() for idx in self.table.selectedIndexes()))
        for row in selected:
            if row in (9, 10):
                QMessageBox.warning(self.table, "Error", "Only digital rows can be swapped.")
                return
        if len(selected) != 2:
            QMessageBox.warning(self.table, "Error", "Select exactly two rows.")
            return
        r1, r2 = selected
        row1, row2 = self._copy_digital_row(r1), self._copy_digital_row(r2)
        self._paste_digital_row(r1, row2)
        self._paste_digital_row(r2, row1)

    # --- Public API : config ---

    def save_config(self, path: str):
        config = configparser.ConfigParser()
        cols = self.table.columnCount()
        headers = [str(c) for c in range(cols)]
        for row in range(self.table.rowCount()):
            header = self.table.verticalHeaderItem(row)
            section = header.text() if header else str(row)
            config[section] = {}
            for col in range(cols):
                widget = self.table.cellWidget(row, col)
                if isinstance(widget, QComboBox):
                    val = str(widget.currentIndex())
                elif isinstance(widget, QCheckBox):
                    val = str(widget.isChecked())
                else:
                    item = self.table.item(row, col)
                    val = item.text() if item else ""
                config[section][headers[col]] = val
        with open(path, "w", encoding="utf-8") as f:
            config.write(f)
        print(f"Pulse config saved to {path}")

    def load_config(self, path: str):
        config = configparser.ConfigParser()
        with open(path, "r", encoding="utf-8") as f:
            config.read_file(f)
        sections = config.sections()
        if not sections:
            print("Empty config file.")
            return
        headers = list(config[sections[0]].keys())
        self.table.setRowCount(len(sections))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        for col, key in enumerate(headers):
            col_data = [config.get(s, key, fallback="") for s in sections]
            self._create_column(col)
            self._fill_column(col, col_data)

    def update_combobox_items(self, new_names: list):
        """Refresh all ComboBox items when variable names change."""
        self.list_variable_names = new_names
        for col in range(self.table.columnCount()):
            combo = self.table.cellWidget(0, col)
            if isinstance(combo, QComboBox):
                idx = combo.currentIndex()
                combo.clear()
                combo.addItems(new_names)
                combo.setCurrentIndex(idx)

    def refresh(self):
        self.table.viewport().update()
