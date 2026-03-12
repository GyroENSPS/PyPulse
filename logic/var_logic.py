# Logique du tableau de variables utilisateur.
# Gère les noms, les expressions et l'ordre de résolution.


class VarLogic:
    """
    Gère les variables définies par l'utilisateur dans le tableau des variables.
    Chaque variable a : un nom, une expression Python, et un flag 'variable de balayage'.
    """

    def __init__(self):
        pass

    def read_var_table(self) -> tuple:
        """
        Lit le tableau et retourne (var_names, var_instructions, sweep_var_indices).
        """
        pass

    def sort_and_resolve(self) -> list:
        """
        Trie les variables par dépendances et évalue leurs valeurs.
        Retourne la liste ordonnée de valeurs numériques.
        """
        pass

    def swap_vars(self, row_a: int, row_b: int):
        """Échange deux lignes du tableau des variables."""
        pass

    def update_param_names(self):
        """Met à jour les noms de paramètres dans les ComboBox du tableau de pulses."""
        pass
