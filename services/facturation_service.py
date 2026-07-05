# Importation des modules nécessaires pour interagir avec la base de données (les "repositories")
from repositories import facture_repo, or_repo, ligne_piece_repo, ligne_mo_repo
# Importation du modèle de données Facture
from models.facture import Facture

def generer_facture(or_id: int, client_id: int, tva: float = 20.0) -> Facture:
    """
    Génère une nouvelle facture ou met à jour une facture existante pour un Ordre de Réparation (OR) donné.
    Elle fait la somme des pièces et de la main-d'œuvre, met à jour le statut de l'OR et sauvegarde les modifications.
    """
    # Vérifie si une facture a déjà été créée pour cet Ordre de Réparation
    existante = facture_repo.get_by_or(or_id)
    
    # Récupère toutes les lignes de pièces associées à cet Ordre de Réparation
    pieces = ligne_piece_repo.get_by_or(or_id)
    # Récupère toutes les lignes de main-d'œuvre (MO) associées à cet Ordre de Réparation
    mos = ligne_mo_repo.get_by_or(or_id)

    # Calcule le Total HT (Hors Taxes) en additionnant le total de chaque pièce et de chaque main-d'œuvre
    total_ht = round(
        sum(p.total_ht or 0 for p in pieces) + # Somme des pièces
        sum(m.total_ht or 0 for m in mos),     # Somme de la main-d'œuvre
        2 # Arrondi à 2 décimales
    )
    # Calcule le Total TTC (Toutes Taxes Comprises) en appliquant le taux de TVA
    montant_ttc = round(total_ht * (1 + tva / 100), 2)

    # Si la facture existe déjà, on met à jour ses montants et on la sauvegarde
    if existante:
        # Mise à jour du montant HT
        existante.montant_ht = total_ht
        # Mise à jour du taux de TVA
        existante.tva = tva
        # Mise à jour du montant TTC
        existante.montant_ttc = montant_ttc
        # Sauvegarde des modifications dans la base de données
        facture_repo.update(existante)
        # S'assure que le statut de l'Ordre de Réparation est bien marqué comme "facturé"
        or_repo.update_statut(or_id, 'facture')
        # Retourne la facture mise à jour
        return existante

    # Si c'est une nouvelle facture, on génère un nouveau numéro unique
    numero = facture_repo.generate_numero()
    # On crée un nouvel objet Facture avec les informations calculées
    f = Facture(
        or_id=or_id,                # L'identifiant de l'Ordre de Réparation
        client_id=client_id,        # L'identifiant du client
        numero=numero,              # Le numéro généré
        montant_ht=total_ht,        # Le montant Hors Taxes
        tva=tva,                    # Le taux de TVA
        montant_ttc=montant_ttc,    # Le montant Toutes Taxes Comprises
        statut='non_payee'          # Le statut initial est "non payée"
    )
    # On met à jour le statut de l'Ordre de Réparation à "facturé"
    or_repo.update_statut(or_id, 'facture')
    # On sauvegarde la nouvelle facture dans la base de données et on la retourne
    return facture_repo.create(f)

def marquer_payee(facture_id: int, mode_paiement: str) -> Facture:
    """
    Marque une facture comme étant payée avec un mode de paiement spécifique (par exemple : Espèces, Carte).
    """
    # Récupère la facture dans la base de données grâce à son identifiant
    f = facture_repo.get_by_id(facture_id)
    # Si la facture n'est pas trouvée, on déclenche une erreur
    if not f:
        raise ValueError(f"Facture #{facture_id} introuvable")
    
    # Met à jour le statut et le mode de paiement dans la base de données
    facture_repo.marquer_payee(facture_id, mode_paiement)
    # Met à jour l'objet en mémoire pour que le code puisse l'utiliser avec les nouvelles valeurs
    f.statut = 'payee'
    f.mode_paiement = mode_paiement
    # Retourne la facture mise à jour
    return f

def get_factures_impayees():
    """
    Récupère toutes les factures qui sont actuellement non payées.
    """
    # Retourne une liste contenant toutes les factures dont le statut est 'non_payee'
    return [f for f in facture_repo.get_all() if f.statut == 'non_payee']

def get_ca_total():
    """
    Calcule le Chiffre d'Affaires total en additionnant toutes les factures payées.
    """
    # Récupère toutes les factures de la base de données
    factures = facture_repo.get_all()
    # Fait la somme des montants TTC des factures uniquement si elles sont payées, puis arrondit à 2 décimales
    return round(sum((f.montant_ttc or 0) for f in factures if f.statut == 'payee'), 2)
