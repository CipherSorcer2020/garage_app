# -*- coding: utf-8 -*-
# Data Model representation of Utilisateur table

from dataclasses import dataclass
from typing import Optional

@dataclass
class Utilisateur:
    """
    Data Model representing a Utilisateur in the application.
    This class is a simple Python dataclass holding Utilisateur properties.
    """

    nom: str
    prenom: str
    login: str
    mot_de_passe: str
    role: str = 'user'
    id: Optional[int] = None
