# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QFormLayout, QLineEdit, QDateTimeEdit, QComboBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, QDateTime
from repositories import rendez_vous_repo, client_repo, vehicule_repo
from models.rendez_vous import RendezVous

class RendezVousDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouveau Rendez-vous")
        self.setMinimumWidth(400)
        self._clients = {c.id: c for c in client_repo.get_all()}
        self._vehicules = vehicule_repo.get_all()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.cb_client = QComboBox()
        for c in self._clients.values():
            self.cb_client.addItem(f"{c.nom} {c.prenom}", c.id)
        self.cb_client.currentIndexChanged.connect(self._on_client_changed)
        form.addRow("Client *", self.cb_client)

        self.cb_vehicule = QComboBox()
        form.addRow("Véhicule *", self.cb_vehicule)

        self.dt_prevue = QDateTimeEdit()
        self.dt_prevue.setDateTime(QDateTime.currentDateTime().addDays(1))
        self.dt_prevue.setCalendarPopup(True)
        form.addRow("Date et Heure *", self.dt_prevue)

        self.sp_duree = QSpinBox()
        self.sp_duree.setRange(15, 480)
        self.sp_duree.setSingleStep(15)
        self.sp_duree.setValue(60)
        self.sp_duree.setSuffix(" min")
        form.addRow("Durée estimée", self.sp_duree)

        self.le_desc = QLineEdit()
        form.addRow("Motif / Description", self.le_desc)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Enregistrer")
        btn_save.setObjectName("btn_primary")
        btn_save.clicked.connect(self._save)
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)
        
        self._on_client_changed()

    def _on_client_changed(self):
        self.cb_vehicule.clear()
        client_id = self.cb_client.currentData()
        for v in self._vehicules:
            if v.client_id == client_id:
                self.cb_vehicule.addItem(v.immatriculation, v.id)

    def _save(self):
        cid = self.cb_client.currentData()
        vid = self.cb_vehicule.currentData()
        
        if not cid or not vid:
            QMessageBox.warning(self, "Erreur", "Un client et un véhicule doivent être sélectionnés.")
            return

        dt = self.dt_prevue.dateTime().toPyDateTime()
        
        r = RendezVous(
            client_id=cid,
            vehicule_id=vid,
            date_heure_prevue=dt,
            duree_estimee_minutes=self.sp_duree.value(),
            description=self.le_desc.text().strip()
        )
        rendez_vous_repo.create(r)
        self.accept()
