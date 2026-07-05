# -*- coding: utf-8 -*-
# Spécifie l'encodage du fichier en UTF-8.
# GUI Panel Widget for Or view
# Ce widget représente le panneau des Ordres de Réparation (OR).
# Represents one of the main dashboard tabs in the user interface.
# Il s'agit de l'un des onglets principaux du tableau de bord.

# Importations des composants graphiques de PyQt6.
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QAbstractItemView, QMessageBox, QLabel, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
# Importation des dépôts de données nécessaires.
from repositories import or_repo, vehicule_repo, client_repo, utilisateur_repo
# Importation du service de gestion des OR.
from services import or_service
# Importation de la boîte de dialogue de création d'OR.
from ui.dialogs.or_dialog import ORDialog


# Dictionnaire associant chaque statut d'OR à une couleur spécifique (pour l'interface).
STATUT_COLORS = {
    'reception':             '#5B8CFF', # Bleu
    'diagnostic':            '#A78BFA', # Violet
    'devis':                 '#FB923C', # Orange
    'accord_devis':          '#34D399', # Vert émeraude
    'affectation_mecanicien':'#FCD34D', # Jaune
    'en_cours':              '#F97316', # Orange foncé
    'test':                  '#22D3EE', # Cyan
    'facture':               '#4ADE80', # Vert
    'livre':                 '#6B7280', # Gris
}

# Dictionnaire associant le nom technique d'un statut à son libellé affiché à l'utilisateur.
STATUT_LABELS = {
    'reception':             'Réception',
    'diagnostic':            'Diagnostic',
    'devis':                 'Devis',
    'accord_devis':          'Accord devis',
    'affectation_mecanicien':'Affectation',
    'en_cours':              'En cours',
    'test':                  'Test',
    'facture':               'Facturé',
    'livre':                 'Livré',
}


class ORWidget(QWidget):
    # Classe principale de la page des Ordres de Réparation.
    def __init__(self):
        """
        UI lifecycle method: '__init__'.
        Constructeur du widget.
        """
        super().__init__()
        # Construit l'interface.
        self._build()
        # Charge les données.
        self.refresh()

    def _build(self):
        """
        UI lifecycle method: '_build'.
        Crée et dispose les éléments graphiques de la page.
        """
        # Layout vertical principal.
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Barre d'outils supérieure.
        toolbar = QHBoxLayout()
        # Menu déroulant pour filtrer par statut.
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Tous les statuts", "")
        # Boucle pour ajouter chaque statut dans la liste déroulante.
        for k, v in STATUT_LABELS.items():
            self.filter_combo.addItem(v, k)
        # Connecte le changement de filtre à la méthode correspondante.
        self.filter_combo.currentIndexChanged.connect(self._filter)

        # Bouton pour créer un nouvel OR.
        btn_add = QPushButton("+ Nouvel OR")
        btn_add.setObjectName("btn_primary")
        btn_add.clicked.connect(self._add)

        # Ajoute les éléments à la barre d'outils.
        toolbar.addWidget(QLabel("Filtrer :"))
        toolbar.addWidget(self.filter_combo)
        toolbar.addStretch()
        toolbar.addWidget(btn_add)
        layout.addLayout(toolbar)

        # Tableau d'affichage des OR (0 ligne, 6 colonnes).
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["N° OR", "Véhicule", "Client", "Entrée", "Statut", "Mécanicien"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        # Double clic pour ouvrir les détails de l'OR.
        self.table.doubleClicked.connect(self._open_detail)
        layout.addWidget(self.table)

        # Barre d'actions en bas de page.
        actions = QHBoxLayout()
        # Bouton pour voir/modifier un OR.
        btn_detail = QPushButton("Ouvrir / Avancer")
        btn_detail.setObjectName("btn_primary")
        btn_detail.clicked.connect(self._open_detail)
        # Bouton pour supprimer un OR.
        btn_del = QPushButton("Supprimer")
        btn_del.setObjectName("btn_danger")
        btn_del.clicked.connect(self._delete)
        
        # Ajoute les boutons avec alignement à droite.
        actions.addStretch()
        actions.addWidget(btn_detail)
        actions.addWidget(btn_del)
        layout.addLayout(actions)

    def refresh(self):
        """
        UI lifecycle method: 'refresh'.
        Récupère toutes les données nécessaires et met à jour le tableau.
        """
        # Récupération des données depuis les bases.
        self._ors = or_repo.get_all()
        # Création de dictionnaires pour associer rapidement un ID à son objet.
        self._vehicules = {v.id: v for v in vehicule_repo.get_all()}
        self._clients = {c.id: c for c in client_repo.get_all()}
        self._mecas = {u.id: u for u in utilisateur_repo.get_all()}
        # Remplit le tableau avec tous les OR.
        self._fill_table(self._ors)

    def _fill_table(self, ors):
        """
        UI lifecycle method: '_fill_table'.
        Peuple le tableau avec la liste d'Ordres de Réparation fournie.
        """
        self.table.setRowCount(0)
        # Boucle sur chaque OR.
        for o in ors:
            row = self.table.rowCount()
            self.table.insertRow(row)
            # Retrouve le véhicule concerné.
            v = self._vehicules.get(o.vehicule_id)
            veh_str = f"{v.immatriculation}" if v else "—"
            # Retrouve le client propriétaire du véhicule.
            client = self._clients.get(v.client_id) if v else None
            client_str = f"{client.nom} {client.prenom or ''}" if client else "—"
            # Retrouve le mécanicien affecté (s'il y en a un).
            meca = self._mecas.get(o.mecanicien_id)
            meca_str = f"{meca.nom}" if meca else "—"
            # Récupère le nom affichable du statut et sa couleur.
            statut_label = STATUT_LABELS.get(o.statut, o.statut)
            color = STATUT_COLORS.get(o.statut, "#8A8F9E")

            # Prépare les valeurs de la ligne.
            vals = [f"#{o.id}", veh_str, client_str, str(o.date_entree or "—"), statut_label, meca_str]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                # Sauvegarde l'ID de l'OR.
                item.setData(Qt.ItemDataRole.UserRole, o.id)
                # Applique la couleur spéciale sur la colonne du Statut (index 4).
                if col == 4:
                    item.setForeground(QColor(color))
                self.table.setItem(row, col, item)

    def _filter(self):
        """
        UI lifecycle method: '_filter'.
        Filtre le tableau selon le statut sélectionné dans la liste déroulante.
        """
        # Récupère la donnée associée au choix actuel (la clé du statut).
        statut = self.filter_combo.currentData()
        if statut:
            # Si un statut précis est choisi, filtre la liste.
            self._fill_table([o for o in self._ors if o.statut == statut])
        else:
            # Sinon, affiche tout.
            self._fill_table(self._ors)

    def _selected_id(self):
        """
        UI lifecycle method: '_selected_id'.
        Renvoie l'ID de l'OR de la ligne sélectionnée.
        """
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def _add(self):
        """
        UI lifecycle method: '_add'.
        Ouvre la fenêtre de création d'un nouvel OR.
        """
        dlg = ORDialog(self)
        # Si on valide le formulaire...
        if dlg.exec():
            # Appelle le service pour créer un nouvel Ordre de Réparation.
            or_service.creer_or(dlg.vehicule_id, dlg.description)
            # Met à jour la liste affichée.
            self.refresh()

    def _open_detail(self):
        """
        UI lifecycle method: '_open_detail'.
        Ouvre la vue détaillée d'un OR (pour ajouter des pièces, avancer le statut, etc.).
        """
        or_id = self._selected_id()
        if not or_id:
            return
        # Import local pour éviter les imports croisés circulaires.
        from ui.dialogs.or_detail_dialog import ORDetailDialog
        # Ouvre le dialogue de détail.
        dlg = ORDetailDialog(or_id, self)
        dlg.exec()
        # Actualise au cas où des modifications ont été faites (ex: changement de statut).
        self.refresh()

    def _delete(self):
        """
        UI lifecycle method: '_delete'.
        Supprime l'OR sélectionné après confirmation.
        """
        or_id = self._selected_id()
        if not or_id:
            return
        # Demande confirmation.
        reply = QMessageBox.question(self, "Confirmer", "Supprimer cet OR ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # Supprime l'OR de la base de données.
            or_repo.delete(or_id)
            # Rafraîchit l'affichage.
            self.refresh()