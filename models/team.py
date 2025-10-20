class Team:
    """
    Representa un equipo con identidad visual para el tablero.
    - name: nombre del club/equipo
    - logo: ruta al archivo de imagen (PNG/JPG/SVG)
    - color_primary / color_secondary: colores hex (#rrggbb)
    """
    def __init__(self, name: str, logo: str, color_primary: str, color_secondary: str):
        self.name = name
        self.logo = logo
        self.color_primary = color_primary
        self.color_secondary = color_secondary

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "logo": self.logo,
            "color_primary": self.color_primary,
            "color_secondary": self.color_secondary,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Team":
        return cls(
            name=d.get("name", "Equipo"),
            logo=d.get("logo", ""),
            color_primary=d.get("color_primary", "#000000"),
            color_secondary=d.get("color_secondary", "#FFFFFF"),
        )

