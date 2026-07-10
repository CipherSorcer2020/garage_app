# -*- coding: utf-8 -*-
# Repository Data Access Layer for ligne_piece_repo
# Exécute des requêtes SQL brutes et mappe les lignes de résultat aux modèles de données.

from config.database import get_connection, get_db
from models.ligne_piece import LignePiece

def _row(r):
    """
    Convertit une ligne SQL en objet LignePiece.
    """
    # Mappe les données (référence, désignation, quantité, prix) dans le modèle LignePiece
    return LignePiece(id=r[0], or_id=r[1], reference=r[2], designation=r[3], quantite=r[4], prix_unitaire_ht=float(r[5]) if r[5] else None)

def get_by_or(or_id: int):
    """
    Récupère toutes les lignes de pièces détachées associées à un ordre de réparation.
    """
    with get_db() as (cur, conn):
        # Sélectionne toutes les pièces pour l'or_id spécifié
        cur.execute("SELECT id, or_id, reference, designation, quantite, prix_unitaire_ht FROM lignes_pieces WHERE or_id=%s", (or_id,))
        rows = cur.fetchall()
    # Retourne une liste des objets instanciés
    return [_row(r) for r in rows]

def create(l: LignePiece):
    """
    Ajoute une nouvelle pièce utilisée pour un ordre de réparation.
    """
    with get_db() as (cur, conn):
        # Insère la ligne de pièce et renvoie l'ID
        cur.execute(
            "INSERT INTO lignes_pieces (or_id, reference, designation, quantite, prix_unitaire_ht) VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (l.or_id, l.reference, l.designation, l.quantite, l.prix_unitaire_ht)
        )
        # Assigne l'identifiant généré à l'objet
        l.id = cur.fetchone()[0]
    return l

def delete(ligne_id: int):
    """
    Supprime une ligne de pièce spécifique via son ID.
    """
    with get_db() as (cur, conn):
        # Supprime la ligne dans la base de données
        cur.execute("DELETE FROM lignes_pieces WHERE id=%s", (ligne_id,))

def delete_by_or(or_id: int):
    """
    Supprime toutes les pièces détachées associées à un ordre de réparation.
    """
    with get_db() as (cur, conn):
        # Suppression par lot en filtrant par or_id
        cur.execute("DELETE FROM lignes_pieces WHERE or_id=%s", (or_id,))
