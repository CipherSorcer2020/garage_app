# -*- coding: utf-8 -*-
# Repository Data Access Layer for or_repo
# Exécute des requêtes SQL brutes et mappe les lignes de résultat aux modèles de données.

from config.database import get_connection, get_db
from models.ordre_reparation import OrdreReparation

def _row_to_or(r):
    """
    Convertit une ligne SQL en un objet OrdreReparation (OR).
    """
    # Construit l'objet avec les identifiants, le statut, les dates et la description
    return OrdreReparation(id=r[0], vehicule_id=r[1], mecanicien_id=r[2], statut=r[3], date_entree=r[4], date_sortie=r[5], description=r[6], kilometrage=r[7], niveau_carburant=r[8])

def get_all():
    """
    Récupère tous les ordres de réparation (du plus récent au plus ancien).
    """
    with get_db() as (cur, conn):
        # Requête avec un tri décroissant sur la date d'entrée
        cur.execute("SELECT id, vehicule_id, mecanicien_id, statut, date_entree, date_sortie, description, kilometrage, niveau_carburant FROM ordres_reparation ORDER BY date_entree DESC")
        rows = cur.fetchall()
    return [_row_to_or(r) for r in rows]

def get_by_id(or_id: int):
    """
    Récupère un OR spécifique par son identifiant.
    """
    with get_db() as (cur, conn):
        # Recherche l'OR correspondant à l'ID
        cur.execute("SELECT id, vehicule_id, mecanicien_id, statut, date_entree, date_sortie, description, kilometrage, niveau_carburant FROM ordres_reparation WHERE id=%s", (or_id,))
        r = cur.fetchone()
    # Renvoie l'OR si trouvé, sinon None
    return _row_to_or(r) if r else None

def get_by_statut(statut: str):
    """
    Récupère tous les OR ayant un statut spécifique (ex: 'en_cours', 'termine').
    """
    with get_db() as (cur, conn):
        # Filtre les résultats en fonction de la colonne statut
        cur.execute("SELECT id, vehicule_id, mecanicien_id, statut, date_entree, date_sortie, description, kilometrage, niveau_carburant FROM ordres_reparation WHERE statut=%s ORDER BY date_entree DESC", (statut,))
        rows = cur.fetchall()
    return [_row_to_or(r) for r in rows]

def get_by_vehicule(vehicule_id: int):
    """
    Récupère l'historique des OR pour un véhicule donné.
    """
    with get_db() as (cur, conn):
        # Filtre par véhicule
        cur.execute("SELECT id, vehicule_id, mecanicien_id, statut, date_entree, date_sortie, description, kilometrage, niveau_carburant FROM ordres_reparation WHERE vehicule_id=%s ORDER BY date_entree DESC", (vehicule_id,))
        rows = cur.fetchall()
    return [_row_to_or(r) for r in rows]

def create(o: OrdreReparation):
    """
    Crée un nouvel ordre de réparation.
    """
    with get_db() as (cur, conn):
        # Insère le nouvel OR et renvoie l'ID généré. Utilise la date du jour (CURRENT_DATE) pour la date d'entrée.
        cur.execute(
            "INSERT INTO ordres_reparation (vehicule_id, mecanicien_id, statut, date_entree, description, kilometrage, niveau_carburant) VALUES (%s,%s,%s,CURRENT_DATE,%s,%s,%s) RETURNING id",
            (o.vehicule_id, o.mecanicien_id, o.statut, o.description, o.kilometrage, o.niveau_carburant)
        )
        # Récupère l'ID inséré
        o.id = cur.fetchone()[0]
    return o

def update_statut(or_id: int, statut: str):
    """
    Met à jour uniquement le statut d'un OR (ex: passer de 'en_cours' à 'termine').
    """
    with get_db() as (cur, conn):
        # Met à jour la colonne statut
        cur.execute("UPDATE ordres_reparation SET statut=%s WHERE id=%s", (statut, or_id))

def update(o: OrdreReparation):
    """
    Met à jour toutes les informations d'un ordre de réparation existant.
    """
    with get_db() as (cur, conn):
        # Met à jour l'ensemble des colonnes de l'OR
        cur.execute(
            "UPDATE ordres_reparation SET vehicule_id=%s, mecanicien_id=%s, statut=%s, date_entree=%s, date_sortie=%s, description=%s, kilometrage=%s, niveau_carburant=%s WHERE id=%s",
            (o.vehicule_id, o.mecanicien_id, o.statut, o.date_entree, o.date_sortie, o.description, o.kilometrage, o.niveau_carburant, o.id)
        )

def delete(or_id: int):
    """
    Supprime un ordre de réparation.
    """
    with get_db() as (cur, conn):
        # Exécute la suppression en base
        cur.execute("DELETE FROM ordres_reparation WHERE id=%s", (or_id,))
