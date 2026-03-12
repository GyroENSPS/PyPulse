# SequenceBuilder — convertit un Pattern en objet Sequence PulseStreamer.
# Fait le lien entre la logique métier (Pattern) et l'API bas niveau.


class SequenceBuilder:
    """
    Prend un Pattern (multi-canaux) et le convertit en Sequence
    prête à être streamée par la PulseStreamer.
    """

    def __init__(self, ps_driver):
        """ps_driver : instance de PulseStreamerDriver."""
        pass

    def build(self, pattern) -> object:
        """
        Convertit un Pattern en objet Sequence (API pulsestreamer).
        Affecte les canaux digitaux (setDigital) et analogiques (setAnalog).
        Retourne l'objet Sequence.
        """
        pass
