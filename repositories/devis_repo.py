from config.database import get_connection
from models.devis import Devis

def _row_to_devis(r):
    return Devis(id=r[0], or_id=r[1], montant_ht=float(r[2]) if r[2] else None, tva=float(r[3]), statut=r[4], date_creation=r[5], accepte=r[6])

def get_by_or(or_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, or_id, montant_ht, tva, statut, date_creation, accepte FROM devis WHERE or_id=%s", (or_id,))
    r = cur.fetchone()
    cur.close(); conn.close()
    return _row_to_devis(r) if r else None

def create(d: Devis):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO devis (or_id, montant_ht, tva, statut, date_creation, accepte) VALUES (%s,%s,%s,%s,CURRENT_DATE,%s) RETURNING id",
        (d.or_id, d.montant_ht, d.tva, d.statut, d.accepte)
    )
    d.id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return d

def update(d: Devis):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE devis SET montant_ht=%s, tva=%s, statut=%s, accepte=%s WHERE id=%s",
        (d.montant_ht, d.tva, d.statut, d.accepte, d.id)
    )
    conn.commit(); cur.close(); conn.close()

def accepter(devis_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE devis SET accepte=TRUE, statut='accepte' WHERE id=%s", (devis_id,))
    conn.commit(); cur.close(); conn.close()

def refuser(devis_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE devis SET accepte=FALSE, statut='refuse' WHERE id=%s", (devis_id,))
    conn.commit(); cur.close(); conn.close()
