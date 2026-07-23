# -*- coding: utf-8 -*-
from typing import List, Optional
from config.database import get_db
from models.dossier_sinistre import DossierSinistre

def _row_to_ds(r) -> DossierSinistre:
    return DossierSinistre(
        id=r[0], or_id=r[1], nom_assurance=r[2],
        numero_dossier=r[3], statut=r[4],
        montant_couvert=float(r[5]) if r[5] else 0.0,
        date_creation=r[6]
    )

def get_all() -> List[DossierSinistre]:
    with get_db() as (cur, conn):
        cur.execute("SELECT id, or_id, nom_assurance, numero_dossier, statut, montant_couvert, date_creation FROM dossiers_sinistres ORDER BY date_creation DESC")
        rows = cur.fetchall()
    return [_row_to_ds(r) for r in rows]

def get_by_or(or_id: int) -> Optional[DossierSinistre]:
    with get_db() as (cur, conn):
        cur.execute("SELECT id, or_id, nom_assurance, numero_dossier, statut, montant_couvert, date_creation FROM dossiers_sinistres WHERE or_id=%s", (or_id,))
        r = cur.fetchone()
    return _row_to_ds(r) if r else None

def create(ds: DossierSinistre) -> DossierSinistre:
    with get_db() as (cur, conn):
        cur.execute(
            "INSERT INTO dossiers_sinistres (or_id, nom_assurance, numero_dossier, statut, montant_couvert) VALUES (%s,%s,%s,%s,%s) RETURNING id, date_creation",
            (ds.or_id, ds.nom_assurance, ds.numero_dossier, ds.statut, ds.montant_couvert)
        )
        row = cur.fetchone()
        ds.id = row[0]
        ds.date_creation = row[1]
    return ds

def update(ds: DossierSinistre) -> None:
    with get_db() as (cur, conn):
        cur.execute(
            "UPDATE dossiers_sinistres SET nom_assurance=%s, numero_dossier=%s, statut=%s, montant_couvert=%s WHERE id=%s",
            (ds.nom_assurance, ds.numero_dossier, ds.statut, ds.montant_couvert, ds.id)
        )
