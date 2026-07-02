from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                              QTextEdit, QDialogButtonBox, QLabel)
from repositories import vehicule_repo, client_repo


class ORDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouvel ordre de réparation")
        self.setMinimumWidth(420)
        self.vehicule_id = None
        self.description = None
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._vehicules = vehicule_repo.get_all()
        self._clients = {c.id: c for c in client_repo.get_all()}

        self.vehicule_combo = QComboBox()
        for v in self._vehicules:
            client = self._clients.get(v.client_id)
            label = f"{v.immatriculation} — {v.marque or ''} {v.modele or ''} ({client.nom if client else '?'})"
            self.vehicule_combo.addItem(label, v.id)

        self.desc = QTextEdit()
        self.desc.setPlaceholderText("Description du problème signalé par le client…")
        self.desc.setMaximumHeight(100)

        form.addRow("Véhicule *", self.vehicule_combo)
        form.addRow("Description", self.desc)
        layout.addLayout(form)

        self.error = QLabel("")
        self.error.setStyleSheet("color: #E05252;")
        layout.addWidget(self.error)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._validate)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _validate(self):
        self.vehicule_id = self.vehicule_combo.currentData()
        self.description = self.desc.toPlainText().strip() or None
        if not self.vehicule_id:
            self.error.setText("Sélectionner un véhicule.")
            return
        self.accept()
