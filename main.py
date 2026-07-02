import sys
import os

# Ensure the root project directory is in the Python system path
# so that absolute imports (e.g. from ui..., from config...) function correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from ui.windows.main_window import MainWindow

def main():
    """
    Main entry point for the Garage Management application.
    Initializes the PyQt6 application, sets fonts, applies stylesheet,
    and runs the main event window.
    """
    # Initialize the QApplication representing the Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Gestion Atelier")
    
    # Configure the global application font
    font = QFont("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)

    # Load and apply QSS stylesheet (custom dark theme)
    qss_path = os.path.join(os.path.dirname(__file__), "ui", "styles", "theme.qss")
    with open(qss_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    # Instantiate and display the main GUI window
    window = MainWindow()
    window.show()
    
    # Start the event loop and safely exit Python when the UI is closed
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
