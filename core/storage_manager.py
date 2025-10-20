import json
from pathlib import Path

# Directorio de datos del proyecto
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Rutas a los archivos JSON
TEAMS_FILE = DATA_DIR / "teams.json"
GAME_TYPES_FILE = DATA_DIR / "game_types.json"
CONFIG_FILE = DATA_DIR / "config.json"


# -------------------------------------------------
# 🔧 Utilidades internas
# -------------------------------------------------
def _read_json(path: Path, default):
    """Lee un archivo JSON, devolviendo 'default' si no existe."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, obj):
    """Guarda un objeto Python como JSON formateado."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# -------------------------------------------------
# 🧩 Gestión de equipos (teams)
# -------------------------------------------------
def load_teams():
    """Carga los equipos desde teams.json."""
    return _read_json(TEAMS_FILE, [])


def save_teams(items):
    """Guarda los equipos en teams.json."""
    _write_json(TEAMS_FILE, items)


# -------------------------------------------------
# 🏀 Gestión de tipos de juego (game_types)
# -------------------------------------------------
def load_game_types():
    """Carga los tipos de juego desde game_types.json."""
    return _read_json(GAME_TYPES_FILE, [])


def save_game_types(items):
    """Guarda los tipos de juego en game_types.json."""
    _write_json(GAME_TYPES_FILE, items)


# -------------------------------------------------
# ⚙️ Configuración general
# -------------------------------------------------
def load_config():
    """Carga la configuración general (últimos valores usados)."""
    default = {
        "last_selected_local": "",
        "last_selected_visit": "",
        "last_selected_game_type": "",
        "pre_game_countdown": "00:00"
    }
    return _read_json(CONFIG_FILE, default)


def save_config(cfg):
    """Guarda la configuración general en config.json."""
    _write_json(CONFIG_FILE, cfg)

