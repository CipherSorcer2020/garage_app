# -*- coding: utf-8 -*-
# Repository Data Access Layer for client_repo
# Exécute des requêtes SQL brutes et mappe les lignes de résultat aux modèles de données.

# Importation de la fonction pour obtenir une connexion à la base de données
from config.database import get_connection
# Importation du modèle Client
from models.client import Client

def get_all():
    """
    Récupère tous les clients depuis la base de données.
    """
    # Établit une connexion à la base de données
    conn = get_connection()
    # Crée un curseur pour exécuter des requêtes
    cur = conn.cursor()
    # Exécute la requête SQL pour sélectionner tous les clients, triés par nom
    cur.execute("SELECT id, nom, prenom, telephone, email, adresse, date_creation FROM clients ORDER BY nom")
    # Récupère toutes les lignes de résultat
    rows = cur.fetchall()
    # Ferme le curseur et la connexion pour libérer les ressources
    cur.close(); conn.close()
    # Crée et retourne une liste d'objets Client à partir des lignes récupérées
    return [Client(id=r[0], nom=r[1], prenom=r[2], telephone=r[3], email=r[4], adresse=r[5], date_creation=r[6]) for r in rows]

def get_by_id(client_id: int):
    """
    Récupère un client spécifique par son identifiant.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Exécute la requête SQL pour trouver un client par son id
    cur.execute("SELECT id, nom, prenom, telephone, email, adresse, date_creation FROM clients WHERE id=%s", (client_id,))
    # Récupère une seule ligne (le client correspondant)
    r = cur.fetchone()
    cur.close(); conn.close()
    # Si un client a été trouvé, crée et retourne l'objet Client correspondant
    if r:
        return Client(id=r[0], nom=r[1], prenom=r[2], telephone=r[3], email=r[4], adresse=r[5], date_creation=r[6])
    # Sinon, retourne None
    return None

def search(query: str):
    """
    Recherche des clients dont le nom, prénom ou téléphone correspond à la requête.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Exécute une requête SQL avec l'opérateur ILIKE pour une recherche insensible à la casse
    cur.execute(
        "SELECT id, nom, prenom, telephone, email, adresse FROM clients WHERE nom ILIKE %s OR prenom ILIKE %s OR telephone ILIKE %s ORDER BY nom",
        (f"%{query}%", f"%{query}%", f"%{query}%")
    )
    rows = cur.fetchall()
    cur.close(); conn.close()
    # Retourne une liste de clients correspondant à la recherche
    return [Client(id=r[0], nom=r[1], prenom=r[2], telephone=r[3], email=r[4], adresse=r[5]) for r in rows]

def create(client: Client):
    """
    Crée un nouveau client dans la base de données.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Insère un nouveau client et retourne l'id généré
    cur.execute(
        "INSERT INTO clients (nom, prenom, telephone, email, adresse) VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (client.nom, client.prenom, client.telephone, client.email, client.adresse)
    )
    # Assigne l'id généré par la base de données à l'objet client
    client.id = cur.fetchone()[0]
    # Valide (commit) la transaction dans la base de données
    conn.commit(); cur.close(); conn.close()
    # Retourne l'objet client mis à jour avec son nouvel id
    return client

def update(client: Client):
    """
    Met à jour les informations d'un client existant.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Met à jour les champs du client correspondant à l'id
    cur.execute(
        "UPDATE clients SET nom=%s, prenom=%s, telephone=%s, email=%s, adresse=%s WHERE id=%s",
        (client.nom, client.prenom, client.telephone, client.email, client.adresse, client.id)
    )
    # Valide les modifications
    conn.commit(); cur.close(); conn.close()

def delete(client_id: int):
    """
    Supprime un client et toutes ses données associées (factures, ordres de réparation, véhicules).
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Supprimer dans l'ordre pour respecter les clés étrangères (Foreign Keys)
        # Supprime d'abord les factures du client
        cur.execute("""
            DELETE FROM factures WHERE client_id = %s;
            DELETE FROM ordres_reparation WHERE vehicule_id IN 
                (SELECT id FROM vehicules WHERE client_id = %s);
            DELETE FROM vehicules WHERE client_id = %s;
            DELETE FROM clients WHERE id = %s;
        """, (client_id, client_id, client_id, client_id))
        # Valide toutes les suppressions si aucune erreur ne s'est produite
        conn.commit()
    except Exception as e:
        # En cas d'erreur, annule toutes les modifications (rollback)
        conn.rollback()
        # Relève l'exception pour la gérer plus haut
        raise e
    finally:
        # S'assure que le curseur et la connexion sont fermés quoi qu'il arrive
        cur.close()
        conn.close()