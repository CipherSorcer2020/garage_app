# -*- coding: utf-8 -*-
# Représentation du modèle de données de la table Vehicule

from dataclasses import dataclass
from typing import Optional

@dataclass
class Vehicule:
    """
    Modèle de données représentant un Vehicule dans l'application.
    Cette classe est une simple "dataclass" Python qui contient les propriétés d'un Vehicule.
    """

    # L'immatriculation du véhicule
    immatriculation: str
    
    # L'identifiant du client propriétaire du véhicule
    client_id: int
    
    # Le numéro de châssis (VIN) du véhicule (optionnel)
    vin: Optional[str] = None
    
    # La marque du véhicule (optionnelle)
    marque: Optional[str] = None
    
    # Le modèle du véhicule (optionnel)
    modele: Optional[str] = None
    
    # L'année de fabrication du véhicule (optionnelle)
    annee: Optional[int] = None
    
    # Le kilométrage du véhicule (optionnel)
    kilometrage: Optional[int] = None

    # L'identifiant unique du technicien responsable du vehicule (optionnel)
    technicien_id: Optional[int] = None

    # L'identifiant unique du véhicule dans la base de données (optionnel)
    id: Optional[int] = None

