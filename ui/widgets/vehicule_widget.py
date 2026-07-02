# -*- coding: utf-8 -*-
# GUI Panel Widget for Vehicule view
# Represents one of the main dashboard tabs in the user interface.

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QLineEdit,
                              QHeaderView, QAbstractItemView, QMessageBox)
from PyQt6.QtCore import Qt
from repositories import vehicule_repo, client_repo
from ui.dialogs.vehicule_dialog import VehiculeDialog


class VehiculeWidget(QWidget):
    def __init__(self):
        """
        UI lifecycle method: '__init__'.
        """
        super().__init__()
        self._build()
        self.refresh()

    def _build(self):
        """
        UI lifecycle method: '_build'.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setObjectName("search_input")
        self.search.setPlaceholderText("Rechercher par immatriculation, marque…")
        self.search.textChanged.connect(self._search)

        btn_add = QPushButton("+ Nouveau véhicule")
        btn_add.setObjectName("btn_primary")
        btn_add.clicked.connect(self._add)

        toolbar.addWidget(self.search)
        toolbar.addStretch()
        toolbar.addWidget(btn_add)
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Immatriculation", "Marque", "Modèle", "Année", "Kilométrage", "Client"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._edit)
        layout.addWidget(self.table)

        actions = QHBoxLayout()
        btn_edit = QPushButton("Modifier")
        btn_edit.clicked.connect(self._edit)
        btn_del = QPushButton("Supprimer")
        btn_del.setObjectName("btn_danger")
        btn_del.clicked.connect(self._delete)
        actions.addStretch()
        actions.addWidget(btn_edit)
        actions.addWidget(btn_del)
        layout.addLayout(actions)

    def refresh(self):
        """
        UI lifecycle method: 'refresh'.
        """
        self._vehicules = vehicule_repo.get_all()
        self._clients = {c.id: c for c in client_repo.get_all()}
        self._fill_table(self._vehicules)

    def _fill_table(self, vehicules):
        """
        UI lifecycle method: '_fill_table'.
        """
        self.table.setRowCount(0)
        for v in vehicules:
            row = self.table.rowCount()
            self.table.insertRow(row)
            client = self._clients.get(v.client_id)
            client_nom = f"{client.nom} {client.prenom or ''}" if client else "—"
            for col, val in enumerate([v.immatriculation, v.marque or "", v.modele or "",
                                        str(v.annee) if v.annee else "", str(v.kilometrage) if v.kilometrage else "", client_nom]):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, v.id)
                self.table.setItem(row, col, item)

    def _search(self, text):
        """
        UI lifecycle method: '_search'.
        """
        t = text.lower()
        filtered = [v for v in self._vehicules if t in (v.immatriculation or "").lower()
                    or t in (v.marque or "").lower() or t in (v.modele or "").lower()]
        self._fill_table(filtered)

    def _selected_id(self):
        """
        UI lifecycle method: '_selected_id'.
        """
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def _add(self):
        """
        UI lifecycle method: '_add'.
        """
        dlg = VehiculeDialog(self)
        if dlg.exec():
            vehicule_repo.create(dlg.get_vehicule())
            self.refresh()

    def _edit(self):
        """
        UI lifecycle method: '_edit'.
        """
        vid = self._selected_id()
        if not vid:
            return
        v = vehicule_repo.get_by_id(vid)
        dlg = VehiculeDialog(self, vehicule=v)
        if dlg.exec():
            updated = dlg.get_vehicule()
            updated.id = vid
            vehicule_repo.update(updated)
            self.refresh()

    def _delete(self):
        """
        UI lifecycle method: '_delete'.
        """
        vid = self._selected_id()
        if not vid:
            return
        reply = QMessageBox.question(self, "Confirmer", "Supprimer ce véhicule ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            vehicule_repo.delete(vid)
            self.refresh()