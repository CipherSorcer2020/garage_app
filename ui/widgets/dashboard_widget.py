# -*- coding: utf-8 -*-
# Spécifie l'encodage du fichier en UTF-8 pour supporter les caractères spéciaux et accents.
# GUI Panel Widget for Dashboard view
# Ce widget représente le panneau du tableau de bord.
# Represents one of the main dashboard tabs in the user interface.
# Il sert d'onglet principal dans l'interface utilisateur.

# Importation des composants graphiques de base (Widgets, Mises en page, Labels) depuis PyQt6
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame)
# Importation de Qt pour des paramètres globaux et constantes (ex: alignement)
from PyQt6.QtCore import Qt

class StatCard(QFrame):
    # Cette classe représente une "carte de statistique" (un encadré) dans le tableau de bord.
    def __init__(self, label: str, value: str, accent: bool = False):
        """
        UI lifecycle method: '__init__'.
        Initialise la carte avec un titre (label), une valeur (value) et une option de couleur (accent).
        """
        # Appel du constructeur de la classe parente (QFrame)
        super().__init__()
        # Définit le nom d'objet pour appliquer des styles CSS spécifiques
        self.setObjectName("card")
        # Crée une disposition verticale (de haut en bas) pour cette carte
        layout = QVBoxLayout(self)
        
        # Crée un label texte pour afficher la valeur de la statistique
        val = QLabel(value)
        # Nom de l'objet pour les styles CSS
        val.setObjectName("stat_value")
        # Si 'accent' est vrai, la couleur sera orange/rouge (#E8724A), sinon blanc cassé (#E8E6E1)
        color = "#E8724A" if accent else "#E8E6E1"
        # Applique le style (taille de police, gras, couleur) directement au composant
        val.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        
        # Crée un label texte pour afficher le titre de la statistique
        lbl = QLabel(label)
        # Nom de l'objet pour les styles CSS
        lbl.setObjectName("label_muted")
        # Applique un style discret (couleur grise, petite police) au titre
        lbl.setStyleSheet("color: #8A8F9E; font-size: 12px;")
        
        # Ajoute le label de la valeur dans la disposition de la carte
        layout.addWidget(val)
        # Ajoute le label du titre en dessous
        layout.addWidget(lbl)
        
        # Sauvegarde la référence du label de valeur pour pouvoir le mettre à jour plus tard
        self.val_label = val

    def set_value(self, v: str):
        """
        UI lifecycle method: 'set_value'.
        Permet de modifier dynamiquement la valeur affichée dans la carte.
        """
        # Change le texte du label contenant la valeur
        self.val_label.setText(v)


class DashboardWidget(QWidget):
    # Classe principale du tableau de bord
    def __init__(self):
        """
        UI lifecycle method: '__init__'.
        Initialise le widget du tableau de bord.
        """
        # Appel du constructeur parent
        super().__init__()
        # Construit l'interface graphique du tableau de bord
        self._build()

    def _build(self):
        """
        UI lifecycle method: '_build'.
        Méthode pour assembler les différents éléments visuels du tableau de bord.
        """
        # Crée un layout vertical pour agencer les éléments principaux
        layout = QVBoxLayout(self)
        # Définit les marges internes (gauche, haut, droite, bas)
        layout.setContentsMargins(24, 24, 24, 24)
        # Définit l'espace entre les éléments du layout
        layout.setSpacing(20)

        # Crée un texte de bienvenue
        hello = QLabel("Bonjour 👋")
        # Applique une grande police en gras
        hello.setStyleSheet("font-size: 22px; font-weight: bold;")
        # Ajoute ce message dans le layout
        layout.addWidget(hello)

        # Crée un texte secondaire descriptif
        sub = QLabel("Voici l'état de l'atelier aujourd'hui.")
        # Le met en gris pour qu'il soit plus discret
        sub.setStyleSheet("color: #8A8F9E;")
        # Ajoute ce texte sous le message de bienvenue
        layout.addWidget(sub)

        # Crée une disposition en grille pour aligner les cartes de statistiques
        grid = QGridLayout()
        # Espace entre les cases de la grille
        grid.setSpacing(16)

        # Crée une carte pour les Ordres de Réparation (OR) en cours
        self.card_or = StatCard("OR en cours", "—")
        # Crée une carte pour le nombre de clients
        self.card_clients = StatCard("Clients enregistrés", "—")
        # Crée une carte pour les factures impayées avec l'option 'accent' pour attirer l'attention
        self.card_impayees = StatCard("Factures impayées", "—", accent=True)
        # Crée une carte pour le Chiffre d'Affaires total
        self.card_ca = StatCard("CA total (payé)", "— DH")

        # Place la carte des OR en ligne 0, colonne 0
        grid.addWidget(self.card_or, 0, 0)
        # Place la carte des clients en ligne 0, colonne 1
        grid.addWidget(self.card_clients, 0, 1)
        # Place la carte des impayés en ligne 0, colonne 2
        grid.addWidget(self.card_impayees, 0, 2)
        # Place la carte du CA en ligne 0, colonne 3
        grid.addWidget(self.card_ca, 0, 3)

        # Ajoute la grille de cartes au layout principal
        layout.addLayout(grid)
        # Ajoute un espace vide (ressort) en bas pour pousser le tout vers le haut
        layout.addStretch()

    def refresh(self):
        """
        UI lifecycle method: 'refresh'.
        Met à jour les données affichées sur les cartes de statistiques.
        """
        try:
            # Importation locale des différents accès aux données (repositories et services)
            # On le fait ici pour éviter des imports circulaires au début du fichier
            import repositories.or_repo as or_repo
            import repositories.client_repo as client_repo
            import repositories.facture_repo as facture_repo
            from services.facturation_service import get_ca_total, get_factures_impayees

            # Récupère tous les ordres de réparation (OR) qui ne sont ni livrés ni facturés
            ors = [o for o in or_repo.get_all() if o.statut not in ('livre', 'facture')]
            # Met à jour la carte avec le nombre d'OR en cours
            self.card_or.set_value(str(len(ors)))
            # Met à jour la carte avec le nombre total de clients
            self.card_clients.set_value(str(len(client_repo.get_all())))
            # Met à jour la carte avec le nombre de factures impayées
            self.card_impayees.set_value(str(len(get_factures_impayees())))

            # Calcule le chiffre d'affaires total généré
            ca = get_ca_total()
            # Affiche le CA formaté avec 2 décimales (ex: 1200.50 DH), ou 0.00 DH si vide
            self.card_ca.set_value(f"{ca:.2f} DH" if ca is not None else "0.00 DH")
        except Exception as e:
            # Si une erreur survient lors du chargement des données, l'affiche dans la console
            print(f"Dashboard error: {e}")