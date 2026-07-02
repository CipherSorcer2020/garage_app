# -*- coding: utf-8 -*-
# Data Model representation of Vehicule table

from dataclasses import dataclass
from typing import Optional

@dataclass
class Vehicule:
    """
    Data Model representing a Vehicule in the application.
    This class is a simple Python dataclass holding Vehicule properties.
    """

    immatriculation: str
    client_id: int
    vin: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    annee: Optional[int] = None
    kilometrage: Optional[int] = None
    id: Optional[int] = None
