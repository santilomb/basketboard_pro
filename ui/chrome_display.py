"""Widgets that render the display using Google Chrome via CEF."""

from __future__ import annotations

from typing import Optional, Tuple

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QCloseEvent, QShowEvent
from PySide6.QtWidgets import QWidget

from ui.chrome_runtime import (
    cef_module,
    chrome_available,
    initialize_chrome,
    message_loop_step,
)

if not chrome_available():  # pragma: no cover - import guard
    raise ImportError("cefpython3 is required to use the Chrome display backend")


class ChromeDisplayView(QWidget):
    """Embed a Chromium browser to render HTML for the public display."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        initialize_chrome()

        self.setAttribute(Qt.WA_NativeWindow, True)
        self.setAttribute(Qt.WA_DontCreateNativeAncestors, True)

        self._cef = cef_module()
        self._browser = None
        self._pending: Optional[Tuple[str, str]] = None

        self._pump = QTimer(self)
        self._pump.timeout.connect(message_loop_step)
        self._pump.start(15)

    # ------------------------------------------------------------------
    # Public API compatible with QWebEngineView
    # ------------------------------------------------------------------
    def setHtml(self, html: str, base_url) -> None:  # noqa: N802 - Qt-style name
        base = base_url.toString() if hasattr(base_url, "toString") else str(base_url)
        if self._browser is None:
            self._pending = (html, base)
            return
        self._browser.GetMainFrame().LoadString(html, base)

    # ------------------------------------------------------------------
    # Qt events
    # ------------------------------------------------------------------
    def showEvent(self, event: QShowEvent) -> None:  # type: ignore[override]
        super().showEvent(event)
        if self._browser is None:
            self._create_browser()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if self._browser is None:
            return
        self._browser.SetBounds(0, 0, self.width(), self.height())
        self._browser.NotifyMoveOrResizeStarted()

    def closeEvent(self, event: QCloseEvent) -> None:  # type: ignore[override]
        if self._browser is not None:
            self._browser.CloseBrowser(True)
            self._browser = None
        self._pump.stop()
        super().closeEvent(event)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _create_browser(self) -> None:
        if self._browser is not None:
            return

        cef = self._cef
        if cef is None:
            return

        window_info = cef.WindowInfo()
        rect = [0, 0, self.width(), self.height()]
        window_info.SetAsChild(int(self.winId()), rect)
        self._browser = cef.CreateBrowserSync(window_info, url="about:blank")

        if self._pending is not None:
            html, base = self._pending
            self._browser.GetMainFrame().LoadString(html, base)
            self._pending = None

