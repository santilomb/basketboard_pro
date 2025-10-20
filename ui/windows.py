from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,  # ⬅️ agregado para usar QApplication.beep()
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout,
    QComboBox, QLineEdit, QGroupBox
)


def _h1(text):
    """Etiqueta grande para valores principales."""
    lab = QLabel(text)
    lab.setAlignment(Qt.AlignCenter)
    lab.setFont(QFont("Arial", 64, QFont.Bold))
    return lab


def _h2(text):
    """Etiqueta mediana para subtítulos."""
    lab = QLabel(text)
    lab.setAlignment(Qt.AlignCenter)
    lab.setFont(QFont("Arial", 28, QFont.Bold))
    return lab


# ==========================================================
# 🖥️ Pantalla principal para el público
# ==========================================================
class DisplayWindow(QWidget):
    """Ventana que muestra el marcador y los datos al público."""

    def __init__(self, manager):
        super().__init__()
        self.setWindowTitle("BasketBoard Pro — Display")
        self.manager = manager
        self.manager.updated.connect(self.refresh)

        # --- Componentes visuales ---
        self.lbl_time = _h1("10:00")
        self.lbl_local = _h1("0")
        self.lbl_visit = _h1("0")
        self.lbl_period = _h2("Período 1")
        self.lbl_fouls = _h2("Faltas L 0 | V 0")

        layout = QVBoxLayout(self)

        row = QHBoxLayout()
        col_left = QVBoxLayout()
        col_right = QVBoxLayout()
        col_center = QVBoxLayout()

        col_left.addWidget(_h2("LOCAL"))
        col_left.addWidget(self.lbl_local)

        col_center.addWidget(self.lbl_time)
        col_center.addWidget(self.lbl_period)
        col_center.addWidget(self.lbl_fouls)

        col_right.addWidget(_h2("VISITA"))
        col_right.addWidget(self.lbl_visit)

        row.addLayout(col_left, 1)
        row.addLayout(col_center, 1)
        row.addLayout(col_right, 1)

        layout.addLayout(row)
        self.refresh()

    def refresh(self):
        """Actualiza los valores en pantalla."""
        m = self.manager.match
        self.lbl_time.setText(self.manager.timer.remaining_mmss)
        self.lbl_local.setText(str(m.points_local))
        self.lbl_visit.setText(str(m.points_visit))
        self.lbl_period.setText(f"Período {m.current_period}")
        self.lbl_fouls.setText(f"Faltas L {m.fouls_local} | V {m.fouls_visit}")

    def beep(self):
        """Feedback al finalizar tiempo o countdown."""
        QApplication.beep()  # ⬅️ beep nativo del sistema (sin dependencias extra)
        self.lbl_time.setText("00:00")
        self.repaint()


# ==========================================================
# 🧑‍💻 Ventana de control del operador
# ==========================================================
class OperatorWindow(QWidget):
    """Ventana para el operador que controla el partido."""

    def __init__(self, manager, teams, game_types):
        super().__init__()
        self.setWindowTitle("BasketBoard Pro — Operador")
        self.manager = manager
        self.manager.updated.connect(self.refresh)

        main_layout = QVBoxLayout(self)

        # --------------------------------------------------
        # 🏗️ Sección: Crear partido
        # --------------------------------------------------
        group_setup = QGroupBox("Crear partido")
        setup_layout = QGridLayout(group_setup)

        self.cb_local = QComboBox()
        self.cb_local.addItems([t.name for t in teams] or ["Local"])

        self.cb_visit = QComboBox()
        self.cb_visit.addItems([t.name for t in teams[1:]] or ["Visitante"])

        self.cb_game_type = QComboBox()
        self.cb_game_type.addItems([g.name for g in game_types] or ["Genérico"])

        setup_layout.addWidget(QLabel("Equipo local:"), 0, 0)
        setup_layout.addWidget(self.cb_local, 0, 1)
        setup_layout.addWidget(QLabel("Equipo visitante:"), 1, 0)
        setup_layout.addWidget(self.cb_visit, 1, 1)
        setup_layout.addWidget(QLabel("Tipo de juego:"), 2, 0)
        setup_layout.addWidget(self.cb_game_type, 2, 1)

        # --------------------------------------------------
        # 🕐 Sección: Cronómetro
        # --------------------------------------------------
        group_time = QGroupBox("Reloj de juego")
        time_layout = QHBoxLayout(group_time)

        self.lbl_time = _h2(self.manager.timer.remaining_mmss)
        btn_start_pause = QPushButton("Iniciar / Pausar")
        btn_reset = QPushButton("Reset")

        btn_start_pause.clicked.connect(self.manager.start_pause)
        btn_reset.clicked.connect(self.manager.reset_time)

        time_layout.addWidget(self.lbl_time, 1)
        time_layout.addWidget(btn_start_pause)
        time_layout.addWidget(btn_reset)

        # --------------------------------------------------
        # 🏀 Sección: Puntos y faltas
        # --------------------------------------------------
        group_score = QGroupBox("Marcador")
        grid = QGridLayout(group_score)

        # Local
        btn_local_plus1 = QPushButton("Local +1")
        btn_local_plus2 = QPushButton("Local +2")
        btn_local_plus3 = QPushButton("Local +3")
        btn_local_minus = QPushButton("Local -1")
        btn_local_plus1.clicked.connect(lambda: self.manager.score_local(1))
        btn_local_plus2.clicked.connect(lambda: self.manager.score_local(2))
        btn_local_plus3.clicked.connect(lambda: self.manager.score_local(3))
        btn_local_minus.clicked.connect(lambda: self.manager.score_local(-1))

        # Visitante
        btn_visit_plus1 = QPushButton("Visita +1")
        btn_visit_plus2 = QPushButton("Visita +2")
        btn_visit_plus3 = QPushButton("Visita +3")
        btn_visit_minus = QPushButton("Visita -1")
        btn_visit_plus1.clicked.connect(lambda: self.manager.score_visit(1))
        btn_visit_plus2.clicked.connect(lambda: self.manager.score_visit(2))
        btn_visit_plus3.clicked.connect(lambda: self.manager.score_visit(3))
        btn_visit_minus.clicked.connect(lambda: self.manager.score_visit(-1))

        # Faltas
        btn_foul_local_plus = QPushButton("Falta L +")
        btn_foul_local_minus = QPushButton("Falta L -")
        btn_foul_visit_plus = QPushButton("Falta V +")
        btn_foul_visit_minus = QPushButton("Falta V -")
        btn_foul_local_plus.clicked.connect(lambda: self.manager.foul_local(1))
        btn_foul_local_minus.clicked.connect(lambda: self.manager.foul_local(-1))
        btn_foul_visit_plus.clicked.connect(lambda: self.manager.foul_visit(1))
        btn_foul_visit_minus.clicked.connect(lambda: self.manager.foul_visit(-1))

        grid.addWidget(btn_local_plus1, 0, 0)
        grid.addWidget(btn_local_plus2, 0, 1)
        grid.addWidget(btn_local_plus3, 0, 2)
        grid.addWidget(btn_local_minus, 0, 3)
        grid.addWidget(btn_visit_plus1, 1, 0)
        grid.addWidget(btn_visit_plus2, 1, 1)
        grid.addWidget(btn_visit_plus3, 1, 2)
        grid.addWidget(btn_visit_minus, 1, 3)
        grid.addWidget(btn_foul_local_plus, 2, 0)
        grid.addWidget(btn_foul_local_minus, 2, 1)
        grid.addWidget(btn_foul_visit_plus, 2, 2)
        grid.addWidget(btn_foul_visit_minus, 2, 3)

        # --------------------------------------------------
        # 🔢 Sección: Período
        # --------------------------------------------------
        group_period = QGroupBox("Período actual")
        layout_period = QHBoxLayout(group_period)

        self.lbl_period = _h2(str(self.manager.match.current_period))
        btn_next_period = QPushButton("Siguiente período")
        btn_next_period.clicked.connect(self.manager.next_period)

        layout_period.addWidget(QLabel("Actual:"))
        layout_period.addWidget(self.lbl_period)
        layout_period.addWidget(btn_next_period)

        # --------------------------------------------------
        # ⏳ Sección: Countdown previo
        # --------------------------------------------------
        group_pre = QGroupBox("Cuenta regresiva previa")
        layout_pre = QHBoxLayout(group_pre)

        self.ed_pre = QLineEdit("00:30")
        btn_set_pre = QPushButton("Fijar")
        btn_run_pre = QPushButton("Iniciar countdown")

        btn_set_pre.clicked.connect(lambda: self.manager.set_pregame_countdown(self.ed_pre.text()))
        btn_run_pre.clicked.connect(self.manager.start_pregame)

        layout_pre.addWidget(QLabel("MM:SS"))
        layout_pre.addWidget(self.ed_pre)
        layout_pre.addWidget(btn_set_pre)
        layout_pre.addWidget(btn_run_pre)

        # --------------------------------------------------
        # 🧩 Armar layout general
        # --------------------------------------------------
        main_layout.addWidget(group_setup)
        main_layout.addWidget(group_time)
        main_layout.addWidget(group_score)
        main_layout.addWidget(group_period)
        main_layout.addWidget(group_pre)

        self.refresh()

    # --------------------------------------------------
    # 🔄 Actualización visual
    # --------------------------------------------------
    def refresh(self):
        """Actualiza etiquetas de reloj y período."""
        m = self.manager.match
        self.lbl_time.setText(self.manager.timer.remaining_mmss)
        self.lbl_period.setText(str(m.current_period))

