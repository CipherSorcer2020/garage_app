# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional

@dataclass
class Fournisseur:
    nom: str
    contact: str = ""
    telephone: str = ""
    email: str = ""
    adresse: str = ""
    id: Optional[int] = None
