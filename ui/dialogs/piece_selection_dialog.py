"""Dialog allowing the user to select spare parts and quantities for an order."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QSpinBox, QPushButton, QHBoxLayout,
    QMessageBox, QFormLayout, QLabel
)
from PyQt6.QtCore import Qt

from repositories import piece_repo

class PieceSelectionDialog(QDialog):
    """Display all available pieces with a spinbox to choose quantity.

    After the user clicks **Valider**, the dialog stores a list of tuples
    ``(Piece, chosen_quantity)`` in ``self.selected_items``.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sélection des pièces")
        self.setMinimumSize(600, 400)
        self.selected_items = []
        self._load_data()
        self._build()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Référence", "Désignation", "En stock", "Prix", "Qté à utiliser"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self._refresh_table()

        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Valider")
        self.btn_cancel = QPushButton("Annuler")
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.btn_ok.clicked.connect(self._accept)
        self.btn_cancel.clicked.connect(self.reject)

    # ------------------------------------------------------------------
    # Data handling
    # ------------------------------------------------------------------
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
            qty_spin = QSpinBox()
            qty_spin.setRange(0, p.quantite)
            self.table.setCellWidget(row, 5, qty_spin)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    def _accept(self):
        self.selected_items = []
        for row in range(self.table.rowCount()):
            qty_widget = self.table.cellWidget(row, 5)
            qty = qty_widget.value()
            if qty > 0:
                piece = self._pieces[row]
                self.selected_items.append((piece, qty))
        self.accept()

    # ------------------------------------------------------------------
    # Convenience static method
    # ------------------------------------------------------------------
    @staticmethod
    def exec_dialog(parent=None):
        dlg = PieceSelectionDialog(parent)
        if dlg.exec():
            return dlg.selected_items
        return []
