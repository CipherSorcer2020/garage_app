# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class RendezVous:
    client_id: int
    vehicule_id: int
    date_heure_prevue: datetime
    duree_estimee_minutes: int = 60
    statut: str = 'planifie'
    description: str = ""
    id: Optional[int] = None
