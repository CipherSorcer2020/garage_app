from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Facture:
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
