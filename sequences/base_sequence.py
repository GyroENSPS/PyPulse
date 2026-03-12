# Classe de base abstraite pour toutes les séquences de mesure.


class BaseSequence:
    """
    Toutes les séquences (Programme 1, Rabi, T1…) héritent de cette classe.
    Impose l'interface : build_pattern() → run().
    """

    def __init__(self, ps_driver):
        """ps_driver : instance de PulseStreamerDriver."""
        pass

    def build_pattern(self, **kwargs):
        """
        Construit et retourne un objet Pattern correspondant à la séquence.
        Les paramètres propres à chaque séquence sont passés en kwargs.
        À surcharger dans chaque sous-classe.
        """
        pass

    def run(self, **kwargs):
        """
        Appelle build_pattern(), construit la Sequence et lance le streaming.
        À surcharger dans chaque sous-classe.
        """
        pass

    def stop(self):
        """Arrête le streaming en cours."""
        pass
