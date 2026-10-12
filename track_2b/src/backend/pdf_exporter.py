"""
ChronoMine AI — Swiss Bautagebuch & Regierapport (SIA 118) PDF Exporter
Generates official Swiss civil engineering daily site logs & force-account claims.
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from src.backend.models import BautagebuchResponse, InfrastructureDecisionResponse

def generate_bautagebuch_pdf(data: BautagebuchResponse) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Swiss typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        spaceAfter=10
    )
    
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#dc2626'), # Swiss red
        spaceBefore=10,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1e293b')
    )
    
    bold_style = ParagraphStyle(
        'BoldCustom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    elements = []
    
    # Header Banner
    header_data = [
        [
            Paragraph("<b>CHRONOMINE AI — SWISSTUNNELCOPILOT</b><br/><font color='#64748b'>Système Souverain d'Ingénierie Souterraine</font>", body_style),
            Paragraph(f"<b>DATE :</b> {data.date}<br/><b>LOCALISATION :</b> {data.location_pk}", body_style),
            Paragraph(f"<b>NORME :</b> SIA 118 / SIA 198<br/><b>STATUT :</b> RÉGIE ART. 44", body_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[200, 160, 160])
    t_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 10))
    
    # Document Title
    elements.append(Paragraph("BAUTAGEBUCH & REGIERAPPORT (SIA 118 ART. 44)", title_style))
    elements.append(Paragraph(
        "Journal officiel des travaux souterrains et relevé des prestations en régie imprévues selon les normes SIA 118 et SIA 198.",
        subtitle_style
    ))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#dc2626'), spaceAfter=10))
    
    # 1. Synthèse du Journal de Chantier
    elements.append(Paragraph("1. SYNTHÈSE DU CHANTIER / TAGESBERICHT", h2_style))
    summary_text = data.summary_de if data.summary_de else data.summary_fr
    elements.append(Paragraph(f"<b>Rapport officiel :</b> {summary_text}", body_style))
    if data.delay_hours > 0:
        elements.append(Paragraph(
            f"<font color='#dc2626'><b>Interruption de chantier constatée :</b> {data.delay_hours} heure(s)</font>",
            body_style
        ))
    elements.append(Spacer(1, 8))
    
    # Événements détaillés
    if data.events:
        elements.append(Paragraph("<b>Événements consignés par le chef de poste :</b>", bold_style))
        for ev in data.events:
            elements.append(Paragraph(f"• {ev}", body_style))
        elements.append(Spacer(1, 8))
    
    # 2. Bordereau de Régie (SIA 118 Art. 44)
    regie = data.regierapport
    elements.append(Paragraph("2. BORDEREAU DE RÉGIE — TRAVAUX IMPRÉVUS (SIA 118 ART. 44)", h2_style))
    elements.append(Paragraph(f"<b>Motif de la prestation :</b> {regie.claim_reason}", body_style))
    elements.append(Spacer(1, 6))
    
    # Tableau de la main-d'œuvre
    table_rows = [
        [
            Paragraph("<b>Désignation de la main-d'œuvre</b>", bold_style),
            Paragraph("<b>Heures</b>", bold_style),
            Paragraph("<b>Tarif horaire (CHF)</b>", bold_style),
            Paragraph("<b>Total (CHF)</b>", bold_style)
        ]
    ]
    
    total_chf = 0.0
    for wf in regie.workforce_hours:
        role = wf.get("role", "Ouvrier spécialisé")
        hours = float(wf.get("hours", 0.0))
        rate = float(wf.get("rate_chf", 95.0))
        subtotal = hours * rate
        total_chf += subtotal
        table_rows.append([
            Paragraph(role, body_style),
            Paragraph(f"{hours:.1f} h", body_style),
            Paragraph(f"{rate:.2f} CHF", body_style),
            Paragraph(f"{subtotal:.2f} CHF", body_style)
        ])
        
    table_rows.append([
        Paragraph("<b>TOTAL MAIN-D'ŒUVRE RÉGIE</b>", bold_style),
        Paragraph("", body_style),
        Paragraph("", body_style),
        Paragraph(f"<b>{total_chf:.2f} CHF</b>", bold_style)
    ])
    
    t_workforce = Table(table_rows, colWidths=[240, 70, 100, 110])
    t_workforce.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_workforce)
    elements.append(Spacer(1, 8))
    
    # Matériel et matériaux
    if regie.equipment_used or regie.materials_used:
        mat_text = ""
        if regie.equipment_used:
            mat_text += f"<b>Machines & engins mobilisés :</b> {', '.join(regie.equipment_used)}<br/>"
        if regie.materials_used:
            mat_text += f"<b>Matériaux & fournitures d'urgence :</b> {', '.join(regie.materials_used)}"
        elements.append(Paragraph(mat_text, body_style))
        elements.append(Spacer(1, 8))
        
    # 3. Sécurité SUVA
    if data.safety_hazard_detected:
        elements.append(Paragraph("3. SÉCURITÉ DU TRAVAIL & CONFORMITÉ SUVA (BauAV 2022)", h2_style))
        elements.append(Paragraph(
            f"<font color='#dc2626'><b>Alerte sécurité :</b> {data.safety_rule_infraction or 'Infraction constatée aux prescriptions de la BauAV 2022'}</font>",
            body_style
        ))
        elements.append(Spacer(1, 8))
        
    # 4. Signatures et Visas (SIA 118 Art. 47)
    elements.append(Spacer(1, 14))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=8))
    elements.append(Paragraph("4. VISAS ET SIGNATURES CONTRACTUELLES (SIA 118 ART. 47)", h2_style))
    elements.append(Paragraph("<i>Les soussignés certifient l'exactitude des événements, du temps d'arrêt et des prestations en régie consignés ci-dessus.</i>", body_style))
    elements.append(Spacer(1, 8))
    
    sig_data = [
        [
            Paragraph("<b>POUR L'ENTREPRENEUR :</b><br/>(Chef de chantier / Conducteur de travaux)<br/><br/><br/>Date et signature : ...................................", body_style),
            Paragraph("<b>POUR LA DIRECTION DES TRAVAUX :</b><br/>(Ingénieur représentant le Maître de l'Ouvrage)<br/><br/><br/>Visa et signature : ...................................", body_style)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[260, 260])
    t_sig.setStyle(TableStyle([
        ('BOX', (0, 0), (0, 0), 1, colors.HexColor('#94a3b8')),
        ('BOX', (1, 0), (1, 0), 1, colors.HexColor('#94a3b8')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(t_sig)
    
    # Build
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def generate_decision_report_pdf(data: InfrastructureDecisionResponse) -> bytes:
    """Generates official Swiss Infrastructure Strategic Decision & Arbitration Report (Pont vs Tunnel)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        spaceAfter=10
    )
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#dc2626'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1e293b')
    )

    elements = []
    today = datetime.now().strftime("%Y-%m-%d")

    # Header Cartouche
    header_data = [
        [
            Paragraph("<b>SWISSBAU COPILOT — APERTUS v1.5</b><br/><font color='#64748b'>Aide à la Décision Stratégique & Maîtrise d'Ouvrage</font>", body_style),
            Paragraph(f"<b>PROJET :</b> {data.project_name}<br/><b>DATE :</b> {today}", body_style),
            Paragraph("<b>JURIDICTION :</b> SUISSE (LAT / OPB)<br/><b>OPTIMISATION :</b> EMPLACEMENT & TRACÉ", body_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[200, 160, 160])
    t_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("RAPPORT D'OPTIMISATION D'EMPLACEMENT ET D'IMPLANTATION D'INFRASTRUCTURE", title_style))
    loc_subtitle = f" · Emplacement : {data.optimal_location_name}" if data.optimal_location_name else ""
    elements.append(Paragraph(
        f"Comparatif multicritères (Oppositions riveraines LAT/OPB, Coûts fonciers & CapEx, Délais de recours, Impact environnemental). Solution retenue : <b>{data.recommended_variant}</b>{loc_subtitle}",
        subtitle_style
    ))

    # 1. Synthèse
    elements.append(Paragraph("1. SYNTHÈSE DÉCISIONNELLE DU MAÎTRE D'OUVRAGE (FR / DE)", h2_style))
    elements.append(Paragraph(f"<b>Français :</b> {data.decision_summary_fr}", body_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"<b>Deutsch :</b> {data.decision_summary_de}", body_style))
    if data.siting_tradeoff_analysis_fr:
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(f"<b>Analyse du compromis d'implantation :</b> {data.siting_tradeoff_analysis_fr}", body_style))
    elements.append(Spacer(1, 8))

    # 2. Tableau comparatif des variantes
    elements.append(Paragraph("2. MATRICE COMPARATIVE MULTICRITÈRES DES SITES CANDIDATS", h2_style))
    table_rows = [
        [
            Paragraph("<b>Variante / Site</b>", body_style),
            Paragraph("<b>Type</b>", body_style),
            Paragraph("<b>Coût (Score)</b>", body_style),
            Paragraph("<b>Risque Oppositions</b>", body_style),
            Paragraph("<b>Recours (mois)</b>", body_style),
            Paragraph("<b>Impact Env.</b>", body_style),
            Paragraph("<b>Score Global</b>", body_style),
        ]
    ]
    for ev in data.evaluations:
        site_label = f"<b>{ev.variant_name}</b>"
        if ev.location_name and ev.location_name != ev.variant_name:
            site_label += f"<br/><font color='#64748b'>{ev.location_name}</font>"
        table_rows.append([
            Paragraph(site_label, body_style),
            Paragraph(ev.type.upper(), body_style),
            Paragraph(f"{ev.cost_score}/100", body_style),
            Paragraph(f"<b>{ev.opposition_risk_level}</b>", body_style),
            Paragraph(f"{ev.estimated_litigation_delay_months} m.", body_style),
            Paragraph(f"{ev.environmental_score}/100", body_style),
            Paragraph(f"<b>{ev.total_score} pts</b>", body_style),
        ])

    t_eval = Table(table_rows, colWidths=[120, 55, 60, 85, 70, 60, 70])
    t_eval.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_eval)
    elements.append(Spacer(1, 10))

    # 3. Bases juridiques & Recommandation
    elements.append(Paragraph("3. BASES JURIDIQUES SUISSES & STRATÉGIE DE MISE À L'ENQUÊTE", h2_style))
    for legal in data.swiss_legal_basis:
        elements.append(Paragraph(f"• {legal}", body_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"<b>Recommandation stratégique :</b> {data.strategic_recommendation}", body_style))
    elements.append(Spacer(1, 12))

    # Signatures
    sig_data = [
        [
            Paragraph("<b>POUR LE MAÎTRE DE L'OUVRAGE (BAUHERR) :</b><br/><br/><br/>Date et signature : ...................................", body_style),
            Paragraph("<b>DIRECTION DU PROJET & JURISTE :</b><br/><br/><br/>Visa et signature : ...................................", body_style)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[260, 260])
    t_sig.setStyle(TableStyle([
        ('BOX', (0, 0), (0, 0), 1, colors.HexColor('#94a3b8')),
        ('BOX', (1, 0), (1, 0), 1, colors.HexColor('#94a3b8')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(t_sig)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
