from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Diagnostic:
    or_id: int
    observations: Optional[str] = None
    date_diagnostic: Optional[date] = None
    id: Optional[int] = None
