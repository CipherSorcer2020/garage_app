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

def _generer_document_pdf(doc_type, document, client, vehicule, pieces, mos, or_obj, output_dir):
    """
    Fonction utilitaire pour factoriser la génération de PDF (Factures et Devis)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    is_facture = (doc_type == 'facture')
    
    if is_facture:
        path = os.path.join(output_dir, f"{document.numero}.pdf")
        titre_doc = f"FACTURE N° {document.numero}"
        date_doc = document.date_emission or date.today()
    else:
        path = os.path.join(output_dir, f"DEVIS-OR{document.or_id}.pdf")
        titre_doc = f"DEVIS N° DEVIS-OR{document.or_id}"
        date_doc = document.date_creation or date.today()
        
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

    # --- Bloc d'informations ---
    if is_facture:
        info_data = [
            [Paragraph(f"<b>{titre_doc}</b>", styles['Normal']),
             Paragraph(f"<b>Client :</b> {client.nom} {client.prenom or ''}", styles['Normal'])],
            [Paragraph(f"Date : {date_doc}", styles['Normal']),
             Paragraph(f"Tél : {client.telephone or '-'}", styles['Normal'])],
            [Paragraph(f"Statut : {'✓ Payée' if document.statut == 'payee' else '⏳ Non payée'}", styles['Normal']),
             Paragraph(f"Véhicule : {vehicule.marque or ''} {vehicule.modele or ''} — {vehicule.immatriculation}", styles['Normal'])],
        ]
    else:
        info_data = [
            [Paragraph(f"<b>{titre_doc}</b>", styles['Normal']),
             Paragraph(f"<b>Client :</b> {client.nom} {client.prenom or ''}", styles['Normal'])],
            [Paragraph(f"Date : {date_doc}", styles['Normal']),
             Paragraph(f"Véhicule : {vehicule.marque or ''} {vehicule.modele or ''} — {vehicule.immatriculation}", styles['Normal'])],
        ]
        
    if or_obj:
        info_data.append([
            Paragraph(f"Kilométrage : {or_obj.kilometrage or '—'} km", styles['Normal']),
            Paragraph(f"Carburant : {or_obj.niveau_carburant or '—'}", styles['Normal'])
        ])
        if or_obj.visual_condition:
            info_data.append([Paragraph(f"État visuel : {or_obj.visual_condition}", styles['Normal']), ""])
        if or_obj.accessoires:
            info_data.append([Paragraph(f"Accessoires : {or_obj.accessoires}", styles['Normal']), ""])
        if or_obj.signature:
            from io import BytesIO
            from reportlab.platypus import Image as RLImage
            sig_buf = BytesIO(or_obj.signature)
            sig_img = RLImage(sig_buf, width=50*mm, preserveAspectRatio=True)
            info_data.append([Paragraph("Signature du client :", styles['Normal']), sig_img])
        
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
    tva_montant = round((document.montant_ttc or 0) - (document.montant_ht or 0), 2)
    totaux = [
        ['', 'Total HT', f"{document.montant_ht:.2f} DH"],
        ['', f'TVA ({document.tva:.0f}%)', f"{tva_montant:.2f} DH"],
        ['', 'TOTAL TTC', f"{document.montant_ttc:.2f} DH"],
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
    
    if is_facture:
        if document.mode_paiement:
            story.append(Spacer(1, 4*mm))
            story.append(Paragraph(f"Mode de paiement : {document.mode_paiement}", styles['Normal']))
    else:
        story.append(Spacer(1, 8*mm))
        story.append(Paragraph("Bon pour accord : _______________________     Date : _______________", styles['Normal']))

    doc.build(story)
    return path

def generer_facture_pdf(facture, client, vehicule, pieces, mos, or_obj, output_dir='output') -> str:
    """
    Génère un fichier PDF pour une facture et le sauvegarde.
    """
    return _generer_document_pdf('facture', facture, client, vehicule, pieces, mos, or_obj, output_dir)

def generer_devis_pdf(devis, client, vehicule, pieces, mos, or_obj, output_dir='output') -> str:
    """
    Génère un fichier PDF pour un devis et le sauvegarde.
    """
    return _generer_document_pdf('devis', devis, client, vehicule, pieces, mos, or_obj, output_dir)
