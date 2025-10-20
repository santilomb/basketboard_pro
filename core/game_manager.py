from PySide6.QtCore import QObject, Signal

from models.match import Match

from .timer import CountdownTimer, mmss_to_secs


class GameManager(QObject):
    """
    Controla la lógica del partido de básquet.
    Se encarga del cronómetro, puntos, faltas, períodos y sirena.
    """

    updated = Signal()   # Se emite cuando hay que refrescar la interfaz
    siren = Signal()     # Se emite cuando termina el tiempo o countdown

    def __init__(self, match):
        super().__init__()
        self.match = match

        # --- Timer principal del juego ---
        self.timer = CountdownTimer(match.game_type.time_per_quarter)
        self.timer.tick.connect(self._on_tick)
        self.timer.finished.connect(self._on_period_finished)

        # --- Timer para countdown previo al partido ---
        self.countdown = CountdownTimer("00:00")
        self.countdown.finished.connect(self._on_countdown_finished)

    # -------------------------------------------------
    # 🕐 Control del tiempo del partido
    # -------------------------------------------------
    def start_pause(self):
        """Inicia o pausa el cronómetro del partido."""
        if self.timer.remaining_secs <= 0:
            return
        if self.timer._qtimer.isActive():
            self.timer.pause()
        else:
            self.timer.start()
        self.updated.emit()

    def reset_time(self):
        """Reinicia el tiempo del cuarto actual."""
        self.timer.reset(self.match.game_type.time_per_quarter)
        self.updated.emit()

    def set_time(self, mmss: str):
        """Ajusta manualmente el tiempo restante."""
        self.timer.reset(mmss)
        self.updated.emit()

    # -------------------------------------------------
    # 🏀 Control del marcador
    # -------------------------------------------------
    def score_local(self, pts: int):
        """Suma o resta puntos al equipo local."""
        self.match.points_local = max(0, self.match.points_local + pts)
        self.updated.emit()

    def score_visit(self, pts: int):
        """Suma o resta puntos al equipo visitante."""
        self.match.points_visit = max(0, self.match.points_visit + pts)
        self.updated.emit()

    # -------------------------------------------------
    # 🚫 Control de faltas
    # -------------------------------------------------
    def foul_local(self, delta: int = 1):
        """Incrementa o decrementa las faltas del equipo local."""
        self.match.fouls_local = max(0, self.match.fouls_local + delta)
        self.updated.emit()

    def foul_visit(self, delta: int = 1):
        """Incrementa o decrementa las faltas del equipo visitante."""
        self.match.fouls_visit = max(0, self.match.fouls_visit + delta)
        self.updated.emit()

    # -------------------------------------------------
    # 🔢 Control del período
    # -------------------------------------------------
    def next_period(self):
        """Avanza al siguiente período y resetea faltas y tiempo."""
        self.match.current_period += 1
        self.reset_time()
        self.match.fouls_local = 0
        self.match.fouls_visit = 0
        self.updated.emit()

    # -------------------------------------------------
    # ⏳ Countdown previo al inicio del partido
    # -------------------------------------------------
    def set_pregame_countdown(self, mmss: str):
        """Configura la cuenta regresiva antes del partido."""
        self.countdown.reset(mmss)

    def start_pregame(self):
        """Inicia el countdown previo (si se configuró un tiempo > 0)."""
        if mmss_to_secs(self.countdown.remaining_mmss) > 0:
            self.countdown.start()
            self.updated.emit()

    # -------------------------------------------------
    # 🔁 Configuración completa del partido
    # -------------------------------------------------
    def configure_match(self, match: Match):
        """Reemplaza el partido actual por uno nuevo y reinicia temporizadores."""
        self.timer.pause()
        self.countdown.pause()
        self.match = match
        self.timer.reset(self.match.game_type.time_per_quarter)
        self.countdown.reset("00:00")
        self.updated.emit()

    # -------------------------------------------------
    # 🔔 Eventos internos
    # -------------------------------------------------
    def _on_tick(self, *_):
        self.updated.emit()

    def _on_period_finished(self):
        """Se ejecuta cuando el reloj llega a 0:00."""
        self.siren.emit()
        self.updated.emit()

    def _on_countdown_finished(self):
        """Cuando termina la cuenta regresiva previa, suena la sirena e inicia el partido."""
        self.siren.emit()
        self.timer.start()
        self.updated.emit()

