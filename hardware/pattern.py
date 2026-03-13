import numpy as np


class Pattern:
    """
    Canaux digitaux : 0–7  (valeur : 0 ou 1)
    Canaux analogiques : 0–1  (valeur : float en V)
    Stockage : {canal: [(durée_ns, valeur), ...]}
    """

    def __init__(self):
        self.p = {}

    def set_digital(self, channel: int, pattern: list):
        self.p[channel] = pattern

    def set_analog(self, channel: int, pattern: list):
        self.p[channel] = pattern

    def get_channels(self):
        return self.p.keys()

    def get_pattern(self, channel: int) -> list:
        return self.p[channel]

    def get_length(self, channel: int = -1) -> int:
        if channel >= 0:
            return int(np.sum([t[0] for t in self.p[channel]]))
        return max(self.get_length(c) for c in self.get_channels()) if self.p else 0

    def equalize(self):
        length = self.get_length()
        for c in self.get_channels():
            diff = length - self.get_length(c)
            if diff > 0:
                self.p[c] = self.p[c] + [(diff, 0)]

    def repeat(self, n: int) -> 'Pattern':
        self.equalize()
        for c in self.get_channels():
            self.p[c] = self.p[c] * n
        return self

    def append(self, other: 'Pattern') -> 'Pattern':
        self.equalize()
        other.equalize()
        length = self.get_length()
        # Canaux présents dans other mais pas dans self → ajouter silence initial
        for c in other.get_channels():
            if c not in self.get_channels():
                self.p[c] = [(length, 0)]
        for c in self.get_channels():
            if c in other.get_channels():
                self.p[c] = self.p[c] + other.p[c]
        return self
