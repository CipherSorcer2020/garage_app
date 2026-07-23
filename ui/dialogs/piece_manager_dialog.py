"""Dialog for managing spare parts inventory (CRUD)."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
    QLineEdit, QLabel, QSpinBox, QFormLayout
)
from PyQt6.QtCore import Qt

from repositories import piece_repo

class PieceManagerDialog(QDialog):
    """Simple CRUD UI for pieces.

    - List all pieces in a table.
    - Add / Edit / Delete via separate form fields at the bottom.
    - Emits acceptance without returning data (inventory is persisted directly).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion du stock de pièces")
        self.setMinimumSize(800, 500)
        self._load_data()
        self._build()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build(self):
        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Référence", "Désignation", "Quantité", "Prix unitaire"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.currentRowChanged.connect(self._on_row_selected)
        layout.addWidget(self.table)

        # Form for add / edit
        form = QFormLayout()
        self.ref_edit = QLineEdit()
        self.desig_edit = QLineEdit()
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(0, 100000)
        self.price_edit = QLineEdit()
        form.addRow("Référence", self.ref_edit)
        form.addRow("Désignation", self.desig_edit)
        form.addRow("Quantité", self.qty_spin)
        form.addRow("Prix unitaire", self.price_edit)
        self.low_stock_label = QLabel()
        self.low_stock_label.setStyleSheet("color: #E05252; font-weight: bold;")
        layout.addWidget(self.low_stock_label)
        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Ajouter")
        self.btn_update = QPushButton("Modifier")
        self.btn_del = QPushButton("Supprimer")
        self.btn_po = QPushButton("Générer bon de commande")
        self.btn_close = QPushButton("Fermer")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_update)
        btn_layout.addWidget(self.btn_del)
        btn_layout.addWidget(self.btn_po)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

        # Connections
        self.btn_close.clicked.connect(self.accept)
        self.btn_po.clicked.connect(self._export_purchase_order)

    # ------------------------------------------------------------------
    # Data handling
    # ------------------------------------------------------------------
    def _update_low_stock_label(self):
        low_items = piece_repo.get_low_stock(threshold=5)
        if low_items:
            msg = f"Attention : {len(low_items)} article(s) en dessous du seuil de stock !"
            self.low_stock_label.setText(msg)
        else:
            self.low_stock_label.setText("")

    def _load_data(self):
        self._pieces = piece_repo.get_all()

    def _refresh_table(self):
        self.table.setRowCount(0)
        for p in self._pieces:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(row, 1, QTableWidgetItem(p.reference))
            self.table.setItem(row, 2, QTableWidgetItem(p.designation))
            self.table.setItem(row, 3, QTableWidgetItem(str(p.quantite)))
            self.table.setItem(row, 4, QTableWidgetItem(f"{p.prix_unitaire:.2f}"))
        self.table.resizeRowsToContents()

    def _clear_form(self):
        self.ref_edit.clear()
        self.desig_edit.clear()
        self.qty_spin.setValue(0)
        self.price_edit.clear()

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    def _on_row_selected(self, row):
        if row < 0 or row >= len(self._pieces):
            self._clear_form()
            return
        p = self._pieces[row]
        self.ref_edit.setText(p.reference)
        self.desig_edit.setText(p.designation)
        self.qty_spin.setValue(p.quantite)
        self.price_edit.setText(str(p.prix_unitaire))

    def _add_piece(self):
        try:
            p = piece_repo.create(
                piece_repo.Piece(
                    reference=self.ref_edit.text().strip(),
                    designation=self.desig_edit.text().strip(),
                    quantite=self.qty_spin.value(),
                    prix_unitaire=float(self.price_edit.text() or 0),
                    emplacement=""
                )
            )
            QMessageBox.information(self, "Succès", f"Pièce {p.id} créée.")
            self._load_data()
            self._refresh_table()
            self._clear_form()
            self._update_low_stock_label()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _update_piece(self):
        current = self.table.currentRow()
        if current < 0:
            QMessageBox.warning(self, "Attention", "Sélectionnez une ligne à modifier.")
            return
        p = self._pieces[current]
        p.reference = self.ref_edit.text().strip()
        p.designation = self.desig_edit.text().strip()
        p.quantite = self.qty_spin.value()
        try:
            p.prix_unitaire = float(self.price_edit.text() or 0)
            piece_repo.update(p)
            QMessageBox.information(self, "Succès", "Pièce mise à jour.")
            self._load_data()
            self._refresh_table()
            self._update_low_stock_label()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _delete_piece(self):
        current = self.table.currentRow()
        if current < 0:
            QMessageBox.warning(self, "Attention", "Sélectionnez une ligne à supprimer.")
            return
        p = self._pieces[current]
        if QMessageBox.question(self, "Confirmer", f"Supprimer la pièce {p.id} ?") == QMessageBox.StandardButton.Yes:
            try:
                piece_repo.delete(p.id)
                QMessageBox.information(self, "Succès", "Pièce supprimée.")
                self._load_data()
                self._refresh_table()
                self._clear_form()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    # ------------------------------------------------------------------
    # Show dialog (convenient static method)
    # ------------------------------------------------------------------
    def _export_purchase_order(self):
        """Export low‑stock pieces to a CSV file for purchase ordering."""
        import csv, os
        low_items = piece_repo.get_low_stock(threshold=5)
        if not low_items:
            QMessageBox.information(self, "Info", "Aucun article en dessous du seuil de stock.")
            return
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "purchase_orders.csv"))
        try:
            with open(csv_path, mode="w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Référence", "Désignation", "Quantité en stock", "Quantité à commander"])
                for p in low_items:
                    qty_to_order = max(0, 10 - p.quantite)  # placeholder logic
                    writer.writerow([p.reference, p.designation, p.quantite, qty_to_order])
            QMessageBox.information(self, "Bon de commande", f"Bon de commande généré : {csv_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de créer le bon de commande : {e}")

    @staticmethod
    def exec_dialog(parent=None):
        dlg = PieceManagerDialog(parent)
        dlg._refresh_table()
        dlg.exec()
        return dlg
