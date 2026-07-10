# -*- coding: utf-8 -*-
# Repository Data Access Layer for ligne_mo_repo
# Exécute des requêtes SQL brutes et mappe les lignes de résultat aux modèles de données.

from config.database import get_connection, get_db
from models.ligne_main_oeuvre import LigneMainOeuvre

def _row(r):
    """
    Convertit une ligne SQL en objet LigneMainOeuvre.
    """
    # Mappe les colonnes vers les attributs, en convertissant les types numériques
    return LigneMainOeuvre(id=r[0], or_id=r[1], description=r[2], duree_heures=float(r[3]) if r[3] else None, taux_horaire_ht=float(r[4]) if r[4] else None)

def get_by_or(or_id: int):
    """
    Récupère toutes les lignes de main d'œuvre associées à un ordre de réparation.
    """
    with get_db() as (cur, conn):
        # Sélectionne les lignes liées à l'or_id spécifié
        cur.execute("SELECT id, or_id, description, duree_heures, taux_horaire_ht FROM lignes_main_oeuvre WHERE or_id=%s", (or_id,))
        rows = cur.fetchall()
    # Retourne la liste des objets LigneMainOeuvre
    return [_row(r) for r in rows]

def create(l: LigneMainOeuvre):
    """
    Ajoute une nouvelle ligne de main d'œuvre dans la base de données.
    """
    with get_db() as (cur, conn):
        # Insère les informations de main d'œuvre et récupère le nouvel ID
        cur.execute(
            "INSERT INTO lignes_main_oeuvre (or_id, description, duree_heures, taux_horaire_ht) VALUES (%s,%s,%s,%s) RETURNING id",
            (l.or_id, l.description, l.duree_heures, l.taux_horaire_ht)
        )
        l.id = cur.fetchone()[0]
    return l

def delete(ligne_id: int):
    """
    Supprime une ligne de main d'œuvre spécifique.
    """
    with get_db() as (cur, conn):
        # Exécute la suppression basée sur l'ID de la ligne
        cur.execute("DELETE FROM lignes_main_oeuvre WHERE id=%s", (ligne_id,))

def delete_by_or(or_id: int):
    """
    Supprime toutes les lignes de main d'œuvre associées à un ordre de réparation.
    """
    with get_db() as (cur, conn):
        # Supprime toutes les lignes liées à l'or_id donné
        cur.execute("DELETE FROM lignes_main_oeuvre WHERE or_id=%s", (or_id,))
