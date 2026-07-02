from config.database import get_connection
from models.ligne_main_oeuvre import LigneMainOeuvre

def _row(r):
    return LigneMainOeuvre(id=r[0], or_id=r[1], description=r[2], duree_heures=float(r[3]) if r[3] else None, taux_horaire_ht=float(r[4]) if r[4] else None)

def get_by_or(or_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, or_id, description, duree_heures, taux_horaire_ht FROM lignes_main_oeuvre WHERE or_id=%s", (or_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_row(r) for r in rows]

def create(l: LigneMainOeuvre):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO lignes_main_oeuvre (or_id, description, duree_heures, taux_horaire_ht) VALUES (%s,%s,%s,%s) RETURNING id",
        (l.or_id, l.description, l.duree_heures, l.taux_horaire_ht)
    )
    l.id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return l

def delete(ligne_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM lignes_main_oeuvre WHERE id=%s", (ligne_id,))
    conn.commit(); cur.close(); conn.close()

def delete_by_or(or_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM lignes_main_oeuvre WHERE or_id=%s", (or_id,))
    conn.commit(); cur.close(); conn.close()
