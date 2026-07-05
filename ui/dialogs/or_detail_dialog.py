# -*- coding: utf-8 -*-
# GUI Modal Dialog for Or_detail
# Renders an input form popup window for creation or editing.

# Importations des composants UI nécessaires depuis PyQt6
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QTextEdit, QTabWidget, QWidget,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QFormLayout, QDoubleSpinBox, QSpinBox, QLineEdit,
                              QComboBox, QMessageBox, QAbstractItemView)
# Importation du namespace Qt pour des constantes diverses (alignements, etc.)
from PyQt6.QtCore import Qt
# Importation des services métiers pour les opérations sur les OR et la facturation
from services import or_service, facturation_service
# Importation des dépôts de données
from repositories import vehicule_repo, client_repo, utilisateur_repo, or_repo
# Importation des composants graphiques (labels et couleurs) liés aux statuts
from ui.widgets.or_widget import STATUT_LABELS, STATUT_COLORS
# Importation de QColor (bien que non utilisée explicitement en dessous)
from PyQt6.QtGui import QColor


# Définition de la classe ORDetailDialog héritant de QDialog
class ORDetailDialog(QDialog):
    # Constructeur de la classe, qui prend l'identifiant de l'OR (or_id)
    def __init__(self, or_id: int, parent=None):
        """
        Modal Dialog method: '__init__'.
        """
        # Appel du constructeur parent
        super().__init__(parent)
        # Mémorise l'ID de l'OR à afficher
        self.or_id = or_id
        # Définit le titre de la fenêtre avec l'ID de l'OR
        self.setWindowTitle(f"OR #{or_id}")
        # Fixe une taille minimale pour la fenêtre de dialogue (780x600 pixels)
        self.setMinimumSize(780, 600)
        # Charge toutes les données de l'OR depuis les bases de données
        self._load()
        # Construit l'interface graphique de la boîte de dialogue
        self._build()

    # Méthode pour charger les données nécessaires
    def _load(self):
        """
        Modal Dialog method: '_load'.
        """
        # Récupère l'OR complet (détails, pièces, MO, devis, etc.) via le service dédié
        self.data = or_service.get_or_complet(self.or_id)
        # Raccourci vers l'objet "or"
        self.o = self.data['or']
        # Récupère le véhicule associé à cet OR
        v = vehicule_repo.get_by_id(self.o.vehicule_id)
        self.vehicule = v
        # Si le véhicule existe, on récupère le client associé, sinon on met None
        self.client = client_repo.get_by_id(v.client_id) if v else None
        # Récupère la liste de tous les utilisateurs (pour affecter un mécanicien)
        self.mecas = utilisateur_repo.get_all()

    # Méthode pour construire la disposition globale de la fenêtre
    def _build(self):
        """
        Modal Dialog method: '_build'.
        """
        # Mise en place d'un layout vertical principal
        layout = QVBoxLayout(self)
        # Définit un espacement entre les éléments du layout
        layout.setSpacing(16)

        # Création d'une zone (layout horizontal) pour les informations d'en-tête
        info = QHBoxLayout()
        # Formate les informations du véhicule (immatriculation, marque, modèle)
        veh_str = f"{self.vehicule.immatriculation} — {self.vehicule.marque or ''} {self.vehicule.modele or ''}" if self.vehicule else "—"
        # Formate les informations du client (nom, prénom)
        client_str = f"{self.client.nom} {self.client.prenom or ''}" if self.client else "—"
        
        # Ajoute des étiquettes (QLabel) pour afficher le véhicule et le client en gras
        info.addWidget(QLabel(f"<b>Véhicule :</b> {veh_str}"))
        info.addWidget(QLabel(f"<b>Client :</b> {client_str}"))

        # Récupère le statut actuel de l'OR
        statut = self.o.statut
        # Création d'un badge visuel pour afficher le statut (avec libellé correspondant)
        badge = QLabel(STATUT_LABELS.get(statut, statut))
        # Applique une couleur de texte spécifique en fonction du statut
        badge.setStyleSheet(f"color: {STATUT_COLORS.get(statut, '#8A8F9E')}; font-weight: bold; font-size: 13px;")
        
        # Ajoute un espace flexible pour repousser le badge à droite
        info.addStretch()
        # Ajoute le label "Statut :" et le badge lui-même
        info.addWidget(QLabel("Statut :"))
        info.addWidget(badge)
        # Intègre le layout d'en-tête au layout principal
        layout.addLayout(info)

        # Création d'un widget de type onglets (QTabWidget)
        tabs = QTabWidget()
        # Ajout de l'onglet "Diagnostic"
        tabs.addTab(self._tab_diagnostic(), "Diagnostic")
        # Ajout de l'onglet "Devis & Pièces"
        tabs.addTab(self._tab_devis(), "Devis & Pièces")
        # Ajout de l'onglet "Affectation" pour désigner un mécanicien
        tabs.addTab(self._tab_affectation(), "Affectation")
        # Ajout du système d'onglets au layout principal
        layout.addWidget(tabs)

        # Création d'une zone pour les boutons d'action en bas de la fenêtre
        actions = QHBoxLayout()
        # Bouton pour faire avancer le statut de l'OR
        btn_avancer = QPushButton("▶ Avancer le statut")
        btn_avancer.setObjectName("btn_primary") # Style spécifique via nom d'objet
        btn_avancer.clicked.connect(self._avancer)

        # Bouton pour générer une facture à partir de l'OR
        btn_facture = QPushButton("Générer facture")
        btn_facture.clicked.connect(self._generer_facture)

        # Bouton pour fermer la boîte de dialogue
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.accept)

        # Ajout des boutons dans le layout horizontal
        actions.addWidget(btn_avancer)
        actions.addWidget(btn_facture)
        actions.addStretch() # Espace flexible au milieu
        actions.addWidget(btn_close) # Bouton fermer poussé à droite
        # Ajout de cette zone d'actions au layout principal
        layout.addLayout(actions)

    # Méthode pour construire l'onglet du diagnostic
    def _tab_diagnostic(self):
        """
        Modal Dialog method: '_tab_diagnostic'.
        """
        # Création d'un widget conteneur et de son layout vertical
        w = QWidget()
        layout = QVBoxLayout(w)
        # Label indicatif
        layout.addWidget(QLabel("Observations du technicien :"))
        # Création d'une zone de texte multiligne pour saisir les observations
        self.diag_text = QTextEdit()
        self.diag_text.setPlaceholderText("Saisir les observations de diagnostic…")
        
        # Si un diagnostic existe déjà dans les données, on pré-remplit la zone de texte
        if self.data['diagnostic']:
            self.diag_text.setText(self.data['diagnostic'].observations or "")
        layout.addWidget(self.diag_text)
        
        # Bouton pour sauvegarder le diagnostic
        btn = QPushButton("Enregistrer diagnostic")
        btn.setObjectName("btn_primary")
        btn.clicked.connect(self._save_diagnostic)
        layout.addWidget(btn)
        
        return w

    # Méthode pour construire l'onglet devis (pièces et main-d'œuvre)
    def _tab_devis(self):
        """
        Modal Dialog method: '_tab_devis'.
        """
        w = QWidget()
        layout = QVBoxLayout(w)

        # -- Section Pièces détachées --
        layout.addWidget(QLabel("<b>Pièces détachées</b>"))
        # Création d'un tableau pour les pièces (0 ligne au départ, 4 colonnes)
        self.table_pieces = QTableWidget(0, 4)
        # Définition des en-têtes des colonnes
        self.table_pieces.setHorizontalHeaderLabels(["Désignation", "Référence", "Qté", "Prix U. HT"])
        # Ajustement des colonnes pour qu'elles s'étirent et occupent tout l'espace
        self.table_pieces.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Activation des couleurs alternées pour les lignes (meilleure lisibilité)
        self.table_pieces.setAlternatingRowColors(True)
        # Masquage de l'en-tête vertical (numéros de lignes)
        self.table_pieces.verticalHeader().setVisible(False)
        
        # Remplissage du tableau avec les pièces existantes récupérées
        for p in self.data['pieces']:
            self._add_piece_row(p.designation, p.reference or "", p.quantite, p.prix_unitaire_ht or 0)
        layout.addWidget(self.table_pieces)

        # Formulaire horizontal pour ajouter une nouvelle pièce
        add_piece = QHBoxLayout()
        # Champs de saisie (texte, entier, décimal)
        self.p_desig = QLineEdit(); self.p_desig.setPlaceholderText("Désignation")
        self.p_ref = QLineEdit(); self.p_ref.setPlaceholderText("Réf.")
        self.p_qty = QSpinBox(); self.p_qty.setRange(1, 999); self.p_qty.setValue(1)
        self.p_prix = QDoubleSpinBox(); self.p_prix.setRange(0, 999999); self.p_prix.setDecimals(2)
        
        # Bouton d'ajout d'une pièce
        btn_ap = QPushButton("+ Ajouter")
        btn_ap.clicked.connect(self._add_piece)
        
        # Ajout des champs dans le layout horizontal
        for w2 in [self.p_desig, self.p_ref, self.p_qty, self.p_prix, btn_ap]:
            add_piece.addWidget(w2)
        layout.addLayout(add_piece)

        # -- Section Main d'œuvre (MO) --
        layout.addWidget(QLabel("<b>Main d'œuvre</b>"))
        # Création d'un tableau pour la main-d'œuvre (0 ligne au départ, 3 colonnes)
        self.table_mo = QTableWidget(0, 3)
        self.table_mo.setHorizontalHeaderLabels(["Description", "Durée (h)", "Taux HT/h"])
        self.table_mo.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_mo.setAlternatingRowColors(True)
        self.table_mo.verticalHeader().setVisible(False)
        
        # Remplissage avec la MO existante
        for m in self.data['main_oeuvre']:
            self._add_mo_row(m.description, m.duree_heures or 0, m.taux_horaire_ht or 0)
        layout.addWidget(self.table_mo)

        # Formulaire horizontal pour ajouter de la main-d'œuvre
        add_mo = QHBoxLayout()
        self.mo_desc = QLineEdit(); self.mo_desc.setPlaceholderText("Description MO")
        self.mo_duree = QDoubleSpinBox(); self.mo_duree.setRange(0, 999); self.mo_duree.setDecimals(1)
        self.mo_taux = QDoubleSpinBox(); self.mo_taux.setRange(0, 9999); self.mo_taux.setDecimals(2)
        
        # Bouton d'ajout pour la MO
        btn_amo = QPushButton("+ Ajouter")
        btn_amo.clicked.connect(self._add_mo)
        
        # Ajout au layout
        for w2 in [self.mo_desc, self.mo_duree, self.mo_taux, btn_amo]:
            add_mo.addWidget(w2)
        layout.addLayout(add_mo)

        # Bouton global pour enregistrer tout le devis (pièces + MO)
        btn_save = QPushButton("Enregistrer le devis")
        btn_save.setObjectName("btn_primary")
        btn_save.clicked.connect(self._save_devis)
        layout.addWidget(btn_save)

        # Si un devis est déjà enregistré, on affiche le récapitulatif
        if self.data['devis']:
            d = self.data['devis']
            # Affiche les montants totaux HT et TTC, et l'état d'acceptation
            total = QLabel(f"Total HT : {d.montant_ht:.2f} DH  |  TTC : {d.montant_ttc:.2f} DH  |  {'✓ Accepté' if d.accepte else '⏳ En attente'}")
            total.setStyleSheet("color: #E8724A; font-weight: bold;")
            layout.addWidget(total)

            # Boutons d'action pour accepter ou refuser le devis
            btns_devis = QHBoxLayout()
            btn_acc = QPushButton("✓ Accepter devis")
            btn_acc.setObjectName("btn_primary")
            btn_acc.clicked.connect(self._accepter_devis)
            
            btn_ref = QPushButton("✗ Refuser devis")
            btn_ref.setObjectName("btn_danger") # Style bouton d'avertissement/danger
            btn_ref.clicked.connect(self._refuser_devis)
            
            btns_devis.addWidget(btn_acc)
            btns_devis.addWidget(btn_ref)
            btns_devis.addStretch()
            layout.addLayout(btns_devis)

        return w

    # Méthode pour construire l'onglet d'affectation
    def _tab_affectation(self):
        """
        Modal Dialog method: '_tab_affectation'.
        """
        w = QWidget()
        layout = QFormLayout(w)
        # Création d'une liste déroulante pour les mécaniciens
        self.meca_combo = QComboBox()
        # Ajoute tous les utilisateurs/mécaniciens existants
        for m in self.mecas:
            self.meca_combo.addItem(f"{m.nom} {m.prenom}", m.id)
            
        # Si un mécanicien est déjà affecté à l'OR, on le sélectionne par défaut
        if self.o.mecanicien_id:
            idx = next((i for i, m in enumerate(self.mecas) if m.id == self.o.mecanicien_id), 0)
            self.meca_combo.setCurrentIndex(idx)
            
        # Ajout du champ au layout
        layout.addRow("Mécanicien :", self.meca_combo)
        
        # Bouton pour valider l'affectation
        btn = QPushButton("Affecter")
        btn.setObjectName("btn_primary")
        btn.clicked.connect(self._affecter)
        layout.addRow("", btn) # Ajoute le bouton à la suite
        
        return w

    # Méthode utilitaire pour ajouter une ligne dans le tableau des pièces
    def _add_piece_row(self, desig, ref, qty, prix):
        """
        Modal Dialog method: '_add_piece_row'.
        """
        # Compte le nombre de lignes actuel
        row = self.table_pieces.rowCount()
        # Insère une nouvelle ligne à la fin
        self.table_pieces.insertRow(row)
        # Remplit chaque cellule avec un QTableWidgetItem
        self.table_pieces.setItem(row, 0, QTableWidgetItem(desig))
        self.table_pieces.setItem(row, 1, QTableWidgetItem(ref))
        self.table_pieces.setItem(row, 2, QTableWidgetItem(str(qty)))
        # Formate le prix avec 2 décimales
        self.table_pieces.setItem(row, 3, QTableWidgetItem(f"{prix:.2f}"))

    # Méthode utilitaire pour ajouter une ligne dans le tableau de la main-d'œuvre
    def _add_mo_row(self, desc, duree, taux):
        """
        Modal Dialog method: '_add_mo_row'.
        """
        row = self.table_mo.rowCount()
        self.table_mo.insertRow(row)
        self.table_mo.setItem(row, 0, QTableWidgetItem(desc))
        self.table_mo.setItem(row, 1, QTableWidgetItem(str(duree)))
        self.table_mo.setItem(row, 2, QTableWidgetItem(f"{taux:.2f}"))

    # Action déclenchée par le bouton d'ajout de pièce
    def _add_piece(self):
        """
        Modal Dialog method: '_add_piece'.
        """
        # Vérifie qu'une désignation a été saisie
        if self.p_desig.text().strip():
            # Appelle la méthode d'insertion dans le tableau
            self._add_piece_row(self.p_desig.text().strip(), self.p_ref.text().strip(),
                                self.p_qty.value(), self.p_prix.value())
            # Réinitialise les champs de saisie pour une prochaine pièce
            self.p_desig.clear(); self.p_ref.clear(); self.p_qty.setValue(1); self.p_prix.setValue(0)

    # Action déclenchée par le bouton d'ajout de main-d'œuvre
    def _add_mo(self):
        """
        Modal Dialog method: '_add_mo'.
        """
        # Vérifie qu'une description a été saisie
        if self.mo_desc.text().strip():
            # Ajoute la ligne au tableau
            self._add_mo_row(self.mo_desc.text().strip(), self.mo_duree.value(), self.mo_taux.value())
            # Réinitialise les champs de saisie
            self.mo_desc.clear(); self.mo_duree.setValue(0); self.mo_taux.setValue(0)

    # Sauvegarde le diagnostic saisi
    def _save_diagnostic(self):
        """
        Modal Dialog method: '_save_diagnostic'.
        """
        # Récupère le texte saisi
        obs = self.diag_text.toPlainText().strip()
        # Fait appel au service pour enregistrer ce diagnostic en base
        or_service.ajouter_diagnostic(self.or_id, obs)
        # Affiche une boîte de message de confirmation
        QMessageBox.information(self, "OK", "Diagnostic enregistré.")

    # Sauvegarde l'intégralité du devis (pièces + MO)
    def _save_devis(self):
        """
        Modal Dialog method: '_save_devis'.
        """
        # Récupération des données du tableau des pièces sous forme de liste de dictionnaires
        pieces = []
        for row in range(self.table_pieces.rowCount()):
            pieces.append({
                'designation': self.table_pieces.item(row, 0).text(),
                'reference': self.table_pieces.item(row, 1).text(),
                'quantite': int(self.table_pieces.item(row, 2).text()),
                'prix_unitaire_ht': float(self.table_pieces.item(row, 3).text()),
            })
            
        # Même chose pour la main d'œuvre
        mos = []
        for row in range(self.table_mo.rowCount()):
            mos.append({
                'description': self.table_mo.item(row, 0).text(),
                'duree_heures': float(self.table_mo.item(row, 1).text()),
                'taux_horaire_ht': float(self.table_mo.item(row, 2).text()),
            })
            
        # Appel du service pour créer le devis complet
        d = or_service.creer_devis(self.or_id, pieces, mos)
        # Affichage du message de succès avec le nouveau total calculé
        QMessageBox.information(self, "Devis", f"Devis enregistré — Total HT : {d.montant_ht:.2f} DH | TTC : {d.montant_ttc:.2f} DH")

    # Action pour accepter un devis existant
    def _accepter_devis(self):
        """
        Modal Dialog method: '_accepter_devis'.
        """
        # Appel du service pour marquer le devis comme accepté
        or_service.accepter_devis(self.or_id)
        QMessageBox.information(self, "OK", "Devis accepté.")

    # Action pour refuser un devis existant
    def _refuser_devis(self):
        """
        Modal Dialog method: '_refuser_devis'.
        """
        # Appel du service pour marquer le devis comme refusé
        or_service.refuser_devis(self.or_id)
        QMessageBox.information(self, "OK", "Devis refusé.")

    # Action pour valider l'affectation d'un mécanicien à l'OR
    def _affecter(self):
        """
        Modal Dialog method: '_affecter'.
        """
        # Récupère l'ID du mécanicien sélectionné (stocké dans currentData)
        meca_id = self.meca_combo.currentData()
        # Fait appel au service pour mettre à jour l'OR
        or_service.affecter_mecanicien(self.or_id, meca_id)
        QMessageBox.information(self, "OK", "Mécanicien affecté.")

    # Fait avancer le statut de l'OR à l'étape suivante
    def _avancer(self):
        """
        Modal Dialog method: '_avancer'.
        """
        try:
            # Tente de passer au statut suivant selon la logique métier définie
            o = or_service.avancer_statut(self.or_id)
            # Affiche le nouveau statut si ça a fonctionné
            QMessageBox.information(self, "Statut", f"Nouveau statut : {STATUT_LABELS.get(o.statut, o.statut)}")
            # Ferme la fenêtre pour forcer le rafraîchissement global
            self.accept()
        except ValueError as e:
            # Affiche un avertissement si on ne peut pas avancer (ex: devis non accepté)
            QMessageBox.warning(self, "Attention", str(e))

    # Génère une facture finale pour cet OR
    def _generer_facture(self):
        """
        Modal Dialog method: '_generer_facture'.
        """
        try:
            # Vérifie qu'un client est bien défini
            if not self.client:
                QMessageBox.warning(self, "Erreur", "Client introuvable.")
                return
            # Demande au service de facturation de créer la facture
            f = facturation_service.generer_facture(self.or_id, self.client.id)
            # Affiche le numéro de facture et le montant
            QMessageBox.information(self, "Facture", f"Facture {f.numero} générée — TTC : {f.montant_ttc:.2f} DH")
            # Ferme la fenêtre après génération
            self.accept()
        except Exception as e:
            # Affiche une erreur critique si quelque chose échoue (ex: OR non terminé)
            QMessageBox.critical(self, "Erreur", str(e))