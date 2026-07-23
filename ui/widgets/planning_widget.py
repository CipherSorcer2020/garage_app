# -*- coding: utf-8 -*-
# Widget de planning atelier (vue calendrier hebdomadaire).
# Affiche les OR actifs sous forme de carte couleur par statut,
# organises par technicien (colonnes) et par jour de la semaine (lignes).

from datetime import date, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QScrollArea, QFrame, QSizePolicy, QToolTip,
    QComboBox,
)
from PyQt6.QtCore import Qt, QDate, QMimeData, QByteArray, QPoint
from PyQt6.QtGui import QColor, QFont, QCursor, QDrag

from repositories import or_repo, vehicule_repo, technicien_repo, client_repo


# ──────────────────────────────────────────────────────────────
# Couleurs par statut
# ──────────────────────────────────────────────────────────────
STATUT_COLORS = {
    "reception":             "#3A7BD5",   # bleu
    "diagnostic":            "#F7971E",   # orange
    "devis":                 "#8E44AD",   # violet
    "accord_devis":          "#16A085",   # vert fonce
    "affectation_mecanicien":"#2980B9",   # bleu clair
    "en_cours":              "#E8724A",   # orange primaire
    "test":                  "#F39C12",   # jaune
    "facture":               "#27AE60",   # vert
    "livre":                 "#7F8C8D",   # gris (termine)
}

STATUT_LABELS = {
    "reception":              "Reception",
    "diagnostic":             "Diagnostic",
    "devis":                  "Devis",
    "accord_devis":           "Accord devis",
    "affectation_mecanicien": "Affectation",
    "en_cours":               "En cours",
    "test":                   "Test",
    "facture":                "Facture",
    "livre":                  "Livre",
}

JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


# ──────────────────────────────────────────────────────────────
# Carte d'un OR (carte coloree dans la grille)
# ──────────────────────────────────────────────────────────────
class ORCard(QFrame):
    """Carte representant un Ordre de Reparation dans la grille du planning."""

    def __init__(self, or_obj, label: str, parent=None):
        super().__init__(parent)
        # L'objet OR associe a cette carte
        self._or = or_obj
        # Texte d'infobulle (vehicule + client + description)
        self._tooltip = label

        color = STATUT_COLORS.get(or_obj.statut, "#2A2D35")
        statut_txt = STATUT_LABELS.get(or_obj.statut, or_obj.statut)

        # Style de la carte : fond colore, coins arrondis, texte blanc
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 6px;
                border: 1px solid rgba(255,255,255,0.15);
            }}
        """)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setToolTip(label)
        self.setMinimumHeight(52)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(1)

        # Ligne 1 : numero OR + statut
        top = QHBoxLayout()
        lbl_id = QLabel(f"OR#{or_obj.id}")
        lbl_id.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 10px; font-weight: bold;")
        lbl_status = QLabel(statut_txt)
        lbl_status.setStyleSheet("color: rgba(255,255,255,0.75); font-size: 9px;")
        lbl_status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        top.addWidget(lbl_id)
        top.addWidget(lbl_status)
        layout.addLayout(top)

        # Ligne 2 : immatriculation / description courte
        short = label.split("\n")[0] if "\n" in label else label
        lbl_main = QLabel(short)
        lbl_main.setStyleSheet("color: #FFFFFF; font-size: 11px; font-weight: bold;")
        lbl_main.setMaximumWidth(160)
        layout.addWidget(lbl_main)

        self._drag_start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if not self._drag_start_pos:
            return
        
        # Determine if we moved enough to start a drag
        if (event.position().toPoint() - self._drag_start_pos).manhattanLength() < 5:
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        # Store OR ID and Vehicule ID as simple text
        data = f"{self._or.id}:{self._or.vehicule_id}"
        mime_data.setText(data)
        drag.setMimeData(mime_data)

        # Optional: set pixmap to look nice
        drag.exec(Qt.DropAction.MoveAction)


# ──────────────────────────────────────────────────────────────
# Cellule Jour (droppable target)
# ──────────────────────────────────────────────────────────────
class DayCell(QWidget):
    """Cellule representant un jour pour un technicien donne."""
    def __init__(self, target_date: date, technicien_id: int | None, planning_widget, parent=None):
        super().__init__(parent)
        self.target_date = target_date
        self.technicien_id = technicien_id
        self.planning_widget = planning_widget
        self.setAcceptDrops(True)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(3)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet(self.styleSheet() + "border: 2px dashed #E8724A;")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        # Reset style by refreshing grid
        self.planning_widget.refresh()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            data = event.mimeData().text()
            parts = data.split(':')
            if len(parts) == 2:
                or_id = int(parts[0])
                vehicule_id = int(parts[1])

                # 1. Update OR date_entree
                o = or_repo.get_by_id(or_id)
                if o:
                    o.date_entree = self.target_date
                    or_repo.update(o)
                
                # 2. Update Vehicule's technicien
                technicien_repo.affecter_vehicule(vehicule_id, self.technicien_id)
                
                event.acceptProposedAction()
                # Refresh entire grid to reflect new state
                self.planning_widget.refresh()
                return
        event.ignore()


# ──────────────────────────────────────────────────────────────
# Widget principal du planning
# ──────────────────────────────────────────────────────────────
class PlanningWidget(QWidget):
    """Vue calendrier hebdomadaire de l'atelier.
    Les colonnes representent les jours de la semaine (Lun→Dim).
    Les lignes representent les techniciens.
    Les OR sont affiches sous forme de cartes colorees par statut.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Semaine courante : date du lundi
        self._week_start = self._get_monday(date.today())
        self._build()

    # ── Construction de l'interface ────────────────────────────
    def _build(self):
        """Cree le layout principal avec la barre de navigation et la grille."""
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # ---- Barre de navigation de semaine -------------------
        nav = QHBoxLayout()

        self.btn_prev = QPushButton("◀  Semaine precedente")
        self.btn_prev.clicked.connect(self._prev_week)
        nav.addWidget(self.btn_prev)

        nav.addStretch()

        self.lbl_week = QLabel()
        self.lbl_week.setStyleSheet("font-size: 14px; font-weight: bold; color: #E8E6E1;")
        self.lbl_week.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav.addWidget(self.lbl_week)

        nav.addStretch()

        self.btn_today = QPushButton("Aujourd'hui")
        self.btn_today.setObjectName("btn_primary")
        self.btn_today.clicked.connect(self._go_today)
        nav.addWidget(self.btn_today)

        self.btn_next = QPushButton("Semaine suivante  ▶")
        self.btn_next.clicked.connect(self._next_week)
        nav.addWidget(self.btn_next)

        root.addLayout(nav)

        # ---- Legende des statuts ------------------------------
        legend = QHBoxLayout()
        legend.addWidget(QLabel("Statuts :"))
        for statut, color in STATUT_COLORS.items():
            dot = QLabel(f"● {STATUT_LABELS.get(statut, statut)}")
            dot.setStyleSheet(f"color: {color}; font-size: 11px; margin-right: 8px;")
            legend.addWidget(dot)
        legend.addStretch()
        root.addLayout(legend)

        # ---- Zone scrollable pour la grille -------------------
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        root.addWidget(self.scroll)

        # Conteneur de la grille (sera recharge a chaque navigation)
        self.grid_container = QWidget()
        self.scroll.setWidget(self.grid_container)
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(4)

        self.refresh()

    # ── Navigation ─────────────────────────────────────────────
    def _prev_week(self):
        """Recule d'une semaine."""
        self._week_start -= timedelta(weeks=1)
        self.refresh()

    def _next_week(self):
        """Avance d'une semaine."""
        self._week_start += timedelta(weeks=1)
        self.refresh()

    def _go_today(self):
        """Revient a la semaine courante."""
        self._week_start = self._get_monday(date.today())
        self.refresh()

    @staticmethod
    def _get_monday(d: date) -> date:
        """Retourne le lundi de la semaine contenant la date d."""
        return d - timedelta(days=d.weekday())

    # ── Chargement et affichage des donnees ────────────────────
    def refresh(self):
        """Recharge les donnees et reconstruit la grille du planning."""
        # Mise a jour du titre de semaine
        end = self._week_start + timedelta(days=6)
        self.lbl_week.setText(
            f"Semaine du {self._week_start.strftime('%d %b %Y')}  →  {end.strftime('%d %b %Y')}"
        )

        # Supprime tous les anciens widgets de la grille
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Recupere les donnees
        all_ors = or_repo.get_all()
        techniciens = technicien_repo.get_all()
        vehicules   = {v.id: v for v in vehicule_repo.get_all()}
        clients     = {c.id: c for c in client_repo.get_all()}

        # Jours de la semaine affichee
        days = [self._week_start + timedelta(days=i) for i in range(7)]
        today = date.today()

        # ── En-tete : cellule vide + jours ─────────────────────
        corner = QLabel("")
        corner.setFixedWidth(130)
        self.grid_layout.addWidget(corner, 0, 0)

        for col, d in enumerate(days):
            day_label = f"{JOURS[col]}\n{d.strftime('%d/%m')}"
            lbl = QLabel(day_label)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            is_today = (d == today)
            style = (
                "font-weight: bold; color: #E8724A; background: #252830; "
                "border-radius: 6px; padding: 6px;"
                if is_today
                else "font-weight: bold; color: #8A8F9E; padding: 6px;"
            )
            lbl.setStyleSheet(style)
            lbl.setFixedHeight(50)
            self.grid_layout.addWidget(lbl, 0, col + 1)

        # ── Lignes : une ligne par technicien ──────────────────
        # Ajoute aussi une ligne "Non affecte" pour les OR sans technicien
        tech_rows = list(techniciens) + [None]  # None = non affecte

        for row, tech in enumerate(tech_rows):
            # Etiquette du technicien (colonne gauche)
            if tech is not None:
                tech_lbl = QLabel(f"🔧 {tech.prenom} {tech.nom}\n{tech.qualification}")
            else:
                tech_lbl = QLabel("— Non affecte —")
            tech_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tech_lbl.setStyleSheet(
                "color: #E8E6E1; font-size: 11px; font-weight: bold;"
                " background: #1F2229; border-radius: 6px; padding: 6px;"
            )
            tech_lbl.setFixedWidth(130)
            tech_lbl.setMinimumHeight(60)
            self.grid_layout.addWidget(tech_lbl, row + 1, 0)

            # Cellules pour chaque jour
            for col, d in enumerate(days):
                tech_id = tech.id if tech else None
                cell = DayCell(d, tech_id, self)
                base_style = (
                    "background: #1F2229; border-radius: 6px;"
                    if d != today
                    else "background: #252830; border-radius: 6px; border: 1px solid #E8724A;"
                )
                cell.setStyleSheet(base_style)
                cell_layout = cell.layout

                # Filtre les OR correspondant a ce technicien et ce jour
                for o in all_ors:
                    if not o.date_entree:
                        continue
                    or_date = o.date_entree if isinstance(o.date_entree, date) else o.date_entree
                    if or_date != d:
                        continue

                    # Determine le technicien responsable via le vehicule
                    veh = vehicules.get(o.vehicule_id)
                    or_tech_id = veh.technicien_id if veh else None

                    # Verifie si l'OR appartient a la ligne de technicien courante
                    if tech is None:
                        if or_tech_id is not None:
                            continue
                    else:
                        if or_tech_id != tech.id:
                            continue

                    # Construction de l'etiquette de la carte
                    immat = veh.immatriculation if veh else f"Veh#{o.vehicule_id}"
                    client = clients.get(veh.client_id) if veh else None
                    client_nom = client.nom if client else "?"
                    desc = (o.description or "")[:40]
                    card_label = f"{immat} ({client_nom})\n{desc}"

                    card = ORCard(o, card_label, cell)
                    cell_layout.addWidget(card)

                # Si aucune carte : affiche un espace vide discret
                if cell_layout.count() == 0:
                    placeholder = QLabel("")
                    placeholder.setMinimumHeight(52)
                    cell_layout.addWidget(placeholder)

                cell.setMinimumHeight(60)
                self.grid_layout.addWidget(cell, row + 1, col + 1)

        # Etire les colonnes de jours uniformement
        for col in range(1, 8):
            self.grid_layout.setColumnStretch(col, 1)
