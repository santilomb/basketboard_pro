# 🏀 BasketBoard Pro

Proyecto base en **Python + PySide6 (Qt for Python)** para un **tablero de básquet** digital.  
Permite controlar un partido en dos pantallas:
- **Pantalla del operador**: donde se manejan puntos, faltas, períodos y tiempo.
- **Pantalla del público**: marcador visual sincronizado.

---

## 🚀 Características principales

- Control de **puntos, faltas y períodos**.
- **Cuenta regresiva previa** al inicio del partido (countdown).
- Control de **tiempo de cuarto** con sirena automática al llegar a 0.
- **Presets configurables**:
  - Equipos (nombre, logo, colores).
  - Tipos de juego (cantidad de cuartos, duración, descansos).
- Persistencia local en **archivos JSON**, sin base de datos.
- Interfaz compatible con **2 monitores** (operador y público).

---

## ⚙️ Requisitos

- Python 3.10 o superior  
- Librerías indicadas en `requirements.txt`

---

## ▶️ Instalación rápida

```bash
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
python main.py

---

## 📁 Estructura general

basketboard_pro/
├── core/          # Lógica principal (controlador, timers, almacenamiento)
├── models/        # Clases base (Team, GameType, Match)
├── ui/            # Ventanas de operador y display
├── utils/         # Colores, logger, helpers
└── data/          # JSON de presets y configuración

---

## 🧩 Próximas mejoras

- Soporte de sonido real para sirena.
- Sincronización remota (control desde tableta o celular).
- Temas personalizados según colores del club.

---

## 👨💻 Autor

Desarrollado por Santiago Lombardi — proyecto de tablero de básquet digital.
