# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QFormLayout, QLineEdit, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from repositories import fournisseur_repo
from models.fournisseur import Fournisseur

class FournisseurDialog(QDialog):
    def __init__(self, f_id=None, parent=None):
        super().__init__(parent)
        self.f_id = f_id
        self._fournisseur = None
        self.setWindowTitle("Fournisseur")
        self.setMinimumWidth(400)
        self._build_ui()
        if f_id:
            self._load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.f_nom = QLineEdit()
        form.addRow("Nom *", self.f_nom)
        self.f_contact = QLineEdit()
        form.addRow("Contact", self.f_contact)
        self.f_telephone = QLineEdit()
        form.addRow("Téléphone", self.f_telephone)
        self.f_email = QLineEdit()
        form.addRow("Email", self.f_email)
        self.f_adresse = QLineEdit()
        form.addRow("Adresse", self.f_adresse)

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

    def _load_data(self):
        self._fournisseur = fournisseur_repo.get_by_id(self.f_id)
        if self._fournisseur:
            self.f_nom.setText(self._fournisseur.nom)
            self.f_contact.setText(self._fournisseur.contact)
            self.f_telephone.setText(self._fournisseur.telephone)
            self.f_email.setText(self._fournisseur.email)
            self.f_adresse.setText(self._fournisseur.adresse)

    def _save(self):
        nom = self.f_nom.text().strip()
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire.")
            return

        if self._fournisseur:
            self._fournisseur.nom = nom
            self._fournisseur.contact = self.f_contact.text().strip()
            self._fournisseur.telephone = self.f_telephone.text().strip()
            self._fournisseur.email = self.f_email.text().strip()
            self._fournisseur.adresse = self.f_adresse.text().strip()
            fournisseur_repo.update(self._fournisseur)
        else:
            f = Fournisseur(
                nom=nom,
                contact=self.f_contact.text().strip(),
                telephone=self.f_telephone.text().strip(),
                email=self.f_email.text().strip(),
                adresse=self.f_adresse.text().strip()
            )
            fournisseur_repo.create(f)

        self.accept()
