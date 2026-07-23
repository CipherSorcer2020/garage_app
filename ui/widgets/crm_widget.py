# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QLabel, QComboBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from repositories import notification_repo, client_repo
from services import notification_service

class CRMWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Formulaire d'envoi rapide
        send_layout = QHBoxLayout()
        self.cb_client = QComboBox()
        self.cb_canal = QComboBox()
        self.cb_canal.addItems(["email", "sms", "whatsapp"])
        
        self.te_msg = QTextEdit()
        self.te_msg.setPlaceholderText("Message à envoyer au client...")
        self.te_msg.setMaximumHeight(60)
        
        btn_send = QPushButton("Envoyer Notification")
        btn_send.setObjectName("btn_primary")
        btn_send.clicked.connect(self._send_manual)
        
        col_left = QVBoxLayout()
        col_left.addWidget(QLabel("Client :"))
        col_left.addWidget(self.cb_client)
        col_left.addWidget(QLabel("Canal :"))
        col_left.addWidget(self.cb_canal)
        
        send_layout.addLayout(col_left)
        send_layout.addWidget(self.te_msg, stretch=1)
        send_layout.addWidget(btn_send)
        
        layout.addLayout(send_layout)
        layout.addWidget(QLabel("<b>Historique des Notifications</b>"))
        
        # Table d'historique
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Date", "Client", "Type", "Canal", "Statut"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def refresh(self):
        self._clients = {c.id: c for c in client_repo.get_all()}
        self.cb_client.clear()
        for c in self._clients.values():
            self.cb_client.addItem(f"{c.nom} {c.prenom}", c.id)
            
        notifs = notification_repo.get_all()
        self.table.setRowCount(0)
        for n in notifs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            c = self._clients.get(n.client_id)
            c_name = f"{c.nom} {c.prenom}" if c else "?"
            dt_str = n.date_creation.strftime("%d/%m/%Y %H:%M") if n.date_creation else "?"
            
            self.table.setItem(row, 0, QTableWidgetItem(dt_str))
            self.table.setItem(row, 1, QTableWidgetItem(c_name))
            self.table.setItem(row, 2, QTableWidgetItem(n.type_notification))
            self.table.setItem(row, 3, QTableWidgetItem(n.canal))
            self.table.setItem(row, 4, QTableWidgetItem(n.statut))

    def _send_manual(self):
        cid = self.cb_client.currentData()
        msg = self.te_msg.toPlainText().strip()
        canal = self.cb_canal.currentText()
        
        if not cid or not msg:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un client et écrire un message.")
            return
            
        notification_service.envoyer_notification(cid, "relance_manuelle", msg, canal)
        self.te_msg.clear()
        self.refresh()
        QMessageBox.information(self, "Succès", "Notification envoyée avec succès !")
