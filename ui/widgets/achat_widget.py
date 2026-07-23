# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QTabWidget, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from repositories import fournisseur_repo, commande_fournisseur_repo
from ui.dialogs.fournisseur_dialog import FournisseurDialog

class AchatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        # Onglet Fournisseurs
        self.tab_fournisseurs = QWidget()
        tf_layout = QVBoxLayout(self.tab_fournisseurs)
        
        self.table_f = QTableWidget(0, 5)
        self.table_f.setHorizontalHeaderLabels(["ID", "Nom", "Contact", "Téléphone", "Email"])
        self.table_f.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_f.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_f.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tf_layout.addWidget(self.table_f)
        
        btn_layout_f = QHBoxLayout()
        btn_add_f = QPushButton("+ Nouveau Fournisseur")
        btn_add_f.setObjectName("btn_primary")
        btn_add_f.clicked.connect(self._add_fournisseur)
        btn_edit_f = QPushButton("Modifier")
        btn_edit_f.clicked.connect(self._edit_fournisseur)
        
        btn_layout_f.addStretch()
        btn_layout_f.addWidget(btn_edit_f)
        btn_layout_f.addWidget(btn_add_f)
        tf_layout.addLayout(btn_layout_f)
        
        # Onglet Commandes
        self.tab_commandes = QWidget()
        tc_layout = QVBoxLayout(self.tab_commandes)
        self.table_c = QTableWidget(0, 5)
        self.table_c.setHorizontalHeaderLabels(["ID", "Fournisseur", "Statut", "Date Commande", "Date Réception"])
        self.table_c.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_c.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_c.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tc_layout.addWidget(self.table_c)
        
        btn_layout_c = QHBoxLayout()
        btn_add_c = QPushButton("+ Nouvelle Commande (A VENIR)")
        btn_layout_c.addStretch()
        btn_layout_c.addWidget(btn_add_c)
        tc_layout.addLayout(btn_layout_c)
        
        self.tabs.addTab(self.tab_fournisseurs, "Fournisseurs")
        self.tabs.addTab(self.tab_commandes, "Commandes")
        layout.addWidget(self.tabs)

    def refresh(self):
        self._refresh_fournisseurs()
        self._refresh_commandes()

    def _refresh_fournisseurs(self):
        fournisseurs = fournisseur_repo.get_all()
        self.table_f.setRowCount(0)
        for f in fournisseurs:
            r = self.table_f.rowCount()
            self.table_f.insertRow(r)
            id_item = QTableWidgetItem(str(f.id))
            id_item.setData(Qt.ItemDataRole.UserRole, f.id)
            self.table_f.setItem(r, 0, id_item)
            self.table_f.setItem(r, 1, QTableWidgetItem(f.nom))
            self.table_f.setItem(r, 2, QTableWidgetItem(f.contact))
            self.table_f.setItem(r, 3, QTableWidgetItem(f.telephone))
            self.table_f.setItem(r, 4, QTableWidgetItem(f.email))

    def _refresh_commandes(self):
        cmds = commande_fournisseur_repo.get_all()
        fournisseurs = {f.id: f.nom for f in fournisseur_repo.get_all()}
        self.table_c.setRowCount(0)
        for c in cmds:
            r = self.table_c.rowCount()
            self.table_c.insertRow(r)
            id_item = QTableWidgetItem(str(c.id))
            id_item.setData(Qt.ItemDataRole.UserRole, c.id)
            self.table_c.setItem(r, 0, id_item)
            self.table_c.setItem(r, 1, QTableWidgetItem(fournisseurs.get(c.fournisseur_id, "?")))
            self.table_c.setItem(r, 2, QTableWidgetItem(c.statut))
            self.table_c.setItem(r, 3, QTableWidgetItem(str(c.date_commande) if c.date_commande else ""))
            self.table_c.setItem(r, 4, QTableWidgetItem(str(c.date_reception) if c.date_reception else ""))

    def _add_fournisseur(self):
        dlg = FournisseurDialog(parent=self)
        if dlg.exec():
            self.refresh()

    def _edit_fournisseur(self):
        row = self.table_f.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un fournisseur.")
            return
        fid = self.table_f.item(row, 0).data(Qt.ItemDataRole.UserRole)
        dlg = FournisseurDialog(fid, parent=self)
        if dlg.exec():
            self.refresh()
