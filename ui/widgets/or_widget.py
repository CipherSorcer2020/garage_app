# -*- coding: utf-8 -*-
# GUI Panel Widget for Or view
# Represents one of the main dashboard tabs in the user interface.

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QAbstractItemView, QMessageBox, QLabel, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from repositories import or_repo, vehicule_repo, client_repo, utilisateur_repo
from services import or_service
from ui.dialogs.or_dialog import ORDialog


STATUT_COLORS = {
    'reception':             '#5B8CFF',
    'diagnostic':            '#A78BFA',
    'devis':                 '#FB923C',
    'accord_devis':          '#34D399',
    'affectation_mecanicien':'#FCD34D',
    'en_cours':              '#F97316',
    'test':                  '#22D3EE',
    'facture':               '#4ADE80',
    'livre':                 '#6B7280',
}

STATUT_LABELS = {
    'reception':             'Réception',
    'diagnostic':            'Diagnostic',
    'devis':                 'Devis',
    'accord_devis':          'Accord devis',
    'affectation_mecanicien':'Affectation',
    'en_cours':              'En cours',
    'test':                  'Test',
    'facture':               'Facturé',
    'livre':                 'Livré',
}


class ORWidget(QWidget):
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
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Tous les statuts", "")
        for k, v in STATUT_LABELS.items():
            self.filter_combo.addItem(v, k)
        self.filter_combo.currentIndexChanged.connect(self._filter)

        btn_add = QPushButton("+ Nouvel OR")
        btn_add.setObjectName("btn_primary")
        btn_add.clicked.connect(self._add)

        toolbar.addWidget(QLabel("Filtrer :"))
        toolbar.addWidget(self.filter_combo)
        toolbar.addStretch()
        toolbar.addWidget(btn_add)
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["N° OR", "Véhicule", "Client", "Entrée", "Statut", "Mécanicien"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._open_detail)
        layout.addWidget(self.table)

        actions = QHBoxLayout()
        btn_detail = QPushButton("Ouvrir / Avancer")
        btn_detail.setObjectName("btn_primary")
        btn_detail.clicked.connect(self._open_detail)
        btn_del = QPushButton("Supprimer")
        btn_del.setObjectName("btn_danger")
        btn_del.clicked.connect(self._delete)
        actions.addStretch()
        actions.addWidget(btn_detail)
        actions.addWidget(btn_del)
        layout.addLayout(actions)

    def refresh(self):
        """
        UI lifecycle method: 'refresh'.
        """
        self._ors = or_repo.get_all()
        self._vehicules = {v.id: v for v in vehicule_repo.get_all()}
        self._clients = {c.id: c for c in client_repo.get_all()}
        self._mecas = {u.id: u for u in utilisateur_repo.get_all()}
        self._fill_table(self._ors)

    def _fill_table(self, ors):
        """
        UI lifecycle method: '_fill_table'.
        """
        self.table.setRowCount(0)
        for o in ors:
            row = self.table.rowCount()
            self.table.insertRow(row)
            v = self._vehicules.get(o.vehicule_id)
            veh_str = f"{v.immatriculation}" if v else "—"
            client = self._clients.get(v.client_id) if v else None
            client_str = f"{client.nom} {client.prenom or ''}" if client else "—"
            meca = self._mecas.get(o.mecanicien_id)
            meca_str = f"{meca.nom}" if meca else "—"
            statut_label = STATUT_LABELS.get(o.statut, o.statut)
            color = STATUT_COLORS.get(o.statut, "#8A8F9E")

            vals = [f"#{o.id}", veh_str, client_str, str(o.date_entree or "—"), statut_label, meca_str]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, o.id)
                if col == 4:
                    item.setForeground(QColor(color))
                self.table.setItem(row, col, item)

    def _filter(self):
        """
        UI lifecycle method: '_filter'.
        """
        statut = self.filter_combo.currentData()
        if statut:
            self._fill_table([o for o in self._ors if o.statut == statut])
        else:
            self._fill_table(self._ors)

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
        dlg = ORDialog(self)
        if dlg.exec():
            or_service.creer_or(dlg.vehicule_id, dlg.description)
            self.refresh()

    def _open_detail(self):
        """
        UI lifecycle method: '_open_detail'.
        """
        or_id = self._selected_id()
        if not or_id:
            return
        from ui.dialogs.or_detail_dialog import ORDetailDialog
        dlg = ORDetailDialog(or_id, self)
        dlg.exec()
        self.refresh()

    def _delete(self):
        """
        UI lifecycle method: '_delete'.
        """
        or_id = self._selected_id()
        if not or_id:
            return
        reply = QMessageBox.question(self, "Confirmer", "Supprimer cet OR ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            or_repo.delete(or_id)
            self.refresh()