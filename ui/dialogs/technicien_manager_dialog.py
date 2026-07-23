# -*- coding: utf-8 -*-
# Dialogue de gestion des techniciens.
# Comporte deux onglets :
#   1. Liste des techniciens avec possibilite d'affectation a un vehicule
#   2. Formulaire d'ajout / modification d'un technicien

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QFormLayout, QLineEdit, QLabel, QComboBox, QMessageBox,
    QAbstractItemView, QDoubleSpinBox
)
from PyQt6.QtCore import Qt

from repositories import technicien_repo, vehicule_repo


class TechnicienManagerDialog(QDialog):
    """Fenetre de gestion des techniciens avec deux onglets :
    - Onglet 1 : liste et affectation a un vehicule
    - Onglet 2 : ajout / modification d'un technicien
    """

    def __init__(self, vehicule_id: int = None, parent=None):
        """
        Args:
            vehicule_id: si fourni, le dialogue pre-selectionne ce vehicule
                         pour l'affectation d'un technicien.
        """
        super().__init__(parent)
        # Identifiant du vehicule pour lequel on veut affecter un technicien (optionnel)
        self._vehicule_id = vehicule_id
        # Technicien en cours de modification (None = creation)
        self._editing_tech = None
        self.setWindowTitle("Gestion des techniciens")
        self.setMinimumSize(700, 480)
        self._build()
        self._refresh_list()

    # ------------------------------------------------------------------
    # Construction de l'interface
    # ------------------------------------------------------------------
    def _build(self):
        """Cree les onglets et les widgets de la fenetre."""
        root = QVBoxLayout(self)

        # Widget d'onglets principal
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        # ---- Onglet 1 : Liste ----------------------------------------
        self.tabs.addTab(self._build_list_tab(), "Liste des techniciens")

        # ---- Onglet 2 : Formulaire -----------------------------------
        self.tabs.addTab(self._build_form_tab(), "Ajouter / Modifier")

        # Bouton fermer en bas
        btn_close = QPushButton("Fermer")
        btn_close.setObjectName("btn_primary")
        btn_close.clicked.connect(self.accept)
        root.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

    # -- Onglet liste --------------------------------------------------
    def _build_list_tab(self) -> QWidget:
        """Construit l'onglet de liste des techniciens."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Titre contextuel
        if self._vehicule_id:
            v = vehicule_repo.get_by_id(self._vehicule_id)
            label_txt = f"Affecter un technicien au vehicule : {v.immatriculation if v else self._vehicule_id}"
        else:
            label_txt = "Tous les techniciens enregistres"
        layout.addWidget(QLabel(label_txt))

        # Tableau des techniciens
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Prenom", "Qualification", "Telephone", "Coût horaire"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Boutons d'action
        btn_layout = QHBoxLayout()

        self.btn_edit = QPushButton("Modifier")
        self.btn_edit.clicked.connect(self._load_for_edit)
        btn_layout.addWidget(self.btn_edit)

        self.btn_del = QPushButton("Supprimer")
        self.btn_del.setObjectName("btn_danger")
        self.btn_del.clicked.connect(self._delete_tech)
        btn_layout.addWidget(self.btn_del)

        btn_layout.addStretch()

        # Bouton d'affectation visible seulement si un vehicule est passe en parametre
        if self._vehicule_id:
            self.btn_affecter = QPushButton("Affecter ce technicien")
            self.btn_affecter.setObjectName("btn_primary")
            self.btn_affecter.clicked.connect(self._affecter)
            btn_layout.addWidget(self.btn_affecter)

        layout.addLayout(btn_layout)
        return widget

    # -- Onglet formulaire --------------------------------------------
    def _build_form_tab(self) -> QWidget:
        """Construit l'onglet du formulaire d'ajout / modification."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()

        # Champs du formulaire
        self.f_nom = QLineEdit()
        self.f_nom.setPlaceholderText("Nom de famille")
        form.addRow("Nom *", self.f_nom)

        self.f_prenom = QLineEdit()
        self.f_prenom.setPlaceholderText("Prenom")
        form.addRow("Prenom", self.f_prenom)

        self.f_qualification = QLineEdit()
        self.f_qualification.setPlaceholderText("ex: Mecanicien, Electricien, Carrossier...")
        form.addRow("Qualification", self.f_qualification)

        self.f_telephone = QLineEdit()
        self.f_telephone.setPlaceholderText("ex: 0612345678")
        form.addRow("Telephone", self.f_telephone)

        self.f_cout_horaire = QDoubleSpinBox()
        self.f_cout_horaire.setRange(0.0, 10000.0)
        self.f_cout_horaire.setSuffix(" €/h")
        form.addRow("Coût horaire", self.f_cout_horaire)

        layout.addLayout(form)

        # Label d'erreur
        self.form_error = QLabel("")
        self.form_error.setStyleSheet("color: #E05252;")
        layout.addWidget(self.form_error)

        # Boutons
        btn_row = QHBoxLayout()
        self.btn_reset = QPushButton("Effacer")
        self.btn_reset.clicked.connect(self._reset_form)
        btn_row.addWidget(self.btn_reset)

        btn_row.addStretch()

        self.btn_save = QPushButton("Enregistrer")
        self.btn_save.setObjectName("btn_primary")
        self.btn_save.clicked.connect(self._save_tech)
        btn_row.addWidget(self.btn_save)

        layout.addLayout(btn_row)
        layout.addStretch()
        return widget

    # ------------------------------------------------------------------
    # Logique metier
    # ------------------------------------------------------------------
    def _refresh_list(self):
        """Recharge la liste des techniciens depuis la base de donnees."""
        techs = technicien_repo.get_all()
        self.table.setRowCount(0)
        for t in techs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            # Stocke l'ID dans la colonne 0 (non-editable)
            id_item = QTableWidgetItem(str(t.id))
            id_item.setData(Qt.ItemDataRole.UserRole, t.id)
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, QTableWidgetItem(t.nom))
            self.table.setItem(row, 2, QTableWidgetItem(t.prenom))
            self.table.setItem(row, 3, QTableWidgetItem(t.qualification))
            self.table.setItem(row, 4, QTableWidgetItem(t.telephone))
            self.table.setItem(row, 5, QTableWidgetItem(f"{t.cout_horaire:.2f} €/h"))

    def _selected_tech_id(self):
        """Retourne l'ID du technicien selectionne dans la liste, ou None."""
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _load_for_edit(self):
        """Charge le technicien selectionne dans le formulaire pour modification."""
        tech_id = self._selected_tech_id()
        if not tech_id:
            QMessageBox.warning(self, "Selection", "Veuillez selectionner un technicien.")
            return
        t = technicien_repo.get_by_id(tech_id)
        if not t:
            return
        # Remplit le formulaire avec les donnees du technicien
        self._editing_tech = t
        self.f_nom.setText(t.nom)
        self.f_prenom.setText(t.prenom)
        self.f_qualification.setText(t.qualification)
        self.f_telephone.setText(t.telephone)
        self.f_cout_horaire.setValue(t.cout_horaire)
        self.btn_save.setText("Modifier")
        # Bascule sur l'onglet formulaire
        self.tabs.setCurrentIndex(1)

    def _reset_form(self):
        """Remet le formulaire a zero (mode creation)."""
        self._editing_tech = None
        self.f_nom.clear()
        self.f_prenom.clear()
        self.f_qualification.clear()
        self.f_telephone.clear()
        self.f_cout_horaire.setValue(0.0)
        self.form_error.setText("")
        self.btn_save.setText("Enregistrer")

    def _save_tech(self):
        """Valide et enregistre le technicien (creation ou modification)."""
        nom = self.f_nom.text().strip()
        if not nom:
            self.form_error.setText("Le nom est obligatoire.")
            return
        self.form_error.setText("")

        prenom = self.f_prenom.text().strip()
        qualification = self.f_qualification.text().strip()
        telephone = self.f_telephone.text().strip()
        cout = self.f_cout_horaire.value()

        if self._editing_tech:
            # Mode modification
            self._editing_tech.nom = nom
            self._editing_tech.prenom = prenom
            self._editing_tech.qualification = qualification
            self._editing_tech.telephone = telephone
            self._editing_tech.cout_horaire = cout
            technicien_repo.update(self._editing_tech)
            QMessageBox.information(self, "Succes", "Technicien modifie avec succes.")
        else:
            # Mode creation
            from models.technicien import Technicien
            t = Technicien(nom=nom, prenom=prenom, qualification=qualification, telephone=telephone, cout_horaire=cout)
            technicien_repo.create(t)
            QMessageBox.information(self, "Succes", "Technicien ajoute avec succes.")

        self._reset_form()
        self._refresh_list()
        # Revient sur l'onglet liste apres l'enregistrement
        self.tabs.setCurrentIndex(0)

    def _delete_tech(self):
        """Supprime le technicien selectionne apres confirmation."""
        tech_id = self._selected_tech_id()
        if not tech_id:
            QMessageBox.warning(self, "Selection", "Veuillez selectionner un technicien.")
            return
        reply = QMessageBox.question(
            self, "Confirmation",
            "Supprimer ce technicien ? Les vehicules associes seront desaffectes.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            technicien_repo.delete(tech_id)
            self._refresh_list()

    def _affecter(self):
        """Affecte le technicien selectionne au vehicule passe en parametre."""
        tech_id = self._selected_tech_id()
        if not tech_id:
            QMessageBox.warning(self, "Selection", "Veuillez selectionner un technicien.")
            return
        technicien_repo.affecter_vehicule(self._vehicule_id, tech_id)
        QMessageBox.information(self, "Affectation", "Technicien affecte avec succes.")
        self.accept()

    # ------------------------------------------------------------------
    # Methode statique pratique pour ouvrir le dialogue
    # ------------------------------------------------------------------
    @staticmethod
    def exec_dialog(vehicule_id: int = None, parent=None):
        """Ouvre la fenetre de gestion des techniciens.

        Args:
            vehicule_id: si fourni, active le bouton d'affectation pour ce vehicule.
        """
        dlg = TechnicienManagerDialog(vehicule_id=vehicule_id, parent=parent)
        dlg.exec()
        return dlg
