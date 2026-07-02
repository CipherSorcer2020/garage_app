from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QLineEdit,
                              QHeaderView, QAbstractItemView, QMessageBox)
from PyQt6.QtCore import Qt
import repositories.client_repo as client_repo
from ui.dialogs.client_dialog import ClientDialog


class ClientWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._build()
        self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Toolbar
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setObjectName("search_input")
        self.search.setPlaceholderText("Rechercher un client…")
        self.search.textChanged.connect(self._search)

        btn_add = QPushButton("+ Nouveau client")
        btn_add.setObjectName("btn_primary")
        btn_add.clicked.connect(self._add)

        toolbar.addWidget(self.search)
        toolbar.addStretch()
        toolbar.addWidget(btn_add)
        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Nom", "Prénom", "Téléphone", "Email", "Adresse"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._edit)
        layout.addWidget(self.table)

        # Actions
        actions = QHBoxLayout()
        btn_edit = QPushButton("Modifier")
        btn_edit.clicked.connect(self._edit)
        btn_del = QPushButton("Supprimer")
        btn_del.setObjectName("btn_danger")
        btn_del.clicked.connect(self._delete)
        actions.addStretch()
        actions.addWidget(btn_edit)
        actions.addWidget(btn_del)
        layout.addLayout(actions)

    def refresh(self):
        self._clients = client_repo.get_all()
        self._fill_table(self._clients)

    def _fill_table(self, clients):
        self.table.setRowCount(0)
        for c in clients:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, val in enumerate([c.nom, c.prenom or "", c.telephone or "", c.email or "", c.adresse or ""]):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, c.id)
                self.table.setItem(row, col, item)

    def _search(self, text):
        if text.strip():
            self._fill_table(client_repo.search(text))
        else:
            self._fill_table(self._clients)

    def _selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def _add(self):
        dlg = ClientDialog(self)
        if dlg.exec():
            client_repo.create(dlg.get_client())
            self.refresh()

    def _edit(self):
        cid = self._selected_id()
        if not cid:
            return
        c = client_repo.get_by_id(cid)
        dlg = ClientDialog(self, client=c)
        if dlg.exec():
            updated = dlg.get_client()
            updated.id = cid
            client_repo.update(updated)
            self.refresh()

    def _delete(self):
        cid = self._selected_id()
        if not cid:
            return
        reply = QMessageBox.question(self, "Confirmer", "Supprimer ce client ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            client_repo.delete(cid)
            self.refresh()
