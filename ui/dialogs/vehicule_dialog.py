# -*- coding: utf-8 -*-
# GUI Modal Dialog for Vehicule
# Renders an input form popup window for creation or editing.

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                              QSpinBox, QComboBox, QDialogButtonBox, QLabel)
from models.vehicule import Vehicule
from repositories import client_repo
import re

class VehiculeDialog(QDialog):
    def __init__(self, parent=None, vehicule: Vehicule = None):
        """
        Modal Dialog method: '__init__'.
        """
        super().__init__(parent)
        self.setWindowTitle("Nouveau véhicule" if not vehicule else "Modifier véhicule")
        self.setMinimumWidth(400)
        self._build(vehicule)

    def _build(self, v):
        """
        Modal Dialog method: '_build'.
        """
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.clients = client_repo.get_all()
        self.client_combo = QComboBox()
        for c in self.clients:
            self.client_combo.addItem(f"{c.nom} {c.prenom or ''}", c.id)
        if v:
            idx = next((i for i, c in enumerate(self.clients) if c.id == v.client_id), 0)
            self.client_combo.setCurrentIndex(idx)

        self.immat = QLineEdit(v.immatriculation if v else "")
        self.vin = QLineEdit(v.vin or "" if v else "")
        self.marque = QLineEdit(v.marque or "" if v else "")
        self.modele = QLineEdit(v.modele or "" if v else "")
        self.annee = QSpinBox()
        self.annee.setRange(1950, 2030)
        self.annee.setValue(v.annee if v and v.annee else 2020)
        self.km = QSpinBox()
        self.km.setRange(0, 9999999)
        self.km.setValue(v.kilometrage if v and v.kilometrage else 0)

        form.addRow("Client *", self.client_combo)
        form.addRow("Immatriculation *", self.immat)
        form.addRow("VIN", self.vin)
        form.addRow("Marque", self.marque)
        form.addRow("Modèle", self.modele)
        form.addRow("Année", self.annee)
        form.addRow("Kilométrage", self.km)
        layout.addLayout(form)

        self.error = QLabel("")
        self.error.setStyleSheet("color: #E05252;")
        layout.addWidget(self.error)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._validate)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _validate(self):
        """
        Modal Dialog method: '_validate'.
        """
        immat = self.immat.text().strip()
        if not immat:
            self.error.setText("L'immatriculation est obligatoire.")
        return
    
        # Format : 1-99999 / A-Z (une ou plusieurs lettres) / 1-88
        pattern = r'^([1-9]\d{0,4})-([A-Za-z])-([1-9]|[1-7][0-8]|88)$'
        if not re.match(pattern, immat):
            self.error.setText("Format invalide. Exemple : 12345-A-5  ou  100-AB-22")
        return
    
        self.accept()

    def get_vehicule(self) -> Vehicule:
        """
        Modal Dialog method: 'get_vehicule'.
        """
        return Vehicule(
            client_id=self.client_combo.currentData(),
            immatriculation=self.immat.text().strip().upper(),
            vin=self.vin.text().strip() or None,
            marque=self.marque.text().strip() or None,
            modele=self.modele.text().strip() or None,
            annee=self.annee.value(),
            kilometrage=self.km.value(),
        )