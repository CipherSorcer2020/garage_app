# -*- coding: utf-8 -*-
from typing import List, Optional
from datetime import datetime
from config.database import get_db
from models.rendez_vous import RendezVous

def _row_to_rdv(r) -> RendezVous:
    return RendezVous(
        id=r[0], client_id=r[1], vehicule_id=r[2],
        date_heure_prevue=r[3], duree_estimee_minutes=r[4],
        statut=r[5], description=r[6]
    )

def get_all() -> List[RendezVous]:
    with get_db() as (cur, conn):
        cur.execute("SELECT id, client_id, vehicule_id, date_heure_prevue, duree_estimee_minutes, statut, description FROM rendez_vous ORDER BY date_heure_prevue ASC")
        rows = cur.fetchall()
    return [_row_to_rdv(r) for r in rows]

def get_upcoming() -> List[RendezVous]:
    with get_db() as (cur, conn):
        cur.execute("SELECT id, client_id, vehicule_id, date_heure_prevue, duree_estimee_minutes, statut, description FROM rendez_vous WHERE date_heure_prevue >= CURRENT_DATE ORDER BY date_heure_prevue ASC")
        rows = cur.fetchall()
    return [_row_to_rdv(r) for r in rows]

def create(r: RendezVous) -> RendezVous:
    with get_db() as (cur, conn):
        cur.execute(
            "INSERT INTO rendez_vous (client_id, vehicule_id, date_heure_prevue, duree_estimee_minutes, statut, description) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
            (r.client_id, r.vehicule_id, r.date_heure_prevue, r.duree_estimee_minutes, r.statut, r.description)
        )
        r.id = cur.fetchone()[0]
    return r

def update_statut(rdv_id: int, statut: str) -> None:
    with get_db() as (cur, conn):
        cur.execute("UPDATE rendez_vous SET statut=%s WHERE id=%s", (statut, rdv_id))
