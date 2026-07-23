# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from repositories import dossier_sinistre_repo

class SinistreWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Suivi des Dossiers Sinistres (Assurances)</b>"))
        
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Date", "OR #", "Assurance", "N° Dossier", "Montant Couvert", "Statut"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        btn_paye = QPushButton("Marquer comme 'Payé'")
        btn_paye.setObjectName("btn_primary")
        btn_paye.clicked.connect(self._mark_paye)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_paye)
        layout.addLayout(btn_layout)

    def refresh(self):
        dossiers = dossier_sinistre_repo.get_all()
        self.table.setRowCount(0)
        for d in dossiers:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            dt_str = d.date_creation.strftime("%d/%m/%Y") if d.date_creation else "?"
            
            id_item = QTableWidgetItem(dt_str)
            id_item.setData(Qt.ItemDataRole.UserRole, d.id)
            
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, QTableWidgetItem(str(d.or_id)))
            self.table.setItem(row, 2, QTableWidgetItem(d.nom_assurance))
            self.table.setItem(row, 3, QTableWidgetItem(d.numero_dossier))
            self.table.setItem(row, 4, QTableWidgetItem(f"{d.montant_couvert:.2f} €"))
            self.table.setItem(row, 5, QTableWidgetItem(d.statut))

    def _mark_paye(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un dossier.")
            return
            
        did = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        # We need a quick way to just update the status to paye
        dossiers = dossier_sinistre_repo.get_all()
        target = next((x for x in dossiers if x.id == did), None)
        if target:
            target.statut = 'paye'
            dossier_sinistre_repo.update(target)
            self.refresh()
