# -*- coding: utf-8 -*-
# Représentation du modèle de données de la table Utilisateur

from dataclasses import dataclass
from typing import Optional

@dataclass
class Utilisateur:
    """
    Modèle de données représentant un Utilisateur dans l'application.
    Cette classe est une simple "dataclass" Python qui contient les propriétés d'un Utilisateur.
    """

    # Le nom de l'utilisateur
    nom: str
    
    # Le prénom de l'utilisateur
    prenom: str
    
    # L'identifiant de connexion de l'utilisateur
    login: str
    
    # Le mot de passe de l'utilisateur (généralement stocké de façon sécurisée)
    mot_de_passe: str
    
    # Le rôle de l'utilisateur dans l'application, par défaut 'user'
    role: str = 'user'
    
    # L'identifiant unique de l'utilisateur (optionnel)
    id: Optional[int] = None

