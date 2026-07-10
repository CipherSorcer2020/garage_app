# -*- coding: utf-8 -*-
# GUI Modal Dialog for Or
# Renders an input form popup window for creation or editing.

# Importation des widgets nécessaires de l'interface graphique PyQt6
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                              QTextEdit, QDialogButtonBox, QLabel, QSpinBox)
# Importation des dépôts (repositories) pour accéder aux données des véhicules et clients
from repositories import vehicule_repo, client_repo


# Classe ORDialog pour afficher la boîte de dialogue d'un Ordre de Réparation (OR)
class ORDialog(QDialog):
    # Constructeur de la fenêtre, initialise l'objet lors de sa création
    def __init__(self, parent=None):
        """
        Modal Dialog method: '__init__'.
        """
        # Initialisation de la classe parente QDialog
        super().__init__(parent)
        # Définition du titre de la fenêtre modale
        self.setWindowTitle("Nouvel ordre de réparation")
        # Définition de la largeur minimale de la fenêtre à 420 pixels
        self.setMinimumWidth(420)
        # Initialisation des attributs de l'ordre de réparation
        self.vehicule_id = None
        self.description = None
        self.kilometrage = None
        self.niveau_carburant = None
        # Appel de la méthode pour construire l'interface de la fenêtre
        self._build()

    # Méthode chargée de créer et placer les éléments de l'interface
    def _build(self):
        """
        Modal Dialog method: '_build'.
        """
        # Création du layout (gestionnaire d'affichage) vertical principal
        layout = QVBoxLayout(self)
        # Création d'un layout formulaire pour un alignement "Label : Champ"
        form = QFormLayout()

        # Récupération de la liste de tous les véhicules via le dépôt
        self._vehicules = vehicule_repo.get_all()
        # Récupération et création d'un dictionnaire des clients indexé par leur ID
        self._clients = {c.id: c for c in client_repo.get_all()}

        # Création d'une liste déroulante (QComboBox) pour sélectionner un véhicule
        self.vehicule_combo = QComboBox()
        # Boucle pour ajouter chaque véhicule dans la liste déroulante
        for v in self._vehicules:
            # Récupération du client associé au véhicule
            client = self._clients.get(v.client_id)
            # Création de l'étiquette affichée dans la liste (ex: 1234-A-1 — Peugeot 208 (Dupont))
            label = f"{v.immatriculation} — {v.marque or ''} {v.modele or ''} ({client.nom if client else '?'})"
            # Ajout de l'élément dans la liste avec son ID comme donnée cachée
            self.vehicule_combo.addItem(label, v.id)

        # Création d'un champ de texte multiligne pour la description du problème
        self.desc = QTextEdit()
        # Affichage d'un texte d'aide (placeholder) quand le champ est vide
        self.desc.setPlaceholderText("Description du problème signalé par le client…")
        # Limitation de la hauteur de la zone de texte à 100 pixels
        self.desc.setMaximumHeight(100)
        
        # Kilométrage
        self.kilo_spin = QSpinBox()
        self.kilo_spin.setRange(0, 1000000)
        self.kilo_spin.setSuffix(" km")
        self.kilo_spin.setSpecialValueText("Non renseigné")
        
        # Niveau de carburant
        self.carburant_combo = QComboBox()
        self.carburant_combo.addItems(["", "Vide", "1/4", "1/2", "3/4", "Plein"])

        # Ajout de la liste déroulante au formulaire avec le label "Véhicule *"
        form.addRow("Véhicule *", self.vehicule_combo)
        form.addRow("Kilométrage", self.kilo_spin)
        form.addRow("Niveau Carburant", self.carburant_combo)
        # Ajout de la zone de texte au formulaire avec le label "Description"
        form.addRow("Description", self.desc)
        # Ajout du layout formulaire au layout principal de la fenêtre
        layout.addLayout(form)

        # Création d'un label pour afficher un message d'erreur si besoin
        self.error = QLabel("")
        # Définition de la couleur du texte de l'erreur en rouge
        self.error.setStyleSheet("color: #E05252;")
        # Ajout du label d'erreur au layout principal
        layout.addWidget(self.error)

        # Ajout des boutons standard OK et Annuler de la boîte de dialogue
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        # Si on clique sur OK, on appelle la méthode de validation interne (_validate)
        btns.accepted.connect(self._validate)
        # Si on clique sur Annuler, on ferme simplement la fenêtre (reject)
        btns.rejected.connect(self.reject)
        # Ajout des boutons à la fin du layout principal
        layout.addWidget(btns)

    # Méthode pour valider les données du formulaire avant d'accepter
    def _validate(self):
        """
        Modal Dialog method: '_validate'.
        """
        # Récupération de l'ID du véhicule sélectionné dans la liste déroulante
        self.vehicule_id = self.vehicule_combo.currentData()
        # Récupération du texte de la description, ou None s'il est vide
        self.description = self.desc.toPlainText().strip() or None
        
        self.kilometrage = self.kilo_spin.value() or None
        self.niveau_carburant = self.carburant_combo.currentText().strip() or None
        # Vérification qu'un véhicule a bien été sélectionné
        if not self.vehicule_id:
            # Si non, on affiche un message d'erreur
            self.error.setText("Sélectionner un véhicule.")
            # On arrête la validation
            return
        # Si tout est bon, on accepte et on ferme la fenêtre de dialogue
        self.accept()