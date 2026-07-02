from repositories import or_repo, diagnostic_repo, devis_repo, ligne_piece_repo, ligne_mo_repo
from models.ordre_reparation import OrdreReparation
from models.diagnostic import Diagnostic
from models.devis import Devis
from models.ligne_piece import LignePiece
from models.ligne_main_oeuvre import LigneMainOeuvre

STATUTS = [
    'reception',
    'diagnostic',
    'devis',
    'accord_devis',
    'affectation_mecanicien',
    'en_cours',
    'test',
    'facture',
    'livre'
]

def statut_suivant(statut_actuel: str) -> str | None:
    if statut_actuel in STATUTS:
        idx = STATUTS.index(statut_actuel)
        if idx < len(STATUTS) - 1:
            return STATUTS[idx + 1]
    return None

def creer_or(vehicule_id: int, description: str = None) -> OrdreReparation:
    o = OrdreReparation(vehicule_id=vehicule_id, statut='reception', description=description)
    return or_repo.create(o)

def avancer_statut(or_id: int) -> OrdreReparation:
    o = or_repo.get_by_id(or_id)
    if not o:
        raise ValueError(f"OR #{or_id} introuvable")
    suivant = statut_suivant(o.statut)
    if not suivant:
        raise ValueError(f"L'OR est déjà au statut final : {o.statut}")
    or_repo.update_statut(or_id, suivant)
    o.statut = suivant
    return o

def affecter_mecanicien(or_id: int, mecanicien_id: int) -> OrdreReparation:
    o = or_repo.get_by_id(or_id)
    if not o:
        raise ValueError(f"OR #{or_id} introuvable")
    o.mecanicien_id = mecanicien_id
    o.statut = 'affectation_mecanicien'
    or_repo.update(o)
    return o

def ajouter_diagnostic(or_id: int, observations: str) -> Diagnostic:
    o = or_repo.get_by_id(or_id)
    if not o:
        raise ValueError(f"OR #{or_id} introuvable")
    existant = diagnostic_repo.get_by_or(or_id)
    if existant:
        existant.observations = observations
        diagnostic_repo.update(existant)
        return existant
    d = Diagnostic(or_id=or_id, observations=observations)
    or_repo.update_statut(or_id, 'diagnostic')
    return diagnostic_repo.create(d)

def creer_devis(or_id: int, lignes_pieces: list, lignes_mo: list, tva: float = 20.0) -> Devis:
    ligne_piece_repo.delete_by_or(or_id)
    ligne_mo_repo.delete_by_or(or_id)

    total_pieces = 0.0
    for lp in lignes_pieces:
        piece = LignePiece(or_id=or_id, designation=lp['designation'],
                           reference=lp.get('reference'), quantite=lp.get('quantite', 1),
                           prix_unitaire_ht=lp.get('prix_unitaire_ht', 0))
        ligne_piece_repo.create(piece)
        total_pieces += piece.total_ht or 0

    total_mo = 0.0
    for lmo in lignes_mo:
        mo = LigneMainOeuvre(or_id=or_id, description=lmo['description'],
                             duree_heures=lmo.get('duree_heures', 0),
                             taux_horaire_ht=lmo.get('taux_horaire_ht', 0))
        ligne_mo_repo.create(mo)
        total_mo += mo.total_ht or 0

    montant_ht = round(total_pieces + total_mo, 2)

    existant = devis_repo.get_by_or(or_id)
    if existant:
        existant.montant_ht = montant_ht
        existant.tva = tva
        existant.statut = 'en_attente'
        existant.accepte = False
        devis_repo.update(existant)
        or_repo.update_statut(or_id, 'devis')
        return existant

    d = Devis(or_id=or_id, montant_ht=montant_ht, tva=tva)
    or_repo.update_statut(or_id, 'devis')
    return devis_repo.create(d)

def accepter_devis(or_id: int):
    d = devis_repo.get_by_or(or_id)
    if not d:
        raise ValueError(f"Aucun devis pour OR #{or_id}")
    devis_repo.accepter(d.id)
    or_repo.update_statut(or_id, 'accord_devis')
    return d

def refuser_devis(or_id: int):
    d = devis_repo.get_by_or(or_id)
    if not d:
        raise ValueError(f"Aucun devis pour OR #{or_id}")
    devis_repo.refuser(d.id)
    or_repo.update_statut(or_id, 'reception')
    return d

def cloturer_or(or_id: int):
    or_repo.update_statut(or_id, 'livre')

def get_or_complet(or_id: int) -> dict:
    o = or_repo.get_by_id(or_id)
    if not o:
        raise ValueError(f"OR #{or_id} introuvable")
    return {
        'or': o,
        'diagnostic': diagnostic_repo.get_by_or(or_id),
        'devis': devis_repo.get_by_or(or_id),
        'pieces': ligne_piece_repo.get_by_or(or_id),
        'main_oeuvre': ligne_mo_repo.get_by_or(or_id),
    }
