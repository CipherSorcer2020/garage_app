# -*- coding: utf-8 -*-
# Modele de donnees representant un Technicien dans l'application.

from dataclasses import dataclass
from typing import Optional

@dataclass
class Technicien:
    """Un technicien peut etre responsable de plusieurs vehicules,
    mais chaque vehicule n'a qu'un seul technicien responsable.
    """
    # Identifiant unique du technicien (genere par la base de donnees)
    id: Optional[int] = None
    # Nom de famille du technicien
    nom: str = ''
    # Prenom du technicien
    prenom: str = ''
    # Qualification / specialite du technicien (ex: Electricien, Mecanicien)
    qualification: str = ''
    # Numero de telephone du technicien
    telephone: str = ''
    # Cout horaire du technicien
    cout_horaire: float = 0.0

    @property
    def nom_complet(self) -> str:
        """Retourne le nom complet (prenom + nom) du technicien."""
        return f"{self.prenom} {self.nom}".strip()
