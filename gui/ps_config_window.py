# Fenêtre de configuration de la PulseStreamer (IP, horloge…).


class PSConfigWindow:
    """
    Fenêtre secondaire permettant de configurer :
    - l'adresse IP de la PulseStreamer
    - la source d'horloge (interne / externe 10 MHz)
    """

    def __init__(self):
        pass

    def load_config(self):
        """Charge la configuration depuis le fichier .cfg."""
        pass

    def save_config(self):
        """Sauvegarde la configuration dans le fichier .cfg."""
        pass

    def apply_config(self):
        """Applique la configuration à l'instance PulseStreamerDriver."""
        pass
