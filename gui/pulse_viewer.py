# Widget de visualisation des séquences d'impulsions (pyqtgraph).
# Affiche les formes d'onde de chaque canal en superposition verticale.


class PulseViewer:
    """
    Graphique pyqtgraph représentant les patterns de tous les canaux.
    Chaque canal est décalé verticalement.
    Les zones de paramètre variable sont surlignées (LinearRegionItem).
    """

    def __init__(self):
        pass

    def plot_pattern(self, pattern, channel_labels: list):
        """
        Trace le Pattern complet (tous les canaux).
        channel_labels : noms affichés pour chaque canal.
        """
        pass

    def highlight_variable_region(self, t_start: float, t_end: float):
        """Surligne une région temporelle (paramètre variable)."""
        pass

    def clear(self):
        """Efface le graphique."""
        pass
