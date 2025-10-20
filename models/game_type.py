class GameType:
    """
    Representa un tipo de juego preconfigurado.
    Define la estructura temporal del partido: cantidad de cuartos,
    duración de cada cuarto, descansos entre ellos y entretiempo.
    """
    def __init__(
        self,
        name: str,
        quarters: int,
        time_per_quarter: str,
        rest_between_quarters: str,
        halftime_rest: str
    ):
        self.name = name
        self.quarters = quarters
        self.time_per_quarter = time_per_quarter
        self.rest_between_quarters = rest_between_quarters
        self.halftime_rest = halftime_rest

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "quarters": self.quarters,
            "time_per_quarter": self.time_per_quarter,
            "rest_between_quarters": self.rest_between_quarters,
            "halftime_rest": self.halftime_rest,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GameType":
        return cls(
            name=d.get("name", "Genérico"),
            quarters=int(d.get("quarters", 4)),
            time_per_quarter=d.get("time_per_quarter", "10:00"),
            rest_between_quarters=d.get("rest_between_quarters", "02:00"),
            halftime_rest=d.get("halftime_rest", "05:00"),
        )

