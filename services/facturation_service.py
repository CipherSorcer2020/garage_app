from repositories import facture_repo, or_repo, ligne_piece_repo, ligne_mo_repo
from models.facture import Facture

def generer_facture(or_id: int, client_id: int, tva: float = 20.0) -> Facture:
    existante = facture_repo.get_by_or(or_id)
    
    pieces = ligne_piece_repo.get_by_or(or_id)
    mos = ligne_mo_repo.get_by_or(or_id)

    total_ht = round(
        sum(p.total_ht or 0 for p in pieces) +
        sum(m.total_ht or 0 for m in mos),
        2
    )
    montant_ttc = round(total_ht * (1 + tva / 100), 2)

    if existante:
        existante.montant_ht = total_ht
        existante.tva = tva
        existante.montant_ttc = montant_ttc
        facture_repo.update(existante)
        or_repo.update_statut(or_id, 'facture')
        return existante

    numero = facture_repo.generate_numero()
    f = Facture(
        or_id=or_id,
        client_id=client_id,
        numero=numero,
        montant_ht=total_ht,
        tva=tva,
        montant_ttc=montant_ttc,
        statut='non_payee'
    )
    or_repo.update_statut(or_id, 'facture')
    return facture_repo.create(f)

def marquer_payee(facture_id: int, mode_paiement: str) -> Facture:
    f = facture_repo.get_by_id(facture_id)
    if not f:
        raise ValueError(f"Facture #{facture_id} introuvable")
    facture_repo.marquer_payee(facture_id, mode_paiement)
    f.statut = 'payee'
    f.mode_paiement = mode_paiement
    return f

def get_factures_impayees():
    return [f for f in facture_repo.get_all() if f.statut == 'non_payee']

def get_ca_total():
    factures = facture_repo.get_all()
    return round(sum((f.montant_ttc or 0) for f in factures if f.statut == 'payee'), 2)
