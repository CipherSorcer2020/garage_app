# -*- coding: utf-8 -*-
# Repository (couche d'acces aux donnees) pour les Techniciens.
# Execute des requetes SQL et mappe les resultats au modele Technicien.

from typing import List, Optional
from config.database import get_db
from models.technicien import Technicien


def _row_to_technicien(row) -> Technicien:
    """Convertit une ligne SQL en objet Technicien."""
    return Technicien(
        id=row[0],
        nom=row[1],
        prenom=row[2],
        qualification=row[3],
        telephone=row[4],
        cout_horaire=float(row[5]) if row[5] is not None else 0.0,
    )


def get_all() -> List[Technicien]:
    """Retourne tous les techniciens, tries par nom."""
    with get_db() as (cur, _):
        cur.execute(
            "SELECT id, nom, prenom, qualification, telephone, cout_horaire FROM techniciens ORDER BY nom, prenom"
        )
        rows = cur.fetchall()
    return [_row_to_technicien(r) for r in rows]


def get_by_id(tech_id: int) -> Optional[Technicien]:
    """Retourne un technicien par son identifiant, ou None s'il n'existe pas."""
    with get_db() as (cur, _):
        cur.execute(
            "SELECT id, nom, prenom, qualification, telephone, cout_horaire FROM techniciens WHERE id=%s",
            (tech_id,),
        )
        row = cur.fetchone()
    return _row_to_technicien(row) if row else None


def get_by_vehicule(vehicule_id: int) -> Optional[Technicien]:
    """Retourne le technicien responsable d'un vehicule donne, ou None."""
    with get_db() as (cur, _):
        cur.execute(
            """SELECT t.id, t.nom, t.prenom, t.qualification, t.telephone, t.cout_horaire
               FROM techniciens t
               JOIN vehicules v ON v.technicien_id = t.id
               WHERE v.id = %s""",
            (vehicule_id,),
        )
        row = cur.fetchone()
    return _row_to_technicien(row) if row else None


def create(tech: Technicien) -> Technicien:
    """Insere un nouveau technicien en base et retourne l'objet avec son ID."""
    with get_db() as (cur, _):
        cur.execute(
            "INSERT INTO techniciens (nom, prenom, qualification, telephone, cout_horaire) VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (tech.nom, tech.prenom, tech.qualification, tech.telephone, tech.cout_horaire),
        )
        tech.id = cur.fetchone()[0]
    return tech


def update(tech: Technicien) -> None:
    """Met a jour les informations d'un technicien existant."""
    with get_db() as (cur, _):
        cur.execute(
            "UPDATE techniciens SET nom=%s, prenom=%s, qualification=%s, telephone=%s, cout_horaire=%s WHERE id=%s",
            (tech.nom, tech.prenom, tech.qualification, tech.telephone, tech.cout_horaire, tech.id),
        )


def delete(tech_id: int) -> None:
    """Supprime un technicien de la base de donnees."""
    with get_db() as (cur, _):
        cur.execute("DELETE FROM techniciens WHERE id=%s", (tech_id,))


def affecter_vehicule(vehicule_id: int, technicien_id: Optional[int]) -> None:
    """Affecte (ou desaffecte si None) un technicien a un vehicule."""
    with get_db() as (cur, _):
        cur.execute(
            "UPDATE vehicules SET technicien_id=%s WHERE id=%s",
            (technicien_id, vehicule_id),
        )
