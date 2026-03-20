"""
client.py — Remote control of PyPulse via TCP command server.

Prerequisites:
    - PyPulse GUI must be running before connecting.
    - Default: localhost:5025

Quick start (Jupyter notebook):
    import sys
    sys.path.insert(0, r"C:\\path\\to\\PyPulse")
    from client import PyPulseClient

    ps = PyPulseClient()
    ps.connect()
    ps.set_min(0)
    ps.set_max(1000000)
    ps.compute_sequence()
    ps.run_continuous()
    ...
    ps.stop()
    ps.disconnect()
"""

import socket


class PyPulseClient:

    def __init__(self, host="localhost", port=5025):
        self.host  = host
        self.port  = port
        self._sock = None

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self.host, self.port))
        print(f"[PyPulseClient] Connected to {self.host}:{self.port}")

    def disconnect(self):
        if self._sock:
            self._sock.close()
            self._sock = None
            print("[PyPulseClient] Disconnected.")

    def send(self, cmd: str) -> str:
        self._sock.sendall((cmd + "\n").encode())
        return self._sock.recv(4096).decode().strip()

    # --- Identification ---
    def idn(self) -> str:
        return self.send("*IDN?")

    # --- Streaming ---
    def run_continuous(self) -> str:
        return self.send("RUN_CONTINUOUS")

    def run_n_times(self) -> str:
        return self.send("RUN_N_TIMES")

    def stop(self) -> str:
        return self.send("STOP")

    # --- Séquence ---
    def compute_sequence(self) -> str:
        return self.send("COMPUTE_SEQUENCE")

    # --- Config ---
    def load_pulse_config(self, path: str) -> str:
        return self.send(f"LOAD_PULSE_CONFIG {path}")

    def load_var_config(self, path: str) -> str:
        return self.send(f"LOAD_VAR_CONFIG {path}")

    # --- Paramètres sweep ---
    def set_min(self, value: int) -> str:
        return self.send(f"SET_MIN {value}")

    def set_max(self, value: int) -> str:
        return self.send(f"SET_MAX {value}")

    def set_num_points(self, value: int) -> str:
        return self.send(f"SET_NUM_POINTS {value}")

    def set_n_repeat(self, value: int) -> str:
        return self.send(f"SET_N_REPEAT {value}")

    def set_var(self, name: str, expression: str) -> str:
        """
        Update a variable expression in the variable table.

        Example:
            >>> ps.set_var("tau", "t_pi * 2")
            'OK'
        """
        return self.send(f"SET_VAR {name} {expression}")

    # --- Getters ---
    def get(self, key: str) -> str:
        return self.send(f"GET? {key}")


# --- Example usage ---
if __name__ == "__main__":
    ps = PyPulseClient()
    ps.connect()
    print(ps.idn())                          # PyPulse,1.0
    ps.load_pulse_config("config/pulse_config/my_sequence.cfg")
    ps.set_min(0)
    ps.set_max(2000000)
    ps.set_num_points(50)
    ps.compute_sequence()
    ps.run_continuous()
    ps.disconnect()
