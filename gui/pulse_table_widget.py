# Widget tableau de la séquence d'impulsions.
# Reproduit la logique de PulseTableLogic de Pypulse_v2.


class PulseTableWidget:
    """
    Tableau interactif représentant la séquence d'impulsions :
    - Ligne 0       : ComboBox — sélection du paramètre de durée
    - Lignes 1–8    : CheckBox — état des canaux digitaux DO0–DO7
    - Lignes 9–10   : valeur flottante — canaux analogiques AO0–AO1
    Chaque colonne correspond à un segment de la séquence.
    """

    def __init__(self):
        pass

    # --- Colonnes ---

    def add_column_left(self):
        """Insère une colonne à gauche de la colonne sélectionnée."""
        pass

    def add_column_right(self):
        """Insère une colonne à droite de la colonne sélectionnée."""
        pass

    def remove_column(self):
        """Supprime la colonne sélectionnée."""
        pass

    def move_column_left(self):
        """Déplace la colonne sélectionnée vers la gauche."""
        pass

    def move_column_right(self):
        """Déplace la colonne sélectionnée vers la droite."""
        pass

    # --- Lignes ---

    def invert_row(self):
        """Inverse l'état de toute la ligne sélectionnée."""
        pass

    def swap_rows(self):
        """Échange le contenu de deux lignes sélectionnées."""
        pass

    # --- Export / Import ---

    def save_config(self, path: str):
        """Exporte la configuration du tableau dans un fichier .cfg."""
        pass

    def load_config(self, path: str):
        """Charge une configuration de tableau depuis un fichier .cfg."""
        pass

    # --- Affichage ---

    def refresh(self):
        """Rafraîchit l'affichage du tableau."""
        pass
