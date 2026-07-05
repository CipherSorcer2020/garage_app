# -*- coding: utf-8 -*-
# Spécifie l'encodage du fichier en UTF-8 pour supporter les caractères accentués.
# GUI Panel Widget for Facture view
# Ce widget représente le panneau de gestion des factures.
# Represents one of the main dashboard tabs in the user interface.
# Il est affiché comme l'un des onglets principaux du tableau de bord.

# Importation des widgets de base depuis PyQt6.
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QAbstractItemView, QComboBox, QLabel, QMessageBox)
# Importation de Qt pour les paramètres généraux.
from PyQt6.QtCore import Qt
# Importation de QColor pour gérer les couleurs des textes dans le tableau.
from PyQt6.QtGui import QColor
# Importation des dépôts (repositories) pour accéder aux données en base.
from repositories import facture_repo, client_repo, vehicule_repo, or_repo
# Importation des services métiers pour les calculs (CA) et la génération PDF.
from services import facturation_service, pdf_service


class FactureWidget(QWidget):
    # Classe principale de l'interface des factures.
    def __init__(self):
        """
        UI lifecycle method: '__init__'.
        Constructeur du widget de facturation.
        """
        # Initialise le widget parent.
        super().__init__()
        # Construit l'interface graphique.
        self._build()
        # Charge les données au démarrage.
        self.refresh()

    def _build(self):
        """
        UI lifecycle method: '_build'.
        Assemble les différents éléments de la page de facturation.
        """
        # Création du layout vertical principal.
        layout = QVBoxLayout(self)
        # Marges de la fenêtre.
        layout.setContentsMargins(24, 24, 24, 24)
        # Espacement entre les composants.
        layout.setSpacing(16)

        # Création de la barre d'outils supérieure (Filtres).
        toolbar = QHBoxLayout()
        # Menu déroulant (ComboBox) pour filtrer les factures.
        self.filter_combo = QComboBox()
        # Ajout des options de filtre.
        self.filter_combo.addItems(["Toutes", "Non payées", "Payées"])
        # Connecte le changement de sélection à la méthode de filtrage.
        self.filter_combo.currentIndexChanged.connect(self._filter)

        # Ajoute le texte explicatif et le menu déroulant à la barre d'outils.
        toolbar.addWidget(QLabel("Afficher :"))
        toolbar.addWidget(self.filter_combo)
        # Pousse les éléments vers la gauche.
        toolbar.addStretch()
        # Ajoute la barre d'outils au layout principal.
        layout.addLayout(toolbar)

        # Tableau des factures (0 ligne au départ, 6 colonnes).
        self.table = QTableWidget(0, 6)
        # Définit les titres des colonnes.
        self.table.setHorizontalHeaderLabels(["N° Facture", "Client", "Montant HT", "TVA %", "Montant TTC", "Statut"])
        # Les colonnes s'étirent automatiquement pour occuper l'espace.
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Permet de sélectionner des lignes entières.
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # Interdit l'édition directe dans les cellules du tableau.
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Active l'alternance de couleurs pour une meilleure lisibilité.
        self.table.setAlternatingRowColors(True)
        # Masque la colonne des numéros de ligne à gauche.
        self.table.verticalHeader().setVisible(False)
        # Ajoute le tableau au layout principal.
        layout.addWidget(self.table)

        # Barre d'actions sous le tableau.
        actions = QHBoxLayout()
        # Bouton pour marquer une facture comme payée.
        btn_pay = QPushButton("Marquer payée")
        # Attribue le style principal (bleu/primaire).
        btn_pay.setObjectName("btn_primary")
        # Connecte le clic à l'action.
        btn_pay.clicked.connect(self._marquer_payee)

        # Bouton pour générer le PDF de la facture.
        btn_pdf = QPushButton("Générer PDF")
        btn_pdf.clicked.connect(self._generer_pdf)

        # Aligne les boutons à droite.
        actions.addStretch()
        actions.addWidget(btn_pay)
        actions.addWidget(btn_pdf)
        # Ajoute la barre d'actions au layout principal.
        layout.addLayout(actions)

        # Résumé CA (Chiffre d'Affaires).
        self.lbl_ca = QLabel()
        # Applique un style (couleur orange, gras) au label du CA.
        self.lbl_ca.setStyleSheet("color: #E8724A; font-size: 14px; font-weight: bold;")
        # Ajoute le label en bas de la page.
        layout.addWidget(self.lbl_ca)

    def refresh(self):
        """
        UI lifecycle method: 'refresh'.
        Recharge les factures, les clients, et le CA depuis la base de données.
        """
        # Récupère toutes les factures.
        self._factures = facture_repo.get_all()
        # Crée un dictionnaire des clients pour un accès rapide via leur ID.
        self._clients = {c.id: c for c in client_repo.get_all()}
        # Remplit le tableau avec toutes les factures.
        self._fill_table(self._factures)
        # Calcule le chiffre d'affaires total encaissé (factures payées).
        ca = facturation_service.get_ca_total()
        # Met à jour le texte du label CA avec le montant formaté.
        self.lbl_ca.setText(f"CA total encaissé : {ca:.2f} DH")

    def _fill_table(self, factures):
        """
        UI lifecycle method: '_fill_table'.
        Peuple le tableau visuel avec une liste de factures.
        """
        # Vide le tableau.
        self.table.setRowCount(0)
        # Boucle sur chaque facture à afficher.
        for f in factures:
            # Récupère le numéro de la nouvelle ligne.
            row = self.table.rowCount()
            # Ajoute une ligne au tableau.
            self.table.insertRow(row)
            # Récupère le client correspondant à la facture.
            client = self._clients.get(f.client_id)
            # Construit le nom complet du client.
            client_str = f"{client.nom} {client.prenom or ''}" if client else "—"
            # Détermine la couleur du texte du statut (vert si payée, orange sinon).
            statut_color = "#4ADE80" if f.statut == "payee" else "#E8724A"
            # Détermine le texte du statut avec un émoji.
            statut_label = "✓ Payée" if f.statut == "payee" else "⏳ Non payée"
            
            # Prépare les valeurs pour chaque colonne.
            vals = [f.numero, client_str,
                    f"{f.montant_ht:.2f} DH" if f.montant_ht else "—",
                    f"{f.tva:.0f}%",
                    f"{f.montant_ttc:.2f} DH" if f.montant_ttc else "—",
                    statut_label]
            
            # Boucle sur les valeurs pour créer les cellules.
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                # Attache l'ID de la facture à chaque cellule de la ligne.
                item.setData(Qt.ItemDataRole.UserRole, f.id)
                # Si on est sur la colonne du statut (colonne 5), on applique la couleur.
                if col == 5:
                    item.setForeground(QColor(statut_color))
                # Place la cellule dans le tableau.
                self.table.setItem(row, col, item)

    def _filter(self):
        """
        UI lifecycle method: '_filter'.
        Filtre la liste des factures affichées en fonction de l'option choisie.
        """
        # Récupère l'index sélectionné dans la liste déroulante.
        idx = self.filter_combo.currentIndex()
        if idx == 1:
            # Si "Non payées", affiche uniquement celles dont le statut est "non_payee".
            self._fill_table([f for f in self._factures if f.statut == "non_payee"])
        elif idx == 2:
            # Si "Payées", affiche uniquement celles dont le statut est "payee".
            self._fill_table([f for f in self._factures if f.statut == "payee"])
        else:
            # Sinon ("Toutes"), affiche toutes les factures.
            self._fill_table(self._factures)

    def _selected_facture(self):
        """
        UI lifecycle method: '_selected_facture'.
        Renvoie l'objet facture correspondant à la ligne sélectionnée.
        """
        # Récupère la ligne courante.
        row = self.table.currentRow()
        if row < 0:
            return None
        # Récupère l'ID de la facture depuis la donnée cachée.
        fid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        # Interroge la base pour renvoyer la facture complète.
        return facture_repo.get_by_id(fid)

    def _marquer_payee(self):
        """
        UI lifecycle method: '_marquer_payee'.
        Permet de passer une facture en statut "payée".
        """
        # Récupère la facture sélectionnée.
        f = self._selected_facture()
        if not f:
            return
        # Vérifie si elle est déjà payée.
        if f.statut == "payee":
            QMessageBox.information(self, "Info", "Cette facture est déjà payée.")
            return
        # Importe la boîte de dialogue de saisie locale.
        from PyQt6.QtWidgets import QInputDialog
        # Liste des modes de paiement possibles.
        modes = ["Espèces", "Carte bancaire", "Chèque", "Virement"]
        # Ouvre une fenêtre pour choisir le mode de paiement.
        mode, ok = QInputDialog.getItem(self, "Mode de paiement", "Choisir :", modes, 0, False)
        # Si l'utilisateur a cliqué sur "OK"...
        if ok:
            # Appelle le service pour enregistrer le paiement et changer le statut.
            facturation_service.marquer_payee(f.id, mode)
            # Rafraîchit l'affichage.
            self.refresh()

    def _generer_pdf(self):
        """
        UI lifecycle method: '_generer_pdf'.
        Génère un fichier PDF pour la facture sélectionnée.
        """
        # Récupère la facture sélectionnée.
        f = self._selected_facture()
        if not f:
            return
        try:
            # Importation des dépôts pour obtenir les lignes (pièces et main d'oeuvre) de l'Ordre de Réparation.
            from repositories import ligne_piece_repo, ligne_mo_repo
            # Récupère le client associé.
            client = self._clients.get(f.client_id)
            # Récupère l'ordre de réparation (OR) correspondant à la facture.
            o = or_repo.get_by_id(f.or_id)
            # Récupère le véhicule lié à l'OR.
            vehicule = vehicule_repo.get_by_id(o.vehicule_id) if o else None
            # Récupère la liste des pièces utilisées.
            pieces = ligne_piece_repo.get_by_or(f.or_id)
            # Récupère la liste des interventions (Main d'Oeuvre - MO).
            mos = ligne_mo_repo.get_by_or(f.or_id)
            # Appelle le service pour générer le document PDF et obtient le chemin du fichier.
            path = pdf_service.generer_facture_pdf(f, client, vehicule, pieces, mos)
            # Affiche un message de succès avec le chemin du fichier.
            QMessageBox.information(self, "PDF généré", f"Facture enregistrée :\n{path}")
        except Exception as e:
            # En cas d'erreur (ex: problème de droits d'écriture, fichier ouvert), affiche un message d'erreur.
            QMessageBox.critical(self, "Erreur", str(e))