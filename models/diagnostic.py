# -*- coding: utf-8 -*-
# Data Model representation of Diagnostic table

from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Diagnostic:
    """
    Data Model representing a Diagnostic in the application.
    This class is a simple Python dataclass holding Diagnostic properties.
    """

    or_id: int
    observations: Optional[str] = None
    date_diagnostic: Optional[date] = None
    id: Optional[int] = None
