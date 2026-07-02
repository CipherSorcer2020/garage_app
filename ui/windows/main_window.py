import sys
import os
# Ensure project path is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QPushButton, QLabel, QStackedWidget, QStatusBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.widgets.dashboard_widget import DashboardWidget
from ui.widgets.client_widget import ClientWidget
from ui.widgets.vehicule_widget import VehiculeWidget
from ui.widgets.or_widget import ORWidget
from ui.widgets.facture_widget import FactureWidget

class MainWindow(QMainWindow):
    """
    The primary GUI window for the application.
    Contains the side navigation bar, the top header, and a stacked widget
    to switch between different panel views (Dashboard, Clients, Vehicles, Work Orders, Invoices).
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion Atelier — Garage Auto")
        self.setMinimumSize(1200, 720)
        self._build_ui()

    def _build_ui(self):
        """
        Builds the overall window layout structure: sidebar on the left,
        main page content on the right.
        """
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Build and add Sidebar
        self.sidebar = self._make_sidebar()
        root.addWidget(self.sidebar)

        # Right-hand container
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        # Page Title Header
        self.header = self._make_header("Tableau de bord")
        right.addWidget(self.header)

        # Stacked pages layout (only one page is visible at a time)
        self.stack = QStackedWidget()
        self.dashboard = DashboardWidget()
        self.clients = ClientWidget()
        self.vehicules = VehiculeWidget()
        self.ors = ORWidget()
        self.factures = FactureWidget()

        # Add all panel widgets to stack index
        for w in [self.dashboard, self.clients, self.vehicules, self.ors, self.factures]:
            self.stack.addWidget(w)

        right.addWidget(self.stack)

        right_widget = QWidget()
        right_widget.setLayout(right)
        root.addWidget(right_widget)

        # Status Bar at bottom
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Connecté à garage_db")

    def _make_sidebar(self):
        """
        Helper to construct the side panel containing navigation buttons.
        """
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # App Logo Label
        title = QLabel("🔧 Atelier")
        title.setObjectName("app_title")
        layout.addWidget(title)

        # Add buttons for each page index
        self.nav_buttons = []
        pages = [
            ("  Tableau de bord", 0),
            ("  Clients", 1),
            ("  Véhicules", 2),
            ("  Ordres de réparation", 3),
            ("  Facturation", 4),
        ]
        for label, idx in pages:
            btn = QPushButton(label)
            btn.setCheckable(False)
            # Bind button clicks to navigation handler
            btn.clicked.connect(lambda _, i=idx, l=label: self._navigate(i, l.strip()))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Version label at bottom of sidebar
        version = QLabel("v1.0.0")
        version.setObjectName("label_muted")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        layout.setContentsMargins(8, 0, 8, 12)
        return sidebar

    def _make_header(self, title: str):
        """
        Helper to build the top navigation header.
        """
        header = QWidget()
        header.setObjectName("page_header")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("page_title")
        layout.addWidget(self.title_label)
        layout.addStretch()
        return header

    def _navigate(self, index: int, title: str):
        """
        Handles page-switching inside the QStackedWidget and updates active button styles.
        """
        self.stack.setCurrentIndex(index)
        self.title_label.setText(title)
        
        # Update stylesheet properties to highlight active nav button
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", "true" if i == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Refresh data on navigation if the active widget has a refresh method
        widgets = [self.dashboard, self.clients, self.vehicules, self.ors, self.factures]
        if hasattr(widgets[index], 'refresh'):
            widgets[index].refresh()
