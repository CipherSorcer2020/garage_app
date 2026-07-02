from dataclasses import dataclass
from typing import Optional

@dataclass
class LigneMainOeuvre:
    or_id: int
    description: str
    duree_heures: Optional[float] = None
    taux_horaire_ht: Optional[float] = None
    id: Optional[int] = None

    @property
    def total_ht(self) -> Optional[float]:
        if self.duree_heures is None or self.taux_horaire_ht is None:
            return None
        return round(self.duree_heures * self.taux_horaire_ht, 2)
