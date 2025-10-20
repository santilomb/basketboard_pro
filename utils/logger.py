import logging
import sys
from typing import Optional

# Logger de módulo (simple y reutilizable)
_logger = logging.getLogger("basketboard")
if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(stream=sys.stderr)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s",
                                  datefmt="%H:%M:%S")
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.propagate = False


def set_level(level: int | str):
    """
    Cambia el nivel del logger.
    Ej: set_level(logging.DEBUG) o set_level("DEBUG")
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    _logger.setLevel(level)


def add_file_handler(path: str, level: Optional[int | str] = None):
    """Agrega escritura a archivo de log (append)."""
    fh = logging.FileHandler(path, encoding="utf-8")
    if level is not None:
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        fh.setLevel(level)
    fh.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    ))
    _logger.addHandler(fh)


def info(msg: str): _logger.info(msg)
def warning(msg: str): _logger.warning(msg)
def error(msg: str): _logger.error(msg)
def debug(msg: str): _logger.debug(msg)

