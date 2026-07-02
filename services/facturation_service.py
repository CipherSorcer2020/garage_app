from repositories import facture_repo, or_repo, ligne_piece_repo, ligne_mo_repo
from models.facture import Facture

def generer_facture(or_id: int, client_id: int, tva: float = 20.0) -> Facture:
    """
    Generates a new invoice or updates an existing one for a given Work Order (OR).
    It totals up parts and labor prices, updates OR status, and persists changes.
    """
    # Check if an invoice has already been created for this Work Order
    existante = facture_repo.get_by_or(or_id)
    
    # Fetch all lines of parts and labor associated with this work order
    pieces = ligne_piece_repo.get_by_or(or_id)
    mos = ligne_mo_repo.get_by_or(or_id)

    # Calculate Total HT (excluding taxes) by summing parts and labor lines
    total_ht = round(
        sum(p.total_ht or 0 for p in pieces) +
        sum(m.total_ht or 0 for m in mos),
        2
    )
    # Calculate Total TTC (including TVA)
    montant_ttc = round(total_ht * (1 + tva / 100), 2)

    # If the invoice already exists, update its amounts and save
    if existante:
        existante.montant_ht = total_ht
        existante.tva = tva
        existante.montant_ttc = montant_ttc
        facture_repo.update(existante)
        # Ensure status of the Work Order is marked as invoiced
        or_repo.update_statut(or_id, 'facture')
        return existante

    # If it is a new invoice, generate a new unique invoice number
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
    # Update Work Order status to 'facture'
    or_repo.update_statut(or_id, 'facture')
    # Save the new invoice in the database
    return facture_repo.create(f)

def marquer_payee(facture_id: int, mode_paiement: str) -> Facture:
    """
    Marks an invoice as paid with a specific payment method (e.g. Cash, Card).
    """
    f = facture_repo.get_by_id(facture_id)
    if not f:
        raise ValueError(f"Facture #{facture_id} introuvable")
    
    # Update database record status and payment mode
    facture_repo.marquer_payee(facture_id, mode_paiement)
    f.statut = 'payee'
    f.mode_paiement = mode_paiement
    return f

def get_factures_impayees():
    """
    Retrieves all invoices that are currently unpaid.
    """
    return [f for f in facture_repo.get_all() if f.statut == 'non_payee']

def get_ca_total():
    """
    Calculates the Total Revenue (Chiffre d'Affaires) by summing all paid invoices.
    """
    factures = facture_repo.get_all()
    return round(sum((f.montant_ttc or 0) for f in factures if f.statut == 'payee'), 2)
