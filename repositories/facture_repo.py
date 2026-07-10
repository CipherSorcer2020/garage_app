# -*- coding: utf-8 -*-
# Repository Data Access Layer for facture_repo
# Exécute des requêtes SQL brutes et mappe les lignes de résultat aux modèles de données.

# Importation pour la connexion DB et le modèle Facture
from config.database import get_connection, get_db
from models.facture import Facture

def _row(r):
    """
    Convertit une ligne issue de la base de données en un objet Facture.
    """
    # Mappe chaque colonne au constructeur du modèle Facture (les montants sont convertis en float s'ils existent)
    return Facture(id=r[0], or_id=r[1], client_id=r[2], numero=r[3], montant_ht=float(r[4]) if r[4] else None,
                   tva=float(r[5]), montant_ttc=float(r[6]) if r[6] else None, statut=r[7], date_emission=r[8], mode_paiement=r[9])

def get_all():
    """
    Récupère toutes les factures, triées par date d'émission de la plus récente à la plus ancienne.
    """
    with get_db() as (cur, conn):
        # Requête de sélection complète sur les factures, avec un tri DESC sur la date
        cur.execute("SELECT id, or_id, client_id, numero, montant_ht, tva, montant_ttc, statut, date_emission, mode_paiement FROM factures ORDER BY date_emission DESC")
        rows = cur.fetchall()
    # Transforme chaque ligne récupérée en objet Facture
    return [_row(r) for r in rows]

def get_by_id(facture_id: int):
    """
    Récupère une facture spécifique via son ID.
    """
    with get_db() as (cur, conn):
        # Requête filtrée par ID
        cur.execute("SELECT id, or_id, client_id, numero, montant_ht, tva, montant_ttc, statut, date_emission, mode_paiement FROM factures WHERE id=%s", (facture_id,))
        r = cur.fetchone()
    # Retourne l'objet ou None
    return _row(r) if r else None

def get_by_or(or_id: int):
    """
    Récupère la facture associée à un Ordre de Réparation spécifique.
    """
    with get_db() as (cur, conn):
        # Requête filtrée par or_id
        cur.execute("SELECT id, or_id, client_id, numero, montant_ht, tva, montant_ttc, statut, date_emission, mode_paiement FROM factures WHERE or_id=%s", (or_id,))
        r = cur.fetchone()
    return _row(r) if r else None

def get_by_client(client_id: int):
    """
    Récupère toutes les factures d'un client spécifique.
    """
    with get_db() as (cur, conn):
        # Requête filtrée par client_id
        cur.execute("SELECT id, or_id, client_id, numero, montant_ht, tva, montant_ttc, statut, date_emission, mode_paiement FROM factures WHERE client_id=%s ORDER BY date_emission DESC", (client_id,))
        rows = cur.fetchall()
    # Retourne une liste de factures pour le client donné
    return [_row(r) for r in rows]

def generate_numero():
    """
    Génère un numéro de facture unique (ex: F-2023-0001).
    """
    from datetime import date
    with get_db() as (cur, conn):
        # Récupère l'année courante
        year = date.today().year
        # Compte le nombre de factures émises cette année
        cur.execute("SELECT COUNT(*) FROM factures WHERE EXTRACT(YEAR FROM date_emission)=%s", (year,))
        count = cur.fetchone()[0]
    # Formate le numéro: 'F' suivi de l'année et du compteur incrémenté sur 4 chiffres
    return f"F-{year}-{str(count + 1).zfill(4)}"

def create(f: Facture):
    """
    Crée une nouvelle facture en base de données.
    """
    with get_db() as (cur, conn):
        # Insère les détails de la facture et retourne l'id
        cur.execute(
            "INSERT INTO factures (or_id, client_id, numero, montant_ht, tva, montant_ttc, statut, date_emission, mode_paiement) VALUES (%s,%s,%s,%s,%s,%s,%s,CURRENT_DATE,%s) RETURNING id",
            (f.or_id, f.client_id, f.numero, f.montant_ht, f.tva, f.montant_ttc, f.statut, f.mode_paiement)
        )
        # Met à jour l'objet facture avec son nouvel ID
        f.id = cur.fetchone()[0]
    return f

def marquer_payee(facture_id: int, mode_paiement: str):
    """
    Met à jour le statut d'une facture à 'payee' avec le mode de paiement utilisé.
    """
    with get_db() as (cur, conn):
        # Exécute la mise à jour
        cur.execute("UPDATE factures SET statut='payee', mode_paiement=%s WHERE id=%s", (mode_paiement, facture_id))

def update(f: Facture):
    """
    Met à jour les montants et le statut d'une facture existante.
    """
    with get_db() as (cur, conn):
        # Modifie plusieurs champs d'une facture spécifique
        cur.execute(
            "UPDATE factures SET montant_ht=%s, tva=%s, montant_ttc=%s, statut=%s, mode_paiement=%s WHERE id=%s",
            (f.montant_ht, f.tva, f.montant_ttc, f.statut, f.mode_paiement, f.id)
        )
