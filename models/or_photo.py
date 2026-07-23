# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class ORPhoto:
    """Modèle représentant une photo associée à un Ordre de Réparation."""
    or_id: int
    image_data: bytes
    description: str = ""
    date_ajout: Optional[datetime] = None
    id: Optional[int] = None
