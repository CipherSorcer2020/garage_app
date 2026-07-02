from dataclasses import dataclass
from typing import Optional

@dataclass
class LignePiece:
    or_id: int
    designation: str
    quantite: int = 1
    reference: Optional[str] = None
    prix_unitaire_ht: Optional[float] = None
    id: Optional[int] = None

    @property
    def total_ht(self) -> Optional[float]:
        if self.prix_unitaire_ht is None:
            return None
        return round(self.quantite * self.prix_unitaire_ht, 2)
