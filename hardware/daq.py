# Driver carte NI DAQ
import nidaqmx
from PyQt5.QtCore import QObject, pyqtSignal


class DAQDriver(QObject):
    """Interface bas niveau pour la carte NI DAQ."""

    data_acquired = pyqtSignal(object)  # émet un np.ndarray à chaque acquisition
    error_occurred = pyqtSignal(str)

    def __init__(self, device_name: str = "Dev1"):
        super().__init__()
        self.device_name = device_name

    def read_analog(self, channel: str, n_samples: int, rate: float) -> list:
        """Lecture analogique simple (bloquante)."""
        task_path = f"{self.device_name}/{channel}"
        try:
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(task_path)
                task.timing.cfg_samp_clk_timing(rate, samps_per_chan=n_samples)
                data = task.read(number_of_samples_per_channel=n_samples)
            self.data_acquired.emit(data)
            return data
        except Exception as e:
            self.error_occurred.emit(str(e))
            print(f"[DAQ] Erreur : {e}")
            return []
