from dataclasses import dataclass
from typing import Optional

@dataclass
class Vehicule:
    immatriculation: str
    client_id: int
    vin: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee: Optional[int] = None
    kilometrage: Optional[int] = None
    id: Optional[int] = None
