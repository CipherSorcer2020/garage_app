# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date

@dataclass
class LigneCommandeFournisseur:
    commande_id: int
    piece_id: int
    quantite_commandee: int = 1
    quantite_recue: int = 0
    prix_achat_unitaire: float = 0.0
    id: Optional[int] = None

@dataclass
class CommandeFournisseur:
    fournisseur_id: int
    statut: str = 'brouillon'
    date_commande: Optional[date] = None
    date_reception: Optional[date] = None
    lignes: List[LigneCommandeFournisseur] = field(default_factory=list)
    id: Optional[int] = None
