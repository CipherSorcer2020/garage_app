# -*- coding: utf-8 -*-
# Repository Data Access Layer for diagnostic_repo
# Exécute des requêtes SQL brutes et mappe les lignes de résultat aux modèles de données.

# Importation de la fonction pour se connecter à la base de données
from config.database import get_connection
# Importation du modèle Diagnostic
from models.diagnostic import Diagnostic

def get_by_or(or_id: int):
    """
    Récupère le diagnostic lié à un Ordre de Réparation (OR) spécifique.
    """
    # Ouvre la connexion et crée le curseur
    conn = get_connection()
    cur = conn.cursor()
    # Recherche le diagnostic par or_id
    cur.execute("SELECT id, or_id, observations, date_diagnostic FROM diagnostics WHERE or_id=%s", (or_id,))
    # Récupère le résultat (un seul diagnostic attendu par OR)
    r = cur.fetchone()
    # Ferme les ressources
    cur.close(); conn.close()
    # Si un résultat est trouvé, retourne l'objet Diagnostic, sinon None
    return Diagnostic(id=r[0], or_id=r[1], observations=r[2], date_diagnostic=r[3]) if r else None

def create(d: Diagnostic):
    """
    Insère un nouveau diagnostic dans la base de données.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Insère les observations et l'ID de l'OR, avec la date courante (CURRENT_DATE)
    cur.execute(
        "INSERT INTO diagnostics (or_id, observations, date_diagnostic) VALUES (%s,%s,CURRENT_DATE) RETURNING id",
        (d.or_id, d.observations)
    )
    # Récupère et assigne l'ID nouvellement créé à l'objet
    d.id = cur.fetchone()[0]
    # Sauvegarde et ferme
    conn.commit(); cur.close(); conn.close()
    # Retourne l'objet avec son ID
    return d

def update(d: Diagnostic):
    """
    Met à jour les observations d'un diagnostic existant.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Modifie le champ observations pour le diagnostic spécifié par son ID
    cur.execute("UPDATE diagnostics SET observations=%s WHERE id=%s", (d.observations, d.id))
    # Valide les changements et ferme la connexion
    conn.commit(); cur.close(); conn.close()