from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class OrdreReparation:
    vehicule_id: int
    statut: str = 'reception'
    mecanicien_id: Optional[int] = None
    date_entree: Optional[date] = None
    date_sortie: Optional[date] = None
    description: Optional[str] = None
    id: Optional[int] = None
