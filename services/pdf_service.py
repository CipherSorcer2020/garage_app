# Importation de composants ReportLab pour gérer la taille des pages (A4) et les couleurs
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
# Importation de l'unité de mesure en millimètres pour un placement précis
from reportlab.lib.units import mm
# Importation des éléments structurels pour construire le PDF (document, tableau, style de tableau, paragraphes, espaces)
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# Importation des feuilles de style pour les paragraphes
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# Importation de constantes pour l'alignement du texte (droite, centré)
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
# Importation du module date pour obtenir la date actuelle
from datetime import date
# Importation du module os pour gérer les dossiers et fichiers
import os

# Récupération de la feuille de style par défaut pour ReportLab
styles = getSampleStyleSheet()

def _style_table(data, col_widths):
    """
    Fonction utilitaire (interne) pour appliquer un joli style aux tableaux.
    Prend en paramètre les données du tableau et la largeur des colonnes.
    """
    # Création du tableau avec ses largeurs de colonnes spécifiques
    t = Table(data, colWidths=col_widths)
    # Application d'une série de styles visuels
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),  # Fond gris-bleu pour la première ligne (entête)
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),                # Texte en blanc pour l'entête
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),            # Police en gras pour l'entête
        ('FONTSIZE',   (0, 0), (-1, 0), 10),                          # Taille de texte 10 pour l'entête
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]), # Alternance de couleurs sur les lignes
        ('FONTSIZE',   (0, 1), (-1, -1), 9),                          # Taille de texte 9 pour le contenu
        ('GRID',       (0, 0), (-1, -1), 0.25, colors.HexColor('#CCCCCC')), # Grille fine grise
        ('ALIGN',      (2, 1), (-1, -1), 'RIGHT'),                    # Alignement à droite pour les colonnes de chiffres
        ('TOPPADDING', (0, 0), (-1, -1), 4),                          # Espacement en haut de chaque cellule
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),                       # Espacement en bas de chaque cellule
    ]))
    return t # Retourne le tableau formaté

def generer_facture_pdf(facture, client, vehicule, pieces, mos, output_dir='output') -> str:
    """
    Génère un fichier PDF pour une facture et le sauvegarde.
    """
    # Crée le dossier de destination s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    # Construit le chemin complet du fichier (ex: output/F-1234.pdf)
    path = os.path.join(output_dir, f"{facture.numero}.pdf")
    
    # Prépare le document PDF au format A4 avec des marges de 20mm partout
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    
    # Cette liste "story" contiendra tous les éléments qui composent le PDF dans l'ordre d'affichage
    story = []
    # Largeur utile de la page (A4 fait 210mm, moins 40mm de marges = 170mm)
    W = 170*mm

    # --- Section de l'En-tête de l'entreprise ---
    # Style pour le nom du garage (gros et en gras)
    titre = ParagraphStyle('titre', fontSize=20, fontName='Helvetica-Bold', spaceAfter=2)
    # Style pour l'adresse (petit et gris)
    sous = ParagraphStyle('sous', fontSize=9, textColor=colors.HexColor('#666666'))
    
    # Ajoute le nom et l'adresse à la liste des éléments à dessiner
    story.append(Paragraph("GARAGE AUTO", titre))
    story.append(Spacer(1, 6*mm)) # Un petit espace vide (6mm)
    story.append(Paragraph("123 Rue de l'Atelier — Casablanca | Tel: 05 22 00 00 00", sous))
    story.append(Spacer(1, 24*mm)) # Un grand espace vide (24mm)

    # --- Bloc d'informations : Détails de la facture et du client ---
    # Construction des lignes d'information (gauche = Facture, droite = Client/Véhicule)
    info_data = [
        [Paragraph(f"<b>FACTURE N° {facture.numero}</b>", styles['Normal']),
         Paragraph(f"<b>Client :</b> {client.nom} {client.prenom or ''}", styles['Normal'])],
        [Paragraph(f"Date : {facture.date_emission or date.today()}", styles['Normal']),
         Paragraph(f"Tél : {client.telephone or '-'}", styles['Normal'])],
        [Paragraph(f"Statut : {'✓ Payée' if facture.statut == 'payee' else '⏳ Non payée'}", styles['Normal']),
         Paragraph(f"Véhicule : {vehicule.marque or ''} {vehicule.modele or ''} — {vehicule.immatriculation}", styles['Normal'])],
    ]
    # On met ces infos dans un tableau coupé en deux colonnes égales
    t_info = Table(info_data, colWidths=[W/2, W/2])
    t_info.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('TOPPADDING', (0,0),(-1,-1), 3)]))
    # Ajout du bloc info et d'un petit espacement
    story.append(t_info)
    story.append(Spacer(1, 6*mm))

    # --- Section des pièces détachées ---
    if pieces: # S'il y a des pièces à facturer
        story.append(Paragraph("<b>Pièces détachées</b>", styles['Normal'])) # Titre de la section
        story.append(Spacer(1, 2*mm))
        # Initialise le tableau avec l'en-tête
        data = [['Réf.', 'Désignation', 'Qté', 'P.U. HT', 'Total HT']]
        # Ajoute une ligne pour chaque pièce
        for p in pieces:
            data.append([p.reference or '-', p.designation, str(p.quantite),
                         f"{p.prix_unitaire_ht:.2f} DH" if p.prix_unitaire_ht else '-',
                         f"{p.total_ht:.2f} DH" if p.total_ht else '-'])
        # Applique le style et l'ajoute au document
        story.append(_style_table(data, [20*mm, 70*mm, 15*mm, 30*mm, 35*mm]))
        story.append(Spacer(1, 4*mm))

    # --- Section de la main d'œuvre ---
    if mos: # S'il y a des heures de main d'œuvre
        story.append(Paragraph("<b>Main d'œuvre</b>", styles['Normal']))
        story.append(Spacer(1, 2*mm))
        # En-tête du tableau
        data = [['Description', 'Durée (h)', 'Taux HT/h', 'Total HT']]
        # Boucle sur chaque intervention
        for m in mos:
            data.append([m.description,
                         f"{m.duree_heures:.1f}" if m.duree_heures else '-',
                         f"{m.taux_horaire_ht:.2f} DH" if m.taux_horaire_ht else '-',
                         f"{m.total_ht:.2f} DH" if m.total_ht else '-'])
        # Applique le style et l'ajoute au document
        story.append(_style_table(data, [80*mm, 25*mm, 30*mm, 35*mm]))
        story.append(Spacer(1, 6*mm))

    # --- Section des totaux finaux ---
    # Calcul du montant total de la TVA (TTC - HT)
    tva_montant = round((facture.montant_ttc or 0) - (facture.montant_ht or 0), 2)
    
    # On prépare un tableau pour l'affichage des totaux
    totaux = [
        ['', 'Total HT', f"{facture.montant_ht:.2f} DH"],
        ['', f'TVA ({facture.tva:.0f}%)', f"{tva_montant:.2f} DH"],
        ['', 'TOTAL TTC', f"{facture.montant_ttc:.2f} DH"],
    ]
    # Ce tableau n'utilise que la partie droite de la page
    t_totaux = Table(totaux, colWidths=[W - 80*mm, 40*mm, 40*mm])
    # Style spécifique : on aligne à droite, on met en gras et on ajoute une ligne au-dessus du total TTC
    t_totaux.setStyle(TableStyle([
        ('ALIGN',      (1, 0), (-1, -1), 'RIGHT'),         # Aligne le texte à droite
        ('FONTNAME',   (1, 2), (-1, 2),  'Helvetica-Bold'),# Total TTC en gras
        ('FONTSIZE',   (0, 0), (-1, -1), 10),              # Taille du texte
        ('LINEABOVE',  (1, 2), (-1, 2),  1, colors.HexColor('#2C3E50')), # Ligne séparatrice
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_totaux)

    # --- Section du mode de paiement (s'il est déjà payé) ---
    if facture.mode_paiement:
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph(f"Mode de paiement : {facture.mode_paiement}", styles['Normal']))

    # Finalement, on construit le PDF avec tous les éléments ajoutés dans "story"
    doc.build(story)
    # On retourne le chemin où le fichier a été enregistré
    return path

def generer_devis_pdf(devis, client, vehicule, pieces, mos, output_dir='output') -> str:
    """
    Génère un fichier PDF pour un devis et le sauvegarde.
    Fonctionnement très similaire à generer_facture_pdf.
    """
    # Création du dossier si nécessaire
    os.makedirs(output_dir, exist_ok=True)
    # Le nom du fichier inclut l'ID de l'Ordre de Réparation (ex: DEVIS-OR1.pdf)
    path = os.path.join(output_dir, f"DEVIS-OR{devis.or_id}.pdf")
    
    # Configuration initiale du document PDF
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    story = []
    W = 170*mm

    # --- En-tête ---
    titre = ParagraphStyle('titre', fontSize=20, fontName='Helvetica-Bold', spaceAfter=2)
    sous = ParagraphStyle('sous', fontSize=9, textColor=colors.HexColor('#666666'))
    
    story.append(Paragraph("GARAGE AUTO", titre))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("123 Rue de l'Atelier — Casablanca | Tel: 05 22 00 00 00", sous))
    story.append(Spacer(1, 24*mm))

    # --- Bloc d'informations : Détails du devis et du client ---
    info_data = [
        [Paragraph(f"<b>DEVIS N° DEVIS-OR{devis.or_id}</b>", styles['Normal']),
         Paragraph(f"<b>Client :</b> {client.nom} {client.prenom or ''}", styles['Normal'])],
        [Paragraph(f"Date : {devis.date_creation or date.today()}", styles['Normal']),
         Paragraph(f"Véhicule : {vehicule.marque or ''} {vehicule.modele or ''} — {vehicule.immatriculation}", styles['Normal'])],
    ]
    t_info = Table(info_data, colWidths=[W/2, W/2])
    t_info.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('TOPPADDING', (0,0),(-1,-1), 3)]))
    story.append(t_info)
    story.append(Spacer(1, 6*mm))

    # --- Pièces ---
    if pieces:
        story.append(Paragraph("<b>Pièces détachées</b>", styles['Normal']))
        story.append(Spacer(1, 2*mm))
        data = [['Réf.', 'Désignation', 'Qté', 'P.U. HT', 'Total HT']]
        for p in pieces:
            data.append([p.reference or '-', p.designation, str(p.quantite),
                         f"{p.prix_unitaire_ht:.2f} DH" if p.prix_unitaire_ht else '-',
                         f"{p.total_ht:.2f} DH" if p.total_ht else '-'])
        story.append(_style_table(data, [20*mm, 70*mm, 15*mm, 30*mm, 35*mm]))
        story.append(Spacer(1, 4*mm))

    # --- Main d'œuvre ---
    if mos:
        story.append(Paragraph("<b>Main d'œuvre</b>", styles['Normal']))
        story.append(Spacer(1, 2*mm))
        data = [['Description', 'Durée (h)', 'Taux HT/h', 'Total HT']]
        for m in mos:
            data.append([m.description,
                         f"{m.duree_heures:.1f}" if m.duree_heures else '-',
                         f"{m.taux_horaire_ht:.2f} DH" if m.taux_horaire_ht else '-',
                         f"{m.total_ht:.2f} DH" if m.total_ht else '-'])
        story.append(_style_table(data, [80*mm, 25*mm, 30*mm, 35*mm]))
        story.append(Spacer(1, 6*mm))

    # --- Totaux ---
    tva_montant = round((devis.montant_ttc or 0) - (devis.montant_ht or 0), 2)
    totaux = [
        ['', 'Total HT', f"{devis.montant_ht:.2f} DH"],
        ['', f'TVA ({devis.tva:.0f}%)', f"{tva_montant:.2f} DH"],
        ['', 'TOTAL TTC', f"{devis.montant_ttc:.2f} DH"],
    ]
    t_totaux = Table(totaux, colWidths=[W - 80*mm, 40*mm, 40*mm])
    t_totaux.setStyle(TableStyle([
        ('ALIGN',      (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME',   (1, 2), (-1, 2),  'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, -1), 10),
        ('LINEABOVE',  (1, 2), (-1, 2),  1, colors.HexColor('#2C3E50')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_totaux)
    story.append(Spacer(1, 8*mm))
    
    # --- Zone de signature spécifique aux devis ---
    story.append(Paragraph("Bon pour accord : _______________________     Date : _______________", styles['Normal']))

    # Création du fichier PDF et retour de son chemin
    doc.build(story)
    return path
