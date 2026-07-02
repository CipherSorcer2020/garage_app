import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from ui.windows.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Gestion Atelier")
    font = QFont("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)

    # Load theme
    qss_path = os.path.join(os.path.dirname(__file__), "ui", "styles", "theme.qss")
    with open(qss_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
