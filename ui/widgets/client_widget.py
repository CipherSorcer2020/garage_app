# -*- coding: utf-8 -*-
# Spécifie l'encodage du fichier en UTF-8, permettant d'utiliser des caractères accentués.
# GUI Panel Widget for Client view
# Ce widget représente le panneau de gestion des clients.
# Represents one of the main dashboard tabs in the user interface.
# Il est affiché comme l'un des onglets principaux du tableau de bord.

# Importation des widgets nécessaires depuis PyQt6 pour créer l'interface graphique.
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QLineEdit,
                              QHeaderView, QAbstractItemView, QMessageBox)
# Importation de Qt pour accéder à certaines constantes et énumérations.
from PyQt6.QtCore import Qt
# Importation du module gérant l'accès aux données des clients dans la base de données.
import repositories.client_repo as client_repo
# Importation de la boîte de dialogue utilisée pour créer ou modifier un client.
from ui.dialogs.client_dialog import ClientDialog


class ClientWidget(QWidget):
    # La classe ClientWidget hérite de QWidget, ce qui en fait un composant visuel de base.
    def __init__(self):
        """
        UI lifecycle method: '__init__'.
        Constructeur de la classe, appelé lors de la création d'un nouveau ClientWidget.
        """
        # Appel du constructeur de la classe parente QWidget.
        super().__init__()
        # Appel de la méthode _build pour construire l'interface (placer les éléments).
        self._build()
        # Appel de la méthode refresh pour charger les données des clients.
        self.refresh()

    def _build(self):
        """
        UI lifecycle method: '_build'.
        Méthode chargée de créer et de placer tous les éléments visuels de la page.
        """
        # Création d'un layout vertical qui organisera les éléments de haut en bas.
        layout = QVBoxLayout(self)
        # Définition des marges internes du layout (gauche, haut, droite, bas).
        layout.setContentsMargins(24, 24, 24, 24)
        # Définition de l'espace (espacement) entre les éléments du layout.
        layout.setSpacing(16)

        # Toolbar (Barre d'outils)
        # Création d'un layout horizontal pour la barre de recherche et le bouton d'ajout.
        toolbar = QHBoxLayout()
        # Création d'un champ de texte pour la recherche.
        self.search = QLineEdit()
        # Définition du nom de l'objet, utile pour le styler en CSS.
        self.search.setObjectName("search_input")
        # Texte affiché par défaut quand le champ est vide (placeholder).
        self.search.setPlaceholderText("Rechercher un client…")
        # Connexion du signal textChanged à la méthode _search (appelée à chaque frappe au clavier).
        self.search.textChanged.connect(self._search)

        # Création du bouton pour ajouter un nouveau client.
        btn_add = QPushButton("+ Nouveau client")
        # Définition de son nom d'objet pour appliquer un style spécifique (ex: couleur primaire).
        btn_add.setObjectName("btn_primary")
        # Connexion de l'événement clic sur le bouton à la méthode _add.
        btn_add.clicked.connect(self._add)

        # Ajout de la barre de recherche au layout de la barre d'outils.
        toolbar.addWidget(self.search)
        # Ajout d'un espace flexible pour repousser le bouton d'ajout vers la droite.
        toolbar.addStretch()
        # Ajout du bouton d'ajout à droite.
        toolbar.addWidget(btn_add)
        # Ajout de la barre d'outils complète au layout principal.
        layout.addLayout(toolbar)

        # Table (Tableau de données)
        # Création d'un tableau initialement vide avec 0 ligne et 5 colonnes.
        self.table = QTableWidget(0, 5)
        # Définition des en-têtes (titres) des 5 colonnes.
        self.table.setHorizontalHeaderLabels(["Nom", "Prénom", "Téléphone", "Email", "Adresse"])
        # Configuration pour que les colonnes s'étirent pour prendre tout l'espace horizontal disponible.
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Configuration pour que la sélection se fasse par ligne entière et non par cellule individuelle.
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # Interdiction de modifier le texte directement en double-cliquant dans les cellules.
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Activation des couleurs alternées pour les lignes (pour améliorer la lisibilité).
        self.table.setAlternatingRowColors(True)
        # Masquage des numéros de lignes générés automatiquement sur la gauche du tableau.
        self.table.verticalHeader().setVisible(False)
        # Connexion du double-clic sur une ligne à la méthode d'édition _edit.
        self.table.doubleClicked.connect(self._edit)
        # Ajout du tableau au layout principal.
        layout.addWidget(self.table)

        # Actions (Boutons sous le tableau)
        # Création d'un nouveau layout horizontal pour les boutons de modification et suppression.
        actions = QHBoxLayout()
        # Création du bouton "Modifier".
        btn_edit = QPushButton("Modifier")
        # Connexion du clic à la méthode _edit.
        btn_edit.clicked.connect(self._edit)
        # Création du bouton "Supprimer".
        btn_del = QPushButton("Supprimer")
        # Nom de l'objet pour appliquer un style rouge (bouton d'action dangereuse).
        btn_del.setObjectName("btn_danger")
        # Connexion du clic à la méthode _delete.
        btn_del.clicked.connect(self._delete)
        # Ajout d'un espace flexible à gauche pour aligner les boutons à droite de l'écran.
        actions.addStretch()
        # Ajout du bouton de modification au layout des actions.
        actions.addWidget(btn_edit)
        # Ajout du bouton de suppression au layout des actions.
        actions.addWidget(btn_del)
        # Ajout de cette barre d'actions au layout principal.
        layout.addLayout(actions)

    def refresh(self):
        """
        UI lifecycle method: 'refresh'.
        Met à jour les données affichées dans l'interface (le tableau).
        """
        # Récupération de tous les clients existants depuis la base de données.
        self._clients = client_repo.get_all()
        # Remplissage du tableau visuel avec cette liste complète de clients.
        self._fill_table(self._clients)

    def _fill_table(self, clients):
        """
        UI lifecycle method: '_fill_table'.
        Remplit le tableau avec la liste de clients fournie en paramètre.
        """
        # Réinitialisation du nombre de lignes à 0 pour vider le tableau existant.
        self.table.setRowCount(0)
        # Boucle sur chaque client fourni dans la liste.
        for c in clients:
            # Récupère l'index de la nouvelle ligne à ajouter (à la fin).
            row = self.table.rowCount()
            # Insère une ligne vide à cet index.
            self.table.insertRow(row)
            # Prépare les données du client et boucle sur chaque valeur avec son index de colonne.
            # On utilise "or ''" pour éviter d'afficher 'None' si la donnée est vide.
            for col, val in enumerate([c.nom, c.prenom or "", c.telephone or "", c.email or "", c.adresse or ""]):
                # Crée un élément de tableau (cellule) avec la valeur texte.
                item = QTableWidgetItem(val)
                # Attache l'ID du client à la cellule de manière invisible (pour le retrouver plus tard).
                item.setData(Qt.ItemDataRole.UserRole, c.id)
                # Place l'élément dans la grille du tableau (ligne, colonne).
                self.table.setItem(row, col, item)

    def _search(self, text):
        """
        UI lifecycle method: '_search'.
        Gère la recherche dynamique de clients selon le texte saisi par l'utilisateur.
        """
        # Si le texte n'est pas vide (après avoir retiré les espaces de début et fin).
        if text.strip():
            # Cherche les clients correspondants dans la base et met à jour le tableau.
            self._fill_table(client_repo.search(text))
        else:
            # Sinon (champ vide), réaffiche la liste complète des clients.
            self._fill_table(self._clients)

    def _selected_id(self):
        """
        UI lifecycle method: '_selected_id'.
        Récupère l'identifiant (ID) du client actuellement sélectionné dans le tableau.
        """
        # Obtient l'indice de la ligne sélectionnée dans le tableau.
        row = self.table.currentRow()
        # Si aucune ligne n'est sélectionnée, row vaut -1.
        if row < 0:
            # Retourne Rien (None) s'il n'y a pas de sélection.
            return None
        # Retourne la donnée invisible (UserRole) stockée dans la première cellule de la ligne, c-à-d l'ID.
        return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def _add(self):
        """
        UI lifecycle method: '_add'.
        Ouvre la boîte de dialogue pour créer un nouveau client.
        """
        # Instanciation de la boîte de dialogue (formulaire) pour les clients.
        dlg = ClientDialog(self)
        # Affiche la boîte de dialogue. Si l'utilisateur clique sur 'Enregistrer' (exec() renvoie vrai)...
        if dlg.exec():
            # ... on crée le client dans la base de données avec les informations saisies.
            client_repo.create(dlg.get_client())
            # On rafraîchit le tableau pour y inclure le nouveau client.
            self.refresh()

    def _edit(self):
        """
        UI lifecycle method: '_edit'.
        Ouvre la boîte de dialogue pour modifier le client sélectionné.
        """
        # Récupère l'ID du client sélectionné.
        cid = self._selected_id()
        # Si aucun client n'est sélectionné, on arrête la méthode ici.
        if not cid:
            return
        # Récupère toutes les données de ce client depuis la base.
        c = client_repo.get_by_id(cid)
        # Instancie la boîte de dialogue en lui fournissant ce client existant pour préremplir le formulaire.
        dlg = ClientDialog(self, client=c)
        # Si l'utilisateur valide ses modifications...
        if dlg.exec():
            # ... on récupère l'objet client modifié depuis le formulaire.
            updated = dlg.get_client()
            # On s'assure qu'il conserve son ID d'origine.
            updated.id = cid
            # On met à jour l'enregistrement dans la base de données.
            client_repo.update(updated)
            # On rafraîchit l'affichage.
            self.refresh()

    def _delete(self):
        """
        UI lifecycle method: '_delete'.
        Supprime le client sélectionné après confirmation de l'utilisateur.
        """
        # Récupère l'ID du client sélectionné.
        cid = self._selected_id()
        # Si rien n'est sélectionné, on ne fait rien.
        if not cid:
            return
        # Affiche une boîte de dialogue demandant confirmation pour la suppression (Oui / Non).
        reply = QMessageBox.question(self, "Confirmer", "Supprimer ce client ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        # Si l'utilisateur a cliqué sur "Oui"...
        if reply == QMessageBox.StandardButton.Yes:
            # ... on supprime définitivement le client de la base de données.
            client_repo.delete(cid)
            # On met à jour l'affichage pour retirer ce client du tableau.
            self.refresh()