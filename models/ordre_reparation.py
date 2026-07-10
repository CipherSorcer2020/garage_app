# -*- coding: utf-8 -*-
# Représentation du modèle de données de la table Ordre_reparation

from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class OrdreReparation:
    """
    Modèle de données représentant un Ordre_reparation dans l'application.
    Cette classe est une simple "dataclass" Python qui contient les propriétés d'un ordre de réparation.
    """

    # L'identifiant du véhicule associé
    vehicule_id: int
    
    # Le statut actuel de l'ordre de réparation, par défaut 'reception'
    statut: str = 'reception'
    
    # L'identifiant du mécanicien assigné (optionnel)
    mecanicien_id: Optional[int] = None
    
    # La date d'entrée du véhicule à l'atelier (optionnelle)
    date_entree: Optional[date] = None
    
    # La date de sortie du véhicule de l'atelier (optionnelle)
    date_sortie: Optional[date] = None
    
    # Une description du problème ou des travaux à effectuer (optionnelle)
    description: Optional[str] = None
    
    # Le kilométrage du véhicule à la réception (optionnel)
    kilometrage: Optional[int] = None
    
    # Le niveau de carburant à la réception (optionnel)
    niveau_carburant: Optional[str] = None
    
    # L'identifiant unique de l'ordre de réparation (optionnel)
    id: Optional[int] = None

