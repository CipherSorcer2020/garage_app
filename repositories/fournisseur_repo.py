# -*- coding: utf-8 -*-
from typing import List, Optional
from config.database import get_db
from models.fournisseur import Fournisseur

def _row_to_fournisseur(r) -> Fournisseur:
    return Fournisseur(id=r[0], nom=r[1], contact=r[2], telephone=r[3], email=r[4], adresse=r[5])

def get_all() -> List[Fournisseur]:
    with get_db() as (cur, conn):
        cur.execute("SELECT id, nom, contact, telephone, email, adresse FROM fournisseurs ORDER BY nom")
        rows = cur.fetchall()
    return [_row_to_fournisseur(r) for r in rows]

def get_by_id(fid: int) -> Optional[Fournisseur]:
    with get_db() as (cur, conn):
        cur.execute("SELECT id, nom, contact, telephone, email, adresse FROM fournisseurs WHERE id=%s", (fid,))
        r = cur.fetchone()
    return _row_to_fournisseur(r) if r else None

def create(f: Fournisseur) -> Fournisseur:
    with get_db() as (cur, conn):
        cur.execute("INSERT INTO fournisseurs (nom, contact, telephone, email, adresse) VALUES (%s,%s,%s,%s,%s) RETURNING id",
                    (f.nom, f.contact, f.telephone, f.email, f.adresse))
        f.id = cur.fetchone()[0]
    return f

def update(f: Fournisseur) -> None:
    with get_db() as (cur, conn):
        cur.execute("UPDATE fournisseurs SET nom=%s, contact=%s, telephone=%s, email=%s, adresse=%s WHERE id=%s",
                    (f.nom, f.contact, f.telephone, f.email, f.adresse, f.id))

def delete(fid: int) -> None:
    with get_db() as (cur, conn):
        cur.execute("DELETE FROM fournisseurs WHERE id=%s", (fid,))
