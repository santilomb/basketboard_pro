from PySide6.QtCore import QObject, QTimer, Signal


def _mmss_to_secs(mmss: str) -> int:
    """
    Convierte 'MM:SS' a segundos (int).
    Lanza ValueError si el formato no es válido.
    """
    mmss = (mmss or "").strip()
    if ":" not in mmss:
        raise ValueError(f"Formato inválido (esperado MM:SS): {mmss!r}")
    m, s = mmss.split(":")
    m_i, s_i = int(m), int(s)
    if m_i < 0 or s_i < 0 or s_i > 59:
        raise ValueError(f"Valores fuera de rango en MM:SS: {mmss!r}")
    return m_i * 60 + s_i


def _secs_to_mmss(secs: int) -> str:
    """
    Convierte segundos (int) a formato 'MM:SS'.
    No permite negativos (clampa en 0).
    """
    secs = max(0, int(secs))
    m = secs // 60
    s = secs % 60
    return f"{m:02d}:{s:02d}"


class CountdownTimer(QObject):
    """
    Temporizador de cuenta regresiva con tick de 1 segundo.
    Señales:
      - tick(int remaining_secs, str remaining_mmss)
      - finished()
    """
    tick = Signal(int, str)
    finished = Signal()

    def __init__(self, initial_mmss: str = "10:00", parent=None):
        super().__init__(parent)
        self._remaining = _mmss_to_secs(initial_mmss)
        self._running = False

        self._qtimer = QTimer(self)
        self._qtimer.setInterval(1000)  # 1s
        self._qtimer.timeout.connect(self._on_timeout)

        # emitir un primer tick para inicializar vistas
        self.tick.emit(self._remaining, self.remaining_mmss)

    # -----------------------
    # Propiedades de lectura
    # -----------------------
    @property
    def remaining_secs(self) -> int:
        return self._remaining

    @property
    def remaining_mmss(self) -> str:
        return _secs_to_mmss(self._remaining)

    # -----------------------
    # Control de tiempo
    # -----------------------
    def set_from_mmss(self, mmss: str):
        """Fija el tiempo restante a partir de 'MM:SS' y emite tick inmediato."""
        self._remaining = _mmss_to_secs(mmss)
        self.tick.emit(self._remaining, self.remaining_mmss)

    def start(self):
        """Inicia la cuenta regresiva (si hay tiempo restante)."""
        if self._remaining <= 0:
            return
        if not self._running:
            self._running = True
            self._qtimer.start()

    def pause(self):
        """Pausa la cuenta regresiva."""
        if self._running:
            self._running = False
            self._qtimer.stop()

    def reset(self, mmss: str):
        """Resetea el temporizador al valor indicado y queda en pausa."""
        self.pause()
        self.set_from_mmss(mmss)

    # -----------------------
    # Interno
    # -----------------------
    def _on_timeout(self):
        if self._remaining > 0:
            self._remaining -= 1
            self.tick.emit(self._remaining, self.remaining_mmss)

        if self._remaining <= 0:
            # asegurar estado consistente y notificar fin
            self.pause()
            self.finished.emit()


# Helpers públicos
mmss_to_secs = _mmss_to_secs
secs_to_mmss = _secs_to_mmss

