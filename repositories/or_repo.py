# -*- coding: utf-8 -*-
# Repository Data Access Layer for or_repo
# Executes raw SQL queries and maps result rows to data models.

from config.database import get_connection
from models.ordre_reparation import OrdreReparation

def _row_to_or(r):
    """
    Handles database operations for function '_row_to_or'.
    """
    return OrdreReparation(id=r[0], vehicule_id=r[1], mecanicien_id=r[2], statut=r[3], date_entree=r[4], date_sortie=r[5], description=r[6])

def get_all():
    """
    Handles database operations for function 'get_all'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, vehicule_id, mecanicien_id, statut, date_entree, date_sortie, description FROM ordres_reparation ORDER BY date_entree DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_row_to_or(r) for r in rows]

def get_by_id(or_id: int):
    """
    Handles database operations for function 'get_by_id'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, vehicule_id, mecanicien_id, statut, date_entree, date_sortie, description FROM ordres_reparation WHERE id=%s", (or_id,))
    r = cur.fetchone()
    cur.close(); conn.close()
    return _row_to_or(r) if r else None

def get_by_statut(statut: str):
    """
    Handles database operations for function 'get_by_statut'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, vehicule_id, mecanicien_id, statut, date_entree, date_sortie, description FROM ordres_reparation WHERE statut=%s ORDER BY date_entree DESC", (statut,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_row_to_or(r) for r in rows]

def get_by_vehicule(vehicule_id: int):
    """
    Handles database operations for function 'get_by_vehicule'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, vehicule_id, mecanicien_id, statut, date_entree, date_sortie, description FROM ordres_reparation WHERE vehicule_id=%s ORDER BY date_entree DESC", (vehicule_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_row_to_or(r) for r in rows]

def create(o: OrdreReparation):
    """
    Handles database operations for function 'create'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ordres_reparation (vehicule_id, mecanicien_id, statut, date_entree, description) VALUES (%s,%s,%s,CURRENT_DATE,%s) RETURNING id",
        (o.vehicule_id, o.mecanicien_id, o.statut, o.description)
    )
    o.id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return o

def update_statut(or_id: int, statut: str):
    """
    Handles database operations for function 'update_statut'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE ordres_reparation SET statut=%s WHERE id=%s", (statut, or_id))
    conn.commit(); cur.close(); conn.close()

def update(o: OrdreReparation):
    """
    Handles database operations for function 'update'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE ordres_reparation SET vehicule_id=%s, mecanicien_id=%s, statut=%s, date_entree=%s, date_sortie=%s, description=%s WHERE id=%s",
        (o.vehicule_id, o.mecanicien_id, o.statut, o.date_entree, o.date_sortie, o.description, o.id)
    )
    conn.commit(); cur.close(); conn.close()

def delete(or_id: int):
    """
    Handles database operations for function 'delete'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ordres_reparation WHERE id=%s", (or_id,))
    conn.commit(); cur.close(); conn.close()