# -*- coding: utf-8 -*-
# Repository Data Access Layer for utilisateur_repo
# Exécute des requêtes SQL brutes et mappe les lignes de résultat aux modèles de données.

from config.database import get_connection, get_db
from models.utilisateur import Utilisateur

def _row(r):
    """
    Convertit une ligne de base de données en objet Utilisateur.
    """
    # Mappe l'identifiant, le nom, le prénom, les identifiants de connexion et le rôle (ex: admin, mecanicien)
    return Utilisateur(id=r[0], nom=r[1], prenom=r[2], login=r[3], mot_de_passe=r[4], role=r[5])

def get_all():
    """
    Récupère la liste de tous les utilisateurs du système.
    """
    with get_db() as (cur, conn):
        # Sélectionne tous les utilisateurs et les trie par nom alphabétique
        cur.execute("SELECT id, nom, prenom, login, mot_de_passe, role FROM utilisateurs ORDER BY nom")
        rows = cur.fetchall()
    # Retourne les données sous forme de liste d'objets Utilisateur
    return [_row(r) for r in rows]

def get_by_login(login: str):
    """
    Récupère un utilisateur via son identifiant de connexion (login).
    Utile pour l'authentification.
    """
    with get_db() as (cur, conn):
        # Recherche l'utilisateur correspondant au login fourni
        cur.execute("SELECT id, nom, prenom, login, mot_de_passe, role FROM utilisateurs WHERE login=%s", (login,))
        r = cur.fetchone()
    # Retourne l'utilisateur s'il existe, sinon None
    return _row(r) if r else None

def create(u: Utilisateur):
    """
    Crée un nouvel utilisateur en base de données.
    """
    with get_db() as (cur, conn):
        # Insère les informations de l'utilisateur et récupère l'ID généré
        cur.execute(
            "INSERT INTO utilisateurs (nom, prenom, login, mot_de_passe, role) VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (u.nom, u.prenom, u.login, u.mot_de_passe, u.role)
        )
        # Assigne l'ID au modèle
        u.id = cur.fetchone()[0]
    return u

def delete(utilisateur_id: int):
    """
    Supprime un utilisateur du système.
    """
    with get_db() as (cur, conn):
        # Supprime la ligne correspondant à l'ID
        cur.execute("DELETE FROM utilisateurs WHERE id=%s", (utilisateur_id,))
