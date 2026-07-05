# -*- coding: utf-8 -*-
# Spécifie l'encodage du fichier en UTF-8 pour supporter les accents.
# GUI Panel Widget for Vehicule view
# Ce widget représente le panneau de gestion des véhicules.
# Represents one of the main dashboard tabs in the user interface.
# Il est affiché comme un onglet du tableau de bord.

# Importation des composants graphiques depuis PyQt6.
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QLineEdit,
                              QHeaderView, QAbstractItemView, QMessageBox)
# Importation de Qt pour diverses constantes utiles.
from PyQt6.QtCore import Qt
# Importation des modules pour interagir avec les bases de données (véhicules et clients).
from repositories import vehicule_repo, client_repo
# Importation de la boîte de dialogue d'édition / création de véhicule.
from ui.dialogs.vehicule_dialog import VehiculeDialog


class VehiculeWidget(QWidget):
    # Classe gérant l'interface de la liste des véhicules.
    def __init__(self):
        """
        UI lifecycle method: '__init__'.
        Constructeur du composant VehiculeWidget.
        """
        # Initialise le QWidget parent.
        super().__init__()
        # Construit l'interface graphique.
        self._build()
        # Charge et affiche les données existantes.
        self.refresh()

    def _build(self):
        """
        UI lifecycle method: '_build'.
        Assemble les différents éléments (barre de recherche, tableau, boutons).
        """
        # Layout vertical principal pour empiler les éléments.
        layout = QVBoxLayout(self)
        # Marges de la fenêtre.
        layout.setContentsMargins(24, 24, 24, 24)
        # Espace entre chaque bloc du layout.
        layout.setSpacing(16)

        # Barre d'outils (Toolbar) contenant la recherche et le bouton d'ajout.
        toolbar = QHBoxLayout()
        # Champ de texte pour rechercher un véhicule.
        self.search = QLineEdit()
        self.search.setObjectName("search_input")
        # Texte indicatif quand la barre est vide.
        self.search.setPlaceholderText("Rechercher par immatriculation, marque…")
        # Appelle _search chaque fois que le texte change.
        self.search.textChanged.connect(self._search)

        # Bouton pour créer un nouveau véhicule.
        btn_add = QPushButton("+ Nouveau véhicule")
        btn_add.setObjectName("btn_primary")
        # Appelle _add quand on clique.
        btn_add.clicked.connect(self._add)

        # Ajoute la barre de recherche au layout horizontal.
        toolbar.addWidget(self.search)
        # Ajoute un espace flexible pour pousser le bouton à droite.
        toolbar.addStretch()
        # Ajoute le bouton.
        toolbar.addWidget(btn_add)
        # Ajoute la barre d'outils entière au layout principal.
        layout.addLayout(toolbar)

        # Tableau (Table) pour afficher la liste des véhicules.
        # 0 ligne au départ, 6 colonnes.
        self.table = QTableWidget(0, 6)
        # Définit les titres des colonnes.
        self.table.setHorizontalHeaderLabels(["Immatriculation", "Marque", "Modèle", "Année", "Kilométrage", "Client"])
        # Fait en sorte que les colonnes s'adaptent à la largeur disponible.
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Permet de sélectionner une ligne entière au clic, pas juste une cellule.
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # Empêche l'édition directe du texte dans le tableau.
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Active l'alternance des couleurs de lignes.
        self.table.setAlternatingRowColors(True)
        # Masque la colonne numérotée à gauche.
        self.table.verticalHeader().setVisible(False)
        # Permet d'ouvrir la modification lors d'un double clic sur une ligne.
        self.table.doubleClicked.connect(self._edit)
        # Ajoute le tableau au layout principal.
        layout.addWidget(self.table)

        # Barre d'actions en bas pour la modification et la suppression.
        actions = QHBoxLayout()
        # Bouton Modifier.
        btn_edit = QPushButton("Modifier")
        btn_edit.clicked.connect(self._edit)
        # Bouton Supprimer.
        btn_del = QPushButton("Supprimer")
        btn_del.setObjectName("btn_danger")
        btn_del.clicked.connect(self._delete)
        # Aligne ces boutons sur la droite.
        actions.addStretch()
        actions.addWidget(btn_edit)
        actions.addWidget(btn_del)
        # Ajoute la barre d'actions au layout principal.
        layout.addLayout(actions)

    def refresh(self):
        """
        UI lifecycle method: 'refresh'.
        Recharge les données des véhicules et des clients depuis la base de données.
        """
        # Récupère tous les véhicules.
        self._vehicules = vehicule_repo.get_all()
        # Récupère tous les clients et crée un dictionnaire {id: client} pour un accès rapide.
        self._clients = {c.id: c for c in client_repo.get_all()}
        # Remplit le tableau avec la liste des véhicules.
        self._fill_table(self._vehicules)

    def _fill_table(self, vehicules):
        """
        UI lifecycle method: '_fill_table'.
        Peuple le tableau avec une liste de véhicules donnée.
        """
        # Vide le tableau.
        self.table.setRowCount(0)
        # Pour chaque véhicule...
        for v in vehicules:
            # Récupère le numéro de la nouvelle ligne à ajouter.
            row = self.table.rowCount()
            # Insère la ligne.
            self.table.insertRow(row)
            # Récupère le client associé au véhicule (s'il existe).
            client = self._clients.get(v.client_id)
            # Formate le nom du client ou affiche un tiret ("—") s'il est introuvable.
            client_nom = f"{client.nom} {client.prenom or ''}" if client else "—"
            
            # Liste des valeurs à afficher, dans l'ordre des colonnes.
            # Convertit l'année et le kilométrage en texte de manière sécurisée.
            for col, val in enumerate([v.immatriculation, v.marque or "", v.modele or "",
                                        str(v.annee) if v.annee else "", str(v.kilometrage) if v.kilometrage else "", client_nom]):
                # Crée la cellule.
                item = QTableWidgetItem(val)
                # Sauvegarde l'ID du véhicule dans la cellule.
                item.setData(Qt.ItemDataRole.UserRole, v.id)
                # Ajoute la cellule au tableau.
                self.table.setItem(row, col, item)

    def _search(self, text):
        """
        UI lifecycle method: '_search'.
        Filtre les véhicules selon le texte saisi par l'utilisateur.
        """
        # Convertit le texte de recherche en minuscules.
        t = text.lower()
        # Crée une liste filtrée en gardant ceux dont l'immatriculation, la marque ou le modèle correspond.
        filtered = [v for v in self._vehicules if t in (v.immatriculation or "").lower()
                    or t in (v.marque or "").lower() or t in (v.modele or "").lower()]
        # Remplit le tableau avec ces résultats.
        self._fill_table(filtered)

    def _selected_id(self):
        """
        UI lifecycle method: '_selected_id'.
        Retourne l'identifiant (ID) du véhicule sélectionné dans le tableau.
        """
        # Récupère l'index de la ligne courante.
        row = self.table.currentRow()
        if row < 0:
            return None
        # Retourne la donnée invisible (UserRole) stockée en colonne 0 (l'ID).
        return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def _add(self):
        """
        UI lifecycle method: '_add'.
        Ouvre la boîte de dialogue de création d'un véhicule.
        """
        # Crée la fenêtre de dialogue pour les véhicules.
        dlg = VehiculeDialog(self)
        # Si l'utilisateur confirme (clique sur "Enregistrer")...
        if dlg.exec():
            # ... sauvegarde le nouveau véhicule dans la base.
            vehicule_repo.create(dlg.get_vehicule())
            # Actualise la liste affichée.
            self.refresh()

    def _edit(self):
        """
        UI lifecycle method: '_edit'.
        Ouvre la boîte de dialogue pour modifier le véhicule sélectionné.
        """
        # Récupère l'ID du véhicule sélectionné.
        vid = self._selected_id()
        if not vid:
            return
        # Charge les données complètes de ce véhicule.
        v = vehicule_repo.get_by_id(vid)
        # Ouvre la boîte de dialogue préremplie avec ces données.
        dlg = VehiculeDialog(self, vehicule=v)
        # Si l'utilisateur enregistre les modifications...
        if dlg.exec():
            # ... on récupère les nouvelles données.
            updated = dlg.get_vehicule()
            # On s'assure que l'ID reste le même.
            updated.id = vid
            # On met à jour l'enregistrement en base.
            vehicule_repo.update(updated)
            # On actualise l'affichage.
            self.refresh()

    def _delete(self):
        """
        UI lifecycle method: '_delete'.
        Supprime le véhicule sélectionné après confirmation.
        """
        # Récupère l'ID du véhicule.
        vid = self._selected_id()
        if not vid:
            return
        # Demande confirmation de suppression à l'utilisateur.
        reply = QMessageBox.question(self, "Confirmer", "Supprimer ce véhicule ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        # S'il clique sur "Oui"...
        if reply == QMessageBox.StandardButton.Yes:
            # ... efface le véhicule de la base.
            vehicule_repo.delete(vid)
            # Rafraîchit la liste.
            self.refresh()