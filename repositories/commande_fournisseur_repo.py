# -*- coding: utf-8 -*-
from typing import List, Optional
from config.database import get_db
from models.commande_fournisseur import CommandeFournisseur, LigneCommandeFournisseur

def _row_to_cmd(r) -> CommandeFournisseur:
    return CommandeFournisseur(id=r[0], fournisseur_id=r[1], statut=r[2], date_commande=r[3], date_reception=r[4])

def get_all() -> List[CommandeFournisseur]:
    with get_db() as (cur, conn):
        cur.execute("SELECT id, fournisseur_id, statut, date_commande, date_reception FROM commandes_fournisseurs ORDER BY id DESC")
        rows = cur.fetchall()
    return [_row_to_cmd(r) for r in rows]
