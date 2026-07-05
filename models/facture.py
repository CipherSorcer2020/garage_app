# -*- coding: utf-8 -*-
# Représentation du modèle de données de la table Facture

from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Facture:
    """
    Modèle de données représentant une Facture dans l'application.
    Cette classe est une simple "dataclass" Python qui contient les propriétés d'une Facture.
    """

    # L'identifiant de l'ordre de réparation associé
    or_id: int
    
    # L'identifiant du client associé
    client_id: int
    
    # Le numéro de facture (généralement une chaîne formatée, ex: FAC-2023-001)
    numero: str
    
    # Le montant hors taxes de la facture (optionnel)
    montant_ht: Optional[float] = None
    
    # Le taux de TVA applicable, par défaut 20.00%
    tva: float = 20.00
    
    # Le montant toutes taxes comprises de la facture (optionnel)
    montant_ttc: Optional[float] = None
    
    # Le statut actuel de la facture, par défaut 'non_payee'
    statut: str = 'non_payee'
    
    # La date d'émission de la facture (optionnel)
    date_emission: Optional[date] = None
    
    # Le mode de paiement utilisé par le client (optionnel)
    mode_paiement: Optional[str] = None
    
    # L'identifiant unique de la facture dans la base de données (optionnel)
    id: Optional[int] = None

