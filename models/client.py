# -*- coding: utf-8 -*-
# Data Model representation of Client table

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Client:
    """
    Data Model representing a Client in the application.
    This class is a simple Python dataclass holding Client properties.
    """

    nom: str
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    adresse: Optional[str] = None
    id: Optional[int] = None
    date_creation: Optional[datetime] = None