# -*- coding: utf-8 -*-
# Repository Data Access Layer for vehicule_repo
# Executes raw SQL queries and maps result rows to data models.

from config.database import get_connection
from models.vehicule import Vehicule

def _row_to_vehicule(r):
    """
    Handles database operations for function '_row_to_vehicule'.
    """
    return Vehicule(id=r[0], client_id=r[1], immatriculation=r[2], vin=r[3], marque=r[4], modele=r[5], annee=r[6], kilometrage=r[7])

def get_all():
    """
    Handles database operations for function 'get_all'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, client_id, immatriculation, vin, marque, modele, annee, kilometrage FROM vehicules ORDER BY immatriculation")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_row_to_vehicule(r) for r in rows]

def get_by_id(vehicule_id: int):
    """
    Handles database operations for function 'get_by_id'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, client_id, immatriculation, vin, marque, modele, annee, kilometrage FROM vehicules WHERE id=%s", (vehicule_id,))
    r = cur.fetchone()
    cur.close(); conn.close()
    return _row_to_vehicule(r) if r else None

def get_by_client(client_id: int):
    """
    Handles database operations for function 'get_by_client'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, client_id, immatriculation, vin, marque, modele, annee, kilometrage FROM vehicules WHERE client_id=%s", (client_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_row_to_vehicule(r) for r in rows]

def create(v: Vehicule):
    """
    Handles database operations for function 'create'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO vehicules (client_id, immatriculation, vin, marque, modele, annee, kilometrage) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
        (v.client_id, v.immatriculation, v.vin, v.marque, v.modele, v.annee, v.kilometrage)
    )
    v.id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return v

def update(v: Vehicule):
    """
    Handles database operations for function 'update'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE vehicules SET client_id=%s, immatriculation=%s, vin=%s, marque=%s, modele=%s, annee=%s, kilometrage=%s WHERE id=%s",
        (v.client_id, v.immatriculation, v.vin, v.marque, v.modele, v.annee, v.kilometrage, v.id)
    )
    conn.commit(); cur.close(); conn.close()

def delete(vehicule_id: int):
    """
    Handles database operations for function 'delete'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM vehicules WHERE id=%s", (vehicule_id,))
    conn.commit(); cur.close(); conn.close()