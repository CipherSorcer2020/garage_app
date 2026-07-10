"""
ui/dialogs/historique_vehicule_dialog.py
-----------------------------------------
Dialog affichant l'historique complet d'un vehicule.
Affiche tous les OR passes avec :
- Statut et dates
- Diagnostic
- Pieces utilisees
- Main d'oeuvre
- Montant total
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QTabWidget, QWidget,
    QTextEdit, QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

import repositories.or_repo as or_repo
import repositories.diagnostic_repo as diagnostic_repo
import repositories.ligne_piece_repo as ligne_piece_repo
import repositories.ligne_mo_repo as ligne_mo_repo
import repositories.facture_repo as facture_repo
import repositories.utilisateur_repo as utilisateur_repo
from ui.widgets.or_widget import STATUT_LABELS, STATUT_COLORS


class HistoriqueVehiculeDialog(QDialog):
    """
    Dialog d'historique complet d'un vehicule.
    Affiche la liste de tous les OR dans un tableau,
    et le detail de l'OR selectionne dans un panneau lateral.
    """

    def __init__(self, vehicule, client, parent=None):
        super().__init__(parent)
        self.vehicule = vehicule
        self.client = client
        self.setWindowTitle(f"Historique — {vehicule.immatriculation}")
        self.setMinimumSize(1000, 620)
        self._load_data()
        self._build()

    def _load_data(self):
        """Charge tous les OR du vehicule depuis la BDD."""
        self._ors = or_repo.get_by_vehicule(self.vehicule.id)
        self._mecas = {u.id: u for u in utilisateur_repo.get_all()}

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ── En-tete vehicule ──────────────────────────────────
        header = QFrame()
        header.setObjectName("card")
        header_layout = QHBoxLayout(header)

        veh_info = QVBoxLayout()
        titre = QLabel(f"{self.vehicule.marque or ''} {self.vehicule.modele or ''} — {self.vehicule.immatriculation}")
        titre.setStyleSheet("font-size: 16px; font-weight: bold; color: #E8724A;")
        client_lbl = QLabel(f"Client : {self.client.nom} {self.client.prenom or ''}  |  Tél : {self.client.telephone or '—'}")
        client_lbl.setStyleSheet("color: #8A8F9E;")
        km_lbl = QLabel(f"Kilométrage actuel : {self.vehicule.kilometrage or '—'} km  |  Année : {self.vehicule.annee or '—'}")
        km_lbl.setStyleSheet("color: #8A8F9E;")
        veh_info.addWidget(titre)
        veh_info.addWidget(client_lbl)
        veh_info.addWidget(km_lbl)

        stats = QVBoxLayout()
        stats.setAlignment(Qt.AlignmentFlag.AlignRight)
        nb_or = QLabel(f"{len(self._ors)} intervention(s)")
        nb_or.setStyleSheet("font-size: 20px; font-weight: bold; color: #E8E6E1;")
        # Calcul du total facture pour ce vehicule
        total = 0.0
        for o in self._ors:
            f = facture_repo.get_by_or(o.id)
            if f and f.montant_ttc:
                total += f.montant_ttc
        total_lbl = QLabel(f"Total facturé : {total:.2f} DH")
        total_lbl.setStyleSheet("color: #4ADE80; font-weight: bold;")
        stats.addWidget(nb_or)
        stats.addWidget(total_lbl)

        header_layout.addLayout(veh_info)
        header_layout.addStretch()
        header_layout.addLayout(stats)
        layout.addWidget(header)

        # ── Contenu principal : liste OR + detail ─────────────
        content = QHBoxLayout()
        content.setSpacing(16)

        # Liste des OR (panneau gauche)
        left = QVBoxLayout()
        left_label = QLabel("Interventions")
        left_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #8A8F9E;")
        left.addWidget(left_label)

        self.or_table = QTableWidget(0, 4)
        self.or_table.setHorizontalHeaderLabels(["N° OR", "Date entrée", "Statut", "Montant TTC"])
        self.or_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.or_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.or_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.or_table.setAlternatingRowColors(True)
        self.or_table.verticalHeader().setVisible(False)
        self.or_table.setMinimumWidth(380)
        self.or_table.setMaximumWidth(420)
        self.or_table.currentRowChanged.connect(self._on_or_selected)
        self._fill_or_table()
        left.addWidget(self.or_table)
        content.addLayout(left)

        # Detail OR (panneau droit)
        right = QVBoxLayout()
        right_label = QLabel("Détail de l'intervention")
        right_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #8A8F9E;")
        right.addWidget(right_label)

        self.detail_widget = QTabWidget()
        self.detail_widget.setMinimumWidth(520)

        # Onglet résumé
        self.tab_resume = QWidget()
        self.tab_resume_layout = QVBoxLayout(self.tab_resume)
        self.detail_widget.addTab(self.tab_resume, "Résumé")

        # Onglet pièces
        self.tab_pieces = QWidget()
        tab_pieces_layout = QVBoxLayout(self.tab_pieces)
        self.pieces_table = QTableWidget(0, 4)
        self.pieces_table.setHorizontalHeaderLabels(["Désignation", "Réf.", "Qté", "Total HT"])
        self.pieces_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pieces_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.pieces_table.setAlternatingRowColors(True)
        self.pieces_table.verticalHeader().setVisible(False)
        tab_pieces_layout.addWidget(self.pieces_table)
        self.detail_widget.addTab(self.tab_pieces, "Pièces")

        # Onglet main d'oeuvre
        self.tab_mo = QWidget()
        tab_mo_layout = QVBoxLayout(self.tab_mo)
        self.mo_table = QTableWidget(0, 3)
        self.mo_table.setHorizontalHeaderLabels(["Description", "Durée (h)", "Total HT"])
        self.mo_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.mo_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.mo_table.setAlternatingRowColors(True)
        self.mo_table.verticalHeader().setVisible(False)
        tab_mo_layout.addWidget(self.mo_table)
        self.detail_widget.addTab(self.tab_mo, "Main d'œuvre")

        right.addWidget(self.detail_widget)
        content.addLayout(right)
        layout.addLayout(content)

        # ── Bouton fermer ─────────────────────────────────────
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        # Selectionner le premier OR par defaut
        if self._ors:
            self.or_table.selectRow(0)

    def _fill_or_table(self):
        """Remplit la liste des OR du vehicule."""
        self.or_table.setRowCount(0)
        for o in self._ors:
            row = self.or_table.rowCount()
            self.or_table.insertRow(row)

            # Montant de la facture si disponible
            f = facture_repo.get_by_or(o.id)
            montant_str = f"{f.montant_ttc:.2f} DH" if f and f.montant_ttc else "—"

            statut_label = STATUT_LABELS.get(o.statut, o.statut)
            color = STATUT_COLORS.get(o.statut, "#8A8F9E")

            vals = [f"#{o.id}", str(o.date_entree or "—"), statut_label, montant_str]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, o.id)
                if col == 2:
                    item.setForeground(QColor(color))
                self.or_table.setItem(row, col, item)

    def _on_or_selected(self, row):
        """Charge le detail de l'OR selectionne dans le panneau droit."""
        if row < 0 or row >= len(self._ors):
            return
        o = self._ors[row]
        self._load_detail(o)

    def _load_detail(self, o):
        """Charge et affiche toutes les donnees d'un OR dans les onglets."""

        # ── Onglet Resume ──────────────────────────────────────
        # Vider le layout precedent
        while self.tab_resume_layout.count():
            item = self.tab_resume_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        def info_row(label, value, color=None):
            """Cree une ligne label: valeur."""
            w = QWidget()
            h = QHBoxLayout(w)
            h.setContentsMargins(0, 2, 0, 2)
            lbl = QLabel(f"{label} :")
            lbl.setStyleSheet("color: #8A8F9E; min-width: 140px;")
            val = QLabel(str(value))
            if color:
                val.setStyleSheet(f"color: {color}; font-weight: bold;")
            h.addWidget(lbl)
            h.addWidget(val)
            h.addStretch()
            return w

        meca = self._mecas.get(o.mecanicien_id)
        meca_str = f"{meca.nom} {meca.prenom}" if meca else "Non affecté"
        statut_color = STATUT_COLORS.get(o.statut, "#8A8F9E")

        self.tab_resume_layout.addWidget(info_row("N° OR", f"#{o.id}"))
        self.tab_resume_layout.addWidget(info_row("Statut", STATUT_LABELS.get(o.statut, o.statut), statut_color))
        self.tab_resume_layout.addWidget(info_row("Date entrée", o.date_entree or "—"))
        self.tab_resume_layout.addWidget(info_row("Date sortie", o.date_sortie or "—"))
        self.tab_resume_layout.addWidget(info_row("Mécanicien", meca_str))

        # Description
        if o.description:
            desc_lbl = QLabel("Description du problème :")
            desc_lbl.setStyleSheet("color: #8A8F9E; margin-top: 8px;")
            self.tab_resume_layout.addWidget(desc_lbl)
            desc_val = QLabel(o.description)
            desc_val.setWordWrap(True)
            self.tab_resume_layout.addWidget(desc_val)

        # Diagnostic
        diag = diagnostic_repo.get_by_or(o.id)
        if diag and diag.observations:
            diag_lbl = QLabel("Diagnostic :")
            diag_lbl.setStyleSheet("color: #8A8F9E; margin-top: 8px;")
            self.tab_resume_layout.addWidget(diag_lbl)
            diag_val = QLabel(diag.observations)
            diag_val.setWordWrap(True)
            diag_val.setStyleSheet("color: #A78BFA;")
            self.tab_resume_layout.addWidget(diag_val)

        # Facture
        f = facture_repo.get_by_or(o.id)
        if f:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("color: #2A2D35; margin: 8px 0;")
            self.tab_resume_layout.addWidget(sep)
            self.tab_resume_layout.addWidget(info_row("N° Facture", f.numero))
            self.tab_resume_layout.addWidget(info_row("Montant HT", f"{f.montant_ht:.2f} DH" if f.montant_ht else "—"))
            self.tab_resume_layout.addWidget(info_row("TVA", f"{f.tva:.0f}%"))
            statut_f_color = "#4ADE80" if f.statut == "payee" else "#E8724A"
            self.tab_resume_layout.addWidget(info_row("Montant TTC", f"{f.montant_ttc:.2f} DH" if f.montant_ttc else "—", "#E8724A"))
            self.tab_resume_layout.addWidget(info_row("Paiement", "Payée" if f.statut == "payee" else "Non payée", statut_f_color))
            if f.mode_paiement:
                self.tab_resume_layout.addWidget(info_row("Mode", f.mode_paiement))

        self.tab_resume_layout.addStretch()

        # ── Onglet Pieces ──────────────────────────────────────
        self.pieces_table.setRowCount(0)
        pieces = ligne_piece_repo.get_by_or(o.id)
        for p in pieces:
            row = self.pieces_table.rowCount()
            self.pieces_table.insertRow(row)
            self.pieces_table.setItem(row, 0, QTableWidgetItem(p.designation))
            self.pieces_table.setItem(row, 1, QTableWidgetItem(p.reference or "—"))
            self.pieces_table.setItem(row, 2, QTableWidgetItem(str(p.quantite)))
            self.pieces_table.setItem(row, 3, QTableWidgetItem(f"{p.total_ht:.2f} DH" if p.total_ht else "—"))

        if not pieces:
            self.pieces_table.insertRow(0)
            item = QTableWidgetItem("Aucune pièce enregistrée")
            item.setForeground(QColor("#8A8F9E"))
            self.pieces_table.setItem(0, 0, item)

        # ── Onglet Main d'oeuvre ───────────────────────────────
        self.mo_table.setRowCount(0)
        mos = ligne_mo_repo.get_by_or(o.id)
        for m in mos:
            row = self.mo_table.rowCount()
            self.mo_table.insertRow(row)
            self.mo_table.setItem(row, 0, QTableWidgetItem(m.description))
            self.mo_table.setItem(row, 1, QTableWidgetItem(f"{m.duree_heures:.1f}h" if m.duree_heures else "—"))
            self.mo_table.setItem(row, 2, QTableWidgetItem(f"{m.total_ht:.2f} DH" if m.total_ht else "—"))

        if not mos:
            self.mo_table.insertRow(0)
            item = QTableWidgetItem("Aucune main d'œuvre enregistrée")
            item.setForeground(QColor("#8A8F9E"))
            self.mo_table.setItem(0, 0, item)
