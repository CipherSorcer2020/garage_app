# -*- coding: utf-8 -*-
from typing import List, Optional
from config.database import get_db
from models.retour_piece import RetourPiece

def _row_to_retour(r) -> RetourPiece:
    return RetourPiece(
        id=r[0],
        piece_id=r[1],
        quantite=r[2],
        motif=r[3],
        date_retour=r[4],
        fournisseur_id=r[5]
    )

def create_retour(ret: RetourPiece) -> RetourPiece:
    """Insert a RetourPiece and return it with generated id/date."""
    with get_db() as (cur, conn):
        cur.execute(
            """INSERT INTO retours_piece (piece_id, quantite, motif, date_retour, fournisseur_id)
               VALUES (%s, %s, %s, COALESCE(%s, CURRENT_DATE), %s)
               RETURNING id, date_retour""",
            (ret.piece_id, ret.quantite, ret.motif, ret.date_retour, ret.fournisseur_id)
        )
        row = cur.fetchone()
        ret.id = row[0]
        ret.date_retour = row[1]
    return ret

def get_by_id(retour_id: int) -> Optional[RetourPiece]:
    with get_db() as (cur, conn):
        cur.execute(
            "SELECT id, piece_id, quantite, motif, date_retour, fournisseur_id FROM retours_piece WHERE id=%s",
            (retour_id,)
        )
        r = cur.fetchone()
    return _row_to_retour(r) if r else None

def get_all() -> List[RetourPiece]:
    with get_db() as (cur, conn):
        cur.execute(
            "SELECT id, piece_id, quantite, motif, date_retour, fournisseur_id FROM retours_piece ORDER BY id DESC"
        )
        rows = cur.fetchall()
    return [_row_to_retour(r) for r in rows]
