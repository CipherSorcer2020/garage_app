# Importation des modules systèmes de base de Python.
import sys
import os
# Ensure project path is accessible
# Ajoute le dossier racine du projet au chemin d'import de Python 
# pour s'assurer que les autres modules (ui, repositories...) puissent être trouvés.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Importation des composants graphiques pour construire la fenêtre principale.
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QPushButton, QLabel, QStackedWidget, QStatusBar)
# Importation de Qt pour diverses constantes utiles.
from PyQt6.QtCore import Qt
# Importation pour gérer les polices de caractères.
from PyQt6.QtGui import QFont

# Importation de tous nos "widgets" (pages) personnalisés.
from ui.widgets.dashboard_widget import DashboardWidget
from ui.widgets.client_widget import ClientWidget
from ui.widgets.vehicule_widget import VehiculeWidget
from ui.widgets.or_widget import ORWidget
from ui.widgets.facture_widget import FactureWidget
from ui.widgets.planning_widget import PlanningWidget
from ui.widgets.achat_widget import AchatWidget
from ui.widgets.agenda_widget import AgendaWidget
from ui.widgets.crm_widget import CRMWidget
from ui.widgets.audit_widget import AuditWidget
from ui.dialogs.technicien_manager_dialog import TechnicienManagerDialog
from ui.widgets.retour_widget import RetourWidget
from ui.dialogs.retour_piece_dialog import RetourPieceDialog

class MainWindow(QMainWindow):
    """
    The primary GUI window for the application.
    Fenêtre graphique principale de l'application.
    Contains the side navigation bar, the top header, and a stacked widget
    Contient la barre de navigation latérale, l'en-tête supérieur et un conteneur empilé (QStackedWidget)
    to switch between different panel views (Dashboard, Clients, Vehicles, Work Orders, Invoices).
    permettant de basculer entre les différentes vues (Tableau de bord, Clients, Véhicules, etc.).
    """
    def __init__(self):
        # Initialise la classe parent (QMainWindow).
        super().__init__()
        # Définit le titre de la fenêtre.
        self.setWindowTitle("Gestion Atelier — Garage Auto")
        # Définit la taille minimale de la fenêtre (largeur, hauteur).
        self.setMinimumSize(1200, 720)
        # Construit l'interface de la fenêtre.
        self._build_ui()

    def _build_ui(self):
        """
        Builds the overall window layout structure: sidebar on the left,
        Construit la structure de mise en page globale de la fenêtre :
        main page content on the right.
        la barre latérale à gauche et le contenu principal à droite.
        """
        # Crée un widget central qui contiendra tout le reste.
        central = QWidget()
        self.setCentralWidget(central)
        
        # Crée un layout horizontal (gauche/droite) pour ce widget central.
        root = QHBoxLayout(central)
        # Supprime toutes les marges pour que l'interface occupe tout l'espace.
        root.setContentsMargins(0, 0, 0, 0)
        # Supprime l'espace entre la barre latérale et le contenu.
        root.setSpacing(0)

        # Build and add Sidebar
        # Crée la barre latérale (menu de navigation).
        self.sidebar = self._make_sidebar()
        # L'ajoute sur la gauche du layout principal.
        root.addWidget(self.sidebar)

        # Right-hand container
        # Crée un layout vertical pour la partie droite (qui contiendra l'en-tête et la page).
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        # Page Title Header
        # Crée l'en-tête supérieur de la page (titre de la section actuelle).
        self.header = self._make_header("Tableau de bord")
        # Ajoute l'en-tête en haut de la zone droite.
        right.addWidget(self.header)

        # Stacked pages layout (only one page is visible at a time)
        # Crée un QStackedWidget qui permet d'empiler plusieurs widgets mais d'en afficher un seul à la fois.
        self.stack = QStackedWidget()
        # Instanciation de toutes les pages (vues) de l'application.
        self.dashboard = DashboardWidget()
        self.clients = ClientWidget()
        self.vehicules = VehiculeWidget()
        self.ors = ORWidget()
        self.factures = FactureWidget()
        self.planning = PlanningWidget()
        self.achats = AchatWidget()
        self.agenda = AgendaWidget()
        self.crm = CRMWidget()
        self.audit = AuditWidget()
        self.sinistres = SinistreWidget()
        self.retour_widget = RetourWidget()

        # Add all panel widgets to stack index
        # Ajoute toutes ces pages dans l'empilement. L'ordre d'ajout correspondra a leur index (0, 1, 2...).
        for w in [self.dashboard, self.clients, self.vehicules, self.ors, self.factures, self.planning, self.achats, self.agenda, self.crm, self.audit, self.sinistres, self.retour_widget]:
            self.stack.addWidget(w)

        # Bouton Techniciens dans la sidebar ouvre le dialogue de gestion
        # (pas une page separee, c'est une action modale)
        self._tech_btn_idx = None  # Placeholder : bouton techniciens est un modal

        # Ajoute le conteneur de pages sous l'en-tête.
        right.addWidget(self.stack)

        # Crée un widget pour encapsuler le layout de la partie droite.
        right_widget = QWidget()
        right_widget.setLayout(right)
        # Ajoute cette partie droite complète au layout horizontal racine.
        root.addWidget(right_widget)

        # Status Bar at bottom
        # Ajoute une barre d'état (Status Bar) tout en bas de la fenêtre principale.
        self.setStatusBar(QStatusBar())
        # Affiche un message indiquant l'état de connexion.
        self.statusBar().showMessage("Connecté à garage_db")

    def _make_sidebar(self):
        """
        Helper to construct the side panel containing navigation buttons.
        Méthode d'aide pour construire le panneau latéral avec les boutons de menu.
        """
        # Crée le widget qui servira de barre latérale.
        sidebar = QWidget()
        # Nom de l'objet pour un style CSS spécifique.
        sidebar.setObjectName("sidebar")
        # Layout vertical pour aligner les boutons de haut en bas.
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # App Logo Label
        # Crée l'en-tête du menu (le "logo").
        title = QLabel("🔧 Atelier")
        title.setObjectName("app_title")
        layout.addWidget(title)

        # Add buttons for each page index
        # Initialise une liste pour garder une référence à tous les boutons de navigation.
        self.nav_buttons = []
        # Liste des sections avec leur nom et leur index correspondant dans le QStackedWidget.
        pages = [
            ("  Tableau de bord", 0),
            ("  Clients", 1),
            ("  Véhicules", 2),
            ("  Ordres de réparation", 3),
            ("  Facturation", 4),
            ("  Planning Atelier", 5),
            ("  Achats & Stocks", 6),
            ("  Agenda & RDV", 7),
            ("  CRM & Notifs", 8),
            ("  Retours & Garanties", 9),
            ("  Audit & Traçabilité", 10),
            ("  Assurances", 11),
        ]
        # Boucle sur chaque page pour creer son bouton.
        for label, idx in pages:
            btn = QPushButton(label)
            btn.setCheckable(False)
            btn.clicked.connect(lambda _, i=idx, l=label: self._navigate(i, l.strip()))
            self.nav_buttons.append(btn)
                if label == "  Retours \u0026 Garanties":
                    btn.clicked.disconnect()
                    btn.clicked.connect(lambda _: RetourPieceDialog.exec_dialog(parent=self))
            layout.addWidget(btn)

        # Bouton special Techniciens : ouvre un dialogue modal plutot qu'une page
        btn_tech = QPushButton("  Techniciens")
        btn_tech.clicked.connect(lambda: TechnicienManagerDialog.exec_dialog(parent=self))
        layout.addWidget(btn_tech)

        # Ajoute un ressort (espace extensible) pour repousser la version tout en bas.
        layout.addStretch()

        # Version label at bottom of sidebar
        # Affiche la version de l'application en bas de la barre latérale.
        version = QLabel("v1.0.0")
        version.setObjectName("label_muted")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        # Ajoute des marges spécifiques en bas.
        layout.setContentsMargins(8, 0, 8, 12)
        return sidebar

    def _make_header(self, title: str):
        """
        Helper to build the top navigation header.
        Méthode d'aide pour construire l'en-tête affichant le titre de la page en cours.
        """
        header = QWidget()
        header.setObjectName("page_header")
        # Layout horizontal pour aligner le titre à gauche.
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        
        # Titre actuel de la page.
        self.title_label = QLabel(title)
        self.title_label.setObjectName("page_title")
        layout.addWidget(self.title_label)
        
        # Pousse le titre vers la gauche.
        layout.addStretch()
        return header

    def _navigate(self, index: int, title: str):
        """
        Handles page-switching inside the QStackedWidget and updates active button styles.
        Gère le changement de page dans le conteneur et met à jour l'apparence des boutons.
        """
        # Change la page affichée dans le composant empilé à l'aide de son index.
        self.stack.setCurrentIndex(index)
        # Met à jour le texte du gros titre en haut.
        self.title_label.setText(title)
        
        # Update stylesheet properties to highlight active nav button
        # Boucle sur tous les boutons pour définir lequel est "actif" (pour le style CSS).
        for i, btn in enumerate(self.nav_buttons):
            # Assigne une propriété "active" (true pour le bouton cliqué, false pour les autres).
            btn.setProperty("active", "true" if i == index else "false")
            # Force la mise à jour visuelle (le moteur de style recalcule l'apparence).
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Refresh data on navigation if the active widget has a refresh method
        # Si on navigue vers une page, on déclenche sa méthode "refresh" pour que ses données soient à jour.
        widgets = [self.dashboard, self.clients, self.vehicules, self.ors, self.factures, self.planning, self.achats, self.agenda, self.crm, self.audit, self.sinistres]
        if hasattr(widgets[index], 'refresh'):
            widgets[index].refresh()
