# -*- coding: utf-8 -*-
# Repository Data Access Layer for facture_repo
# Executes raw SQL queries and maps result rows to data models.

from config.database import get_connection
from models.facture import Facture

def _row(r):
    """
    Handles database operations for function '_row'.
    """
    return Facture(id=r[0], or_id=r[1], client_id=r[2], numero=r[3], montant_ht=float(r[4]) if r[4] else None,
                   tva=float(r[5]), montant_ttc=float(r[6]) if r[6] else None, statut=r[7], date_emission=r[8], mode_paiement=r[9])

def get_all():
    """
    Handles database operations for function 'get_all'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, or_id, client_id, numero, montant_ht, tva, montant_ttc, statut, date_emission, mode_paiement FROM factures ORDER BY date_emission DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_row(r) for r in rows]

def get_by_id(facture_id: int):
    """
    Handles database operations for function 'get_by_id'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, or_id, client_id, numero, montant_ht, tva, montant_ttc, statut, date_emission, mode_paiement FROM factures WHERE id=%s", (facture_id,))
    r = cur.fetchone()
    cur.close(); conn.close()
    return _row(r) if r else None

def get_by_or(or_id: int):
    """
    Handles database operations for function 'get_by_or'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, or_id, client_id, numero, montant_ht, tva, montant_ttc, statut, date_emission, mode_paiement FROM factures WHERE or_id=%s", (or_id,))
    r = cur.fetchone()
    cur.close(); conn.close()
    return _row(r) if r else None

def get_by_client(client_id: int):
    """
    Handles database operations for function 'get_by_client'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, or_id, client_id, numero, montant_ht, tva, montant_ttc, statut, date_emission, mode_paiement FROM factures WHERE client_id=%s ORDER BY date_emission DESC", (client_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_row(r) for r in rows]

def generate_numero():
    """
    Handles database operations for function 'generate_numero'.
    """
    from datetime import date
    conn = get_connection()
    cur = conn.cursor()
    year = date.today().year
    cur.execute("SELECT COUNT(*) FROM factures WHERE EXTRACT(YEAR FROM date_emission)=%s", (year,))
    count = cur.fetchone()[0]
    cur.close(); conn.close()
    return f"F-{year}-{str(count + 1).zfill(4)}"

def create(f: Facture):
    """
    Handles database operations for function 'create'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO factures (or_id, client_id, numero, montant_ht, tva, montant_ttc, statut, date_emission, mode_paiement) VALUES (%s,%s,%s,%s,%s,%s,%s,CURRENT_DATE,%s) RETURNING id",
        (f.or_id, f.client_id, f.numero, f.montant_ht, f.tva, f.montant_ttc, f.statut, f.mode_paiement)
    )
    f.id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return f

def marquer_payee(facture_id: int, mode_paiement: str):
    """
    Handles database operations for function 'marquer_payee'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE factures SET statut='payee', mode_paiement=%s WHERE id=%s", (mode_paiement, facture_id))
    conn.commit(); cur.close(); conn.close()

def update(f: Facture):
    """
    Handles database operations for function 'update'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE factures SET montant_ht=%s, tva=%s, montant_ttc=%s, statut=%s, mode_paiement=%s WHERE id=%s",
        (f.montant_ht, f.tva, f.montant_ttc, f.statut, f.mode_paiement, f.id)
    )
    conn.commit(); cur.close(); conn.close()