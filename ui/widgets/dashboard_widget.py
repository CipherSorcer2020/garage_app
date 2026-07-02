from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame)
from PyQt6.QtCore import Qt

class StatCard(QFrame):
    def __init__(self, label: str, value: str, accent: bool = False):
        super().__init__()
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        val = QLabel(value)
        val.setObjectName("stat_value")
        color = "#E8724A" if accent else "#E8E6E1"
        val.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        lbl = QLabel(label)
        lbl.setObjectName("label_muted")
        lbl.setStyleSheet("color: #8A8F9E; font-size: 12px;")
        layout.addWidget(val)
        layout.addWidget(lbl)
        self.val_label = val

    def set_value(self, v: str):
        self.val_label.setText(v)


class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        hello = QLabel("Bonjour 👋")
        hello.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(hello)

        sub = QLabel("Voici l'état de l'atelier aujourd'hui.")
        sub.setStyleSheet("color: #8A8F9E;")
        layout.addWidget(sub)

        grid = QGridLayout()
        grid.setSpacing(16)

        self.card_or = StatCard("OR en cours", "—")
        self.card_clients = StatCard("Clients enregistrés", "—")
        self.card_impayees = StatCard("Factures impayées", "—", accent=True)
        self.card_ca = StatCard("CA total (payé)", "— DH")

        grid.addWidget(self.card_or, 0, 0)
        grid.addWidget(self.card_clients, 0, 1)
        grid.addWidget(self.card_impayees, 0, 2)
        grid.addWidget(self.card_ca, 0, 3)

        layout.addLayout(grid)
        layout.addStretch()

    def refresh(self):
        try:
            import repositories.or_repo as or_repo
            import repositories.client_repo as client_repo
            import repositories.facture_repo as facture_repo
            from services.facturation_service import get_ca_total, get_factures_impayees

            ors = [o for o in or_repo.get_all() if o.statut not in ('livre', 'facture')]
            self.card_or.set_value(str(len(ors)))
            self.card_clients.set_value(str(len(client_repo.get_all())))
            self.card_impayees.set_value(str(len(get_factures_impayees())))

            ca = get_ca_total()
            self.card_ca.set_value(f"{ca:.2f} DH" if ca is not None else "0.00 DH")
        except Exception as e:
            print(f"Dashboard error: {e}")
