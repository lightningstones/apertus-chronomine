"""
Script to compile technical_report.md into a high-quality Swiss-styled PDF report: ChronoMine_Report.pdf
Meets the Hack Apertus submission requirement: "Upload a pdf of your technical report to this directory, named as TeamName_Report.pdf. Max. 6 pages."
"""
import os
import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Preformatted
)

def build_pdf(md_path: Path, output_pdf: Path):
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Swiss typographic styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=8
    )
    
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#dc2626'), # Swiss red accent
        spaceBefore=12,
        spaceAfter=5
    )
    
    h3_style = ParagraphStyle(
        'Heading3Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=7,
        spaceAfter=3
    )
    
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=5
    )
    
    code_style = ParagraphStyle(
        'CodeCustom',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#0f172a'),
        backColor=colors.HexColor('#f1f5f9'),
        spaceBefore=3,
        spaceAfter=5
    )
    
    elements = []
    
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    in_code_block = False
    code_buffer = []
    
    for line in lines:
        stripped = line.strip()
        
        # Handle code blocks
        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                elements.append(Preformatted("\n".join(code_buffer), code_style))
                elements.append(Spacer(1, 4))
                code_buffer = []
            else:
                in_code_block = True
            continue
            
        if in_code_block:
            code_buffer.append(line.rstrip("\n"))
            continue
            
        if not stripped:
            continue
            
        # Title (# )
        if stripped.startswith("# "):
            elements.append(Paragraph(stripped[2:], title_style))
            elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#dc2626'), spaceAfter=8))
        # Heading 2 (## )
        elif stripped.startswith("## "):
            elements.append(Paragraph(stripped[3:], h2_style))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=5))
        # Heading 3 (### )
        elif stripped.startswith("### "):
            elements.append(Paragraph(stripped[4:], h3_style))
        # Metadata or bullet
        elif stripped.startswith("- "):
            clean_text = stripped[2:]
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_text)
            clean_text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', clean_text)
            elements.append(Paragraph(f"• {clean_text}", body_style))
        elif stripped.startswith("---"):
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceAfter=6, spaceBefore=3))
        else:
            clean_text = stripped
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_text)
            clean_text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', clean_text)
            elements.append(Paragraph(clean_text, body_style))
            
    doc.build(elements)
    print(f"Successfully generated PDF: {output_pdf}")

if __name__ == '__main__':
    root_dir = Path(__file__).resolve().parent.parent
    md_file = root_dir / "technical_report.md"
    pdf_file = root_dir / "ChronoMine_Report.pdf"
    build_pdf(md_file, pdf_file)
