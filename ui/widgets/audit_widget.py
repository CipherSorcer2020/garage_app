# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from repositories import audit_log_repo

class AuditWidget(QWidget):
    """Affiche les actions d'audit du système.
    C'est un tableau en lecture‑seule qui peut être filtré par utilisateur.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Journal d'Audit (Traçabilité)</b>"))

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Date", "Utilisateur", "Action", "Table", "Enregistrement", "Détails"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Simple filtre par utilisateur (optionnel, futur)
        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.setObjectName("btn_primary")
        btn_refresh.clicked.connect(self.refresh)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_refresh)
        layout.addLayout(btn_layout)

    def refresh(self):
        logs = audit_log_repo.list_all()
        self.table.setRowCount(0)
        for log in logs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            dt_str = log.timestamp.strftime("%d/%m/%Y %H:%M") if log.timestamp else "?"
            self.table.setItem(row, 0, QTableWidgetItem(dt_str))
            self.table.setItem(row, 1, QTableWidgetItem(str(log.user_id)))
            self.table.setItem(row, 2, QTableWidgetItem(log.action))
            self.table.setItem(row, 3, QTableWidgetItem(log.entity))
            self.table.setItem(row, 4, QTableWidgetItem(str(log.entity_id)))
            self.table.setItem(row, 5, QTableWidgetItem(log.details or ""))
