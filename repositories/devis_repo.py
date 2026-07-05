# -*- coding: utf-8 -*-
# Repository Data Access Layer for devis_repo
# Exécute des requêtes SQL brutes et mappe les lignes de résultat aux modèles de données.

# Importation de la fonction de connexion à la base de données
from config.database import get_connection
# Importation du modèle Devis
from models.devis import Devis

def _row_to_devis(r):
    """
    Fonction utilitaire pour convertir une ligne de résultat SQL en un objet Devis.
    """
    # Instancie et retourne un objet Devis avec les données de la ligne 'r'
    return Devis(id=r[0], or_id=r[1], montant_ht=float(r[2]) if r[2] else None, tva=float(r[3]), statut=r[4], date_creation=r[5], accepte=r[6])

def get_by_or(or_id: int):
    """
    Récupère un devis associé à un Ordre de Réparation (OR) spécifique.
    """
    # Établit la connexion à la base
    conn = get_connection()
    cur = conn.cursor()
    # Exécute la requête pour chercher un devis correspondant à l'ID de l'OR
    cur.execute("SELECT id, or_id, montant_ht, tva, statut, date_creation, accepte FROM devis WHERE or_id=%s", (or_id,))
    # Récupère la première ligne correspondante
    r = cur.fetchone()
    # Ferme la connexion
    cur.close(); conn.close()
    # Retourne un objet Devis si trouvé, sinon retourne None
    return _row_to_devis(r) if r else None

def create(d: Devis):
    """
    Crée un nouveau devis dans la base de données.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Insère les données du devis et retourne le nouvel identifiant généré
    cur.execute(
        "INSERT INTO devis (or_id, montant_ht, tva, statut, date_creation, accepte) VALUES (%s,%s,%s,%s,CURRENT_DATE,%s) RETURNING id",
        (d.or_id, d.montant_ht, d.tva, d.statut, d.accepte)
    )
    # Assigne le nouvel ID à l'objet Devis
    d.id = cur.fetchone()[0]
    # Enregistre les modifications en base
    conn.commit(); cur.close(); conn.close()
    # Retourne l'objet avec son ID
    return d

def update(d: Devis):
    """
    Met à jour un devis existant dans la base de données.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Met à jour les champs de montant, TVA, statut et acceptation pour l'ID donné
    cur.execute(
        "UPDATE devis SET montant_ht=%s, tva=%s, statut=%s, accepte=%s WHERE id=%s",
        (d.montant_ht, d.tva, d.statut, d.accepte, d.id)
    )
    # Valide la mise à jour
    conn.commit(); cur.close(); conn.close()

def accepter(devis_id: int):
    """
    Marque un devis comme accepté.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Change le statut à 'accepte' et le booléen accepte à TRUE
    cur.execute("UPDATE devis SET accepte=TRUE, statut='accepte' WHERE id=%s", (devis_id,))
    # Valide la transaction
    conn.commit(); cur.close(); conn.close()

def refuser(devis_id: int):
    """
    Marque un devis comme refusé.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Change le statut à 'refuse' et le booléen accepte à FALSE
    cur.execute("UPDATE devis SET accepte=FALSE, statut='refuse' WHERE id=%s", (devis_id,))
    # Valide la transaction
    conn.commit(); cur.close(); conn.close()