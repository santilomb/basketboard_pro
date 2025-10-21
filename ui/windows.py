"""Qt windows rendered with modern HTML templates."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Callable, Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, QUrl, Signal, Slot
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView

from core.game_manager import GameManager
from models.game_type import GameType
from models.team import Team
from ui.template_renderer import renderer

ROOT_DIR = Path(__file__).resolve().parent.parent
BASE_URL = QUrl.fromLocalFile(str(ROOT_DIR) + "/")
TEMPLATES_ROOT = Path(__file__).resolve().parent / "templates"


def _template_dir(section: str) -> Path:
    return TEMPLATES_ROOT / section


def _list_templates(section: str) -> List[str]:
    """Return relative template paths available for a section."""

    base_dir = _template_dir(section)
    if not base_dir.exists():
        return []
    templates: List[str] = []
    for path in sorted(base_dir.glob("*/index.html")):
        if path.is_file():
            templates.append(path.relative_to(TEMPLATES_ROOT).as_posix())
    return templates


def _template_label(template_path: str) -> str:
    path = Path(template_path)
    if path.stem.lower() == "index" and path.parent != Path("."):
        raw = path.parent.name
    else:
        raw = path.stem
    stem = raw.replace("_", " ").replace("-", " ")
    return stem.title()


def _template_assets_url(template_name: str) -> str:
    """Return the URL path where the template assets live."""

    path = PurePosixPath(template_name)
    directory = path.parent
    if str(directory) in {".", ""}:
        return "ui/templates"
    return (PurePosixPath("ui/templates") / directory).as_posix()


def _format_game_time(seconds: int) -> Tuple[str, str]:
    """Return formatted time string and style for the main game clock."""

    remaining = max(0, int(seconds))
    if remaining >= 60:
        minutes = remaining // 60
        secs = remaining % 60
        return f"{minutes:02d}:{secs:02d}", "regular"

    return f":{remaining:02d}.0", "critical"


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
    """Public scoreboard rendered through a QWebEngineView."""

    def __init__(
        self,
        manager: GameManager,
        template_name: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.setWindowTitle("BasketBoard Pro — Display")
        self.manager = manager
        available = self.available_templates
        if not available:
            raise RuntimeError("No display templates available")
        default_template = "display/scoreboard_widescreen/index.html"
        if template_name and template_name in available:
            self.template_name = template_name
        elif default_template in available:
            self.template_name = default_template
        else:
            self.template_name = available[0]

        self.manager.updated.connect(self.refresh)

        self.view = QWebEngineView(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        self.refresh()

    def _build_context(self) -> Dict[str, object]:
        match = self.manager.match
        time_value, time_style = _format_game_time(self.manager.timer.remaining_secs)
        state = {
            "time": time_value,
            "time_style": time_style,
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
            "static_url": "ui/static",
            "template_url": _template_assets_url(self.template_name),
        }

    def refresh(self) -> None:
        html = renderer.render(self.template_name, self._build_context())
        self.view.setHtml(html, BASE_URL)

    def set_template(self, template_name: str) -> None:
        if template_name not in self.available_templates:
            return
        self.template_name = template_name
        self.refresh()

    def beep(self) -> None:
        QApplication.beep()
        self.refresh()

    @property
    def available_templates(self) -> List[str]:
        return _list_templates("display")


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
    def setDisplayTemplate(self, template_name: str) -> None:
        self._window.set_display_template(template_name)

    @Slot(str)
    def setOperatorTemplate(self, template_name: str) -> None:
        self._window.set_operator_template(template_name)

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
        on_set_display_template: Callable[[str], None],
        initial_operator_template: Optional[str] = None,
        initial_display_template: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.setWindowTitle("BasketBoard Pro — Operador")

        self.manager = manager
        self.manager.updated.connect(self.refresh)

        self.teams = teams
        self.game_types = game_types
        self._on_create_match = on_create_match
        self._on_set_display_template = on_set_display_template

        operator_templates = self.available_operator_templates
        if not operator_templates:
            raise RuntimeError("No operator templates available")
        display_templates = self.available_display_templates
        if not display_templates:
            raise RuntimeError("No display templates available")

        default_operator_template = "operator/dashboard_dark/index.html"
        if initial_operator_template and initial_operator_template in operator_templates:
            self._operator_template = initial_operator_template
        elif default_operator_template in operator_templates:
            self._operator_template = default_operator_template
        else:
            self._operator_template = operator_templates[0]

        default_display_template = "display/scoreboard_widescreen/index.html"
        if initial_display_template and initial_display_template in display_templates:
            self._display_template = initial_display_template
        elif default_display_template in display_templates:
            self._display_template = default_display_template
        else:
            self._display_template = display_templates[0]

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
        time_value, time_style = _format_game_time(self.manager.timer.remaining_secs)
        state = {
            "time": time_value,
            "time_style": time_style,
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
            "operator_template": self._operator_template,
            "display_template": self._display_template,
        }
        return state

    def _build_template_context(self) -> Dict[str, object]:
        state = self._build_state()
        operator_options = [
            {"value": name, "label": _template_label(name)}
            for name in self.available_operator_templates
        ]
        display_options = [
            {"value": name, "label": _template_label(name)}
            for name in self.available_display_templates
        ]
        return {
            "state": state,
            "teams": [_team_view(team) for team in self.teams],
            "game_types": [_game_type_view(game_type) for game_type in self.game_types],
            "selected": state["selected"],
            "operator_templates": operator_options,
            "display_templates": display_options,
            "operator_template": self._operator_template,
            "display_template": self._display_template,
            "static_url": "ui/static",
            "template_url": _template_assets_url(self._operator_template),
        }

    # ------------------------------------------------------------------
    # Rendering and updates
    # ------------------------------------------------------------------
    def _render_template(self) -> None:
        self._page_ready = False
        html = renderer.render(self._operator_template, self._build_template_context())
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

    def set_display_template(self, template_name: str) -> None:
        if template_name not in self.available_display_templates:
            return
        self._display_template = template_name
        self._on_set_display_template(template_name)
        self.refresh()

    def set_operator_template(self, template_name: str) -> None:
        if template_name not in self.available_operator_templates:
            return
        if template_name == self._operator_template:
            return
        self._operator_template = template_name
        self._render_template()

    @property
    def available_operator_templates(self) -> List[str]:
        return _list_templates("operator")

    @property
    def available_display_templates(self) -> List[str]:
        return _list_templates("display")
