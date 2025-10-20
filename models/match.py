class Match:
    """
    Representa un partido de básquet en curso o a disputar.
    Contiene la referencia a los equipos, el tipo de juego y el estado actual.
    """

    def __init__(self, team_local, team_visit, game_type):
        # --- Datos base ---
        self.team_local = team_local
        self.team_visit = team_visit
        self.game_type = game_type

        # --- Estado dinámico ---
        self.current_period = 1
        self.points_local = 0
        self.points_visit = 0
        self.fouls_local = 0
        self.fouls_visit = 0

    # -------------------------------------------------
    # 📦 Métodos auxiliares
    # -------------------------------------------------
    def reset_scores(self):
        """Reinicia los puntos de ambos equipos."""
        self.points_local = 0
        self.points_visit = 0

    def reset_fouls(self):
        """Reinicia las faltas de ambos equipos."""
        self.fouls_local = 0
        self.fouls_visit = 0

    def next_period(self):
        """Avanza al siguiente período y resetea las faltas."""
        self.current_period += 1
        self.reset_fouls()

    def to_dict(self) -> dict:
        """Convierte el estado actual a un diccionario (útil para debug o guardado)."""
        return {
            "local": self.team_local.name,
            "visit": self.team_visit.name,
            "game_type": self.game_type.name,
            "period": self.current_period,
            "points_local": self.points_local,
            "points_visit": self.points_visit,
            "fouls_local": self.fouls_local,
            "fouls_visit": self.fouls_visit,
        }

