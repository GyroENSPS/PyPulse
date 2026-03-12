# Driver source RF Keysight (via VISA)
from PyQt5.QtCore import QObject, pyqtSignal

try:
    import pyvisa
    VISA_AVAILABLE = True
except ImportError:
    VISA_AVAILABLE = False


class RFSourceDriver(QObject):
    """Interface bas niveau pour la source RF Keysight."""

    error_occurred = pyqtSignal(str)

    def __init__(self, address: str = "TCPIP0::192.168.1.1::inst0::INSTR"):
        super().__init__()
        self.address = address
        self._instrument = None

    def connect(self) -> bool:
        if not VISA_AVAILABLE:
            print("[RF] pyvisa non installé.")
            return False
        try:
            rm = pyvisa.ResourceManager()
            self._instrument = rm.open_resource(self.address)
            print(f"[RF] Connecté à {self.address}")
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False

    def set_frequency(self, freq_hz: float):
        if self._instrument:
            self._instrument.write(f":FREQ {freq_hz}")

    def set_power(self, power_dbm: float):
        if self._instrument:
            self._instrument.write(f":POW {power_dbm}DBM")

    def set_output(self, state: bool):
        val = "ON" if state else "OFF"
        if self._instrument:
            self._instrument.write(f":OUTP {val}")

    def disconnect(self):
        if self._instrument:
            self._instrument.close()
            self._instrument = None
