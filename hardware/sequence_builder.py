from hardware.pattern import Pattern


class SequenceBuilder:
    """
    Convertit final_patterns (list de listes de tuples) en objet Sequence
    prêt à être streamé via PulseStreamerDriver.
    """

    def __init__(self, ps_driver):
        self.driver = ps_driver

    def build(self, final_patterns: list):
        """
        final_patterns : liste de 10 éléments
          [0–7]  → canaux digitaux
          [8–9]  → canaux analogiques
        Retourne un objet Sequence (API pulsestreamer).
        """
        pattern_digital = Pattern()
        pattern_analog  = Pattern()

        for i in range(8):
            if final_patterns[i] is not None:
                pattern_digital.set_digital(i, final_patterns[i])

        for i in range(8, 10):
            if final_patterns[i] is not None:
                pattern_analog.set_analog(i - 8, final_patterns[i])

        sequence = self.driver.create_sequence()

        for channel in pattern_digital.get_channels():
            sequence.setDigital(channel, pattern_digital.get_pattern(channel))

        for channel in pattern_analog.get_channels():
            sequence.setAnalog(channel, pattern_analog.get_pattern(channel))

        print("Sequence ready.")
        return sequence
