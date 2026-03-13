# Programme 1 — Contrôle basique de la PulseStreamer.
# Objectif : valider la connexion et le pipeline complet Pattern → Sequence → stream.

from sequences.base_sequence import BaseSequence


class Programme1(BaseSequence):
    """
    Séquence minimale de test.
    Hérite de BaseSequence.
    """

    def __init__(self, ps_driver):
        pass

    def build_pattern(self, **kwargs):
        """
        Construit le Pattern pour le Programme 1.
        Paramètres attendus en kwargs : à définir.
        """
        pass

    def run(self, **kwargs):
        """
        Construit le Pattern, le convertit en Sequence et lance le streaming.
        """
        pass

    def stop(self):
        """Arrête le streaming."""
        pass
