from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Client:
    nom: str
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    adresse: Optional[str] = None
    id: Optional[int] = None
    date_creation: Optional[datetime] = None