# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from repositories import rendez_vous_repo, client_repo, vehicule_repo
from ui.dialogs.rdv_dialog import RendezVousDialog

class AgendaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Date & Heure", "Client", "Véhicule", "Durée", "Statut", "Motif"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("+ Nouveau Rendez-vous")
        btn_add.setObjectName("btn_primary")
        btn_add.clicked.connect(self._add_rdv)
        
        btn_honore = QPushButton("Marquer Honoré")
        btn_honore.clicked.connect(lambda: self._change_statut('honore'))
        
        btn_noshow = QPushButton("No-Show / Annulé")
        btn_noshow.setObjectName("btn_danger")
        btn_noshow.clicked.connect(lambda: self._change_statut('annule'))
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_noshow)
        btn_layout.addWidget(btn_honore)
        btn_layout.addWidget(btn_add)
        layout.addLayout(btn_layout)

    def refresh(self):
        self._clients = {c.id: c for c in client_repo.get_all()}
        self._vehicules = {v.id: v for v in vehicule_repo.get_all()}
        rdvs = rendez_vous_repo.get_upcoming()
        
        self.table.setRowCount(0)
        for r in rdvs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Format datetime
            dt_str = r.date_heure_prevue.strftime("%d/%m/%Y %H:%M")
            c = self._clients.get(r.client_id)
            v = self._vehicules.get(r.vehicule_id)
            c_name = f"{c.nom} {c.prenom}" if c else "?"
            v_immat = v.immatriculation if v else "?"
            
            id_item = QTableWidgetItem(dt_str)
            id_item.setData(Qt.ItemDataRole.UserRole, r.id)
            
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, QTableWidgetItem(c_name))
            self.table.setItem(row, 2, QTableWidgetItem(v_immat))
            self.table.setItem(row, 3, QTableWidgetItem(f"{r.duree_estimee_minutes} min"))
            self.table.setItem(row, 4, QTableWidgetItem(r.statut))
            self.table.setItem(row, 5, QTableWidgetItem(r.description))

    def _add_rdv(self):
        dlg = RendezVousDialog(parent=self)
        if dlg.exec():
            self.refresh()
            
    def _change_statut(self, statut: str):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un rendez-vous.")
            return
        rid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        rendez_vous_repo.update_statut(rid, statut)
        self.refresh()
