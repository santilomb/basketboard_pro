"""Helpers to integrate the Chromium Embedded Framework (CEF)."""

from __future__ import annotations

from threading import Lock
from typing import Optional

try:  # pragma: no cover - optional dependency, exercised at runtime
    from cefpython3 import cefpython as cef  # type: ignore
except ImportError:  # pragma: no cover - handled dynamically when CEF is absent
    cef = None  # type: ignore

_lock = Lock()
_initialized = False


def chrome_available() -> bool:
    """Return True if the CEF backend can be used."""

    return cef is not None


def initialize_chrome(settings: Optional[dict] = None) -> bool:
    """Initialize CEF once and return whether it is active."""

    global _initialized
    if cef is None or _initialized:
        return _initialized

    with _lock:
        if _initialized:
            return True
        cef.Initialize(settings or {})
        _initialized = True
    return True


def message_loop_step() -> None:
    """Run one iteration of the CEF message loop if active."""

    if cef is None or not _initialized:
        return
    cef.MessageLoopWork()


def shutdown_chrome() -> None:
    """Shutdown CEF if it had been initialised."""

    global _initialized
    if cef is None or not _initialized:
        return
    with _lock:
        if not _initialized:
            return
        cef.Shutdown()
        _initialized = False


def cef_module():
    """Expose the underlying CEF module when present."""

    return cef

