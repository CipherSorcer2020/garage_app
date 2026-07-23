# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Notification:
    client_id: int
    type_notification: str
    canal: str = 'email'
    message: str = ""
    statut: str = 'en_attente'
    date_creation: Optional[datetime] = None
    date_envoi: Optional[datetime] = None
    id: Optional[int] = None
