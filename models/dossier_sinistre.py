# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class DossierSinistre:
    or_id: int
    nom_assurance: str
    numero_dossier: str
    statut: str = 'ouvert'
    montant_couvert: float = 0.0
    date_creation: Optional[date] = None
    id: Optional[int] = None
