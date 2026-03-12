# Classe de base pour toutes les séquences de mesure
from abc import ABC, abstractmethod
from hardware.pulse_streamer import PulseStreamerDriver


class BaseSequence(ABC):
    """
    Classe abstraite dont héritent toutes les séquences (Rabi, T1, T2…).
    Chaque séquence doit implémenter `build_pattern()` et `run()`.
    """

    def __init__(self, ps_driver: PulseStreamerDriver):
        self.ps = ps_driver
        self._pattern_tuples = None  # list[list[tuple]]

    @abstractmethod
    def build_pattern(self, **kwargs) -> list:
        """
        Construit et retourne la liste de 10 patterns
        (indices 0-7 : digitaux, 8-9 : analogiques).
        """
        ...

    @abstractmethod
    def run(self, **kwargs):
        """Charge le pattern et lance le streaming."""
        ...

    def stop(self):
        self.ps.stop()
