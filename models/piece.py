from dataclasses import dataclass
from typing import Optional


@dataclass
class Piece:
    """Represents a spare part in the inventory."""
    id: Optional[int] = None
    reference: str = ""
    designation: str = ""
    quantite: int = 0
    prix_unitaire: float = 0.0
    emplacement: str = ""
