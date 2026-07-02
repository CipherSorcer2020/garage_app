# -*- coding: utf-8 -*-
# Data Model representation of Ligne_piece table

from dataclasses import dataclass
from typing import Optional

@dataclass
class LignePiece:
    """
    Data Model representing a Ligne_piece in the application.
    This class is a simple Python dataclass holding Ligne_piece properties.
    """

    or_id: int
    designation: str
    quantite: int = 1
    reference: Optional[str] = None
    prix_unitaire_ht: Optional[float] = None
    id: Optional[int] = None

    @property
    def total_ht(self) -> Optional[float]:
        if self.prix_unitaire_ht is None:
            return None
        return round(self.quantite * self.prix_unitaire_ht, 2)
