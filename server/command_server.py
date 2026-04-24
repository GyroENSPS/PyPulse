"""
TCP command server — remote control of PyPulse from an external script.
Listens on localhost:5025, SCPI-like text protocol.
Commands simulate button clicks on the interface.
"""

import socket
import threading
from PyQt5.QtCore import QObject, pyqtSignal


class CommandServer(QObject):

    command_received = pyqtSignal(str, object)

    def __init__(self, window, host="localhost", port=5025):
        super().__init__()
        self.window = window
        self.host   = host
        self.port   = port
        self._running = False
        self.command_received.connect(self._execute_command)

    def start(self):
        self._running = True
        t = threading.Thread(target=self._serve, daemon=True)
        t.start()
        print(f"[PyPulse Server] Listening on {self.host}:{self.port}")

    def stop(self):
        self._running = False

    def _serve(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((self.host, self.port))
            srv.listen(5)
            while self._running:
                try:
                    srv.settimeout(1.0)
                    conn, addr = srv.accept()
                    t = threading.Thread(target=self._handle_client,
                                         args=(conn,), daemon=True)
                    t.start()
                except socket.timeout:
                    continue

    def _handle_client(self, conn):
        with conn:
            while True:
                try:
                    data = conn.recv(4096)
                    if not data:
                        break
                    cmd = data.decode().strip()
                    self.command_received.emit(cmd, conn)
                except Exception:
                    break

    def _execute_command(self, cmd: str, conn):
        """Executed in the Qt main thread."""
        try:
            response = self._dispatch(cmd)
        except Exception as e:
            response = f"ERROR {e}"
        try:
            conn.sendall((response + "\n").encode())
        except Exception:
            pass

    def _dispatch(self, cmd: str) -> str:
        w = self.window

        if cmd == "*IDN?":
            return "PyPulse,1.0"

        elif cmd == "RUN_CONTINUOUS":
            w.ui.pushButton_PS_run_continuous.click()
            return "OK"

        elif cmd == "RUN_N_TIMES":
            w.ui.pushButton_PS_run_N_times.click()
            return "OK"

        elif cmd == "STOP":
            w.ui.pushButton_PS_reset.click()
            return "OK"

        elif cmd == "COMPUTE_SEQUENCE":
            w.ui.pushButton_compute_sequence.click()
            return "OK"

        elif cmd == "SAVE_PULSE_CONFIG":
            w.ui.pushButton_save_pulse_config.click()
            return "OK"

        elif cmd.startswith("LOAD_PULSE_CONFIG "):
            path = cmd[18:].strip()
            w.pulse_table.load_config(path)
            return "OK"

        elif cmd.startswith("LOAD_VAR_CONFIG "):
            path = cmd[16:].strip()
            w.var_logic.load_config(path)
            return "OK"

        elif cmd.startswith("SET_MIN "):
            w.ui.spinBox_min.setValue(int(cmd[8:].strip()))
            return "OK"

        elif cmd.startswith("SET_MAX "):
            w.ui.spinBox_max.setValue(int(cmd[8:].strip()))
            return "OK"

        elif cmd.startswith("SET_NUM_POINTS "):
            w.ui.spinBox_num_points.setValue(int(cmd[15:].strip()))
            return "OK"

        elif cmd.startswith("SET_N_REPEAT "):
            w.ui.spinBox_n_repeat.setValue(int(cmd[13:].strip()))
            return "OK"

        elif cmd.startswith("SET_VAR "):
            # Syntax: SET_VAR <name> <expression>
            parts = cmd[8:].split(None, 1)
            if len(parts) < 2:
                return "ERROR Usage: SET_VAR <name> <expression>"
            var_name, expression = parts[0], parts[1]
            table = w.var_logic.table
            for row in range(table.rowCount()):
                name_item = table.item(row, 0)
                if name_item and name_item.text().strip() == var_name:
                    from PyQt5.QtWidgets import QTableWidgetItem
                    table.setItem(row, 1, QTableWidgetItem(expression))
                    return "OK"
            return f"ERROR Variable '{var_name}' not found"

        elif cmd == "GET? min":
            return str(w.ui.spinBox_min.value())

        elif cmd == "GET? max":
            return str(w.ui.spinBox_max.value())

        elif cmd == "GET? num_points":
            return str(w.ui.spinBox_num_points.value())

        elif cmd == "GET? n_repeat":
            return str(w.ui.spinBox_n_repeat.value())

        else:
            return f"ERROR Unknown command: {cmd}"
