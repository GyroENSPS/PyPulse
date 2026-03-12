# Fonctions utilitaires pour la manipulation de patterns
import numpy as np


def pattern_to_arrays(pattern_tuples: list) -> tuple:
    """
    Convertit une liste de tuples (durée, valeur) en deux tableaux numpy
    pour la visualisation.

    Retourne (timings, values).
    """
    timings = np.cumsum([0] + [t[0] for t in pattern_tuples])
    values = np.array([t[1] for t in pattern_tuples] + [0])
    return timings, values


def make_empty_pattern(total_duration_ns: int, value=0) -> list:
    """Retourne un pattern plat (une seule durée, valeur constante)."""
    return [(total_duration_ns, value)]
