from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from datetime import date
import os

styles = getSampleStyleSheet()

def _style_table(data, col_widths):
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('FONTSIZE',   (0, 1), (-1, -1), 9),
        ('GRID',       (0, 0), (-1, -1), 0.25, colors.HexColor('#CCCCCC')),
        ('ALIGN',      (2, 1), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t

def generer_facture_pdf(facture, client, vehicule, pieces, mos, output_dir='output') -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{facture.numero}.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    story = []
    W = 170*mm

    # En-tête
    titre = ParagraphStyle('titre', fontSize=20, fontName='Helvetica-Bold', spaceAfter=2)
    sous = ParagraphStyle('sous', fontSize=9, textColor=colors.HexColor('#666666'))
    story.append(Paragraph("GARAGE AUTO", titre))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("123 Rue de l'Atelier — Casablanca | Tel: 05 22 00 00 00", sous))
    story.append(Spacer(1, 24*mm))

    # Bloc facture + client
    info_data = [
        [Paragraph(f"<b>FACTURE N° {facture.numero}</b>", styles['Normal']),
         Paragraph(f"<b>Client :</b> {client.nom} {client.prenom or ''}", styles['Normal'])],
        [Paragraph(f"Date : {facture.date_emission or date.today()}", styles['Normal']),
         Paragraph(f"Tél : {client.telephone or '-'}", styles['Normal'])],
        [Paragraph(f"Statut : {'✓ Payée' if facture.statut == 'payee' else '⏳ Non payée'}", styles['Normal']),
         Paragraph(f"Véhicule : {vehicule.marque or ''} {vehicule.modele or ''} — {vehicule.immatriculation}", styles['Normal'])],
    ]
    t_info = Table(info_data, colWidths=[W/2, W/2])
    t_info.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('TOPPADDING', (0,0),(-1,-1), 3)]))
    story.append(t_info)
    story.append(Spacer(1, 6*mm))

    # Pièces
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

    # Main d'œuvre
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

    # Totaux
    tva_montant = round((facture.montant_ttc or 0) - (facture.montant_ht or 0), 2)
    totaux = [
        ['', 'Total HT', f"{facture.montant_ht:.2f} DH"],
        ['', f'TVA ({facture.tva:.0f}%)', f"{tva_montant:.2f} DH"],
        ['', 'TOTAL TTC', f"{facture.montant_ttc:.2f} DH"],
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

    if facture.mode_paiement:
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph(f"Mode de paiement : {facture.mode_paiement}", styles['Normal']))

    doc.build(story)
    return path

def generer_devis_pdf(devis, client, vehicule, pieces, mos, output_dir='output') -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"DEVIS-OR{devis.or_id}.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    story = []
    W = 170*mm

    titre = ParagraphStyle('titre', fontSize=20, fontName='Helvetica-Bold', spaceAfter=2)
    sous = ParagraphStyle('sous', fontSize=9, textColor=colors.HexColor('#666666'))
    story.append(Paragraph("GARAGE AUTO", titre))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("123 Rue de l'Atelier — Casablanca | Tel: 05 22 00 00 00", sous))
    story.append(Spacer(1, 24*mm))

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
    story.append(Paragraph("Bon pour accord : _______________________     Date : _______________", styles['Normal']))

    doc.build(story)
    return path
