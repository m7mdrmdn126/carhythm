"""
PDF Report Generation Service for CaRhythm Assessment Scores

⚠️ NOTE: This service uses v1.0 scoring format (0-100 scale)
For v1.1 scoring (direct sum with strength labels), this needs updating.
Current status: Compatible with v1.1 data via backward-compatible score fields.

TODO v1.1 Updates Needed:
- Update score ranges (RIASEC: /15, Big Five: /25, Behavioral: /15)
- Add strength label badges (Low/Medium/High/Very High)
- Add behavioral flags section (procrastination_risk, growth_mindset, etc.)
- Add Ikigai zones visualization
- Update radar charts with new score scales

Generates professional PDF reports with:
- Student information
- Assessment scores for all three modules
- Radar chart visualizations
- Score interpretations
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.pdfgen import canvas
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from typing import Optional
from ..models import StudentResponse, AssessmentScore

def create_radar_chart(labels, values, title, color='blue'):
    """Create a radar chart and return as BytesIO image"""
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values_plot = values + [values[0]]  # Complete the circle
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
    ax.plot(angles, values_plot, 'o-', linewidth=2, color=color)
    ax.fill(angles, values_plot, alpha=0.25, color=color)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=10)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_title(title, size=14, weight='bold', pad=20)
    ax.grid(True)
    
    # Save to BytesIO
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    img_buffer.seek(0)
    
    return img_buffer


def get_score_interpretation(score, trait_type='general'):
    """Return interpretation text based on score range"""
    if score < 30:
        return "Low - Area for development"
    elif score < 70:
        return "Moderate - Typical range"
    else:
        return "High - Strength area"


def generate_pdf_report(response: StudentResponse, scores: AssessmentScore) -> BytesIO:
    """
    Generate a comprehensive PDF report for a student response with scores.
    Returns BytesIO object containing the PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for document elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#3498db'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=6
    )
    
    normal_style = styles['Normal']
    
    # Title Page
    elements.append(Paragraph("CaRhythm Assessment Report", title_style))
    elements.append(Paragraph("Your Career, Your Rhythm", ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=TA_CENTER,
        spaceAfter=40
    )))
    
    # Student Information
    elements.append(Paragraph("Student Information", heading_style))
    
    info_data = [
        ["Name:", response.full_name],
        ["Email:", response.email],
        ["Age Group:", response.age_group],
        ["Country:", response.country],
        ["Origin Country:", response.origin_country],
        ["Assessment Date:", response.created_at.strftime('%B %d, %Y') if response.created_at else 'N/A'],
        ["Report Generated:", datetime.now().strftime('%B %d, %Y at %H:%M')]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # RIASEC Section
    if scores.riasec_complete:
        elements.append(PageBreak())
        elements.append(Paragraph("RIASEC Career Interest Profile", heading_style))
        elements.append(Paragraph(
            f"Your Holland Code: <b>{scores.riasec_profile}</b>",
            ParagraphStyle('ProfileCode', parent=normal_style, fontSize=14, textColor=colors.HexColor('#3498db'), spaceAfter=12)
        ))
        
        # RIASEC Scores Table
        riasec_data = [
            ["Domain", "Score", "Interpretation"],
            ["Realistic (R)", f"{scores.riasec_r_score:.1f}/100", get_score_interpretation(scores.riasec_r_score)],
            ["Investigative (I)", f"{scores.riasec_i_score:.1f}/100", get_score_interpretation(scores.riasec_i_score)],
            ["Artistic (A)", f"{scores.riasec_a_score:.1f}/100", get_score_interpretation(scores.riasec_a_score)],
            ["Social (S)", f"{scores.riasec_s_score:.1f}/100", get_score_interpretation(scores.riasec_s_score)],
            ["Enterprising (E)", f"{scores.riasec_e_score:.1f}/100", get_score_interpretation(scores.riasec_e_score)],
            ["Conventional (C)", f"{scores.riasec_c_score:.1f}/100", get_score_interpretation(scores.riasec_c_score)],
        ]
        
        riasec_table = Table(riasec_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        riasec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        elements.append(riasec_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # RIASEC Radar Chart
        riasec_labels = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional']
        riasec_values = [
            scores.riasec_r_score, scores.riasec_i_score, scores.riasec_a_score,
            scores.riasec_s_score, scores.riasec_e_score, scores.riasec_c_score
        ]
        riasec_chart = create_radar_chart(riasec_labels, riasec_values, 'RIASEC Profile', '#3498db')
        elements.append(Image(riasec_chart, width=4*inch, height=4*inch))
        
        # RIASEC Interpretation
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("What This Means:", subheading_style))
        elements.append(Paragraph(
            f"Your top interest areas are <b>{scores.riasec_profile}</b>. This profile suggests you are "
            "drawn to careers that align with these Holland Code types. Your strongest domain is "
            f"<b>{riasec_labels[riasec_values.index(max(riasec_values))]}</b> with a score of {max(riasec_values):.1f}.",
            normal_style
        ))
    
    # Big Five Section
    if scores.bigfive_complete:
        elements.append(PageBreak())
        elements.append(Paragraph("Big Five Personality Traits", heading_style))
        
        # Big Five Scores Table
        bigfive_data = [
            ["Trait", "Score", "Interpretation"],
            ["Openness", f"{scores.bigfive_openness:.1f}/100", get_score_interpretation(scores.bigfive_openness)],
            ["Conscientiousness", f"{scores.bigfive_conscientiousness:.1f}/100", get_score_interpretation(scores.bigfive_conscientiousness)],
            ["Extraversion", f"{scores.bigfive_extraversion:.1f}/100", get_score_interpretation(scores.bigfive_extraversion)],
            ["Agreeableness", f"{scores.bigfive_agreeableness:.1f}/100", get_score_interpretation(scores.bigfive_agreeableness)],
            ["Neuroticism", f"{scores.bigfive_neuroticism:.1f}/100", get_score_interpretation(scores.bigfive_neuroticism)],
        ]
        
        bigfive_table = Table(bigfive_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        bigfive_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        elements.append(bigfive_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Big Five Radar Chart
        bigfive_labels = ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism']
        bigfive_values = [
            scores.bigfive_openness, scores.bigfive_conscientiousness, scores.bigfive_extraversion,
            scores.bigfive_agreeableness, scores.bigfive_neuroticism
        ]
        bigfive_chart = create_radar_chart(bigfive_labels, bigfive_values, 'Big Five Personality', '#2ecc71')
        elements.append(Image(bigfive_chart, width=4*inch, height=4*inch))
    
    # Work Rhythm Section
    if scores.workrhythm_complete:
        elements.append(PageBreak())
        elements.append(Paragraph("Work Rhythm Traits", heading_style))
        
        # Work Rhythm Scores Table
        workrhythm_data = [
            ["Trait", "Score", "Interpretation"],
            ["Motivation", f"{scores.workrhythm_motivation:.1f}/100", get_score_interpretation(scores.workrhythm_motivation)],
            ["Grit", f"{scores.workrhythm_grit:.1f}/100", get_score_interpretation(scores.workrhythm_grit)],
            ["Self-Efficacy", f"{scores.workrhythm_self_efficacy:.1f}/100", get_score_interpretation(scores.workrhythm_self_efficacy)],
            ["Resilience", f"{scores.workrhythm_resilience:.1f}/100", get_score_interpretation(scores.workrhythm_resilience)],
            ["Learning", f"{scores.workrhythm_learning:.1f}/100", get_score_interpretation(scores.workrhythm_learning)],
            ["Empathy", f"{scores.workrhythm_empathy:.1f}/100", get_score_interpretation(scores.workrhythm_empathy)],
            ["Procrastination", f"{scores.workrhythm_procrastination:.1f}/100", get_score_interpretation(scores.workrhythm_procrastination)],
        ]
        
        workrhythm_table = Table(workrhythm_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        workrhythm_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        elements.append(workrhythm_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Work Rhythm Radar Chart
        workrhythm_labels = ['Motivation', 'Grit', 'Self-Efficacy', 'Resilience', 'Learning', 'Empathy', 'Procrastination']
        workrhythm_values = [
            scores.workrhythm_motivation, scores.workrhythm_grit, scores.workrhythm_self_efficacy,
            scores.workrhythm_resilience, scores.workrhythm_learning, scores.workrhythm_empathy,
            scores.workrhythm_procrastination
        ]
        workrhythm_chart = create_radar_chart(workrhythm_labels, workrhythm_values, 'Work Rhythm Profile', '#f39c12')
        elements.append(Image(workrhythm_chart, width=4*inch, height=4*inch))
    
    # Footer
    elements.append(PageBreak())
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph(
        "Thank you for completing the CaRhythm Assessment!",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, textColor=colors.HexColor('#7f8c8d'))
    ))
    elements.append(Paragraph(
        "Your Career, Your Rhythm",
        ParagraphStyle('FooterSub', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#95a5a6'), spaceAfter=20)
    ))
    elements.append(Paragraph(
        f"© {datetime.now().year} CaRhythm. All rights reserved.",
        ParagraphStyle('Copyright', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#bdc3c7'))
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer
