# -*- coding: utf-8 -*-
# Représentation du modèle de données de la table Devis

from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Devis:
    """
    Modèle de données représentant un Devis dans l'application.
    Cette classe est une simple "dataclass" Python qui contient les propriétés d'un Devis.
    """

    # L'identifiant de l'ordre de réparation associé (champ obligatoire)
    or_id: int
    
    # Le montant hors taxes du devis (optionnel)
    montant_ht: Optional[float] = None
    
    # Le taux de TVA applicable, par défaut 20.00%
    tva: float = 20.00
    
    # L'état actuel du devis, par défaut 'en_attente'
    statut: str = 'en_attente'
    
    # La date de création du devis (optionnel)
    date_creation: Optional[date] = None
    
    # Un indicateur booléen pour savoir si le devis a été accepté par le client
    accepte: bool = False
    
    # L'identifiant unique du devis dans la base de données (optionnel)
    id: Optional[int] = None

    @property
    def montant_ttc(self) -> Optional[float]:
        """
        Calcule et retourne le montant toutes taxes comprises (TTC) du devis.
        Si le montant HT n'est pas défini, retourne None.
        """
        if self.montant_ht is None:
            return None
        # Calcule le TTC et arrondit le résultat à 2 décimales
        return round(self.montant_ht * (1 + self.tva / 100), 2)
