# -*- coding: utf-8 -*-
# Représentation du modèle de données de la table Ligne_piece

from dataclasses import dataclass
from typing import Optional

@dataclass
class LignePiece:
    """
    Modèle de données représentant une Ligne_piece dans l'application.
    Cette classe est une simple "dataclass" Python qui contient les propriétés d'une ligne de pièce.
    """

    # L'identifiant de l'ordre de réparation associé
    or_id: int
    
    # Le nom ou la désignation de la pièce
    designation: str
    
    # La quantité de pièces utilisées, par défaut 1
    quantite: int = 1
    
    # La référence de la pièce (optionnelle)
    reference: Optional[str] = None
    
    # Le prix unitaire hors taxes de la pièce (optionnel)
    prix_unitaire_ht: Optional[float] = None
    
    # L'identifiant unique de la ligne de pièce (optionnel)
    id: Optional[int] = None

    @property
    def total_ht(self) -> Optional[float]:
        """
        Calcule et retourne le coût total hors taxes pour cette ligne de pièce.
        Si le prix unitaire est manquant, retourne None.
        """
        if self.prix_unitaire_ht is None:
            return None
        # Calcule le total en multipliant la quantité par le prix unitaire, et arrondit à 2 décimales
        return round(self.quantite * self.prix_unitaire_ht, 2)
