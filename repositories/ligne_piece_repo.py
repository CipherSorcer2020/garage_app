from config.database import get_connection
from models.ligne_piece import LignePiece

def _row(r):
    return LignePiece(id=r[0], or_id=r[1], reference=r[2], designation=r[3], quantite=r[4], prix_unitaire_ht=float(r[5]) if r[5] else None)

def get_by_or(or_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, or_id, reference, designation, quantite, prix_unitaire_ht FROM lignes_pieces WHERE or_id=%s", (or_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_row(r) for r in rows]

def create(l: LignePiece):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO lignes_pieces (or_id, reference, designation, quantite, prix_unitaire_ht) VALUES (%s,%s,%s,%s,%s) RETURNING id",
        (l.or_id, l.reference, l.designation, l.quantite, l.prix_unitaire_ht)
    )
    l.id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return l

def delete(ligne_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM lignes_pieces WHERE id=%s", (ligne_id,))
    conn.commit(); cur.close(); conn.close()

def delete_by_or(or_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM lignes_pieces WHERE or_id=%s", (or_id,))
    conn.commit(); cur.close(); conn.close()
