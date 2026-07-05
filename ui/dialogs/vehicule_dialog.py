# -*- coding: utf-8 -*-
# GUI Modal Dialog for Vehicule
# Renders an input form popup window for creation or editing.

# Importation des différents widgets depuis la bibliothèque PyQt6 pour l'interface graphique
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                              QSpinBox, QComboBox, QDialogButtonBox, QLabel)
# Importation du modèle de données Véhicule
from models.vehicule import Vehicule
# Importation du module d'accès aux données clients
from repositories import client_repo
# Importation du module pour les expressions régulières (regex)
import re

# Déclaration de la classe VehiculeDialog qui représente une boîte de dialogue modale
class VehiculeDialog(QDialog):
    # Méthode constructeur pour initialiser la boîte de dialogue, avec un véhicule optionnel
    def __init__(self, parent=None, vehicule: Vehicule = None):
        """
        Modal Dialog method: '__init__'.
        """
        # Initialisation de la classe de base QDialog
        super().__init__(parent)
        # Modification du titre de la fenêtre en fonction de l'existence ou non d'un véhicule (création/édition)
        self.setWindowTitle("Nouveau véhicule" if not vehicule else "Modifier véhicule")
        # Ajustement de la largeur minimale de la fenêtre à 400 pixels
        self.setMinimumWidth(400)
        # Appel à la méthode de construction de l'interface en transmettant le véhicule
        self._build(vehicule)

    # Méthode de création de l'interface utilisateur pour le formulaire
    def _build(self, v):
        """
        Modal Dialog method: '_build'.
        """
        # Création du layout (mise en page) principal de type vertical
        layout = QVBoxLayout(self)
        # Création d'un layout spécifique pour un formulaire (étiquette à gauche, champ à droite)
        form = QFormLayout()

        # Récupération de tous les clients existants depuis la base de données ou le dépôt
        self.clients = client_repo.get_all()
        # Création d'une liste déroulante pour le choix du client
        self.client_combo = QComboBox()
        # Boucle sur les clients pour remplir la liste déroulante avec leurs noms et prénoms
        for c in self.clients:
            self.client_combo.addItem(f"{c.nom} {c.prenom or ''}", c.id)
        
        # Si un véhicule est passé (mode modification), pré-sélectionner son client
        if v:
            # Recherche de l'index du client correspondant dans la liste déroulante
            idx = next((i for i, c in enumerate(self.clients) if c.id == v.client_id), 0)
            self.client_combo.setCurrentIndex(idx)

        # Création des champs de saisie textuels (QLineEdit) et pré-remplissage en mode modification
        self.immat = QLineEdit(v.immatriculation if v else "")
        # Texte d'exemple affiché quand le champ est vide (aide l'utilisateur sur le format attendu)
        self.immat.setPlaceholderText("Ex: 12345-A-05")
        # Connecte le signal "editingFinished" (quand l'utilisateur quitte le champ)
        # à la méthode qui formate automatiquement l'immatriculation
        self.immat.editingFinished.connect(self._auto_format_immat)

        self.vin = QLineEdit(v.vin or "" if v else "")
        self.marque = QLineEdit(v.marque or "" if v else "")
        self.modele = QLineEdit(v.modele or "" if v else "")
        
        # Création d'un champ numérique pour l'année du véhicule
        self.annee = QSpinBox()
        self.annee.setRange(1950, 2030) # Définition des bornes (min/max)
        self.annee.setValue(v.annee if v and v.annee else 2020) # Valeur par défaut : 2020
        
        # Création d'un champ numérique pour le kilométrage
        self.km = QSpinBox()
        self.km.setRange(0, 9999999) # Définition de la plage de valeurs
        self.km.setValue(v.kilometrage if v and v.kilometrage else 0)

        # Ajout de chaque champ dans le formulaire avec une étiquette correspondante
        form.addRow("Client *", self.client_combo)
        form.addRow("Immatriculation *", self.immat)
        form.addRow("VIN", self.vin)
        form.addRow("Marque", self.marque)
        form.addRow("Modèle", self.modele)
        form.addRow("Année", self.annee)
        form.addRow("Kilométrage", self.km)
        # Ajout de l'ensemble du formulaire au layout principal
        layout.addLayout(form)

        # Création d'un label réservé pour afficher les messages d'erreur
        self.error = QLabel("")
        self.error.setStyleSheet("color: #E05252;") # Couleur du texte (rouge)
        layout.addWidget(self.error)

        # Création de boutons standards OK et Annuler
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        # Connecte l'action d'acceptation (OK) à notre méthode de validation personnalisée
        btns.accepted.connect(self._validate)
        # Connecte l'action de rejet (Annuler) à la méthode de fermeture de la boîte de dialogue
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _auto_format_immat(self):
        """
        Formate automatiquement l'immatriculation quand l'utilisateur quitte le champ.
        Exemple : "12A52" devient "12-A-52", "12345AB22" devient "12345-AB-22".
        """
        # Récupère le texte et le met en majuscules
        text = self.immat.text().strip().upper()
        # Supprime tout ce qui n'est pas une lettre ou un chiffre (ex: tirets existants)
        clean = re.sub(r'[^A-Z0-9]', '', text)
        # Cherche le patron : chiffres, puis UNE SEULE lettre, puis chiffres
        match = re.match(r'^(\d+)([A-Z])(\d+)$', clean)
        if match:
            # Si le patron est trouvé, reconstruit avec des tirets
            formatted = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
            # Met à jour le champ avec la valeur formatée
            self.immat.setText(formatted)

    # Méthode chargée de valider la saisie de l'utilisateur
    def _validate(self):
        """
        Modal Dialog method: '_validate'.
        """
        # Lance d'abord le formatage automatique
        self._auto_format_immat()
        # Récupération de l'immatriculation saisie, sans les espaces au début et à la fin
        immat = self.immat.text().strip()

        # Vérification si l'immatriculation est vide
        if not immat:
            self.error.setText("L'immatriculation est obligatoire.")
            return

        # Vérification du format attendu : chiffres - UNE SEULE lettre - chiffres (ex: 12345-A-05)
        pattern = r'^\d+-[A-Z]-\d+$'
        if not re.match(pattern, immat):
            # Format invalide : affiche un message d'erreur et bloque la sauvegarde
            self.error.setText("Format invalide. Exemple : 12345-A-05 (une seule lettre autorisée)")
            return

        # Si tout est valide, efface l'erreur et ferme la fenêtre avec succès
        self.error.setText("")
        self.accept()


    # Méthode pour obtenir une nouvelle instance de Vehicule avec les données renseignées
    def get_vehicule(self) -> Vehicule:
        """
        Modal Dialog method: 'get_vehicule'.
        """
        # Création et renvoi de l'objet Vehicule
        return Vehicule(
            client_id=self.client_combo.currentData(), # L'ID du client sélectionné
            immatriculation=self.immat.text().strip().upper(), # L'immatriculation en majuscules
            vin=self.vin.text().strip() or None, # Le VIN s'il existe, sinon None
            marque=self.marque.text().strip() or None, # La marque s'il y en a une, sinon None
            modele=self.modele.text().strip() or None, # Le modèle s'il y en a un, sinon None
            annee=self.annee.value(), # L'année depuis le champ de type SpinBox
            kilometrage=self.km.value(), # Le kilométrage depuis le champ de type SpinBox
        )