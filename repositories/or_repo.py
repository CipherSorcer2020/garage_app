# -*- coding: utf-8 -*-
# Repository Data Access Layer for or_repo
# Exécute des requêtes SQL brutes et mappe les lignes de résultat aux modèles de données.

from config.database import get_connection
from models.ordre_reparation import OrdreReparation

def _row_to_or(r):
    """
    Convertit une ligne SQL en un objet OrdreReparation (OR).
    """
    # Construit l'objet avec les identifiants, le statut, les dates et la description
    return OrdreReparation(id=r[0], vehicule_id=r[1], mecanicien_id=r[2], statut=r[3], date_entree=r[4], date_sortie=r[5], description=r[6])

def get_all():
    """
    Récupère tous les ordres de réparation (du plus récent au plus ancien).
    """
    conn = get_connection()
    cur = conn.cursor()
    # Requête avec un tri décroissant sur la date d'entrée
    cur.execute("SELECT id, vehicule_id, mecanicien_id, statut, date_entree, date_sortie, description FROM ordres_reparation ORDER BY date_entree DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_row_to_or(r) for r in rows]

def get_by_id(or_id: int):
    """
    Récupère un OR spécifique par son identifiant.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Recherche l'OR correspondant à l'ID
    cur.execute("SELECT id, vehicule_id, mecanicien_id, statut, date_entree, date_sortie, description FROM ordres_reparation WHERE id=%s", (or_id,))
    r = cur.fetchone()
    cur.close(); conn.close()
    # Renvoie l'OR si trouvé, sinon None
    return _row_to_or(r) if r else None

def get_by_statut(statut: str):
    """
    Récupère tous les OR ayant un statut spécifique (ex: 'en_cours', 'termine').
    """
    conn = get_connection()
    cur = conn.cursor()
    # Filtre les résultats en fonction de la colonne statut
    cur.execute("SELECT id, vehicule_id, mecanicien_id, statut, date_entree, date_sortie, description FROM ordres_reparation WHERE statut=%s ORDER BY date_entree DESC", (statut,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_row_to_or(r) for r in rows]

def get_by_vehicule(vehicule_id: int):
    """
    Récupère l'historique des OR pour un véhicule donné.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Filtre par véhicule
    cur.execute("SELECT id, vehicule_id, mecanicien_id, statut, date_entree, date_sortie, description FROM ordres_reparation WHERE vehicule_id=%s ORDER BY date_entree DESC", (vehicule_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [_row_to_or(r) for r in rows]

def create(o: OrdreReparation):
    """
    Crée un nouvel ordre de réparation.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Insère le nouvel OR et renvoie l'ID généré. Utilise la date du jour (CURRENT_DATE) pour la date d'entrée.
    cur.execute(
        "INSERT INTO ordres_reparation (vehicule_id, mecanicien_id, statut, date_entree, description) VALUES (%s,%s,%s,CURRENT_DATE,%s) RETURNING id",
        (o.vehicule_id, o.mecanicien_id, o.statut, o.description)
    )
    # Récupère l'ID inséré
    o.id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return o

def update_statut(or_id: int, statut: str):
    """
    Met à jour uniquement le statut d'un OR (ex: passer de 'en_cours' à 'termine').
    """
    conn = get_connection()
    cur = conn.cursor()
    # Met à jour la colonne statut
    cur.execute("UPDATE ordres_reparation SET statut=%s WHERE id=%s", (statut, or_id))
    conn.commit(); cur.close(); conn.close()

def update(o: OrdreReparation):
    """
    Met à jour toutes les informations d'un ordre de réparation existant.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Met à jour l'ensemble des colonnes de l'OR
    cur.execute(
        "UPDATE ordres_reparation SET vehicule_id=%s, mecanicien_id=%s, statut=%s, date_entree=%s, date_sortie=%s, description=%s WHERE id=%s",
        (o.vehicule_id, o.mecanicien_id, o.statut, o.date_entree, o.date_sortie, o.description, o.id)
    )
    conn.commit(); cur.close(); conn.close()

def delete(or_id: int):
    """
    Supprime un ordre de réparation.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Exécute la suppression en base
    cur.execute("DELETE FROM ordres_reparation WHERE id=%s", (or_id,))
    conn.commit(); cur.close(); conn.close()