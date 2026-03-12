# Driver PulseStreamer 8/2 — Swabian Instruments
import numpy as np
from pulsestreamer import PulseStreamer, Sequence, ClockSource
from PyQt5.QtCore import QObject, pyqtSignal


class Pattern:
    """Représente un pattern multi-canaux sous forme de listes de tuples (durée, valeur)."""

    def __init__(self):
        self.p = {}  # {channel_id: [(duration_ns, value), ...]}

    def set_digital(self, channel: int, pattern: list):
        self.p[channel] = pattern

    def set_analog(self, channel: int, pattern: list):
        self.p[channel] = pattern

    def get_length(self, channel: int = -1) -> int:
        """Retourne la durée totale (ns) d'un canal ou du pattern entier."""
        if channel >= 0:
            return int(np.sum(self.p[channel], axis=0)[0])
        return max(self.get_length(c) for c in self.get_channels()) if self.p else 0

    def get_channels(self):
        return self.p.keys()

    def equalize(self):
        """Égalise la durée de tous les canaux en ajoutant un segment LOW à la fin."""
        length = self.get_length()
        for c in self.get_channels():
            diff = length - self.get_length(c)
            if diff > 0:
                self.p[c] = self.p[c] + [(diff, 0)]

    def repeat(self, num: int) -> 'Pattern':
        self.equalize()
        for c in self.get_channels():
            self.p[c] = self.p[c] * num
        return self

    def append(self, pattern: 'Pattern') -> 'Pattern':
        self.equalize()
        pattern.equalize()
        length = self.get_length()
        for c in pattern.get_channels():
            if c not in self.get_channels():
                self.p[c] = [(length, 0)]
        for c in self.get_channels():
            if c in pattern.get_channels():
                self.p[c] = self.p[c] + pattern.p[c]
        return self


class PulseStreamerDriver(QObject):
    """Interface haut niveau pour la PulseStreamer 8/2."""

    streaming_started = pyqtSignal()
    streaming_stopped = pyqtSignal()
    error_occurred = pyqtSignal(str)

    # Canaux digitaux : 0-7 | Canaux analogiques : 8 (AO0), 9 (AO1)
    N_DIGITAL = 8
    N_ANALOG  = 2

    def __init__(self, ip: str = "169.254.8.2", use_ext_clock: bool = False):
        super().__init__()
        self.ip = ip
        self.use_ext_clock = use_ext_clock
        self._ps = None
        self._connected = False

    # ------------------------------------------------------------------
    # Connexion
    # ------------------------------------------------------------------
    def connect(self) -> bool:
        """Ouvre la connexion avec la PulseStreamer."""
        try:
            self._ps = PulseStreamer(self.ip)
            if self.use_ext_clock:
                self._ps.selectClock(ClockSource.EXT_10MHZ)
            self._connected = True
            print(f"[PS] Connecté à {self.ip}")
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            print(f"[PS] Erreur de connexion : {e}")
            return False

    def disconnect(self):
        """Remet la PulseStreamer en état initial et ferme la connexion logique."""
        if self._connected:
            self._ps.reset()
            self._connected = False
            print("[PS] Déconnecté.")

    @property
    def connected(self) -> bool:
        return self._connected

    # ------------------------------------------------------------------
    # Chargement de pattern
    # ------------------------------------------------------------------
    def load_pattern(self, pattern_tuples: list) -> Sequence:
        """
        Convertit une liste de 10 patterns (8 digitaux + 2 analogiques)
        en objet Sequence PulseStreamer.

        pattern_tuples : list[list[tuple]]
            Indices 0-7  → canaux digitaux DO0..DO7
            Indices 8-9  → canaux analogiques AO0, AO1
        """
        if not self._connected:
            raise RuntimeError("PulseStreamer non connectée.")

        pat_dig = Pattern()
        pat_ana = Pattern()

        for i in range(self.N_DIGITAL):
            pat_dig.set_digital(i, pattern_tuples[i])
        for i in range(self.N_ANALOG):
            pat_ana.set_analog(i, pattern_tuples[self.N_DIGITAL + i])

        seq = self._ps.createSequence()
        for ch in pat_dig.get_channels():
            seq.setDigital(ch, pat_dig.p[ch])
        for ch in pat_ana.get_channels():
            seq.setAnalog(ch, pat_ana.p[ch])

        print("[PS] Séquence chargée.")
        return seq

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------
    def run_continuous(self, seq: Sequence):
        """Lance la séquence en boucle infinie."""
        if not self._connected:
            raise RuntimeError("PulseStreamer non connectée.")
        self._ps.stream(seq, PulseStreamer.REPEAT_INFINITELY)
        self.streaming_started.emit()
        print("[PS] Streaming démarré (infini).")

    def run_n_times(self, seq: Sequence, n: int):
        """Lance la séquence n fois."""
        if not self._connected:
            raise RuntimeError("PulseStreamer non connectée.")
        self._ps.stream(seq, n)
        self.streaming_started.emit()
        print(f"[PS] Streaming démarré ({n} répétitions).")

    def stop(self):
        """Arrête le streaming et remet toutes les sorties à 0."""
        if self._connected:
            self._ps.reset()
            self.streaming_stopped.emit()
            print("[PS] Streaming arrêté.")
