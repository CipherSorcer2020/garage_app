# -*- coding: utf-8 -*-
# Data Model representation of Ligne_main_oeuvre table

from dataclasses import dataclass
from typing import Optional

@dataclass
class LigneMainOeuvre:
    """
    Data Model representing a Ligne_main_oeuvre in the application.
    This class is a simple Python dataclass holding Ligne_main_oeuvre properties.
    """

    or_id: int
    description: str
    duree_heures: Optional[float] = None
    taux_horaire_ht: Optional[float] = None
    id: Optional[int] = None

    @property
    def total_ht(self) -> Optional[float]:
        if self.duree_heures is None or self.taux_horaire_ht is None:
            return None
        return round(self.duree_heures * self.taux_horaire_ht, 2)
