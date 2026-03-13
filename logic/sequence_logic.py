# Logique de génération et de calcul des séquences.
# Fait le lien entre le tableau (PulseTableWidget) et le driver (PulseStreamerDriver).


class SequenceLogic:
    """
    Orchestre le pipeline complet :
    tableau → paramètres → Pattern → Sequence → stream.
    """

    def __init__(self, ps_driver):
        pass

    # --- Paramètres ---

    def read_table(self):
        """
        Lit les données du PulseTableWidget et retourne
        (pulse_durations, IO_matrix, variable_index).
        """
        pass

    def resolve_variables(self, var_names: list, var_instructions: list) -> list:
        """
        Évalue les expressions Python des variables utilisateur
        et retourne la liste des valeurs numériques.
        """
        pass

    def update_pulse_durations(self, names: list, instructions: list, point) -> list:
        """
        Recalcule les durées de pulses pour un point de mesure donné
        (en substituant la variable de balayage).
        """
        pass

    # --- Génération de séquence ---

    def build_pattern_from_table(self) -> object:
        """
        Construit un Pattern à partir du tableau courant.
        Retourne un objet Pattern.
        """
        pass

    def build_measurement_sequence(self, num_points: int, n_repeat: int,
                                   min_val, max_val) -> list:
        """
        Génère la séquence complète de mesure (balayage du paramètre variable)
        avec triggers par point et par séquence.
        Retourne la liste de patterns finaux (un par canal).
        """
        pass

    def pattern_calculator(self, pulse_durations: list, io_states: list) -> list:
        """
        Compresse une liste de durées et d'états en une liste de tuples
        (durée, valeur) en fusionnant les segments consécutifs de même valeur.
        """
        pass

    # --- Streaming ---

    def stream_sequence(self, final_patterns: list):
        """Charge et lance en streaming la séquence finale."""
        pass

    def stop_stream(self):
        """Arrête le streaming."""
        pass
