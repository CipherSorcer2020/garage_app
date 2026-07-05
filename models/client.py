# -*- coding: utf-8 -*-
# Représentation du modèle de données de la table Client

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Client:
    """
    Modèle de données représentant un Client dans l'application.
    Cette classe est une simple "dataclass" Python qui contient les propriétés d'un Client.
    """

    # Le nom du client (champ obligatoire)
    nom: str
    
    # Le prénom du client (optionnel, peut être None)
    prenom: Optional[str] = None
    
    # Le numéro de téléphone du client (optionnel)
    telephone: Optional[str] = None
    
    # L'adresse email du client (optionnel)
    email: Optional[str] = None
    
    # L'adresse postale du client (optionnel)
    adresse: Optional[str] = None
    
    # L'identifiant unique du client dans la base de données (optionnel lors de la création)
    id: Optional[int] = None
    
    # La date de création du dossier client (optionnel)
    date_creation: Optional[datetime] = None