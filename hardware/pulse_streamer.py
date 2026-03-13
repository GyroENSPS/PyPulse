# Driver bas niveau — PulseStreamer 8/2 (Swabian Instruments)
# Gère la connexion, la configuration et le streaming.


class PulseStreamerDriver:
    """
    Interface directe avec la PulseStreamer.
    Responsabilité : connexion, horloge, stream, stop, reset.
    """

    def __init__(self, ip: str):
        pass

    # --- Connexion ---

    def connect(self):
        """Établit la connexion avec la PulseStreamer via son IP."""
        pass

    def disconnect(self):
        """Remet les sorties à 0 et libère la connexion."""
        pass

    def is_connected(self) -> bool:
        """Retourne True si la connexion est active."""
        pass

    # --- Horloge ---

    def select_internal_clock(self):
        """Sélectionne l'horloge interne de la PulseStreamer."""
        pass

    def select_external_clock(self):
        """Sélectionne une horloge externe 10 MHz."""
        pass

    # --- Séquence ---

    def create_sequence(self) -> object:
        """Crée et retourne un objet Sequence vide (API pulsestreamer)."""
        pass

    def load_sequence(self, sequence) -> None:
        """Charge un objet Sequence dans la PulseStreamer (sans démarrer)."""
        pass

    # --- Streaming ---

    def stream_infinite(self, sequence) -> None:
        """Lance la séquence en boucle infinie."""
        pass

    def stream_n_times(self, sequence, n: int) -> None:
        """Lance la séquence n fois."""
        pass

    def stop(self) -> None:
        """Arrête le streaming en cours."""
        pass

    def reset(self) -> None:
        """Remet toutes les sorties à 0 (état initial)."""
        pass
