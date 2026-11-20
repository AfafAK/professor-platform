import io
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Line

def generate_pdf_certificate(student_name, training_title, issue_date, certificate_code):
    """Generates an elegant landscape PDF certificate of completion using ReportLab."""
    buffer = io.BytesIO()

    # A4 Landscape or Letter Landscape
    # letter is 612 x 792. Landscape letter is 792 x 612.
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Define custom styles
    title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=34,
        leading=42,
        textColor=colors.HexColor('#0f172a'),
        alignment=1, # Center
        spaceAfter=15
    )

    subtitle_style = ParagraphStyle(
        'CertSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=25
    )

    name_style = ParagraphStyle(
        'CertName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=colors.HexColor('#3b82f6'),
        alignment=1,
        spaceAfter=20
    )

    body_style = ParagraphStyle(
        'CertBody',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=15,
        leading=20,
        textColor=colors.HexColor('#334155'),
        alignment=1,
        spaceAfter=25
    )

    course_style = ParagraphStyle(
        'CertCourse',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=28,
        textColor=colors.HexColor('#6366f1'),
        alignment=1,
        spaceAfter=35
    )

    meta_style = ParagraphStyle(
        'CertMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748b'),
        alignment=1
    )

    story = []

    # Draw double border outline via elements or table
    # We can create a table structure to hold the certificate text and apply a beautiful border

    content = [
        Spacer(1, 15),
        Paragraph("CERTIFICAT DE RÉUSSITE", title_style),
        Paragraph("Le présent certificat est décerné à", subtitle_style),
        Paragraph(student_name, name_style),
        Paragraph("pour avoir validé avec succès tous les modules requis et réussi les quiz de la formation en ligne", body_style),
        Paragraph(f"« {training_title} »", course_style),
        Spacer(1, 20)
    ]

    # Signatures & Info Table
    data = [
        [
            Paragraph(f"Date d'émission : <b>{issue_date}</b>", meta_style),
            Paragraph("<b>Prof. Academix</b><br/>Enseignant-Chercheur", meta_style),
            Paragraph(f"ID Certificat : <b>{certificate_code}</b>", meta_style)
        ]
    ]

    meta_table = Table(data, colWidths=[230, 250, 230])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('LINEBELOW', (1,0), (1,0), 1, colors.HexColor('#94a3b8')), # Signature line
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))

    content.append(meta_table)

    # Wrap in a single cell Table to create a nice certificate frame/border
    border_table = Table([[content]], colWidths=[712])
    border_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 3, colors.HexColor('#3b82f6')),       # Inner blue border
        ('BOX', (-1,-1), (-1,-1), 1, colors.HexColor('#6366f1')),   # Accent shadow line
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),   # White certificate background
        ('TOPPADDING', (0,0), (-1,-1), 30),
        ('BOTTOMPADDING', (0,0), (-1,-1), 30),
        ('LEFTPADDING', (0,0), (-1,-1), 40),
        ('RIGHTPADDING', (0,0), (-1,-1), 40),
    ]))

    story.append(border_table)

    doc.build(story)

    buffer.seek(0)
    return buffer.getvalue()
