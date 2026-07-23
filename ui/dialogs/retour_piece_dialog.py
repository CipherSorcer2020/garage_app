# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from repositories import piece_repo, fournisseur_repo
from services import retour_piece_service

class RetourPieceDialog(QDialog):
    """Dialogue pour créer un retour de pièce."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Nouveau Retour / Garantie")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)

        # Pièce selection
        layout.addWidget(QLabel("Pièce à retourner :"))
        self.cb_piece = QComboBox()
        pieces = piece_repo.get_all()
        for p in pieces:
            self.cb_piece.addItem(f"[{p.reference}] {p.designation}", p.id)
        layout.addWidget(self.cb_piece)

        # Quantité
        layout.addWidget(QLabel("Quantité :"))
        self.sb_quantite = QSpinBox()
        self.sb_quantite.setRange(1, 9999)
        layout.addWidget(self.sb_quantite)

        # Fournisseur selection (optional)
        layout.addWidget(QLabel("Fournisseur (optionnel) :"))
        self.cb_fournisseur = QComboBox()
        self.cb_fournisseur.addItem("-- Aucun --", None)
        fournisseurs = fournisseur_repo.get_all()
        for f in fournisseurs:
            self.cb_fournisseur.addItem(f.nom, f.id)
        layout.addWidget(self.cb_fournisseur)

        # Motif
        layout.addWidget(QLabel("Motif du retour :"))
        self.le_motif = QLineEdit()
        self.le_motif.setPlaceholderText("Ex: Pièce défectueuse, erreur de commande...")
        layout.addWidget(self.le_motif)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        self.btn_save = QPushButton("Enregistrer")
        self.btn_save.setObjectName("btn_primary")
        self.btn_save.clicked.connect(self._save)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)

    def _save(self):
        piece_id = self.cb_piece.currentData()
        if not piece_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une pièce.")
            return
            
        quantite = self.sb_quantite.value()
        motif = self.le_motif.text().strip()
        fournisseur_id = self.cb_fournisseur.currentData()

        try:
            retour_piece_service.creer_retour(
                piece_id=piece_id,
                quantite=quantite,
                motif=motif,
                fournisseur_id=fournisseur_id
            )
            QMessageBox.information(self, "Succès", "Retour enregistré avec succès.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement :\n{str(e)}")

    @staticmethod
    def exec_dialog(parent=None):
        dlg = RetourPieceDialog(parent)
        return dlg.exec()
