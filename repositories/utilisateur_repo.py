# -*- coding: utf-8 -*-
# Repository Data Access Layer for utilisateur_repo
# Executes raw SQL queries and maps result rows to data models.

from config.database import get_connection
from models.utilisateur import Utilisateur

def _row(r):
    """
    Handles database operations for function '_row'.
    """
    return Utilisateur(id=r[0], nom=r[1], prenom=r[2], login=r[3], mot_de_passe=r[4], role=r[5])

def get_all():
    """
    Handles database operations for function 'get_all'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nom, prenom, login, mot_de_passe, role FROM utilisateurs ORDER BY nom")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_row(r) for r in rows]

def get_by_login(login: str):
    """
    Handles database operations for function 'get_by_login'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nom, prenom, login, mot_de_passe, role FROM utilisateurs WHERE login=%s", (login,))
    r = cur.fetchone()
    cur.close(); conn.close()
    return _row(r) if r else None

def create(u: Utilisateur):
    """
    Handles database operations for function 'create'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO utilisateurs (nom, prenom, login, mot_de_passe, role) VALUES (%s,%s,%s,%s,%s) RETURNING id",
        (u.nom, u.prenom, u.login, u.mot_de_passe, u.role)
    )
    u.id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return u

def delete(utilisateur_id: int):
    """
    Handles database operations for function 'delete'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM utilisateurs WHERE id=%s", (utilisateur_id,))
    conn.commit(); cur.close(); conn.close()