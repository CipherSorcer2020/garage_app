import sys
import os

# S'assure que le dossier racine du projet est dans le chemin système Python
# afin que les importations absolues (par ex. from ui..., from config...) fonctionnent correctement
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from ui.windows.main_window import MainWindow

def main():
    """
    Point d'entrée principal pour l'application de Gestion de Garage.
    Initialise l'application PyQt6, configure les polices, applique la feuille de style,
    et lance la fenêtre principale des événements.
    """
    # Initialise la QApplication qui représente l'application Qt
    app = QApplication(sys.argv)
    
    # Définit le nom de l'application
    app.setApplicationName("Gestion Atelier")
    
    # Configure la police globale de l'application
    # Utilise "Segoe UI" avec une taille de 10 points
    font = QFont("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)

    # Charge et applique la feuille de style QSS (thème sombre personnalisé)
    qss_path = os.path.join(os.path.dirname(__file__), "ui", "styles", "theme.qss")
    with open(qss_path, "r", encoding="utf-8") as f:
        # Lit le contenu du fichier et l'applique comme style de l'application
        app.setStyleSheet(f.read())

    # Instancie et affiche la fenêtre principale de l'interface graphique
    window = MainWindow()
    window.show()
    
    # Démarre la boucle d'événements et quitte Python proprement lorsque l'interface est fermée
    sys.exit(app.exec())

# Vérifie si le script est exécuté directement (et non importé) pour lancer la fonction principale
if __name__ == "__main__":
    main()
