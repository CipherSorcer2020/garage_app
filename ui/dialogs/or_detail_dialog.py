# -*- coding: utf-8 -*-
# GUI Modal Dialog for Or_detail
# Renders an input form popup window for creation or editing.

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QTextEdit, QTabWidget, QWidget,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QFormLayout, QDoubleSpinBox, QSpinBox, QLineEdit,
                              QComboBox, QMessageBox, QAbstractItemView)
from PyQt6.QtCore import Qt
from services import or_service, facturation_service
from repositories import vehicule_repo, client_repo, utilisateur_repo, or_repo
from ui.widgets.or_widget import STATUT_LABELS, STATUT_COLORS
from PyQt6.QtGui import QColor


class ORDetailDialog(QDialog):
    def __init__(self, or_id: int, parent=None):
        """
        Modal Dialog method: '__init__'.
        """
        super().__init__(parent)
        self.or_id = or_id
        self.setWindowTitle(f"OR #{or_id}")
        self.setMinimumSize(780, 600)
        self._load()
        self._build()

    def _load(self):
        """
        Modal Dialog method: '_load'.
        """
        self.data = or_service.get_or_complet(self.or_id)
        self.o = self.data['or']
        v = vehicule_repo.get_by_id(self.o.vehicule_id)
        self.vehicule = v
        self.client = client_repo.get_by_id(v.client_id) if v else None
        self.mecas = utilisateur_repo.get_all()

    def _build(self):
        """
        Modal Dialog method: '_build'.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Header info
        info = QHBoxLayout()
        veh_str = f"{self.vehicule.immatriculation} — {self.vehicule.marque or ''} {self.vehicule.modele or ''}" if self.vehicule else "—"
        client_str = f"{self.client.nom} {self.client.prenom or ''}" if self.client else "—"
        info.addWidget(QLabel(f"<b>Véhicule :</b> {veh_str}"))
        info.addWidget(QLabel(f"<b>Client :</b> {client_str}"))

        statut = self.o.statut
        badge = QLabel(STATUT_LABELS.get(statut, statut))
        badge.setStyleSheet(f"color: {STATUT_COLORS.get(statut, '#8A8F9E')}; font-weight: bold; font-size: 13px;")
        info.addStretch()
        info.addWidget(QLabel("Statut :"))
        info.addWidget(badge)
        layout.addLayout(info)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._tab_diagnostic(), "Diagnostic")
        tabs.addTab(self._tab_devis(), "Devis & Pièces")
        tabs.addTab(self._tab_affectation(), "Affectation")
        layout.addWidget(tabs)

        # Actions
        actions = QHBoxLayout()
        btn_avancer = QPushButton("▶ Avancer le statut")
        btn_avancer.setObjectName("btn_primary")
        btn_avancer.clicked.connect(self._avancer)

        btn_facture = QPushButton("Générer facture")
        btn_facture.clicked.connect(self._generer_facture)

        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.accept)

        actions.addWidget(btn_avancer)
        actions.addWidget(btn_facture)
        actions.addStretch()
        actions.addWidget(btn_close)
        layout.addLayout(actions)

    def _tab_diagnostic(self):
        """
        Modal Dialog method: '_tab_diagnostic'.
        """
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Observations du technicien :"))
        self.diag_text = QTextEdit()
        self.diag_text.setPlaceholderText("Saisir les observations de diagnostic…")
        if self.data['diagnostic']:
            self.diag_text.setText(self.data['diagnostic'].observations or "")
        layout.addWidget(self.diag_text)
        btn = QPushButton("Enregistrer diagnostic")
        btn.setObjectName("btn_primary")
        btn.clicked.connect(self._save_diagnostic)
        layout.addWidget(btn)
        return w

    def _tab_devis(self):
        """
        Modal Dialog method: '_tab_devis'.
        """
        w = QWidget()
        layout = QVBoxLayout(w)

        # Pièces
        layout.addWidget(QLabel("<b>Pièces détachées</b>"))
        self.table_pieces = QTableWidget(0, 4)
        self.table_pieces.setHorizontalHeaderLabels(["Désignation", "Référence", "Qté", "Prix U. HT"])
        self.table_pieces.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_pieces.setAlternatingRowColors(True)
        self.table_pieces.verticalHeader().setVisible(False)
        for p in self.data['pieces']:
            self._add_piece_row(p.designation, p.reference or "", p.quantite, p.prix_unitaire_ht or 0)
        layout.addWidget(self.table_pieces)

        add_piece = QHBoxLayout()
        self.p_desig = QLineEdit(); self.p_desig.setPlaceholderText("Désignation")
        self.p_ref = QLineEdit(); self.p_ref.setPlaceholderText("Réf.")
        self.p_qty = QSpinBox(); self.p_qty.setRange(1, 999); self.p_qty.setValue(1)
        self.p_prix = QDoubleSpinBox(); self.p_prix.setRange(0, 999999); self.p_prix.setDecimals(2)
        btn_ap = QPushButton("+ Ajouter")
        btn_ap.clicked.connect(self._add_piece)
        for w2 in [self.p_desig, self.p_ref, self.p_qty, self.p_prix, btn_ap]:
            add_piece.addWidget(w2)
        layout.addLayout(add_piece)

        # MO
        layout.addWidget(QLabel("<b>Main d'œuvre</b>"))
        self.table_mo = QTableWidget(0, 3)
        self.table_mo.setHorizontalHeaderLabels(["Description", "Durée (h)", "Taux HT/h"])
        self.table_mo.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_mo.setAlternatingRowColors(True)
        self.table_mo.verticalHeader().setVisible(False)
        for m in self.data['main_oeuvre']:
            self._add_mo_row(m.description, m.duree_heures or 0, m.taux_horaire_ht or 0)
        layout.addWidget(self.table_mo)

        add_mo = QHBoxLayout()
        self.mo_desc = QLineEdit(); self.mo_desc.setPlaceholderText("Description MO")
        self.mo_duree = QDoubleSpinBox(); self.mo_duree.setRange(0, 999); self.mo_duree.setDecimals(1)
        self.mo_taux = QDoubleSpinBox(); self.mo_taux.setRange(0, 9999); self.mo_taux.setDecimals(2)
        btn_amo = QPushButton("+ Ajouter")
        btn_amo.clicked.connect(self._add_mo)
        for w2 in [self.mo_desc, self.mo_duree, self.mo_taux, btn_amo]:
            add_mo.addWidget(w2)
        layout.addLayout(add_mo)

        btn_save = QPushButton("Enregistrer le devis")
        btn_save.setObjectName("btn_primary")
        btn_save.clicked.connect(self._save_devis)
        layout.addWidget(btn_save)

        if self.data['devis']:
            d = self.data['devis']
            total = QLabel(f"Total HT : {d.montant_ht:.2f} DH  |  TTC : {d.montant_ttc:.2f} DH  |  {'✓ Accepté' if d.accepte else '⏳ En attente'}")
            total.setStyleSheet("color: #E8724A; font-weight: bold;")
            layout.addWidget(total)

            btns_devis = QHBoxLayout()
            btn_acc = QPushButton("✓ Accepter devis")
            btn_acc.setObjectName("btn_primary")
            btn_acc.clicked.connect(self._accepter_devis)
            btn_ref = QPushButton("✗ Refuser devis")
            btn_ref.setObjectName("btn_danger")
            btn_ref.clicked.connect(self._refuser_devis)
            btns_devis.addWidget(btn_acc)
            btns_devis.addWidget(btn_ref)
            btns_devis.addStretch()
            layout.addLayout(btns_devis)

        return w

    def _tab_affectation(self):
        """
        Modal Dialog method: '_tab_affectation'.
        """
        w = QWidget()
        layout = QFormLayout(w)
        self.meca_combo = QComboBox()
        for m in self.mecas:
            self.meca_combo.addItem(f"{m.nom} {m.prenom}", m.id)
        if self.o.mecanicien_id:
            idx = next((i for i, m in enumerate(self.mecas) if m.id == self.o.mecanicien_id), 0)
            self.meca_combo.setCurrentIndex(idx)
        layout.addRow("Mécanicien :", self.meca_combo)
        btn = QPushButton("Affecter")
        btn.setObjectName("btn_primary")
        btn.clicked.connect(self._affecter)
        layout.addRow("", btn)
        return w

    def _add_piece_row(self, desig, ref, qty, prix):
        """
        Modal Dialog method: '_add_piece_row'.
        """
        row = self.table_pieces.rowCount()
        self.table_pieces.insertRow(row)
        self.table_pieces.setItem(row, 0, QTableWidgetItem(desig))
        self.table_pieces.setItem(row, 1, QTableWidgetItem(ref))
        self.table_pieces.setItem(row, 2, QTableWidgetItem(str(qty)))
        self.table_pieces.setItem(row, 3, QTableWidgetItem(f"{prix:.2f}"))

    def _add_mo_row(self, desc, duree, taux):
        """
        Modal Dialog method: '_add_mo_row'.
        """
        row = self.table_mo.rowCount()
        self.table_mo.insertRow(row)
        self.table_mo.setItem(row, 0, QTableWidgetItem(desc))
        self.table_mo.setItem(row, 1, QTableWidgetItem(str(duree)))
        self.table_mo.setItem(row, 2, QTableWidgetItem(f"{taux:.2f}"))

    def _add_piece(self):
        """
        Modal Dialog method: '_add_piece'.
        """
        if self.p_desig.text().strip():
            self._add_piece_row(self.p_desig.text().strip(), self.p_ref.text().strip(),
                                self.p_qty.value(), self.p_prix.value())
            self.p_desig.clear(); self.p_ref.clear(); self.p_qty.setValue(1); self.p_prix.setValue(0)

    def _add_mo(self):
        """
        Modal Dialog method: '_add_mo'.
        """
        if self.mo_desc.text().strip():
            self._add_mo_row(self.mo_desc.text().strip(), self.mo_duree.value(), self.mo_taux.value())
            self.mo_desc.clear(); self.mo_duree.setValue(0); self.mo_taux.setValue(0)

    def _save_diagnostic(self):
        """
        Modal Dialog method: '_save_diagnostic'.
        """
        obs = self.diag_text.toPlainText().strip()
        or_service.ajouter_diagnostic(self.or_id, obs)
        QMessageBox.information(self, "OK", "Diagnostic enregistré.")

    def _save_devis(self):
        """
        Modal Dialog method: '_save_devis'.
        """
        pieces = []
        for row in range(self.table_pieces.rowCount()):
            pieces.append({
                'designation': self.table_pieces.item(row, 0).text(),
                'reference': self.table_pieces.item(row, 1).text(),
                'quantite': int(self.table_pieces.item(row, 2).text()),
                'prix_unitaire_ht': float(self.table_pieces.item(row, 3).text()),
            })
        mos = []
        for row in range(self.table_mo.rowCount()):
            mos.append({
                'description': self.table_mo.item(row, 0).text(),
                'duree_heures': float(self.table_mo.item(row, 1).text()),
                'taux_horaire_ht': float(self.table_mo.item(row, 2).text()),
            })
        d = or_service.creer_devis(self.or_id, pieces, mos)
        QMessageBox.information(self, "Devis", f"Devis enregistré — Total HT : {d.montant_ht:.2f} DH | TTC : {d.montant_ttc:.2f} DH")

    def _accepter_devis(self):
        """
        Modal Dialog method: '_accepter_devis'.
        """
        or_service.accepter_devis(self.or_id)
        QMessageBox.information(self, "OK", "Devis accepté.")

    def _refuser_devis(self):
        """
        Modal Dialog method: '_refuser_devis'.
        """
        or_service.refuser_devis(self.or_id)
        QMessageBox.information(self, "OK", "Devis refusé.")

    def _affecter(self):
        """
        Modal Dialog method: '_affecter'.
        """
        meca_id = self.meca_combo.currentData()
        or_service.affecter_mecanicien(self.or_id, meca_id)
        QMessageBox.information(self, "OK", "Mécanicien affecté.")

    def _avancer(self):
        """
        Modal Dialog method: '_avancer'.
        """
        try:
            o = or_service.avancer_statut(self.or_id)
            QMessageBox.information(self, "Statut", f"Nouveau statut : {STATUT_LABELS.get(o.statut, o.statut)}")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Attention", str(e))

    def _generer_facture(self):
        """
        Modal Dialog method: '_generer_facture'.
        """
        try:
            if not self.client:
                QMessageBox.warning(self, "Erreur", "Client introuvable.")
                return
            f = facturation_service.generer_facture(self.or_id, self.client.id)
            QMessageBox.information(self, "Facture", f"Facture {f.numero} générée — TTC : {f.montant_ttc:.2f} DH")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))