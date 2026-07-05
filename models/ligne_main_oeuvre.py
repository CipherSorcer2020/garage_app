# -*- coding: utf-8 -*-
# Représentation du modèle de données de la table Ligne_main_oeuvre

from dataclasses import dataclass
from typing import Optional

@dataclass
class LigneMainOeuvre:
    """
    Modèle de données représentant une Ligne_main_oeuvre dans l'application.
    Cette classe est une simple "dataclass" Python qui contient les propriétés d'une ligne de main d'oeuvre.
    """

    # L'identifiant de l'ordre de réparation associé
    or_id: int
    
    # La description de la tâche ou de la prestation réalisée
    description: str
    
    # Le nombre d'heures travaillées (optionnel)
    duree_heures: Optional[float] = None
    
    # Le taux horaire hors taxes de la prestation (optionnel)
    taux_horaire_ht: Optional[float] = None
    
    # L'identifiant unique de la ligne de main d'œuvre (optionnel)
    id: Optional[int] = None

    @property
    def total_ht(self) -> Optional[float]:
        """
        Calcule et retourne le coût total hors taxes de cette ligne de main d'œuvre.
        Si la durée ou le taux horaire est manquant, retourne None.
        """
        if self.duree_heures is None or self.taux_horaire_ht is None:
            return None
        # Calcule le total et arrondit le résultat à 2 décimales
        return round(self.duree_heures * self.taux_horaire_ht, 2)
