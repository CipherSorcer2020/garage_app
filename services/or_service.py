# Importation des gestionnaires de base de données (les "repositories")
from repositories import or_repo, diagnostic_repo, devis_repo, ligne_piece_repo, ligne_mo_repo
# Importation des modèles de données nécessaires
from models.ordre_reparation import OrdreReparation
from models.diagnostic import Diagnostic
from models.devis import Devis
from models.ligne_piece import LignePiece
from models.ligne_main_oeuvre import LigneMainOeuvre

# Liste des statuts possibles pour un Ordre de Réparation, dans l'ordre de leur déroulement
STATUTS = [
    'reception',               # Réception du véhicule
    'diagnostic',              # Diagnostic en cours ou terminé
    'devis',                   # Devis créé
    'accord_devis',            # Devis accepté par le client
    'affectation_mecanicien',  # Mécanicien affecté à la tâche
    'en_cours',                # Réparation en cours
    'test',                    # Phase de test du véhicule
    'facture',                 # Facture émise
    'livre'                    # Véhicule rendu au client
]

def statut_suivant(statut_actuel: str) -> str | None:
    """
    Détermine le statut qui vient juste après le statut actuel d'après la liste STATUTS.
    """
    # Vérifie si le statut actuel est bien dans notre liste
    if statut_actuel in STATUTS:
        # Trouve la position (l'index) du statut actuel dans la liste
        idx = STATUTS.index(statut_actuel)
        # S'il ne s'agit pas du tout dernier statut (livre)...
        if idx < len(STATUTS) - 1:
            # On retourne le statut suivant
            return STATUTS[idx + 1]
    # S'il n'y a pas de statut suivant (ou si le statut est inconnu), on ne retourne rien
    return None

def creer_or(vehicule_id: int, description: str = None) -> OrdreReparation:
    """
    Crée un nouvel Ordre de Réparation pour un véhicule donné.
    """
    # Crée un nouvel objet OrdreReparation avec le statut initial 'reception'
    o = OrdreReparation(vehicule_id=vehicule_id, statut='reception', description=description)
    # Le sauvegarde dans la base de données et le retourne
    return or_repo.create(o)

def avancer_statut(or_id: int) -> OrdreReparation:
    """
    Fait passer un Ordre de Réparation à son étape suivante (statut suivant).
    """
    # Récupère l'Ordre de Réparation par son identifiant
    o = or_repo.get_by_id(or_id)
    # Si l'OR n'existe pas, on lève une erreur
    if not o:
        raise ValueError(f"OR #{or_id} introuvable")
    
    # Trouve quel sera le prochain statut
    suivant = statut_suivant(o.statut)
    # Si on est déjà au statut final, on lève une erreur
    if not suivant:
        raise ValueError(f"L'OR est déjà au statut final : {o.statut}")
    
    # Met à jour le statut en base de données
    or_repo.update_statut(or_id, suivant)
    # Met à jour l'objet en mémoire
    o.statut = suivant
    # Retourne l'Ordre de Réparation mis à jour
    return o

def affecter_mecanicien(or_id: int, mecanicien_id: int) -> OrdreReparation:
    """
    Assigne un mécanicien à un Ordre de Réparation.
    """
    # Récupération de l'OR
    o = or_repo.get_by_id(or_id)
    if not o:
        raise ValueError(f"OR #{or_id} introuvable")
    
    # Met à jour l'identifiant du mécanicien associé
    o.mecanicien_id = mecanicien_id
    # Change le statut à 'affectation_mecanicien'
    o.statut = 'affectation_mecanicien'
    # Sauvegarde les modifications dans la base de données
    or_repo.update(o)
    return o

def ajouter_diagnostic(or_id: int, observations: str) -> Diagnostic:
    """
    Ajoute ou met à jour les observations de diagnostic pour un Ordre de Réparation.
    """
    # Récupération de l'OR
    o = or_repo.get_by_id(or_id)
    if not o:
        raise ValueError(f"OR #{or_id} introuvable")
    
    # Vérifie si un diagnostic existe déjà pour cet OR
    existant = diagnostic_repo.get_by_or(or_id)
    # S'il existe déjà...
    if existant:
        # Met à jour ses observations
        existant.observations = observations
        # Sauvegarde la mise à jour
        diagnostic_repo.update(existant)
        return existant
    
    # Si aucun diagnostic n'existait, on en crée un nouveau
    d = Diagnostic(or_id=or_id, observations=observations)
    # On met à jour le statut de l'OR à 'diagnostic'
    or_repo.update_statut(or_id, 'diagnostic')
    # On sauvegarde le nouveau diagnostic
    return diagnostic_repo.create(d)

def creer_devis(or_id: int, lignes_pieces: list, lignes_mo: list, tva: float = 20.0) -> Devis:
    """
    Crée ou met à jour un devis pour un Ordre de Réparation en ajoutant les pièces et la main-d'œuvre.
    """
    # Par précaution, on supprime les anciennes lignes de pièces et de main d'œuvre de cet OR
    ligne_piece_repo.delete_by_or(or_id)
    ligne_mo_repo.delete_by_or(or_id)

    total_pieces = 0.0
    # On boucle sur chaque ligne de pièce fournie
    for lp in lignes_pieces:
        # On crée un objet pièce
        piece = LignePiece(or_id=or_id, designation=lp['designation'],
                           reference=lp.get('reference'), quantite=lp.get('quantite', 1),
                           prix_unitaire_ht=lp.get('prix_unitaire_ht', 0))
        # On le sauvegarde en base
        ligne_piece_repo.create(piece)
        # On ajoute son total au total des pièces
        total_pieces += piece.total_ht or 0

    total_mo = 0.0
    # On boucle sur chaque ligne de main-d'œuvre fournie
    for lmo in lignes_mo:
        # On crée un objet main d'œuvre
        mo = LigneMainOeuvre(or_id=or_id, description=lmo['description'],
                             duree_heures=lmo.get('duree_heures', 0),
                             taux_horaire_ht=lmo.get('taux_horaire_ht', 0))
        # On le sauvegarde en base
        ligne_mo_repo.create(mo)
        # On ajoute son total au total de la main d'œuvre
        total_mo += mo.total_ht or 0

    # On calcule le montant total Hors Taxes (pièces + main d'œuvre)
    montant_ht = round(total_pieces + total_mo, 2)

    # On vérifie si un devis existe déjà pour cet OR
    existant = devis_repo.get_by_or(or_id)
    if existant:
        # On le met à jour avec les nouveaux montants
        existant.montant_ht = montant_ht
        existant.tva = tva
        # On le remet "en attente" d'être accepté
        existant.statut = 'en_attente'
        existant.accepte = False
        devis_repo.update(existant)
        # On s'assure que le statut de l'OR est "devis"
        or_repo.update_statut(or_id, 'devis')
        return existant

    # Sinon, on crée un nouveau devis
    d = Devis(or_id=or_id, montant_ht=montant_ht, tva=tva)
    # On met à jour le statut de l'OR à "devis"
    or_repo.update_statut(or_id, 'devis')
    return devis_repo.create(d)

def accepter_devis(or_id: int):
    """
    Marque le devis comme accepté par le client.
    """
    # Récupère le devis pour cet OR
    d = devis_repo.get_by_or(or_id)
    if not d:
        raise ValueError(f"Aucun devis pour OR #{or_id}")
    # Enregistre l'acceptation du devis en base de données
    devis_repo.accepter(d.id)
    # Met à jour le statut de l'OR à 'accord_devis'
    or_repo.update_statut(or_id, 'accord_devis')
    return d

def refuser_devis(or_id: int):
    """
    Marque le devis comme refusé par le client.
    """
    # Récupère le devis
    d = devis_repo.get_by_or(or_id)
    if not d:
        raise ValueError(f"Aucun devis pour OR #{or_id}")
    # Enregistre le refus du devis en base de données
    devis_repo.refuser(d.id)
    # Reviens au statut 'reception' ou au début du processus
    or_repo.update_statut(or_id, 'reception')
    return d

def cloturer_or(or_id: int):
    """
    Marque un Ordre de Réparation comme étant complètement terminé et livré.
    """
    # Change simplement le statut en 'livre'
    or_repo.update_statut(or_id, 'livre')

def get_or_complet(or_id: int) -> dict:
    """
    Récupère un Ordre de Réparation complet avec toutes ses informations associées 
    (diagnostic, devis, pièces, main-d'œuvre).
    """
    # Récupère les données principales de l'OR
    o = or_repo.get_by_id(or_id)
    if not o:
        raise ValueError(f"OR #{or_id} introuvable")
    # Construit et retourne un dictionnaire (dict) avec tous les détails
    return {
        'or': o,                                     # Les infos de base de l'OR
        'diagnostic': diagnostic_repo.get_by_or(or_id), # Son diagnostic
        'devis': devis_repo.get_by_or(or_id),           # Son devis
        'pieces': ligne_piece_repo.get_by_or(or_id),    # Les pièces nécessaires
        'main_oeuvre': ligne_mo_repo.get_by_or(or_id),  # Les heures de main-d'œuvre
    }
