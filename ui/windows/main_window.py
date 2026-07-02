import sys
import os
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion Atelier — Garage Auto")
        self.setMinimumSize(1200, 720)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self.sidebar = self._make_sidebar()
        root.addWidget(self.sidebar)

        # Content
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        self.header = self._make_header("Tableau de bord")
        right.addWidget(self.header)

        self.stack = QStackedWidget()
        self.dashboard = DashboardWidget()
        self.clients = ClientWidget()
        self.vehicules = VehiculeWidget()
        self.ors = ORWidget()
        self.factures = FactureWidget()

        for w in [self.dashboard, self.clients, self.vehicules, self.ors, self.factures]:
            self.stack.addWidget(w)

        right.addWidget(self.stack)

        right_widget = QWidget()
        right_widget.setLayout(right)
        root.addWidget(right_widget)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Connecté à garage_db")

    def _make_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title = QLabel("🔧 Atelier")
        title.setObjectName("app_title")
        layout.addWidget(title)

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
            btn.clicked.connect(lambda _, i=idx, l=label: self._navigate(i, l.strip()))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        version = QLabel("v1.0.0")
        version.setObjectName("label_muted")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        layout.setContentsMargins(8, 0, 8, 12)
        return sidebar

    def _make_header(self, title: str):
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
        self.stack.setCurrentIndex(index)
        self.title_label.setText(title)
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", "true" if i == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Refresh data on navigation
        widgets = [self.dashboard, self.clients, self.vehicules, self.ors, self.factures]
        if hasattr(widgets[index], 'refresh'):
            widgets[index].refresh()
