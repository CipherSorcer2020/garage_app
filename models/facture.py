# -*- coding: utf-8 -*-
# Data Model representation of Facture table

from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Facture:
    """
    Data Model representing a Facture in the application.
    This class is a simple Python dataclass holding Facture properties.
    """

    or_id: int
    client_id: int
    numero: str
    montant_ht: Optional[float] = None
    tva: float = 20.00
    montant_ttc: Optional[float] = None
    statut: str = 'non_payee'
    date_emission: Optional[date] = None
    mode_paiement: Optional[str] = None
    id: Optional[int] = None
