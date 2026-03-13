# Fenêtre principale de l'application.
# Hérite de QMainWindow et de la classe UI générée par Qt Designer.


class MainWindow:
    """
    Fenêtre principale.
    Instancie le PS_worker dans un QThread dédié.
    Connecte les signaux Qt aux slots de la logique.
    """

    def __init__(self):
        pass

    def init_ps(self):
        """Instancie PulseStreamerDriver et le déplace dans un QThread."""
        pass

    def on_start(self):
        """Slot : bouton Start — lance la séquence sélectionnée."""
        pass

    def on_stop(self):
        """Slot : bouton Stop — arrête le streaming."""
        pass

    def on_reset(self):
        """Slot : bouton Reset — remet les sorties à 0."""
        pass
