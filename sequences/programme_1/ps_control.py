# Programme 1 — Contrôle basique de la PulseStreamer
# Objectif : valider la connexion et streamer une séquence simple
import numpy as np
from hardware.pulse_streamer import PulseStreamerDriver
from sequences.base_sequence import BaseSequence


class SimplePS(BaseSequence):
    """
    Séquence minimale : créneau sur DO0, toutes les autres sorties à 0.
    Permet de valider la connexion et le pipeline de streaming.
    """

    def build_pattern(self, high_ns: int = 500, low_ns: int = 500) -> list:
        """
        Construit un créneau simple sur DO0.

        Paramètres
        ----------
        high_ns : durée du niveau HIGH (ns)
        low_ns  : durée du niveau LOW  (ns)
        """
        # Canal DO0 : créneau haut/bas
        do0 = [(high_ns, 1), (low_ns, 0)]

        # Canaux DO1-DO7 : toujours à 0
        empty = [(high_ns + low_ns, 0)]

        # Canaux analogiques AO0, AO1 : 0.0 V
        analog_empty = [(high_ns + low_ns, 0.0)]

        pattern_tuples = [do0] + [empty] * 7 + [analog_empty, analog_empty]
        self._pattern_tuples = pattern_tuples
        return pattern_tuples

    def run(self, high_ns: int = 500, low_ns: int = 500, n_repeat: int = -1):
        """
        Construit et lance la séquence.

        Paramètres
        ----------
        n_repeat : nombre de répétitions (-1 = infini)
        """
        pattern_tuples = self.build_pattern(high_ns=high_ns, low_ns=low_ns)
        seq = self.ps.load_pattern(pattern_tuples)
        if n_repeat == -1:
            self.ps.run_continuous(seq)
        else:
            self.ps.run_n_times(seq, n_repeat)
