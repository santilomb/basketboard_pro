from PySide6.QtWidgets import QApplication
from core.controller import AppController
from ui.chrome_runtime import chrome_available, initialize_chrome, shutdown_chrome
import sys


def main():
    """Punto de entrada principal de la aplicación BasketBoard Pro."""
    chrome_started = False
    if chrome_available():
        chrome_started = initialize_chrome()

    app = QApplication(sys.argv)
    app.setApplicationName("BasketBoard Pro")

    # Instancia del controlador principal (maneja la lógica y las ventanas)
    controller = AppController()
    controller.show()

    # Ejecutar el loop de la aplicación Qt
    exit_code = app.exec()

    if chrome_started:
        shutdown_chrome()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

