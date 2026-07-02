from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QAbstractItemView, QComboBox, QLabel, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from repositories import facture_repo, client_repo, vehicule_repo, or_repo
from services import facturation_service, pdf_service


class FactureWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._build()
        self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        toolbar = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Toutes", "Non payées", "Payées"])
        self.filter_combo.currentIndexChanged.connect(self._filter)

        toolbar.addWidget(QLabel("Afficher :"))
        toolbar.addWidget(self.filter_combo)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["N° Facture", "Client", "Montant HT", "TVA %", "Montant TTC", "Statut"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        actions = QHBoxLayout()
        btn_pay = QPushButton("Marquer payée")
        btn_pay.setObjectName("btn_primary")
        btn_pay.clicked.connect(self._marquer_payee)

        btn_pdf = QPushButton("Générer PDF")
        btn_pdf.clicked.connect(self._generer_pdf)

        actions.addStretch()
        actions.addWidget(btn_pay)
        actions.addWidget(btn_pdf)
        layout.addLayout(actions)

        # Résumé CA
        self.lbl_ca = QLabel()
        self.lbl_ca.setStyleSheet("color: #E8724A; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.lbl_ca)

    def refresh(self):
        self._factures = facture_repo.get_all()
        self._clients = {c.id: c for c in client_repo.get_all()}
        self._fill_table(self._factures)
        ca = facturation_service.get_ca_total()
        self.lbl_ca.setText(f"CA total encaissé : {ca:.2f} DH")

    def _fill_table(self, factures):
        self.table.setRowCount(0)
        for f in factures:
            row = self.table.rowCount()
            self.table.insertRow(row)
            client = self._clients.get(f.client_id)
            client_str = f"{client.nom} {client.prenom or ''}" if client else "—"
            statut_color = "#4ADE80" if f.statut == "payee" else "#E8724A"
            statut_label = "✓ Payée" if f.statut == "payee" else "⏳ Non payée"
            vals = [f.numero, client_str,
                    f"{f.montant_ht:.2f} DH" if f.montant_ht else "—",
                    f"{f.tva:.0f}%",
                    f"{f.montant_ttc:.2f} DH" if f.montant_ttc else "—",
                    statut_label]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, f.id)
                if col == 5:
                    item.setForeground(QColor(statut_color))
                self.table.setItem(row, col, item)

    def _filter(self):
        idx = self.filter_combo.currentIndex()
        if idx == 1:
            self._fill_table([f for f in self._factures if f.statut == "non_payee"])
        elif idx == 2:
            self._fill_table([f for f in self._factures if f.statut == "payee"])
        else:
            self._fill_table(self._factures)

    def _selected_facture(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        fid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        return facture_repo.get_by_id(fid)

    def _marquer_payee(self):
        f = self._selected_facture()
        if not f:
            return
        if f.statut == "payee":
            QMessageBox.information(self, "Info", "Cette facture est déjà payée.")
            return
        from PyQt6.QtWidgets import QInputDialog
        modes = ["Espèces", "Carte bancaire", "Chèque", "Virement"]
        mode, ok = QInputDialog.getItem(self, "Mode de paiement", "Choisir :", modes, 0, False)
        if ok:
            facturation_service.marquer_payee(f.id, mode)
            self.refresh()

    def _generer_pdf(self):
        f = self._selected_facture()
        if not f:
            return
        try:
            from repositories import ligne_piece_repo, ligne_mo_repo
            client = self._clients.get(f.client_id)
            o = or_repo.get_by_id(f.or_id)
            vehicule = vehicule_repo.get_by_id(o.vehicule_id) if o else None
            pieces = ligne_piece_repo.get_by_or(f.or_id)
            mos = ligne_mo_repo.get_by_or(f.or_id)
            path = pdf_service.generer_facture_pdf(f, client, vehicule, pieces, mos)
            QMessageBox.information(self, "PDF généré", f"Facture enregistrée :\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
