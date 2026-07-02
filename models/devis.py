# -*- coding: utf-8 -*-
# Data Model representation of Devis table

from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Devis:
    """
    Data Model representing a Devis in the application.
    This class is a simple Python dataclass holding Devis properties.
    """

    or_id: int
    montant_ht: Optional[float] = None
    tva: float = 20.00
    statut: str = 'en_attente'
    date_creation: Optional[date] = None
    accepte: bool = False
    id: Optional[int] = None

    @property
    def montant_ttc(self) -> Optional[float]:
        if self.montant_ht is None:
            return None
        return round(self.montant_ht * (1 + self.tva / 100), 2)
