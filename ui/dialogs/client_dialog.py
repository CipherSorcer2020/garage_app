# -*- coding: utf-8 -*-
# GUI Modal Dialog for Client
# Renders an input form popup window for creation or editing.

# Importation des composants graphiques nécessaires depuis PyQt6
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                              QDialogButtonBox, QLabel)
# Importation de la classe Client depuis le module des modèles
from models.client import Client


# Définition de la classe ClientDialog qui hérite de QDialog (une fenêtre modale)
class ClientDialog(QDialog):
    # Constructeur de la classe, appelé lors de la création d'une instance
    def __init__(self, parent=None, client: Client = None):
        """
        Modal Dialog method: '__init__'.
        """
        # Appel du constructeur de la classe parente QDialog
        super().__init__(parent)
        # Définition du titre de la fenêtre (Nouveau ou Modifier selon si un client est fourni)
        self.setWindowTitle("Nouveau client" if not client else "Modifier client")
        # Définition de la largeur minimale de la fenêtre à 400 pixels
        self.setMinimumWidth(400)
        # Appel de la méthode _build pour construire l'interface graphique
        self._build(client)

    # Méthode interne pour construire les éléments de l'interface
    def _build(self, client):
        """
        Modal Dialog method: '_build'.
        """
        # Création d'un layout vertical (les éléments seront empilés de haut en bas)
        layout = QVBoxLayout(self)
        # Création d'un layout de formulaire (pour aligner les étiquettes et les champs)
        form = QFormLayout()

        # Création des champs de texte (QLineEdit) pré-remplis si le client existe
        self.nom = QLineEdit(client.nom if client else "")
        self.prenom = QLineEdit(client.prenom or "" if client else "")
        self.telephone = QLineEdit(client.telephone or "" if client else "")
        self.email = QLineEdit(client.email or "" if client else "")
        self.adresse = QLineEdit(client.adresse or "" if client else "")

        # Ajout des lignes au formulaire avec un label pour chaque champ
        form.addRow("Nom *", self.nom)
        form.addRow("Prénom", self.prenom)
        form.addRow("Téléphone", self.telephone)
        form.addRow("Email", self.email)
        form.addRow("Adresse", self.adresse)
        # Ajout du formulaire au layout principal de la fenêtre
        layout.addLayout(form)

        # Création d'un label pour afficher d'éventuels messages d'erreur
        self.error = QLabel("")
        # Application d'un style CSS pour afficher le texte en rouge
        self.error.setStyleSheet("color: #E05252;")
        # Ajout du label d'erreur au layout principal
        layout.addWidget(self.error)

        # Création de boutons standard "OK" et "Annuler"
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        # Connexion du clic sur "OK" à la méthode de validation interne _validate
        btns.accepted.connect(self._validate)
        # Connexion du clic sur "Annuler" à la méthode reject pour fermer la fenêtre
        btns.rejected.connect(self.reject)
        # Ajout des boutons au layout principal
        layout.addWidget(btns)

    # Méthode de validation des données saisies
    def _validate(self):
        """
        Modal Dialog method: '_validate'.
        """
        # Vérification si le champ nom est vide (après suppression des espaces)
        if not self.nom.text().strip():
            # Affichage d'un message d'erreur et arrêt de la validation
            self.error.setText("Le nom est obligatoire.")
            return
        # Si valide, accepte la boîte de dialogue et la ferme
        self.accept()

    # Méthode pour obtenir une instance de Client avec les données du formulaire
    def get_client(self) -> Client:
        """
        Modal Dialog method: 'get_client'.
        """
        # Retourne un nouvel objet Client instancié avec les valeurs saisies
        return Client(
            nom=self.nom.text().strip(),
            prenom=self.prenom.text().strip() or None,
            telephone=self.telephone.text().strip() or None,
            email=self.email.text().strip() or None,
            adresse=self.adresse.text().strip() or None,
        )