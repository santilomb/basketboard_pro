"""Qt windows rendered with modern HTML templates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, List, Optional

from PySide6.QtCore import QObject, QUrl, Signal, Slot
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView

from core.game_manager import GameManager
from models.game_type import GameType
from models.team import Team
from ui.template_renderer import renderer

try:
    from ui.chrome_display import ChromeDisplayView

    _DISPLAY_BACKEND = "chrome"
except ImportError:  # pragma: no cover - chrome backend optional
    ChromeDisplayView = None
    _DISPLAY_BACKEND = "qt"

ROOT_DIR = Path(__file__).resolve().parent.parent
BASE_URL = QUrl.fromLocalFile(str(ROOT_DIR) + "/")
STATIC_URL = "ui/static"
THEMES = ["dark", "light"]


def _team_view(team: Team) -> Dict[str, str]:
    return {
        "name": team.name,
        "logo": team.logo,
        "color_primary": team.color_primary,
        "color_secondary": team.color_secondary,
    }


def _game_type_view(game_type: GameType) -> Dict[str, str]:
    return {
        "name": game_type.name,
        "quarters": str(game_type.quarters),
        "time_per_quarter": game_type.time_per_quarter,
        "rest_between_quarters": game_type.rest_between_quarters,
        "halftime_rest": game_type.halftime_rest,
    }


class DisplayWindow(QWidget):
    """Public scoreboard rendered through Chrome (CEF) when available."""

    def __init__(self, manager: GameManager, theme: str = "dark") -> None:
        super().__init__()
        self.setWindowTitle("BasketBoard Pro — Display")
        self.manager = manager
        self.theme = theme if theme in THEMES else THEMES[0]

        self.manager.updated.connect(self.refresh)

        if _DISPLAY_BACKEND == "chrome" and ChromeDisplayView is not None:
            self.view = ChromeDisplayView(self)
        else:
            self.view = QWebEngineView(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        self.refresh()

    def _build_context(self) -> Dict[str, object]:
        match = self.manager.match
        state = {
            "time": self.manager.timer.remaining_mmss,
            "period": match.current_period,
            "points_local": match.points_local,
            "points_visit": match.points_visit,
            "fouls_local": match.fouls_local,
            "fouls_visit": match.fouls_visit,
            "team_local": _team_view(match.team_local),
            "team_visit": _team_view(match.team_visit),
            "game_type": _game_type_view(match.game_type),
        }
        return {
            "state": state,
            "theme": self.theme,
            "static_url": STATIC_URL,
        }

    def refresh(self) -> None:
        html = renderer.render("display/scoreboard.html", self._build_context())
        self.view.setHtml(html, BASE_URL)

    def set_theme(self, theme: str) -> None:
        if theme not in THEMES:
            return
        self.theme = theme
        self.refresh()

    def beep(self) -> None:
        QApplication.beep()
        self.refresh()


class OperatorBridge(QObject):
    """Bridge exposed to JavaScript via Qt WebChannel."""

    stateUpdated = Signal(str)

    def __init__(self, window: "OperatorWindow") -> None:
        super().__init__()
        self._window = window

    # ------------------------------------------------------------------
    # Requests from JavaScript to Python
    # ------------------------------------------------------------------
    @Slot()
    def startPause(self) -> None:
        self._window.manager.start_pause()

    @Slot()
    def resetTime(self) -> None:
        self._window.manager.reset_time()

    @Slot()
    def nextPeriod(self) -> None:
        self._window.manager.next_period()

    @Slot()
    def startPregame(self) -> None:
        self._window.manager.start_pregame()

    @Slot(int)
    def scoreLocal(self, delta: int) -> None:
        self._window.manager.score_local(delta)

    @Slot(int)
    def scoreVisit(self, delta: int) -> None:
        self._window.manager.score_visit(delta)

    @Slot(int)
    def foulLocal(self, delta: int) -> None:
        self._window.manager.foul_local(delta)

    @Slot(int)
    def foulVisit(self, delta: int) -> None:
        self._window.manager.foul_visit(delta)

    @Slot(int, int, int)
    def createMatch(self, local_index: int, visit_index: int, game_type_index: int) -> None:
        self._window.create_match(local_index, visit_index, game_type_index)

    @Slot(str)
    def setDisplayTheme(self, theme: str) -> None:
        self._window.set_display_theme(theme)

    @Slot(str)
    def setOperatorTheme(self, theme: str) -> None:
        self._window.set_operator_theme(theme)

    @Slot(str, result=bool)
    def setPregameCountdown(self, value: str) -> bool:
        try:
            self._window.manager.set_pregame_countdown(value)
        except ValueError:
            return False
        else:
            self._window.refresh()
            return True

    @Slot()
    def requestInitialState(self) -> None:
        self.push_state(self._window.last_state)

    # ------------------------------------------------------------------
    # Helpers for Python -> JavaScript notifications
    # ------------------------------------------------------------------
    def push_state(self, state: Optional[Dict[str, object]]) -> None:
        if not state:
            return
        payload = json.dumps(state)
        self.stateUpdated.emit(payload)


class OperatorWindow(QWidget):
    """Operator control panel rendered with HTML templates."""

    def __init__(
        self,
        manager: GameManager,
        teams: List[Team],
        game_types: List[GameType],
        on_create_match: Callable[[int, int, int], None],
        on_set_display_theme: Callable[[str], None],
        initial_operator_theme: str = "dark",
        initial_display_theme: str = "dark",
    ) -> None:
        super().__init__()
        self.setWindowTitle("BasketBoard Pro — Operador")

        self.manager = manager
        self.manager.updated.connect(self.refresh)

        self.teams = teams
        self.game_types = game_types
        self._on_create_match = on_create_match
        self._on_set_display_theme = on_set_display_theme

        self._operator_theme = initial_operator_theme if initial_operator_theme in THEMES else THEMES[0]
        self._display_theme = initial_display_theme if initial_display_theme in THEMES else THEMES[0]

        self.view = QWebEngineView(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        self._channel = QWebChannel(self.view.page())
        self._bridge = OperatorBridge(self)
        self._channel.registerObject("OperatorBridge", self._bridge)
        self.view.page().setWebChannel(self._channel)

        self._page_ready = False
        self.last_state: Optional[Dict[str, object]] = None

        self.view.loadFinished.connect(self._on_load_finished)
        self._render_template()
        self.last_state = self._build_state()

    # ------------------------------------------------------------------
    # State building helpers
    # ------------------------------------------------------------------
    def _team_index(self, team: Team) -> int:
        try:
            return self.teams.index(team)
        except ValueError:
            return 0

    def _game_type_index(self, game_type: GameType) -> int:
        try:
            return self.game_types.index(game_type)
        except ValueError:
            return 0

    def _build_state(self) -> Dict[str, object]:
        match = self.manager.match
        state = {
            "time": self.manager.timer.remaining_mmss,
            "period": match.current_period,
            "points_local": match.points_local,
            "points_visit": match.points_visit,
            "fouls_local": match.fouls_local,
            "fouls_visit": match.fouls_visit,
            "countdown": self.manager.countdown.remaining_mmss,
            "team_local": _team_view(match.team_local),
            "team_visit": _team_view(match.team_visit),
            "game_type": _game_type_view(match.game_type),
            "selected": {
                "local": self._team_index(match.team_local),
                "visit": self._team_index(match.team_visit),
                "game_type": self._game_type_index(match.game_type),
            },
            "operator_theme": self._operator_theme,
            "display_theme": self._display_theme,
        }
        return state

    def _build_template_context(self) -> Dict[str, object]:
        state = self._build_state()
        return {
            "state": state,
            "teams": [_team_view(team) for team in self.teams],
            "game_types": [_game_type_view(game_type) for game_type in self.game_types],
            "selected": state["selected"],
            "themes": THEMES,
            "operator_theme": self._operator_theme,
            "display_theme": self._display_theme,
            "static_url": STATIC_URL,
        }

    # ------------------------------------------------------------------
    # Rendering and updates
    # ------------------------------------------------------------------
    def _render_template(self) -> None:
        html = renderer.render("operator/dashboard.html", self._build_template_context())
        self.view.setHtml(html, BASE_URL)

    def _on_load_finished(self, _success: bool) -> None:
        self._page_ready = True
        self.refresh()

    def refresh(self) -> None:
        state = self._build_state()
        self.last_state = state
        if self._page_ready:
            self._bridge.push_state(state)

    # ------------------------------------------------------------------
    # Callbacks from bridge
    # ------------------------------------------------------------------
    def create_match(self, local_index: int, visit_index: int, game_type_index: int) -> None:
        self._on_create_match(local_index, visit_index, game_type_index)

    def set_display_theme(self, theme: str) -> None:
        if theme not in THEMES:
            return
        self._display_theme = theme
        self._on_set_display_theme(theme)
        self.refresh()

    def set_operator_theme(self, theme: str) -> None:
        if theme not in THEMES:
            return
        self._operator_theme = theme
        self.refresh()
