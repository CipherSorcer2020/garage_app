# -*- coding: utf-8 -*-
# Représentation du modèle de données de la table Diagnostic

from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Diagnostic:
    """
    Modèle de données représentant un Diagnostic dans l'application.
    Cette classe est une simple "dataclass" Python qui contient les propriétés d'un Diagnostic.
    """

    # L'identifiant de l'ordre de réparation associé (champ obligatoire)
    or_id: int
    
    # Les observations faites lors du diagnostic (optionnel)
    observations: Optional[str] = None
    
    # La date à laquelle le diagnostic a été réalisé (optionnel)
    date_diagnostic: Optional[date] = None
    
    # L'identifiant unique du diagnostic dans la base de données (optionnel)
    id: Optional[int] = None
