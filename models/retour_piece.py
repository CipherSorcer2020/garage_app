# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date

@dataclass
class RetourPiece:
    """Représente un retour de pièce au fournisseur (ou garantie).
    - `piece_id` : identifiant de la pièce retournée.
    - `quantite` : nombre de pièces retournées.
    - `motif`    : raison du retour (défaut, erreur de commande, etc.).
    - `date_retour` : date du retour (défaut = today).
    - `fournisseur_id` : fournisseur concerné (facultatif, utile pour la traçabilité).
    - `id` : identifiant DB généré.
    """
    piece_id: int
    quantite: int = 1
    motif: str = ""
    date_retour: Optional[date] = None
    fournisseur_id: Optional[int] = None
    id: Optional[int] = None
