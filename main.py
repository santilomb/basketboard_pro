from PySide6.QtWidgets import QApplication
from core.controller import AppController
import sys


def main():
    """Punto de entrada principal de la aplicación BasketBoard Pro."""
    app = QApplication(sys.argv)
    app.setApplicationName("BasketBoard Pro")

    # Instancia del controlador principal (maneja la lógica y las ventanas)
    controller = AppController()
    controller.show()

    # Ejecutar el loop de la aplicación Qt
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

