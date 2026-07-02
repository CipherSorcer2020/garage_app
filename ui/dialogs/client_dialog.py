# -*- coding: utf-8 -*-
# GUI Modal Dialog for Client
# Renders an input form popup window for creation or editing.

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                              QDialogButtonBox, QLabel)
from models.client import Client


class ClientDialog(QDialog):
    def __init__(self, parent=None, client: Client = None):
        """
        Modal Dialog method: '__init__'.
        """
        super().__init__(parent)
        self.setWindowTitle("Nouveau client" if not client else "Modifier client")
        self.setMinimumWidth(400)
        self._build(client)

    def _build(self, client):
        """
        Modal Dialog method: '_build'.
        """
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.nom = QLineEdit(client.nom if client else "")
        self.prenom = QLineEdit(client.prenom or "" if client else "")
        self.telephone = QLineEdit(client.telephone or "" if client else "")
        self.email = QLineEdit(client.email or "" if client else "")
        self.adresse = QLineEdit(client.adresse or "" if client else "")

        form.addRow("Nom *", self.nom)
        form.addRow("Prénom", self.prenom)
        form.addRow("Téléphone", self.telephone)
        form.addRow("Email", self.email)
        form.addRow("Adresse", self.adresse)
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
        if not self.nom.text().strip():
            self.error.setText("Le nom est obligatoire.")
            return
        self.accept()

    def get_client(self) -> Client:
        """
        Modal Dialog method: 'get_client'.
        """
        return Client(
            nom=self.nom.text().strip(),
            prenom=self.prenom.text().strip() or None,
            telephone=self.telephone.text().strip() or None,
            email=self.email.text().strip() or None,
            adresse=self.adresse.text().strip() or None,
        )