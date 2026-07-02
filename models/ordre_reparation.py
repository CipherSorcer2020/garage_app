# -*- coding: utf-8 -*-
# Data Model representation of Ordre_reparation table

from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class OrdreReparation:
    """
    Data Model representing a Ordre_reparation in the application.
    This class is a simple Python dataclass holding Ordre_reparation properties.
    """

    vehicule_id: int
    statut: str = 'reception'
    mecanicien_id: Optional[int] = None
    date_entree: Optional[date] = None
    date_sortie: Optional[date] = None
    description: Optional[str] = None
    id: Optional[int] = None
