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
        teams = [Team(**t) for t in load_teams()]
        game_types = [GameType(**g) for g in load_game_types()]
        config = load_config()

        # --- Crear partido inicial usando presets ---
        local = teams[0] if teams else Team("Local", "", "#ff0000", "#ffffff")
        visit = teams[1] if len(teams) > 1 else Team("Visitante", "", "#0000ff", "#ffffff")
        gtype = game_types[0] if game_types else GameType("Genérico", 4, "10:00", "02:00", "05:00")

        match = Match(local, visit, gtype)
        self.manager = GameManager(match)

        # --- Crear ventanas ---
        self.display = DisplayWindow(manager=self.manager)
        self.operator = OperatorWindow(manager=self.manager, teams=teams, game_types=game_types)

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

