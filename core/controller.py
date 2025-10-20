from PySide6.QtWidgets import QApplication
from models.match import Match
from models.team import Team
from models.game_type import GameType
from .game_manager import GameManager
from .storage_manager import load_teams, load_game_types, load_config
from ui.windows import OperatorWindow, DisplayWindow


class AppController:
    """
    Controlador principal de la aplicación.
    Coordina la lógica del juego, la persistencia de datos y las interfaces gráficas.
    """

    def __init__(self):
        # --- Cargar configuraciones y presets ---
        self.teams = [Team(**t) for t in load_teams()]
        self.game_types = [GameType(**g) for g in load_game_types()]
        if not self.teams:
            self.teams = [
                Team("Local", "", "#ff0000", "#ffffff"),
                Team("Visitante", "", "#0000ff", "#ffffff"),
            ]
        elif len(self.teams) == 1:
            self.teams.append(Team("Visitante", "", "#0000ff", "#ffffff"))

        if not self.game_types:
            self.game_types = [GameType("Genérico", 4, "10:00", "02:00", "05:00")]
        config = load_config()

        # --- Crear partido inicial usando presets ---
        local = self.teams[0] if self.teams else Team("Local", "", "#ff0000", "#ffffff")
        visit = self.teams[1] if len(self.teams) > 1 else Team("Visitante", "", "#0000ff", "#ffffff")
        gtype = self.game_types[0] if self.game_types else GameType("Genérico", 4, "10:00", "02:00", "05:00")

        match = Match(local, visit, gtype)
        self.manager = GameManager(match)

        # --- Crear ventanas ---
        self.display = DisplayWindow(manager=self.manager)
        self.operator = OperatorWindow(
            manager=self.manager,
            teams=self.teams,
            game_types=self.game_types,
            on_create_match=self.configure_match,
            on_set_display_template=self.set_display_template,
            initial_display_template=self.display.template_name,
        )

        # --- Ajustar tamaños iniciales ---
        self.operator.resize(1000, 700)
        self.display.resize(1280, 720)

        # --- Conectar sirena a feedback visual (o sonido real en el futuro) ---
        self.manager.siren.connect(self.display.beep)

    def show(self):
        """Muestra las ventanas del operador y del display."""
        screens = QApplication.screens()
        if len(screens) > 1:
            # Si hay dos monitores, mostrar display en el segundo
            geometry = screens[1].geometry()
            self.display.move(geometry.left() + 40, geometry.top() + 40)

        self.display.show()
        self.operator.show()

    # ------------------------------------------------------------------
    # Interacciones desencadenadas por la interfaz web
    # ------------------------------------------------------------------
    def configure_match(self, local_index: int, visit_index: int, game_type_index: int) -> None:
        if not self.teams:
            return

        local_index = max(0, min(local_index, len(self.teams) - 1))
        visit_index = max(0, min(visit_index, len(self.teams) - 1))
        local = self.teams[local_index]
        visit = self.teams[visit_index]

        game_type_index = max(0, min(game_type_index, len(self.game_types) - 1))
        game_type = self.game_types[game_type_index] if self.game_types else GameType("Genérico", 4, "10:00", "02:00", "05:00")

        match = Match(local, visit, game_type)
        self.manager.configure_match(match)

    def set_display_template(self, template_name: str) -> None:
        self.display.set_template(template_name)

