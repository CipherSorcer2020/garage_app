# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class AuditLog:
    user_id: int
    action: str                # e.g. "create", "update", "delete"
    entity: str                # model name, e.g. "OrdreReparation"
    entity_id: int
    timestamp: Optional[datetime] = None
    details: Optional[str] = None
    id: Optional[int] = None
