# -*- coding: utf-8 -*-
# Repository Data Access Layer for vehicule_repo
# Exécute des requêtes SQL brutes et mappe les lignes de résultat aux modèles de données.

from config.database import get_connection, get_db
from models.vehicule import Vehicule

def _row_to_vehicule(r):
    """
    Transforme une ligne de résultat SQL en un objet Vehicule.
    """
    # Initialise un Vehicule avec toutes ses caractéristiques (immatriculation, VIN, modèle, etc.)
    return Vehicule(id=r[0], client_id=r[1], immatriculation=r[2], vin=r[3], marque=r[4], modele=r[5], annee=r[6], kilometrage=r[7])

def get_all():
    """
    Récupère tous les véhicules enregistrés, triés par immatriculation.
    """
    with get_db() as (cur, conn):
        # Récupération de tous les véhicules
        cur.execute("SELECT id, client_id, immatriculation, vin, marque, modele, annee, kilometrage FROM vehicules ORDER BY immatriculation")
        rows = cur.fetchall()
    # Construit la liste d'objets Vehicule
    return [_row_to_vehicule(r) for r in rows]

def get_by_id(vehicule_id: int):
    """
    Récupère un véhicule via son identifiant (ID).
    """
    with get_db() as (cur, conn):
        # Recherche du véhicule par ID
        cur.execute("SELECT id, client_id, immatriculation, vin, marque, modele, annee, kilometrage FROM vehicules WHERE id=%s", (vehicule_id,))
        r = cur.fetchone()
    # Retourne le véhicule ou None s'il n'existe pas
    return _row_to_vehicule(r) if r else None

def get_by_client(client_id: int):
    """
    Récupère la liste des véhicules appartenant à un client spécifique.
    """
    with get_db() as (cur, conn):
        # Filtre les véhicules par l'identifiant du client
        cur.execute("SELECT id, client_id, immatriculation, vin, marque, modele, annee, kilometrage FROM vehicules WHERE client_id=%s", (client_id,))
        rows = cur.fetchall()
    # Renvoie la flotte de véhicules du client
    return [_row_to_vehicule(r) for r in rows]

def create(v: Vehicule):
    """
    Ajoute un nouveau véhicule dans la base de données.
    """
    with get_db() as (cur, conn):
        # Insère le véhicule et renvoie l'ID généré
        cur.execute(
            "INSERT INTO vehicules (client_id, immatriculation, vin, marque, modele, annee, kilometrage) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (v.client_id, v.immatriculation, v.vin, v.marque, v.modele, v.annee, v.kilometrage)
        )
        # Affecte le nouvel ID à l'objet
        v.id = cur.fetchone()[0]
    return v

def update(v: Vehicule):
    """
    Met à jour les informations d'un véhicule existant (kilométrage, etc.).
    """
    with get_db() as (cur, conn):
        # Effectue un UPDATE sur tous les champs du véhicule correspondant à l'ID
        cur.execute(
            "UPDATE vehicules SET client_id=%s, immatriculation=%s, vin=%s, marque=%s, modele=%s, annee=%s, kilometrage=%s WHERE id=%s",
            (v.client_id, v.immatriculation, v.vin, v.marque, v.modele, v.annee, v.kilometrage, v.id)
        )

def delete(vehicule_id: int):
    """
    Supprime un véhicule de la base de données.
    """
    with get_db() as (cur, conn):
        # Supprime la ligne correspondant à l'ID
        cur.execute("DELETE FROM vehicules WHERE id=%s", (vehicule_id,))
