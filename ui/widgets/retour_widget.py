# -*- coding: utf-8 -*-
"""UI widget for managing piece returns (Retours & Garanties)."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox
)
from PyQt6.QtCore import Qt

from services import retour_piece_service
from ui.dialogs.retour_piece_dialog import RetourPieceDialog

class RetourWidget(QWidget):
    """Displays a table of RetourPiece records and allows creating new returns."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Table of returns
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Pièce", "Quantité", "Motif", "Date Retour", "Fournisseur"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("+ Nouveau Retour")
        btn_add.clicked.connect(self._add_retour)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_add)
        layout.addLayout(btn_layout)

    # ------------------------------------------------------------------
    def refresh(self):
        """Reload all RetourPiece rows from the DB and repopulate the table."""
        returns = retour_piece_service.lister_retours()
        self.table.setRowCount(0)
        for ret in returns:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(ret.id)))
            self.table.setItem(row, 1, QTableWidgetItem(str(ret.piece_id)))
            self.table.setItem(row, 2, QTableWidgetItem(str(ret.quantite)))
            self.table.setItem(row, 3, QTableWidgetItem(ret.motif or ""))
            self.table.setItem(row, 4, QTableWidgetItem(str(ret.date_retour) if ret.date_retour else ""))
            self.table.setItem(row, 5, QTableWidgetItem(str(ret.fournisseur_id) if ret.fournisseur_id else ""))

    # ------------------------------------------------------------------
    def _add_retour(self):
        """Open the RetourPieceDialog; on success refresh the view."""
        dlg = RetourPieceDialog(parent=self)
        if dlg.exec():
            self.refresh()
        else:
            pass
