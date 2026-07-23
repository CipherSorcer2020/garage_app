# -*- coding: utf-8 -*-
from typing import List
from models.retour_piece import RetourPiece
from repositories import retour_piece_repo

def creer_retour(piece_id: int, quantite: int = 1, motif: str = "", fournisseur_id: int = None) -> RetourPiece:
    """Create a RetourPiece entry and persist it.
    Returns the fully populated RetourPiece (id + date)."""
    ret = RetourPiece(
        piece_id=piece_id,
        quantite=quantite,
        motif=motif,
        fournisseur_id=fournisseur_id,
    )
    return retour_piece_repo.create_retour(ret)

def lister_retours() -> List[RetourPiece]:
    """Return all RetourPiece records ordered by newest first."""
    return retour_piece_repo.get_all()
