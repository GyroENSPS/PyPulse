# Classe Pattern — représentation multi-canaux d'une séquence d'impulsions.
# Un pattern est un dictionnaire {canal: [(durée_ns, valeur), ...]}.


class Pattern:
    """
    Représente un ensemble de canaux (digitaux ou analogiques)
    sous la forme de listes de tuples (durée en ns, valeur).

    Canaux digitaux : 0–7  (valeur : 0 ou 1)
    Canaux analogiques : 0–1  (valeur : float en V)
    """

    def __init__(self):
        pass

    # --- Affectation des canaux ---

    def set_digital(self, channel: int, pattern: list) -> None:
        """Affecte un pattern à un canal digital (0–7)."""
        pass

    def set_analog(self, channel: int, pattern: list) -> None:
        """Affecte un pattern à un canal analogique (0–1)."""
        pass

    # --- Lecture ---

    def get_channels(self) -> list:
        """Retourne la liste de tous les canaux définis."""
        pass

    def get_pattern(self, channel: int) -> list:
        """Retourne le pattern d'un canal donné."""
        pass

    def get_length(self, channel: int = -1) -> int:
        """
        Retourne la durée totale (ns) d'un canal.
        Si channel == -1, retourne le maximum sur tous les canaux.
        """
        pass

    # --- Manipulation ---

    def equalize(self) -> None:
        """
        Égalise la durée de tous les canaux en prolongeant les plus courts
        avec un segment à 0 (LOW / 0 V).
        """
        pass

    def repeat(self, n: int) -> 'Pattern':
        """
        Répète le pattern n fois sur tous les canaux.
        Égalise d'abord les canaux.
        Retourne self.
        """
        pass

    def append(self, other: 'Pattern') -> 'Pattern':
        """
        Concatène un autre Pattern à la suite de celui-ci.
        Égalise les deux patterns avant la concaténation.
        Retourne self.
        """
        pass
