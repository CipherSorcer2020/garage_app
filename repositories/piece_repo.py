"""Repository for managing spare parts inventory (Piece)."""
from typing import List, Optional

from config.database import get_db
from models.piece import Piece


def _row_to_piece(row) -> Piece:
    return Piece(
        id=row[0],
        reference=row[1],
        designation=row[2],
        quantite=row[3],
        prix_unitaire=row[4],
        emplacement=row[5],
    )

def get_all() -> List[Piece]:
    with get_db() as (cur, _):
        cur.execute("SELECT id, reference, designation, quantite, prix_unitaire, emplacement FROM pieces ORDER BY designation ASC")
        rows = cur.fetchall()
    return [_row_to_piece(r) for r in rows]

def get_low_stock(threshold: int = 5) -> List[Piece]:
    """Return pieces with quantity less than or equal to *threshold*.
    Used for UI warnings and re‑order suggestions.
    """
    with get_db() as (cur, _):
        cur.execute(
            "SELECT id, reference, designation, quantite, prix_unitaire, emplacement FROM pieces WHERE quantite <= %s",
            (threshold,)
        )
        rows = cur.fetchall()
    return [_row_to_piece(r) for r in rows]

def get_by_id(piece_id: int) -> Optional[Piece]:
    with get_db() as (cur, _):
        cur.execute("SELECT id, reference, designation, quantite, prix_unitaire, emplacement FROM pieces WHERE id=%s", (piece_id,))
        row = cur.fetchone()
    return _row_to_piece(row) if row else None

def create(piece: Piece) -> Piece:
    with get_db() as (cur, conn):
        cur.execute(
            "INSERT INTO pieces (reference, designation, quantite, prix_unitaire, emplacement) VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (piece.reference, piece.designation, piece.quantite, piece.prix_unitaire, piece.emplacement),
        )
        piece.id = cur.fetchone()[0]
    return piece

def update(piece: Piece) -> None:
    with get_db() as (cur, conn):
        cur.execute(
            "UPDATE pieces SET reference=%s, designation=%s, quantite=%s, prix_unitaire=%s, emplacement=%s WHERE id=%s",
            (piece.reference, piece.designation, piece.quantite, piece.prix_unitaire, piece.emplacement, piece.id),
        )

def delete(piece_id: int) -> None:
    with get_db() as (cur, conn):
        cur.execute("DELETE FROM pieces WHERE id=%s", (piece_id,))
