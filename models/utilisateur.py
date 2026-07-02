from dataclasses import dataclass
from typing import Optional

@dataclass
class Utilisateur:
    nom: str
    prenom: str
    login: str
    mot_de_passe: str
    role: str = 'user'
    id: Optional[int] = None
