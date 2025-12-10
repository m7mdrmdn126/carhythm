"""
CaRhythm v1.1 Enhanced PDF Report Generation Service
Story-like design with comprehensive visualizations and career guidance

Features:
- Story-like magazine design with CaRhythm branding
- 10-15 pages with inspirational quotes
- All visualizations: Radar, Hexagon, Ikigai Venn, Flags Dashboard, Heatmap
- Short explanations of each assessment
- Personalized career recommendations

v2 Template Features (New):
- Modern archetype-focused hero page with large typography
- Science explanation cards with icons
- Career matches with blurred upsell section
- Friction detection CTA with QR code
- RTL support for Arabic names
- Embedded Poppins fonts
- High-resolution charts (600 dpi)
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                                TableStyle, PageBreak, Image, KeepTogether, Frame, Flowable)
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String as ShapeString
from reportlab.graphics import renderPDF
from io import BytesIO
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import json
import qrcode

from ..models import StudentResponse, AssessmentScore

# Try to import RTL support (optional)
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    RTL_SUPPORT = True
except ImportError:
    RTL_SUPPORT = False

# CaRhythm Brand Colors - Coral & Purple Palette
BRAND_CORAL = colors.HexColor('#FF6F61')  # Primary Coral
BRAND_PURPLE = colors.HexColor('#2E1A47')  # Deep Purple
BRAND_PRIMARY = BRAND_CORAL  # Alias for compatibility
BRAND_SECONDARY = BRAND_PURPLE  # Alias for compatibility
BRAND_ACCENT = colors.HexColor('#FFB4A9')  # Light Coral
BRAND_LIGHT = colors.HexColor('#F5F5F5')  # Light Grey
BRAND_TEXT = BRAND_PURPLE  # Deep Purple for text

# Visualization Color Palette
VIZ_COLORS = {
    'primary': '#FF6F61',      # Coral
    'secondary': '#2E1A47',    # Deep Purple
    'accent': '#FFB4A9',       # Light Coral
    'dark': '#1A0E2E',         # Darker Purple
    'neutral': '#F5F5F5',      # Light Grey
    'success': '#4ECDC4',      # Teal (for positive traits)
    'warning': '#FFD166',      # Gold (for medium)
    'danger': '#EF476F'        # Pink (for risks)
}

# Strength Label Colors (modernized)
COLOR_VERY_HIGH = colors.HexColor('#4ECDC4')  # Teal
COLOR_HIGH = colors.HexColor('#FFB4A9')  # Light Coral
COLOR_MEDIUM = colors.HexColor('#FFD166')  # Gold
COLOR_LOW = colors.HexColor('#EF476F')  # Pink

# Logo Path
LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                         'frontend', 'public', 'CaRhythm updated logo.png')

# Font Paths
FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                         'app', 'static', 'fonts')

# Register Poppins fonts if available
try:
    pdfmetrics.registerFont(TTFont('Poppins', os.path.join(FONTS_DIR, 'Poppins-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Poppins-Bold', os.path.join(FONTS_DIR, 'Poppins-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('Poppins-Italic', os.path.join(FONTS_DIR, 'Poppins-Italic.ttf')))
    FONTS_AVAILABLE = True
except:
    FONTS_AVAILABLE = False

# Inspirational Quotes
QUOTES = [
    "Your career is a journey of self-discovery, not a destination.",
    "The future belongs to those who believe in the beauty of their dreams.",
    "Success is not the key to happiness. Happiness is the key to success.",
    "Choose a job you love, and you will never have to work a day in your life.",
    "Your work is going to fill a large part of your life, so make it meaningful.",
    "The only way to do great work is to love what you do.",
]

# Helper function for strength labels
def get_strength_label(score: float, max_score: float) -> str:
    """Calculate strength label from raw score"""
    percentage = (score / max_score) * 100
    if percentage >= 80:
        return 'Very High'
    elif percentage >= 60:
        return 'High'
    elif percentage >= 40:
        return 'Medium'
    else:
        return 'Low'


class NumberedCanvas(pdfcanvas.Canvas):
    """Custom canvas for page numbers and headers"""
    
    def __init__(self, *args, **kwargs):
        pdfcanvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        """Draw header and footer on each page"""
        self.saveState()
        
        # Footer with page number
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.grey)
        page_num_text = f"Page {self._pageNumber} of {page_count}"
        self.drawCentredString(letter[0] / 2, 0.5 * inch, page_num_text)
        
        # Small logo in footer
        if os.path.exists(LOGO_PATH) and self._pageNumber > 1:
            try:
                self.drawImage(LOGO_PATH, 0.75 * inch, 0.4 * inch, 
                             width=0.3*inch, height=0.3*inch, preserveAspectRatio=True, mask='auto')
            except:
                self.setFillColor(BRAND_PRIMARY)
                self.setFont('Helvetica-Bold', 8)
                self.drawString(0.75 * inch, 0.5 * inch, "🎵 CaRhythm")
        else:
            self.setFillColor(BRAND_PRIMARY)
            self.setFont('Helvetica-Bold', 8)
            self.drawString(0.75 * inch, 0.5 * inch, "🎵 CaRhythm")
        
        self.restoreState()


def create_cover_page() -> List:
    """Create beautiful cover page"""
    elements = []
    styles = getSampleStyleSheet()
    
    # Compact top spacer
    elements.append(Spacer(1, 0.8 * inch))
    
    # Add logo if available
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image(LOGO_PATH, width=1.8*inch, height=1.8*inch, kind='proportional')
            elements.append(logo)
            elements.append(Spacer(1, 0.2 * inch))
        except:
            # Fallback to emoji if logo fails
            elements.append(Spacer(1, 0.3 * inch))
    
    # CaRhythm Logo/Title with gradient effect
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Title'],
        fontSize=52,
        textColor=BRAND_PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=0.6 * inch,
        fontName='Helvetica-Bold',
        letterSpacing=1
    )
    elements.append(Paragraph("<font size=60>🎵</font> <font color='#FF6F61'>Ca</font><font color='#764ba2'>Rhythm</font>", title_style))
    
    # Tagline with modern styling
    tagline_style = ParagraphStyle(
        'Tagline',
        fontSize=20,
        textColor=BRAND_SECONDARY,
        alignment=TA_CENTER,
        spaceAfter=1.2 * inch,
        fontName='Helvetica-Oblique',
        letterSpacing=2
    )
    elements.append(Paragraph("<i>Find Your Career Rhythm</i>", tagline_style))
    
    # Main title with modern typography
    main_title_style = ParagraphStyle(
        'MainTitle',
        fontSize=40,
        textColor=BRAND_TEXT,
        alignment=TA_CENTER,
        spaceAfter=0.5 * inch,
        fontName='Helvetica-Bold',
        leading=48,
        letterSpacing=1
    )
    elements.append(Paragraph("<font color='#2E1A47'>Your </font><font color='#FF6F61'>Career DNA</font><br/><font color='#2E1A47'>Report</font>", main_title_style))
    
    elements.append(Spacer(1, 0.5 * inch))
    
    # Decorative line
    line_data = [['', '', '']]
    line_table = Table(line_data, colWidths=[2*inch, 2*inch, 2*inch])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (1, 0), (1, 0), 3, BRAND_ACCENT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(line_table)
    
    elements.append(Spacer(1, 0.5 * inch))
    
    # Quote
    quote_style = ParagraphStyle(
        'CoverQuote',
        fontSize=13,
        textColor=BRAND_SECONDARY,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        spaceAfter=0.8 * inch,
        leading=18
    )
    elements.append(Paragraph('<i>"' + QUOTES[0] + '"</i>', quote_style))
    
    # Date
    date_style = ParagraphStyle(
        'DateStyle',
        fontSize=12,
        textColor=colors.grey,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", date_style))
    
    elements.append(PageBreak())
    
    return elements


def create_welcome_letter(student_name: str) -> List:
    """Create personalized welcome letter"""
    elements = []
    styles = getSampleStyleSheet()
    
    # Section header
    header_style = ParagraphStyle(
        'SectionHeader',
        fontSize=24,
        textColor=BRAND_PRIMARY,
        spaceAfter=0.3 * inch,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph("💌 Welcome to Your Journey", header_style))
    
    # Body text
    body_style = ParagraphStyle(
        'BodyText',
        fontSize=11,
        textColor=BRAND_TEXT,
        alignment=TA_JUSTIFY,
        spaceAfter=0.15 * inch,
        leading=16
    )
    
    welcome_text = f"""
    Dear {student_name},<br/><br/>
    
    Congratulations on completing the CaRhythm Career Assessment! This comprehensive report 
    reveals insights about your interests, personality, and career pathways.<br/><br/>
    
    <b>Inside this report:</b><br/>
    • RIASEC Career Interest Profile (Holland Code)<br/>
    • Big Five Personality Analysis<br/>
    • Behavioral Insights & Development Areas<br/>
    • Ikigai Career Guidance<br/>
    • Career Recommendations & Action Plan<br/><br/>
    
    Share this report with mentors or counselors. These insights are a starting point for 
    self-discovery. Your career journey is uniquely yours—let's find your rhythm!<br/><br/>
    
    <i>— The CaRhythm Team</i>
    """
    
    elements.append(Paragraph(welcome_text, body_style))
    
    elements.append(PageBreak())
    
    return elements


def create_quote_divider(quote_index: int) -> List:
    """Create a decorative quote divider with modern styling"""
    elements = []
    styles = getSampleStyleSheet()
    
    quote_style = ParagraphStyle(
        'QuoteDivider',
        fontSize=14,
        textColor=BRAND_SECONDARY,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        spaceBefore=0.3 * inch,
        spaceAfter=0.3 * inch,
        leading=20,
        backColor=colors.HexColor('#FFF5F4'),
        borderPadding=(15, 15, 15, 15),
        borderWidth=0,
        leftIndent=40,
        rightIndent=40
    )
    
    selected_quote = QUOTES[quote_index % len(QUOTES)]
    quote_text = f'<font color="#FF6F61">❝</font> <i>{selected_quote}</i> <font color="#FF6F61">❞</font>'
    elements.append(Paragraph(quote_text, quote_style))
    
    # Decorative line element
    elements.append(Spacer(1, 0.1 * inch))
    
    return elements


def create_section_header(title: str, emoji: str = "") -> Paragraph:
    """Create consistent section headers with modern styling"""
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'SectionHeader',
        fontSize=24,
        textColor=BRAND_PRIMARY,
        spaceAfter=0.25 * inch,
        spaceBefore=0.4 * inch,
        fontName='Helvetica-Bold',
        leftIndent=10,
        borderPadding=(8, 8, 8, 8),
        backColor=colors.HexColor('#FFF5F4'),
        borderWidth=0,
        borderRadius=3
    )
    
    full_title = f"<font size=26>{emoji}</font> {title}" if emoji else title
    return Paragraph(full_title, header_style)


def create_subsection_header(title: str) -> Paragraph:
    """Create subsection headers with modern accent"""
    styles = getSampleStyleSheet()
    subheader_style = ParagraphStyle(
        'SubsectionHeader',
        fontSize=16,
        textColor=BRAND_SECONDARY,
        spaceAfter=0.18 * inch,
        spaceBefore=0.25 * inch,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderPadding=(0, 0, 3, 0),
        leftIndent=5
    )
    return Paragraph(f"<font color='#FF6F61'>▸</font> {title}", subheader_style)


def create_body_text(text: str, justified: bool = True) -> Paragraph:
    """Create body text paragraph with modern typography"""
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        'BodyText',
        fontSize=11,
        textColor=BRAND_TEXT,
        alignment=TA_JUSTIFY if justified else TA_LEFT,
        spaceAfter=0.12 * inch,
        leading=17,
        leftIndent=5,
        rightIndent=5
    )
    return Paragraph(text, body_style)


def get_strength_color(label: str) -> colors.Color:
    """Get color for strength label"""
    color_map = {
        'Very High': COLOR_VERY_HIGH,
        'High': COLOR_HIGH,
        'Medium': COLOR_MEDIUM,
        'Low': COLOR_LOW
    }
    return color_map.get(label, colors.grey)


def get_strength_color_hex(label: str) -> str:
    """Get hex color string for matplotlib"""
    color_obj = get_strength_color(label)
    # Convert ReportLab color to matplotlib-compatible hex string
    if hasattr(color_obj, 'hexval'):
        hex_val = color_obj.hexval()
        # Replace 0x prefix with # for matplotlib
        return '#' + hex_val.replace('0x', '').replace('#', '')
    return '#808080'  # Default gray


def create_radar_chart_v11(labels: List[str], values: List[float], 
                           max_value: float, title: str) -> BytesIO:
    """Create radar chart for v1.1 scores with modern coral/purple styling"""
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values_plot = values + [values[0]]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    # Shadow effect - plot slightly offset
    shadow_values = [v * 0.98 for v in values_plot]
    ax.plot(angles, shadow_values, 'o-', linewidth=2, color='#D1D1D1', markersize=8, alpha=0.3, zorder=1)
    ax.fill(angles, shadow_values, alpha=0.15, color='#D1D1D1', zorder=1)
    
    # Main plot: gradient effect with coral line and purple fill
    ax.plot(angles, values_plot, 'o-', linewidth=3.5, color='#FF6F61', markersize=12, markeredgecolor='white', markeredgewidth=2, zorder=3)
    ax.fill(angles, values_plot, alpha=0.35, color='#764ba2', zorder=2)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=13, weight='bold', color='#2E1A47', family='sans-serif')
    ax.set_ylim(0, max_value)
    ax.set_yticks(np.linspace(0, max_value, 5))
    ax.set_yticklabels([f'{int(y)}' for y in np.linspace(0, max_value, 5)], size=10, color='#764ba2')
    ax.set_title(title, size=18, weight='bold', pad=30, color='#2E1A47', family='sans-serif')
    ax.grid(True, linestyle='--', alpha=0.5, color='#FFB4A9', linewidth=1.5)
    ax.spines['polar'].set_color('#FF6F61')
    ax.spines['polar'].set_linewidth(2.5)
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    img_buffer.seek(0)
    
    return img_buffer


def create_holland_hexagon(scores: Dict[str, float]) -> BytesIO:
    """Create Holland Hexagon visualization with coral/purple styling"""
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    
    # Hexagon vertices (RIASEC order)
    angles = np.linspace(0, 2*np.pi, 7)[:-1]  # 6 points
    radius = 1.0
    hex_x = radius * np.cos(angles + np.pi/2)
    hex_y = radius * np.sin(angles + np.pi/2)
    
    # Draw hexagon background with gradient fill
    hexagon_bg = mpatches.RegularPolygon((0, 0), 6, radius=radius, 
                                     fill=True, facecolor='#F8F5FA', edgecolor='#2E1A47', linewidth=5, alpha=0.3)
    ax.add_patch(hexagon_bg)
    
    # Draw hexagon with purple outline
    hexagon = mpatches.RegularPolygon((0, 0), 6, radius=radius, 
                                     fill=False, edgecolor='#2E1A47', linewidth=5)
    ax.add_patch(hexagon)
    
    # Labels
    labels = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional']
    codes = ['R', 'I', 'A', 'S', 'E', 'C']
    
    # Normalize scores to 0-1 range for visualization
    max_score = 15.0
    normalized_scores = [scores.get(code, 0) / max_score for code in codes]
    
    # Plot scores with coral color
    score_x = [normalized_scores[i] * hex_x[i] for i in range(6)]
    score_y = [normalized_scores[i] * hex_y[i] for i in range(6)]
    score_x.append(score_x[0])
    score_y.append(score_y[0])
    
    # Shadow effect
    ax.plot(score_x, score_y, 'o-', color='#D1D1D1', linewidth=2.5, markersize=10, alpha=0.3, zorder=1)
    ax.fill(score_x, score_y, alpha=0.15, color='#D1D1D1', zorder=1)
    
    # Main plot
    ax.plot(score_x, score_y, 'o-', color='#FF6F61', linewidth=4, markersize=14, markeredgecolor='white', markeredgewidth=3, zorder=3)
    ax.fill(score_x, score_y, alpha=0.3, color='#FFB4A9', zorder=2)
    
    # Add labels with scores (no percentages) - modern card style
    for i, (label, code) in enumerate(zip(labels, codes)):
        score_val = scores.get(code, 0)
        label_x = 1.35 * hex_x[i]
        label_y = 1.35 * hex_y[i]
        ax.text(label_x, label_y, f"{label}\n{code}: {score_val:.1f}", 
               ha='center', va='center', fontsize=12, weight='bold', color='#2E1A47',
               bbox=dict(boxstyle='round,pad=0.7', facecolor='white', 
                        edgecolor='#FF6F61', linewidth=2.5, alpha=0.95))
    
    ax.set_xlim(-1.7, 1.7)
    ax.set_ylim(-1.7, 1.7)
    ax.axis('off')
    ax.set_title("Holland Hexagon Model\nYour Career Interest Profile", 
                fontsize=16, weight='bold', pad=20, color='#2E1A47')
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    img_buffer.seek(0)
    
    return img_buffer


def create_bar_chart_v11(labels: List[str], values: List[float], 
                        strength_labels: List[str], max_value: float, 
                        title: str) -> BytesIO:
    """Create horizontal bar chart for Big Five with gradient styling"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Create gradient colors from purple to coral based on value
    colors_list = []
    for val in values:
        ratio = val / max_value
        # Interpolate between purple and coral
        r = int(0x2E + (0xFF - 0x2E) * ratio)
        g = int(0x1A + (0x6F - 0x1A) * ratio)
        b = int(0x47 + (0x61 - 0x47) * ratio)
        colors_list.append(f'#{r:02x}{g:02x}{b:02x}')
    
    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, values, color=colors_list, edgecolor='#2E1A47', linewidth=2, height=0.6)
    
    # Create gradient bars with shadow effect
    for i, (bar, val) in enumerate(zip(bars, values)):
        bar.set_alpha(0.9)
        # Add subtle 3D effect with edge highlight
        bar.set_linewidth(0)
    
    # Add shadow bars behind main bars
    shadow_bars = ax.barh(y_pos, values, color='#D1D1D1', alpha=0.2, zorder=1)
    for i, (bar, shadow) in enumerate(zip(bars, shadow_bars)):
        shadow.set_x(0.1)
        shadow.set_y(bar.get_y() - 0.02)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=13, weight='bold', color='#2E1A47', family='sans-serif')
    ax.set_xlabel('Score', fontsize=13, weight='bold', color='#2E1A47')
    ax.set_title(title, fontsize=18, weight='bold', pad=25, color='#2E1A47', family='sans-serif')
    ax.set_xlim(0, max_value * 1.15)
    ax.grid(axis='x', alpha=0.4, linestyle='--', color='#FFB4A9', linewidth=1.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#2E1A47')
    ax.spines['bottom'].set_color('#2E1A47')
    ax.spines['left'].set_linewidth(2)
    ax.spines['bottom'].set_linewidth(2)
    
    # Add value labels on bars with modern badge style (no percentages)
    for i, (bar, val, label) in enumerate(zip(bars, values, strength_labels)):
        width = bar.get_width()
        ax.text(width + max_value * 0.02, bar.get_y() + bar.get_height()/2, 
               f' {val:.1f} ', 
               va='center', ha='left', fontsize=11, weight='bold', color='white',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='#FF6F61', edgecolor='none', alpha=0.9))
        # Add strength label
        ax.text(width + max_value * 0.09, bar.get_y() + bar.get_height()/2, 
               f'{label}', 
               va='center', ha='left', fontsize=10, style='italic', color='#764ba2')
    
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    img_buffer.seek(0)
    
    return img_buffer


def create_ikigai_venn_diagram(ikigai_zones: Dict) -> BytesIO:
    """Create Ikigai Venn diagram with 4 overlapping circles"""
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    
    # Circle positions for 4-way Venn (arranged in square)
    circles = [
        mpatches.Circle((0.3, 0.7), 0.4, alpha=0.3, color='#FF6B6B', label='What you LOVE'),
        mpatches.Circle((0.7, 0.7), 0.4, alpha=0.3, color='#4ECDC4', label='What you\'re GOOD AT'),
        mpatches.Circle((0.3, 0.3), 0.4, alpha=0.3, color='#95E1D3', label='What the WORLD NEEDS'),
        mpatches.Circle((0.7, 0.3), 0.4, alpha=0.3, color='#F38181', label='What you can be PAID FOR'),
    ]
    
    for circle in circles:
        ax.add_patch(circle)
    
    # Center point (Ikigai sweet spot)
    ax.plot(0.5, 0.5, 'o', color='#667eea', markersize=20, zorder=5)
    ax.text(0.5, 0.5, 'IKIGAI\n✨', ha='center', va='center', 
           fontsize=12, weight='bold', color='white', zorder=6)
    
    # Zone labels with slight offsets
    zone_labels = [
        (0.15, 0.85, "Love\nZone", '#FF6B6B'),
        (0.85, 0.85, "Mastery\nZone", '#4ECDC4'),
        (0.15, 0.15, "Contribution\nZone", '#95E1D3'),
        (0.85, 0.15, "Sustainability\nZone", '#F38181'),
    ]
    
    for x, y, text, color in zone_labels:
        ax.text(x, y, text, ha='center', va='center', fontsize=10, 
               weight='bold', color='black',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                        edgecolor=color, linewidth=2))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title("Your Ikigai: Where Career Paths Align", 
                fontsize=14, weight='bold', pad=20)
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    img_buffer.seek(0)
    
    return img_buffer


def create_behavioral_flags_dashboard(flags: Dict[str, bool]) -> BytesIO:
    """Create modern card-style dashboard for behavioral flags"""
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor('white')
    
    flag_names = [
        'Procrastination\nRisk',
        'Perfectionism\nRisk',
        'Low Grit\nRisk',
        'Poor Regulation\nRisk',
        'Growth\nMindset'
    ]
    
    flag_keys = [
        'procrastination_risk',
        'perfectionism_risk',
        'low_grit_risk',
        'poor_regulation_risk',
        'growth_mindset'
    ]
    
    flag_values = [flags.get(key, False) for key in flag_keys]
    
    # Modern gradient colors with shadows
    colors_list = []
    for i, val in enumerate(flag_values):
        if i == 4:  # Growth mindset (positive)
            colors_list.append('#4ECDC4' if val else '#E8E8E8')  # Teal or Light Grey
        else:  # Risks (negative)
            colors_list.append('#EF476F' if val else '#4ECDC4')  # Pink or Teal
    
    x_pos = np.arange(len(flag_names))
    
    # Add shadow effect
    shadow_bars = ax.bar(x_pos, [1]*len(flag_names), color='#D1D1D1', 
                         width=0.8, alpha=0.2, zorder=1)
    for i, shadow in enumerate(shadow_bars):
        shadow.set_x(shadow.get_x() + 0.02)
        shadow.set_y(-0.02)
    
    # Main bars with modern rounded style
    bars = ax.bar(x_pos, [1]*len(flag_names), color=colors_list, 
                  edgecolor='#2E1A47', linewidth=3, width=0.8, alpha=0.9, zorder=2)
    
    # Add status labels with modern icons and styling
    for i, (bar, val) in enumerate(zip(bars, flag_values)):
        if i == 4:  # Growth mindset
            status = "✓ YES" if val else "✗ NO"
            icon = "⭐" if val else "○"
            text_color = 'white' if val else '#999999'
        else:  # Risks
            status = "DETECTED" if val else "CLEAR"
            icon = "⚠️" if val else "✓"
            text_color = 'white' if val else 'white'
        
        # Icon at top
        ax.text(bar.get_x() + bar.get_width()/2, 0.7, icon, 
               ha='center', va='center', fontsize=24, zorder=3)
        
        # Status text at bottom
        ax.text(bar.get_x() + bar.get_width()/2, 0.3, status, 
               ha='center', va='center', fontsize=12, weight='bold',
               color=text_color, zorder=3, family='sans-serif')
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(flag_names, fontsize=12, weight='bold', color='#2E1A47', family='sans-serif')
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_title("Behavioral Flags Dashboard", fontsize=18, weight='bold', pad=25, color='#2E1A47', family='sans-serif')
    
    # Clean modern look - remove all spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    img_buffer.seek(0)
    
    return img_buffer


def create_strength_heatmap(riasec_scores: Dict, bigfive_scores: Dict, 
                           behavioral_scores: Dict) -> BytesIO:
    """Create comprehensive strength heatmap with coral-purple gradient"""
    from matplotlib.colors import LinearSegmentedColormap
    
    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor('white')
    
    # Prepare data - use actual behavioral trait keys from scoring service
    all_labels = (
        ['R', 'I', 'A', 'S', 'E', 'C'] +  # RIASEC
        ['O', 'C', 'E', 'A', 'N'] +  # Big Five
        ['Motiv', 'Grit', 'Self-Eff', 'Resil', 'Learn', 'Empath', 'Tempo']  # Behavioral
    )
    
    all_scores = []
    max_vals = []
    
    # RIASEC (0-15)
    for code in ['R', 'I', 'A', 'S', 'E', 'C']:
        all_scores.append(riasec_scores.get(code, 0))
        max_vals.append(15)
    
    # Big Five (0-25)
    for code in ['O', 'C', 'E', 'A', 'N']:
        all_scores.append(bigfive_scores.get(code, 0))
        max_vals.append(25)
    
    # Behavioral traits - use actual keys from scoring service (variable scale per trait)
    beh_keys = ['motivation_type', 'grit_persistence', 'self_efficacy', 
                'resilience', 'learning_orientation', 'empathy', 'task_start_tempo']
    for key in beh_keys:
        all_scores.append(behavioral_scores.get(key, 0))
        max_vals.append(15)  # Assume max 15 for behavioral traits
    
    # Normalize to 0-1
    normalized = [score/max_val for score, max_val in zip(all_scores, max_vals)]
    
    # Create custom coral-purple colormap (no green) with more contrast
    colors_map = ['#1A0E2E', '#2E1A47', '#764ba2', '#FFB4A9', '#FF6F61']  # Darker Purple -> Deep Purple -> Medium Purple -> Light Coral -> Coral
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('coral_purple', colors_map, N=n_bins)
    
    # Create heatmap with modern styling
    data = np.array([normalized])
    im = ax.imshow(data, cmap=cmap, aspect='auto', vmin=0, vmax=1, interpolation='bilinear')
    
    ax.set_xticks(np.arange(len(all_labels)))
    ax.set_xticklabels(all_labels, rotation=45, ha='right', fontsize=12, weight='bold', color='#2E1A47', family='sans-serif')
    ax.set_yticks([])
    
    # Remove spines for cleaner look
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Add score values with modern badge style
    for i, (score, label) in enumerate(zip(all_scores, all_labels)):
        text_color = 'white' if normalized[i] < 0.5 else '#2E1A47'
        # Main score
        ax.text(i, 0, f'{score:.1f}', ha='center', va='center',
               color=text_color, fontsize=11, weight='bold', family='sans-serif')
    
    ax.set_title("Your Strength Profile Across All Domains", 
                fontsize=18, weight='bold', pad=25, color='#2E1A47', family='sans-serif')
    
    # Add colorbar with modern styling
    cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.15, fraction=0.05, aspect=40)
    cbar.set_label('Relative Strength', fontsize=12, color='#2E1A47', weight='bold')
    cbar.ax.tick_params(labelsize=10, colors='#2E1A47', width=0)
    cbar.outline.set_linewidth(0)
    
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    img_buffer.seek(0)
    
    return img_buffer


def create_mini_heatmap_riasec(scores: Dict) -> BytesIO:
    """Create mini heatmap for RIASEC scores only"""
    from matplotlib.colors import LinearSegmentedColormap
    
    fig, ax = plt.subplots(figsize=(9, 1.5))
    fig.patch.set_facecolor('white')
    
    labels = ['R', 'I', 'A', 'S', 'E', 'C']
    values = [scores.get(code, 0) for code in labels]
    max_val = 15
    normalized = [v/max_val for v in values]
    
    # Create coral-purple colormap with more contrast
    colors_map = ['#1A0E2E', '#2E1A47', '#764ba2', '#FFB4A9', '#FF6F61']
    cmap = LinearSegmentedColormap.from_list('coral_purple', colors_map, N=100)
    
    data = np.array([normalized])
    im = ax.imshow(data, cmap=cmap, aspect='auto', vmin=0, vmax=1, interpolation='bilinear')
    
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, fontsize=13, weight='bold', color='#2E1A47', family='sans-serif')
    ax.set_yticks([])
    
    # Remove spines for modern look
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Add score values with modern badge style
    for i, (score, label) in enumerate(zip(values, labels)):
        text_color = 'white' if normalized[i] < 0.5 else '#2E1A47'
        ax.text(i, 0, f'{score:.1f}', ha='center', va='center',
               color=text_color, fontsize=12, weight='bold', family='sans-serif')
    
    ax.set_title("RIASEC Score Distribution", fontsize=14, weight='bold', pad=15, color='#2E1A47', family='sans-serif')
    
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    img_buffer.seek(0)
    
    return img_buffer


def create_mini_heatmap_bigfive(scores: Dict) -> BytesIO:
    """Create mini heatmap for Big Five scores only"""
    from matplotlib.colors import LinearSegmentedColormap
    
    fig, ax = plt.subplots(figsize=(9, 1.5))
    fig.patch.set_facecolor('white')
    
    labels = ['O', 'C', 'E', 'A', 'N']
    label_names = ['Openness', 'Conscient.', 'Extraversion', 'Agreeableness', 'Neuroticism']
    values = [scores.get(code, 0) for code in labels]
    max_val = 25
    normalized = [v/max_val for v in values]
    
    # Create coral-purple colormap with more contrast
    colors_map = ['#1A0E2E', '#2E1A47', '#764ba2', '#FFB4A9', '#FF6F61']
    cmap = LinearSegmentedColormap.from_list('coral_purple', colors_map, N=100)
    
    data = np.array([normalized])
    im = ax.imshow(data, cmap=cmap, aspect='auto', vmin=0, vmax=1, interpolation='bilinear')
    
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(label_names, fontsize=11, weight='bold', color='#2E1A47', family='sans-serif')
    ax.set_yticks([])
    
    # Remove spines for modern look
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Add score values with modern badge style
    for i, (score, label) in enumerate(zip(values, labels)):
        text_color = 'white' if normalized[i] < 0.5 else '#2E1A47'
        ax.text(i, 0, f'{score:.1f}', ha='center', va='center',
               color=text_color, fontsize=12, weight='bold', family='sans-serif')
    
    ax.set_title("Big Five Score Distribution", fontsize=14, weight='bold', pad=15, color='#2E1A47', family='sans-serif')
    
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    img_buffer.seek(0)
    
    return img_buffer


def create_mini_heatmap_behavioral(scores: Dict) -> BytesIO:
    """Create mini heatmap for Behavioral scores only"""
    from matplotlib.colors import LinearSegmentedColormap
    
    fig, ax = plt.subplots(figsize=(11, 1.5))
    fig.patch.set_facecolor('white')
    
    # Use actual trait keys from scoring
    trait_keys = ['motivation_type', 'grit_persistence', 'self_efficacy', 
                  'resilience', 'learning_orientation', 'empathy', 'task_start_tempo']
    labels = ['Motiv', 'Grit', 'Self-Eff', 'Resil', 'Learn', 'Empath', 'Tempo']
    values = [scores.get(key, 0) for key in trait_keys]
    max_val = 15
    normalized = [v/max_val for v in values]
    
    # Create coral-purple colormap with more contrast
    colors_map = ['#1A0E2E', '#2E1A47', '#764ba2', '#FFB4A9', '#FF6F61']
    cmap = LinearSegmentedColormap.from_list('coral_purple', colors_map, N=100)
    
    data = np.array([normalized])
    im = ax.imshow(data, cmap=cmap, aspect='auto', vmin=0, vmax=1, interpolation='bilinear')
    
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, fontsize=11, weight='bold', color='#2E1A47', family='sans-serif')
    ax.set_yticks([])
    
    # Remove spines for modern look
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Add score values with modern badge style
    for i, (score, label) in enumerate(zip(values, labels)):
        text_color = 'white' if normalized[i] < 0.5 else '#2E1A47'
        ax.text(i, 0, f'{score:.1f}', ha='center', va='center',
               color=text_color, fontsize=11, weight='bold', family='sans-serif')
    
    ax.set_title("Behavioral Traits Distribution", fontsize=14, weight='bold', pad=15, color='#2E1A47', family='sans-serif')
    ax.set_yticks([])
    
    # Add score values
    for i, (score, label) in enumerate(zip(values, labels)):
        text_color = 'white' if normalized[i] < 0.4 else '#2E1A47'
        ax.text(i, 0, f'{score:.1f}', ha='center', va='center',
               color=text_color, fontsize=9, weight='bold')
    
    ax.set_title("Behavioral Traits Score Distribution", fontsize=12, weight='bold', pad=10)
    
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    img_buffer.seek(0)
    
    return img_buffer


def create_riasec_explanation_page() -> List:
    """Create RIASEC explanation page"""
    elements = []
    
    elements.append(create_section_header("Understanding RIASEC", "🔧"))
    
    explanation = """
    <b>RIASEC</b> (also known as the <b>Holland Code</b>) measures your career interests across 
    six dimensions: <b>R</b>ealistic, <b>I</b>nvestigative, <b>A</b>rtistic, <b>S</b>ocial, 
    <b>E</b>nterprising, and <b>C</b>onventional. Your top three codes reveal career fields 
    where you'll thrive.
    """
    elements.append(create_body_text(explanation))
    
    elements.extend(create_quote_divider(1))
    
    # RIASEC dimensions table
    riasec_data = [
        ['Code', 'Dimension', 'Career Examples'],
        ['R', 'Realistic', 'Engineer, Mechanic, Pilot'],
        ['I', 'Investigative', 'Scientist, Analyst, Researcher'],
        ['A', 'Artistic', 'Designer, Writer, Musician'],
        ['S', 'Social', 'Teacher, Counselor, Nurse'],
        ['E', 'Enterprising', 'Manager, Entrepreneur, Lawyer'],
        ['C', 'Conventional', 'Accountant, Administrator, Banker'],
    ]
    
    riasec_table = Table(riasec_data, colWidths=[0.8*inch, 1.8*inch, 3*inch])
    riasec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), BRAND_LIGHT),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
    ]))
    
    elements.append(riasec_table)
    elements.append(Spacer(1, 0.25 * inch))
    
    return elements


def create_bigfive_explanation_page() -> List:
    """Create Big Five explanation page"""
    elements = []
    
    elements.append(create_section_header("Understanding the Big Five", "🧠"))
    
    explanation = """
    The <b>Big Five</b> personality model measures five core traits: <b>Openness</b>, 
    <b>Conscientiousness</b>, <b>Extraversion</b>, <b>Agreeableness</b>, and <b>Neuroticism</b>. 
    These traits influence how you work, relate to others, and approach challenges.
    """
    elements.append(create_body_text(explanation))
    
    elements.append(Spacer(1, 0.15 * inch))
    
    # Big Five traits table
    bigfive_data = [
        ['Trait', 'High Score Means', 'Career Fit'],
        ['Openness (O)', 'Creative, curious, imaginative', 'Creative fields, R&D'],
        ['Conscientiousness (C)', 'Organized, reliable, disciplined', 'Management, administration'],
        ['Extraversion (E)', 'Outgoing, energetic, sociable', 'Sales, leadership, teaching'],
        ['Agreeableness (A)', 'Cooperative, empathetic, kind', 'Helping professions, HR'],
        ['Neuroticism (N)', 'Emotionally sensitive, vigilant', 'Detail-oriented, quality control'],
    ]
    
    bigfive_table = Table(bigfive_data, colWidths=[1.5*inch, 2.2*inch, 2*inch])
    bigfive_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), BRAND_LIGHT),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
    ]))
    
    elements.append(bigfive_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    return elements


def create_behavioral_explanation_page() -> List:
    """Create behavioral traits explanation page"""
    elements = []
    
    elements.append(create_section_header("Understanding Behavioral Traits", "🚩"))
    
    explanation = """
    <b>Behavioral traits</b> measure work habits, mindset, and self-regulation. These are not 
    fixed—they can be developed with practice! Flags highlight areas for growth or celebrate 
    strengths.
    """
    elements.append(create_body_text(explanation))
    
    elements.append(Spacer(1, 0.3 * inch))
    
    return elements


def create_riasec_results_pages(scores: Dict, holland_code: str) -> List:
    """Create RIASEC results pages with visualizations"""
    elements = []
    
    elements.append(create_section_header("Your RIASEC Results", "📊"))
    
    # Holland Code announcement
    holland_text = f"""
    <b>Your Holland Code: {holland_code}</b><br/>
    <br/>
    Your top three interest areas are <b>{holland_code[0]}</b> ({scores.get(holland_code[0], 0):.1f}/15), 
    <b>{holland_code[1]}</b> ({scores.get(holland_code[1], 0):.1f}/15), and 
    <b>{holland_code[2]}</b> ({scores.get(holland_code[2], 0):.1f}/15). This combination reveals your unique career sweet spot!
    """
    elements.append(create_body_text(holland_text))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Add detailed score breakdown table
    riasec_detail_data = [
        ['Code', 'Dimension', 'Your Score', 'Strength'],
        ['R', 'Realistic', f"{scores.get('R', 0):.1f}/15", get_strength_label(scores.get('R', 0), 15)],
        ['I', 'Investigative', f"{scores.get('I', 0):.1f}/15", get_strength_label(scores.get('I', 0), 15)],
        ['A', 'Artistic', f"{scores.get('A', 0):.1f}/15", get_strength_label(scores.get('A', 0), 15)],
        ['S', 'Social', f"{scores.get('S', 0):.1f}/15", get_strength_label(scores.get('S', 0), 15)],
        ['E', 'Enterprising', f"{scores.get('E', 0):.1f}/15", get_strength_label(scores.get('E', 0), 15)],
        ['C', 'Conventional', f"{scores.get('C', 0):.1f}/15", get_strength_label(scores.get('C', 0), 15)],
    ]
    
    detail_table = Table(riasec_detail_data, colWidths=[0.6*inch, 1.5*inch, 1.2*inch, 1.2*inch])
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
    ]))
    elements.append(detail_table)
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Create mini heatmap for RIASEC
    riasec_heatmap = create_mini_heatmap_riasec(scores)
    elements.append(Image(riasec_heatmap, width=6*inch, height=1*inch))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Radar chart (smaller)
    riasec_labels = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional']
    riasec_values = [scores.get('R', 0), scores.get('I', 0), scores.get('A', 0), 
                     scores.get('S', 0), scores.get('E', 0), scores.get('C', 0)]
    radar_img = create_radar_chart_v11(riasec_labels, riasec_values, 15, "RIASEC Profile")
    img = Image(radar_img, width=3.5*inch, height=3.5*inch)
    elements.append(img)
    
    elements.append(PageBreak())
    
    # Holland Hexagon (smaller)
    elements.append(create_subsection_header("Your Position on the Holland Hexagon"))
    hexagon_img = create_holland_hexagon(scores)
    img2 = Image(hexagon_img, width=4*inch, height=4*inch)
    elements.append(img2)
    
    elements.append(PageBreak())
    
    return elements


def create_bigfive_results_pages(scores: Dict, strength_labels: Dict) -> List:
    """Create Big Five results pages"""
    elements = []
    
    elements.append(create_section_header("Your Big Five Personality Profile", "🌟"))
    
    intro_text = """
    Your personality profile shows how you naturally approach work, relationships, and challenges. 
    Each trait exists on a spectrum—there's no "better" or "worse" score!
    """
    elements.append(create_body_text(intro_text))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Mini heatmap for Big Five
    bigfive_heatmap = create_mini_heatmap_bigfive(scores)
    elements.append(Image(bigfive_heatmap, width=6*inch, height=1*inch))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Bar chart (smaller)
    bigfive_trait_names = ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism']
    bigfive_values = [scores.get('O', 0), scores.get('C', 0), scores.get('E', 0), 
                      scores.get('A', 0), scores.get('N', 0)]
    bigfive_strengths = [strength_labels.get('O', 'Medium'), strength_labels.get('C', 'Medium'), 
                         strength_labels.get('E', 'Medium'), strength_labels.get('A', 'Medium'), 
                         strength_labels.get('N', 'Medium')]
    bar_img = create_bar_chart_v11(bigfive_trait_names, bigfive_values, bigfive_strengths, 25, "Big Five Profile")
    img = Image(bar_img, width=5*inch, height=2.5*inch)
    elements.append(img)
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Trait interpretations
    trait_data = [
        ['Trait', 'Your Score', 'Strength'],
        ['Openness', f"{scores.get('O', 0):.1f}/25", strength_labels.get('O', 'Medium')],
        ['Conscientiousness', f"{scores.get('C', 0):.1f}/25", strength_labels.get('C', 'Medium')],
        ['Extraversion', f"{scores.get('E', 0):.1f}/25", strength_labels.get('E', 'Medium')],
        ['Agreeableness', f"{scores.get('A', 0):.1f}/25", strength_labels.get('A', 'Medium')],
        ['Neuroticism', f"{scores.get('N', 0):.1f}/25", strength_labels.get('N', 'Medium')],
    ]
    
    trait_table = Table(trait_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    trait_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
    ]))
    
    elements.append(trait_table)
    
    # Add trait interpretations
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(create_subsection_header("What Your Scores Mean"))
    
    trait_descriptions = {
        'O': ('Openness to Experience', 'Your curiosity, creativity, and willingness to try new things. High scorers are imaginative and prefer variety.'),
        'C': ('Conscientiousness', 'Your organization, reliability, and self-discipline. High scorers are methodical and goal-oriented.'),
        'E': ('Extraversion', 'Your sociability, energy level, and enthusiasm. High scorers are outgoing and thrive in social settings.'),
        'A': ('Agreeableness', 'Your cooperativeness, empathy, and consideration for others. High scorers are warm and value harmony.'),
        'N': ('Neuroticism', 'Your emotional stability and stress management. Lower scores indicate greater resilience and calmness.')
    }
    
    for code, (trait_name, description) in trait_descriptions.items():
        score = scores.get(code, 0)
        strength = strength_labels.get(code, 'Medium')
        
        text = f"""<b>{trait_name} ({strength}):</b> {description} Your score is {score:.1f}/25."""
        elements.append(create_body_text(text))
        elements.append(Spacer(1, 0.15 * inch))
    
    elements.append(PageBreak())
    
    return elements


def create_behavioral_results_page(scores: Dict, flags: Dict, raw_scores: Dict = None) -> List:
    """Create behavioral results page with flags"""
    elements = []
    
    elements.append(create_section_header("Your Behavioral Traits & Flags", "🚦"))
    
    intro_text = """
    Behavioral traits reveal your work habits and mindset. Flags are not judgments—they're 
    opportunities for growth and self-awareness!
    """
    elements.append(create_body_text(intro_text))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Add mini heatmap if raw scores available
    if raw_scores:
        behavioral_heatmap = create_mini_heatmap_behavioral(raw_scores)
        elements.append(Image(behavioral_heatmap, width=6.5*inch, height=1*inch))
        elements.append(Spacer(1, 0.2 * inch))
    
    # Flags dashboard
    flags_img = create_behavioral_flags_dashboard(flags)
    img = Image(flags_img, width=5.5*inch, height=2*inch)
    elements.append(img)
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Scores table - scores here is actually strength_labels dict
    beh_data = [
        ['Trait', 'Strength'],
        ['Motivation', scores.get('motivation', 'Medium')],
        ['Grit', scores.get('grit', 'Medium')],
        ['Self-Regulation', scores.get('self_regulation', 'Medium')],
        ['Time Management', scores.get('time_management', 'Medium')],
        ['Growth Mindset', scores.get('growth_mindset', 'Medium')],
    ]
    
    beh_table = Table(beh_data, colWidths=[3*inch, 2*inch])
    beh_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
    ]))
    
    elements.append(beh_table)
    
    # Add behavioral insights
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(create_subsection_header("Behavioral Insights & Development Tips"))
    
    # Map behavioral traits to user-friendly names and tips
    trait_info = {
        'motivation_type': ('Motivation', 'Your drive to pursue goals and take action. High motivation leads to initiative and persistence.'),
        'grit_persistence': ('Grit & Persistence', 'Your ability to persevere through challenges. Grit predicts long-term success better than talent alone.'),
        'self_efficacy': ('Self-Regulation', 'Your confidence in managing tasks and emotions. Strong self-regulation enables better decision-making.'),
        'resilience': ('Resilience', 'Your ability to bounce back from setbacks. Resilient people adapt well to change and stress.'),
        'learning_orientation': ('Growth Mindset', 'Your belief that abilities can be developed. Growth mindset leads to continuous improvement.'),
        'empathy': ('Empathy', 'Your ability to understand and share others\' feelings. Empathy strengthens relationships and teamwork.'),
        'task_start_tempo': ('Task Initiation', 'Your tendency to start tasks promptly. Good tempo reduces procrastination and stress.')
    }
    
    # Show insights for available traits
    for trait_key, (trait_name, description) in trait_info.items():
        if trait_key in scores or any(trait_key.replace('_', ' ').lower() in k.lower() for k in scores.keys()):
            strength = scores.get(trait_key, scores.get(trait_key.replace('_', ' ').title(), 'Medium'))
            text = f"""<b>{trait_name} ({strength}):</b> {description}"""
            elements.append(create_body_text(text))
            elements.append(Spacer(1, 0.1 * inch))
    
    elements.append(PageBreak())
    
    return elements


def create_ikigai_pages(holland_code: str, riasec_scores: Dict) -> List:
    """Create Ikigai guidance pages"""
    elements = []
    
    elements.append(create_section_header("Your Ikigai: Career Sweet Spot", "✨"))
    
    ikigai_text = """
    <b>Ikigai</b> (生き甲斐) is a Japanese concept meaning "reason for being." It's where your 
    passions, talents, values, and market needs intersect. Let's map your career sweet spot!
    """
    elements.append(create_body_text(ikigai_text))
    
    elements.append(Spacer(1, 0.3 * inch))
    
    # Ikigai Venn diagram
    ikigai_img = create_ikigai_venn_diagram({})
    img = Image(ikigai_img, width=4.5*inch, height=4.5*inch)
    elements.append(img)
    
    elements.extend(create_quote_divider(5))
    
    elements.append(PageBreak())
    
    # Career zones based on Holland code
    elements.append(create_subsection_header("Your Career Zones"))
    
    zone_mapping = {
        'R': "🔧 <b>Technical Mastery:</b> Engineering, trades, hands-on problem-solving",
        'I': "🔬 <b>Intellectual Exploration:</b> Research, analysis, scientific discovery",
        'A': "🎨 <b>Creative Expression:</b> Design, arts, innovation, storytelling",
        'S': "🤝 <b>Human Connection:</b> Teaching, counseling, community service",
        'E': "📈 <b>Strategic Leadership:</b> Business, entrepreneurship, influence",
        'C': "📋 <b>Organizational Excellence:</b> Systems, administration, precision",
    }
    
    zones_text = f"""
    Based on your <b>{holland_code}</b> Holland Code, your primary career zones are:<br/>
    <br/>
    {zone_mapping.get(holland_code[0], '')}<br/>
    {zone_mapping.get(holland_code[1], '')}<br/>
    {zone_mapping.get(holland_code[2], '')}<br/>
    <br/>
    Careers at the intersection of these zones will feel most fulfilling!
    """
    elements.append(create_body_text(zones_text))
    
    elements.append(PageBreak())
    
    return elements


def create_career_recommendations(holland_code: str, bigfive_scores: Dict) -> List:
    """Create personalized career recommendations"""
    elements = []
    
    elements.append(create_section_header("Your Career Pathways", "🎯"))
    
    intro = """
    Based on your assessment results, here are career paths that align with your interests, 
    personality, and strengths. These are starting points—explore what resonates!
    """
    elements.append(create_body_text(intro))
    
    elements.append(Spacer(1, 0.3 * inch))
    
    # Career mapping (simplified - in production, use more sophisticated matching)
    career_map = {
        'RIA': ['Data Engineer', 'Research Scientist', 'Lab Technician', 'Biomedical Engineer'],
        'RIE': ['Software Architect', 'Technology Consultant', 'Systems Engineer'],
        'IAS': ['UX Researcher', 'Educational Psychologist', 'Art Therapist'],
        'IAE': ['Product Manager', 'Design Strategist', 'Innovation Consultant'],
        'ASE': ['Marketing Creative', 'Brand Strategist', 'Social Entrepreneur'],
        'SEC': ['HR Manager', 'Training Coordinator', 'Operations Manager'],
        'ECS': ['Business Analyst', 'Project Manager', 'Customer Success Manager'],
    }
    
    # Get careers (default to first 5 if code not in map)
    careers = career_map.get(holland_code, [
        'Career Counselor', 'Assessment Specialist', 'Learning Designer', 
        'Organizational Development', 'Talent Acquisition'
    ])[:5]
    
    career_text = "<b>Recommended Career Paths:</b><br/><br/>"
    for i, career in enumerate(careers, 1):
        career_text += f"{i}. <b>{career}</b><br/>"
    
    elements.append(create_body_text(career_text))
    
    elements.append(Spacer(1, 0.4 * inch))
    
    next_steps = """
    <b>Next Steps:</b><br/>
    • Research these careers online (O*NET, LinkedIn, industry blogs)<br/>
    • Informational interviews with professionals in these fields<br/>
    • Job shadowing or internships to test the waters<br/>
    • Skill-building through courses, certifications, or projects<br/>
    """
    elements.append(create_body_text(next_steps))
    
    elements.append(PageBreak())
    
    return elements


def create_action_plan(flags: Dict, riasec_scores: Dict) -> List:
    """Create personalized action plan"""
    elements = []
    
    elements.append(create_section_header("Your Action Plan", "📝"))
    
    intro = """
    Knowledge without action is just information. Here's your personalized roadmap to turn 
    insights into growth!
    """
    elements.append(create_body_text(intro))
    
    elements.append(Spacer(1, 0.3 * inch))
    
    # Generate actions based on flags
    actions = ["<b>Immediate Actions (This Week):</b><br/>"]
    
    if flags.get('procrastination_risk'):
        actions.append("• Time-block your calendar: Schedule focused work sessions<br/>")
    if flags.get('perfectionism_risk'):
        actions.append("• Practice 'good enough': Set 80% completion goals<br/>")
    if flags.get('low_grit_risk'):
        actions.append("• Start a 30-day challenge to build persistence<br/>")
    if not flags.get('growth_mindset'):
        actions.append("• Journal daily: 'What did I learn today?'<br/>")
    
    actions.append("• Research 2-3 careers from your recommendations<br/>")
    actions.append("• Update your LinkedIn profile with new insights<br/>")
    
    actions.append("<br/><b>Short-Term Goals (This Month):</b><br/>")
    actions.append("• Connect with 3 professionals in your interest areas<br/>")
    actions.append("• Enroll in one skill-building course or workshop<br/>")
    actions.append("• Create a portfolio project showcasing your strengths<br/>")
    
    actions.append("<br/><b>Long-Term Vision (6-12 Months):</b><br/>")
    actions.append("• Gain experience through internships or volunteer work<br/>")
    actions.append("• Build a professional network in your target industry<br/>")
    actions.append("• Retake this assessment to track your growth!<br/>")
    
    elements.append(create_body_text("".join(actions)))
    
    elements.append(PageBreak())
    
    return elements


def create_about_page() -> List:
    """Create about CaRhythm page"""
    elements = []
    
    elements.append(create_section_header("About CaRhythm", "🎓"))
    
    about_text = """
    <b>CaRhythm</b> is an integrated career assessment platform designed to help students and 
    professionals discover their optimal career pathways through evidence-based psychometric tools.
    <br/><br/>
    <b>Our Approach:</b><br/>
    • <b>Holistic:</b> Combining interests (RIASEC), personality (Big Five), and work habits (Behavioral traits)<br/>
    • <b>Evidence-Based:</b> Using validated assessment frameworks<br/>
    • <b>Actionable:</b> Providing personalized, practical guidance<br/>
    • <b>Growth-Oriented:</b> Supporting development, not just diagnosis<br/>
    <br/>
    <b>Contact Us:</b><br/>
    📧 Email: support@carhythm.com<br/>
    🌐 Website: www.carhythm.com<br/>
    <br/>
    <i>This report is confidential and intended for your personal development. 
    We hope it illuminates your path forward!</i>
    """
    elements.append(create_body_text(about_text))
    
    elements.extend(create_quote_divider(0))
    
    thank_you = """
    <br/><br/>
    <b>Thank you for trusting CaRhythm with your career journey.</b><br/>
    <b>Your story is just beginning. Go write it! ✨</b>
    """
    elements.append(Paragraph(thank_you, ParagraphStyle(
        name='ThankYou',
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=BRAND_PRIMARY,
        alignment=1,  # Center
        spaceAfter=0.3*inch
    )))
    
    return elements


# ============================================================================
# FREEMIUM FUNCTIONS - Blur & Premium CTAs
# ============================================================================

def create_blurred_premium_section(title: str, subtitle: str = "", 
                                   section_emoji: str = "🔒",
                                   height: float = 4.5) -> List:
    """
    Create blurred premium section with modern overlay
    
    Args:
        title: Section title (e.g., "Your Ikigai: Career Sweet Spot")
        subtitle: Optional description
        section_emoji: Emoji for section header
        height: Height in inches for blur block
    
    Returns:
        List of ReportLab elements
    """
    elements = []
    
    # Section header (visible)
    elements.append(create_section_header(title, section_emoji))
    
    if subtitle:
        subtitle_style = ParagraphStyle(
            'SubtitleText',
            fontSize=11,
            textColor=BRAND_TEXT,
            alignment=TA_CENTER,
            spaceAfter=0.3 * inch,
            fontName='Helvetica-Oblique'
        )
        elements.append(Paragraph(subtitle, subtitle_style))
    
    # Modern blur overlay with diagonal pattern
    blur_style = ParagraphStyle(
        'BlurOverlay',
        fontSize=48,
        textColor=colors.Color(0.85, 0.85, 0.85, alpha=0.8),
        alignment=TA_CENTER,
        leading=60
    )
    
    # Create blur pattern (repeating diagonal text)
    blur_lines = []
    num_lines = int(height * 3)  # ~3 lines per inch
    for i in range(num_lines):
        if i % 2 == 0:
            blur_lines.append("   PREMIUM   " * 10)
        else:
            blur_lines.append("      PREMIUM   " * 10)
    
    blur_text = "<br/>".join(blur_lines)
    
    blur_data = [[Paragraph(blur_text, blur_style)]]
    
    blur_table = Table(blur_data, colWidths=[6.5*inch], 
                      rowHeights=[height*inch])
    blur_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 2, BRAND_PURPLE),
        ('LINEBELOW', (0, 0), (-1, -1), 3, BRAND_CORAL),
    ]))
    
    elements.append(blur_table)
    
    # Large padlock overlay
    lock_style = ParagraphStyle(
        'PadlockOverlay',
        fontSize=64,
        textColor=BRAND_CORAL,
        alignment=TA_CENTER,
        spaceBefore=-height*inch/2 - 0.5*inch,  # Overlay on blur
        spaceAfter=height*inch/2 - 1*inch
    )
    elements.append(Paragraph('🔓', lock_style))
    
    # "Available in Premium" text
    overlay_text_style = ParagraphStyle(
        'PremiumOverlayText',
        fontSize=18,
        textColor=BRAND_PURPLE,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=0.15 * inch
    )
    elements.append(Paragraph('<b>Available in Premium Report</b>', overlay_text_style))
    
    # Feature description
    feature_style = ParagraphStyle(
        'FeatureText',
        fontSize=11,
        textColor=BRAND_TEXT,
        fontName='Helvetica',
        alignment=TA_CENTER,
        spaceAfter=0.3 * inch
    )
    
    feature_descriptions = {
        "Ikigai": "Unlock your personalized Ikigai mapping, career zones, and purpose alignment",
        "Career": "Discover 5+ tailored career matches with detailed pathways and salary insights",
        "Action": "Get your 12-month action roadmap with immediate, short-term, and long-term goals"
    }
    
    # Find matching description
    feature_desc = "Unlock comprehensive career guidance and personalized insights"
    for key, desc in feature_descriptions.items():
        if key.lower() in title.lower():
            feature_desc = desc
            break
    
    elements.append(Paragraph(feature_desc, feature_style))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    return elements


def create_mini_qr_cta(checkout_url: str, section_name: str, 
                       discount_code: str = "LAUNCH50") -> List:
    """
    Create mini QR code CTA after blurred section
    
    Args:
        checkout_url: Base URL for premium checkout
        section_name: Name of section (for UTM tracking)
        discount_code: Discount code to embed in URL
    
    Returns:
        List of ReportLab elements
    """
    elements = []
    
    # Build URL with UTM parameters and discount
    utm_params = f"utm_source=pdf_free&utm_medium=qr_code&utm_content={section_name.replace(' ', '_').lower()}&discount={discount_code}"
    full_url = f"{checkout_url}?{utm_params}"
    
    # CTA box
    cta_style = ParagraphStyle(
        'MiniCTA',
        fontSize=12,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        leading=16
    )
    
    cta_data = [[Paragraph(
        f'<b>🎁 Unlock this section now</b><br/>'
        f'<font size=10>Scan below for 50% LAUNCH DISCOUNT</font>',
        cta_style
    )]]
    
    cta_table = Table(cta_data, colWidths=[4.5*inch])
    cta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BRAND_CORAL),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
    ]))
    
    elements.append(cta_table)
    elements.append(Spacer(1, 0.2 * inch))
    
    # Generate and add QR code
    qr_buffer = generate_qr_code(full_url, size=250)
    qr_img = Image(qr_buffer, width=1.3*inch, height=1.3*inch)
    
    # Center QR code
    qr_data = [[qr_img]]
    qr_table = Table(qr_data, colWidths=[2*inch])
    qr_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    elements.append(qr_table)
    
    # QR instruction
    qr_text_style = ParagraphStyle(
        'QRMiniText',
        fontSize=9,
        textColor=BRAND_TEXT,
        fontName='Helvetica-Oblique',
        alignment=TA_CENTER,
        spaceAfter=0.3 * inch,
        spaceBefore=0.1 * inch
    )
    elements.append(Paragraph('📱 Scan to claim your discount', qr_text_style))
    
    elements.append(PageBreak())
    
    return elements


def create_large_discount_cta_page(checkout_url: str, student_name: str,
                                   discount_code: str = "LAUNCH50") -> List:
    """
    Create final premium CTA page with large QR code and compelling copy
    
    Args:
        checkout_url: Base URL for premium checkout
        student_name: User's name for personalization
        discount_code: Discount code to display
    
    Returns:
        List of ReportLab elements
    """
    elements = []
    
    elements.append(Spacer(1, 0.8 * inch))
    
    # Main headline
    headline_style = ParagraphStyle(
        'CTAHeadline',
        fontSize=32,
        textColor=BRAND_PURPLE,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=0.3 * inch,
        leading=38
    )
    elements.append(Paragraph(f'{student_name},<br/>Your Career Compass Awaits', headline_style))
    
    # Subheadline
    subhead_style = ParagraphStyle(
        'CTASubhead',
        fontSize=16,
        textColor=BRAND_CORAL,
        fontName='Helvetica-Oblique',
        alignment=TA_CENTER,
        spaceAfter=0.5 * inch,
        leading=22
    )
    elements.append(Paragraph(
        "You've seen your <b>Identity</b>. Now unlock your <b>Destiny</b>.",
        subhead_style
    ))
    
    # Value proposition box
    value_style = ParagraphStyle(
        'ValueProp',
        fontSize=13,
        textColor=BRAND_TEXT,
        fontName='Helvetica',
        alignment=TA_LEFT,
        leading=20,
        leftIndent=20,
        bulletIndent=10
    )
    
    value_text = """
    <b>Premium Report Includes:</b><br/>
    <br/>
    ✨ <b>Ikigai Career Mapping</b> - Find where passion meets profession<br/>
    🎯 <b>5+ Personalized Career Matches</b> - With salary insights & growth projections<br/>
    📈 <b>12-Month Action Roadmap</b> - Immediate, short & long-term goals<br/>
    💼 <b>Market Reality Analysis</b> - Burnout risks & industry trends<br/>
    🔄 <b>Lifetime Updates</b> - Retake & track your growth journey<br/>
    """
    
    value_data = [[Paragraph(value_text, value_style)]]
    value_table = Table(value_data, colWidths=[5.5*inch])
    value_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BRAND_LIGHT),
        ('PADDING', (0, 0), (-1, -1), 20),
        ('BOX', (0, 0), (-1, -1), 2, BRAND_CORAL),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    
    elements.append(value_table)
    elements.append(Spacer(1, 0.4 * inch))
    
    # Discount banner
    discount_style = ParagraphStyle(
        'DiscountBanner',
        fontSize=24,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        leading=28
    )
    
    discount_data = [[Paragraph(
        f'🎉 <b>EXCLUSIVE LAUNCH OFFER</b><br/>'
        f'<font size=18>50% OFF - First 100 Users Only</font><br/>'
        f'<font size=14>Use code: {discount_code}</font>',
        discount_style
    )]]
    
    discount_table = Table(discount_data, colWidths=[5*inch])
    discount_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BRAND_PURPLE),
        ('PADDING', (0, 0), (-1, -1), 20),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    elements.append(discount_table)
    elements.append(Spacer(1, 0.4 * inch))
    
    # Large QR code
    utm_params = f"utm_source=pdf_free&utm_medium=qr_code&utm_campaign=final_cta&discount={discount_code}"
    full_url = f"{checkout_url}?{utm_params}"
    
    qr_buffer = generate_qr_code(full_url, size=400)
    qr_img = Image(qr_buffer, width=3*inch, height=3*inch)
    
    # Center QR with border
    qr_data = [[qr_img]]
    qr_table = Table(qr_data, colWidths=[3.5*inch])
    qr_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 3, BRAND_CORAL),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(qr_table)
    
    # QR instruction
    qr_final_style = ParagraphStyle(
        'QRFinalText',
        fontSize=14,
        textColor=BRAND_TEXT,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=0.2 * inch,
        spaceBefore=0.3 * inch
    )
    elements.append(Paragraph('📱 <b>Scan now to claim your 50% discount</b>', qr_final_style))
    
    # Urgency message
    urgency_style = ParagraphStyle(
        'UrgencyText',
        fontSize=10,
        textColor=BRAND_CORAL,
        fontName='Helvetica-Oblique',
        alignment=TA_CENTER
    )
    elements.append(Paragraph('⏰ <i>Limited time offer - Don\'t miss out!</i>', urgency_style))
    
    elements.append(PageBreak())
    
    return elements


def generate_qr_code(url: str, size: int = 300) -> BytesIO:
    """Generate QR code for given URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer


def generate_pdf_report(response_data: Dict, scores_data: Dict,
                       is_free_version: bool = False,
                       checkout_url: str = "https://carhythm.com/paid",
                       discount_code: str = "LAUNCH50") -> BytesIO:
    """
    Main function to generate comprehensive PDF report (V1 freemium model)
    
    Args:
        response_data: Student response with name, email, etc.
        scores_data: v1.1 assessment scores (parsed JSON fields)
        is_free_version: If True, blur premium sections (Ikigai, Careers, Action Plan)
        checkout_url: URL for premium upgrade (default: /paid)
        discount_code: Discount code for premium offer
        
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    
    # Parse scores (using new field names from api_v2.py)
    riasec_raw_scores = scores_data.get('riasec_raw_scores', {})
    riasec_strength_labels = scores_data.get('riasec_strength_labels', {})
    holland_code = scores_data.get('holland_code', 'RIA')
    
    bigfive_raw_scores = scores_data.get('bigfive_raw_scores', {})
    bigfive_strength_labels = scores_data.get('bigfive_strength_labels', {})
    
    behavioral_strength_labels = scores_data.get('behavioral_strength_labels', {})
    behavioral_flags = scores_data.get('behavioral_flags', {})
    ikigai_zones = scores_data.get('ikigai_zones', {})
    behavioral_raw_scores = scores_data.get('behavioral_raw_scores', {})
    
    student_name = response_data.get('student_name', 'Student')
    
    # Create document with custom canvas
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=1*inch
    )
    
    # Build story elements
    story = []
    
    # ========== FREE SECTIONS (Always visible) ==========
    
    # 1. Cover Page
    story.extend(create_cover_page())
    
    # 2. Welcome Letter
    story.extend(create_welcome_letter(student_name))
    
    # 3. RIASEC Section (3-4 pages)
    story.extend(create_riasec_explanation_page())
    story.extend(create_riasec_results_pages(riasec_raw_scores, holland_code))
    
    # 4. Big Five Section (2-3 pages)
    story.extend(create_bigfive_explanation_page())
    story.extend(create_bigfive_results_pages(bigfive_raw_scores, bigfive_strength_labels))
    
    # 5. Behavioral Section (2 pages)
    story.extend(create_behavioral_explanation_page())
    story.extend(create_behavioral_results_page(behavioral_strength_labels, behavioral_flags, behavioral_raw_scores))
    
    # ========== PREMIUM SECTIONS (Conditional) ==========
    
    if is_free_version:
        # FREEMIUM: Blur premium sections with CTAs
        
        # 6. Complete Strength Profile (BLURRED)
        story.extend(create_blurred_premium_section(
            "Your Complete Strength Profile",
            "Comprehensive heatmap showing your strengths across all domains at a glance",
            "🔒",
            height=3.5
        ))
        story.extend(create_mini_qr_cta(checkout_url, "Complete Strength Profile", discount_code))
        
        # 7. Ikigai (BLURRED)
        story.extend(create_blurred_premium_section(
            "Your Ikigai: Career Sweet Spot",
            "Japanese concept of 'reason for being' — where passion meets profession",
            "🔒",
            height=5.0
        ))
        story.extend(create_mini_qr_cta(checkout_url, "Ikigai Career Zones", discount_code))
        
        # 8. Career Recommendations (BLURRED)
        story.extend(create_blurred_premium_section(
            "Your Career Pathways",
            "5+ personalized career matches based on your unique profile",
            "🔒",
            height=4.5
        ))
        story.extend(create_mini_qr_cta(checkout_url, "Career Recommendations", discount_code))
        
        # 9. Action Plan (BLURRED)
        story.extend(create_blurred_premium_section(
            "Your Action Plan",
            "12-month roadmap with immediate, short-term, and long-term goals",
            "🔒",
            height=4.0
        ))
        story.extend(create_mini_qr_cta(checkout_url, "Action Plan", discount_code))
        
        # 10. Large Discount CTA Page
        story.extend(create_large_discount_cta_page(checkout_url, student_name, discount_code))
        
    else:
        # PREMIUM: Show full sections
        
        # 6. Comprehensive Heatmap
        if behavioral_raw_scores:
            story.append(create_section_header("Your Complete Strength Profile", "🔥"))
            explanation = """
            This heatmap shows your strengths across all domains at a glance. 
            Coral tones indicate stronger areas, purple shows areas for development.
            """
            story.append(create_body_text(explanation))
            story.append(Spacer(1, 0.2 * inch))
            heatmap_img = create_strength_heatmap(riasec_raw_scores, bigfive_raw_scores, behavioral_raw_scores)
            story.append(Image(heatmap_img, width=6.5*inch, height=3.5*inch))
            story.append(PageBreak())
        
        # 7. Ikigai Guidance (2 pages)
        story.extend(create_ikigai_pages(holland_code, riasec_raw_scores))
        
        # 8. Career Recommendations (1-2 pages)
        story.extend(create_career_recommendations(holland_code, bigfive_raw_scores))
        
        # 9. Action Plan (1 page)
        story.extend(create_action_plan(behavioral_flags, riasec_raw_scores))
    
    # 11. About CaRhythm (Always visible)
    story.extend(create_about_page())
    
    # Build PDF with numbered pages
    doc.build(story, canvasmaker=NumberedCanvas)
    
    buffer.seek(0)
    return buffer


# ============================================================================
# V2 TEMPLATE - Modern Archetype-Focused Design
# ============================================================================

def shaped_text(text: str, lang: Optional[str] = None, auto_detect: bool = True) -> str:
    """
    Shape text for RTL languages (Arabic, Hebrew).
    Auto-detects Arabic characters if auto_detect=True.
    
    Args:
        text: Input text string
        lang: Language code ('ar', 'he', etc.) or None for auto-detect
        auto_detect: If True, detect Arabic characters automatically
        
    Returns:
        Shaped text ready for ReportLab rendering
    """
    if not RTL_SUPPORT or not text:
        return text
    
    # Auto-detect Arabic characters
    has_arabic = auto_detect and any('\u0600' <= c <= '\u06FF' for c in text)
    
    if lang in ('ar', 'arabic') or has_arabic:
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except:
            return text
    
    return text


def get_font_name(style: str = 'regular') -> str:
    """Get font name with fallback to Helvetica"""
    if not FONTS_AVAILABLE:
        font_map = {
            'regular': 'Helvetica',
            'bold': 'Helvetica-Bold',
            'italic': 'Helvetica-Oblique'
        }
        return font_map.get(style, 'Helvetica')
    
    font_map = {
        'regular': 'Poppins',
        'bold': 'Poppins-Bold',
        'italic': 'Poppins-Italic'
    }
    return font_map.get(style, 'Poppins')


def create_high_res_radar_chart(labels: List[str], values: List[float], 
                                max_value: float, title: str) -> BytesIO:
    """Create high-resolution radar chart (600 dpi) for print quality"""
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values_plot = values + [values[0]]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'), dpi=600)
    ax.plot(angles, values_plot, 'o-', linewidth=3, color='#14b8a6', markersize=10)
    ax.fill(angles, values_plot, alpha=0.3, color='#14b8a6')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=12, weight='bold')
    ax.set_ylim(0, max_value)
    ax.set_yticks(np.linspace(0, max_value, 5))
    ax.set_title(title, size=16, weight='bold', pad=25, color='#134e4a')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.spines['polar'].set_color('#14b8a6')
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=600, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    img_buffer.seek(0)
    
    return img_buffer


def create_circular_gauge(value: float, max_value: float, label: str, 
                         color: str = '#14b8a6') -> BytesIO:
    """Create circular gauge visualization"""
    fig, ax = plt.subplots(figsize=(3, 3), dpi=300)
    
    # Create circle
    percentage = (value / max_value) * 100
    circle = plt.Circle((0.5, 0.5), 0.4, color='white', ec=color, linewidth=8, fill=False)
    ax.add_patch(circle)
    
    # Add filled arc for percentage
    theta = np.linspace(0, 2 * np.pi * (percentage / 100), 100)
    x = 0.5 + 0.4 * np.cos(theta - np.pi/2)
    y = 0.5 + 0.4 * np.sin(theta - np.pi/2)
    ax.plot(x, y, color=color, linewidth=8)
    
    # Add percentage text
    ax.text(0.5, 0.5, f'{percentage:.0f}%', ha='center', va='center',
           fontsize=24, weight='bold', color=color)
    
    # Add label
    ax.text(0.5, 0.15, label, ha='center', va='center',
           fontsize=10, weight='bold', color='#134e4a')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_aspect('equal')
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', 
               facecolor='white', transparent=True)
    plt.close(fig)
    img_buffer.seek(0)
    
    return img_buffer


def generate_qr_code(url: str, size: int = 300) -> BytesIO:
    """Generate QR code for given URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer


def create_blurred_overlay_table(data: List[List[str]], blur_text: str = "Available in Premium") -> Table:
    """Create table with blurred/locked overlay effect"""
    table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    
    # Style with semi-transparent overlay effect
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), get_font_name('bold')),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.Color(0.5, 0.5, 0.5, alpha=0.3)),
    ]))
    
    return table


def extract_template_fields_v2(response_data: Dict, scores_data: Dict) -> Dict:
    """
    Extract and compute template fields for V2 PDF
    
    Returns dict with all template variables:
        - user_name, archetype_title, archetype_tagline, archetype_icon_url
        - riasec_code, top_big5_trait, top_big5_score
        - radar_chart_image (BytesIO), career_matches (list)
        - lowest_behavior_trait, friction_warning
        - gauges: nature_gauge, nurture_gauge, rhythm_gauge
    """
    fields = {}
    
    # Basic user info
    fields['user_name'] = shaped_text(response_data.get('student_name', 'Student'))
    fields['user_email'] = response_data.get('student_email', '')
    fields['date'] = datetime.now().strftime('%B %d, %Y')
    
    # RIASEC data
    riasec_scores = scores_data.get('riasec_raw_scores', {})
    holland_code = scores_data.get('holland_code', 'RIA')
    fields['riasec_code'] = holland_code
    fields['holland_code'] = holland_code
    
    # Big Five data
    bigfive_scores = scores_data.get('bigfive_raw_scores', {})
    bigfive_labels = scores_data.get('bigfive_strength_labels', {})
    
    # Find top Big Five trait
    trait_names = {'O': 'Openness', 'C': 'Conscientiousness', 'E': 'Extraversion',
                   'A': 'Agreeableness', 'N': 'Neuroticism'}
    if bigfive_scores:
        top_trait_code = max(bigfive_scores, key=bigfive_scores.get)
        fields['top_big5_trait'] = trait_names.get(top_trait_code, 'Openness')
        fields['top_big5_score'] = bigfive_scores.get(top_trait_code, 0)
        fields['top_big5_percentage'] = (fields['top_big5_score'] / 25) * 100
    else:
        fields['top_big5_trait'] = 'Openness'
        fields['top_big5_score'] = 0
        fields['top_big5_percentage'] = 0
    
    # Behavioral data
    behavioral_scores = scores_data.get('behavioral_raw_scores', {})
    behavioral_labels = scores_data.get('behavioral_strength_labels', {})
    behavioral_flags = scores_data.get('behavioral_flags', {})
    
    # Find lowest behavioral trait for friction warning
    trait_mapping = {
        'motivation_type': 'Motivation',
        'grit_persistence': 'Grit',
        'self_efficacy': 'Self-Regulation',
        'resilience': 'Resilience',
        'learning_orientation': 'Growth Mindset',
        'empathy': 'Empathy',
        'task_start_tempo': 'Task Initiation'
    }
    
    if behavioral_scores:
        lowest_trait_key = min(behavioral_scores, key=behavioral_scores.get)
        fields['lowest_behavior_trait'] = trait_mapping.get(lowest_trait_key, 'Self-Regulation')
        fields['lowest_behavior_score'] = behavioral_scores.get(lowest_trait_key, 0)
    else:
        fields['lowest_behavior_trait'] = 'Self-Regulation'
        fields['lowest_behavior_score'] = 0
    
    # Archetype (simplified - can be expanded with more logic)
    archetype_map = {
        'RIA': ('THE PRAGMATIC INNOVATOR', "The Engineer's Mind with an Artist's Heart"),
        'RIE': ('THE SYSTEMS ARCHITECT', "Building Solutions at Scale"),
        'IAS': ('THE MINDFUL CREATOR', "Where Science Meets Human Connection"),
        'IAE': ('THE STRATEGIC VISIONARY', "Innovation Backed by Analysis"),
        'ASE': ('THE CREATIVE CATALYST', "Inspiring Change Through Expression"),
        'SEC': ('THE ORGANIZATIONAL DIPLOMAT', "Harmony Through Structure"),
        'ECS': ('THE BUSINESS OPERATOR', "Efficiency Meets Leadership"),
    }
    
    archetype = archetype_map.get(holland_code, ('THE CAREER EXPLORER', "Finding Your Unique Path"))
    fields['archetype_title'] = archetype[0]
    fields['archetype_tagline'] = archetype[1]
    fields['archetype_icon_url'] = None  # Can add icon mapping later
    
    # Generate radar chart
    riasec_labels = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional']
    riasec_values = [riasec_scores.get(code, 0) for code in ['R', 'I', 'A', 'S', 'E', 'C']]
    fields['radar_chart_image'] = create_high_res_radar_chart(
        riasec_labels, riasec_values, 15, "Your Psychometric Radar"
    )
    
    # Generate circular gauges
    # Nature: Top Big Five percentage
    fields['nature_gauge'] = create_circular_gauge(
        fields['top_big5_score'], 25, 
        f"{fields['top_big5_percentage']:.0f}% {fields['top_big5_trait']}"
    )
    
    # Nurture: RIASEC code representation (average of top 3)
    top_3_riasec = sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    nurture_avg = sum(score for _, score in top_3_riasec) / 3 if top_3_riasec else 0
    fields['nurture_gauge'] = create_circular_gauge(
        nurture_avg, 15, holland_code
    )
    
    # Rhythm: Behavioral energy (average of all behavioral traits)
    if behavioral_scores:
        rhythm_avg = sum(behavioral_scores.values()) / len(behavioral_scores)
        rhythm_level = "High Voltage" if rhythm_avg > 10 else "Steady Flow" if rhythm_avg > 7 else "Building Momentum"
    else:
        rhythm_avg = 0
        rhythm_level = "Discovering"
    
    fields['rhythm_gauge'] = create_circular_gauge(
        rhythm_avg, 15, rhythm_level
    )
    
    # Career matches (simplified - would use actual matching algorithm)
    career_matches_map = {
        'RIA': [
            {'title': 'Data Engineer', 'score': 94, 'reason': 'Requires the logic of an Investigator and the hands-on skills of a Realist'},
            {'title': 'UX Researcher', 'score': 91, 'reason': 'Combines analytical thinking with creative problem-solving'},
            {'title': 'Biomedical Engineer', 'score': 88, 'reason': 'Perfect blend of technical skills and scientific inquiry'},
        ],
        'IAS': [
            {'title': 'Clinical Psychologist', 'score': 93, 'reason': 'Uses scientific methods to help others with creative empathy'},
            {'title': 'Art Therapist', 'score': 90, 'reason': 'Combines therapeutic knowledge with artistic expression'},
            {'title': 'Educational Researcher', 'score': 87, 'reason': 'Studies learning through both data and human understanding'},
        ],
    }
    
    default_careers = [
        {'title': 'Career Counselor', 'score': 85, 'reason': 'Helps others discover their path using assessment insights'},
        {'title': 'Learning Designer', 'score': 82, 'reason': 'Creates educational experiences tailored to different profiles'},
        {'title': 'Talent Development Specialist', 'score': 80, 'reason': 'Matches people to roles based on their strengths'},
    ]
    
    fields['career_matches'] = career_matches_map.get(holland_code, default_careers)
    
    return fields


def create_hero_page_v2(fields: Dict) -> List:
    """
    Create V2 Hero Page (Page 1)
    - Header: Logo (left) + Date & Name (right)
    - Archetype Title (32pt)
    - Tagline (italic serif)
    - Large radar chart
    - Three circular gauges (Nature, Nurture, Rhythm)
    - Footer CTA
    """
    elements = []
    
    # Header row: Logo left, Date/Name right
    header_data = [['']]
    header_table = Table(header_data, colWidths=[6.5*inch])
    elements.append(header_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Add logo
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image(LOGO_PATH, width=1.2*inch, height=1.2*inch, kind='proportional')
            elements.append(logo)
        except:
            pass
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Date and User Name (right aligned)
    date_style = ParagraphStyle(
        'DateHeader',
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_RIGHT,
        fontName=get_font_name('regular')
    )
    elements.append(Paragraph(f"{fields['date']} | {fields['user_name']}", date_style))
    
    elements.append(Spacer(1, 0.5 * inch))
    
    # Archetype Title (Large, 32pt)
    title_style = ParagraphStyle(
        'ArchetypeTitle',
        fontSize=32,
        textColor=BRAND_PRIMARY,
        alignment=TA_CENTER,
        fontName=get_font_name('bold'),
        leading=38,
        spaceAfter=0.2 * inch
    )
    elements.append(Paragraph(fields['archetype_title'], title_style))
    
    # Tagline (Italic/Serif)
    tagline_style = ParagraphStyle(
        'ArchetypeTagline',
        fontSize=16,
        textColor=BRAND_SECONDARY,
        alignment=TA_CENTER,
        fontName='Times-Italic',  # Serif italic
        spaceAfter=0.4 * inch
    )
    elements.append(Paragraph(f'<i>"{fields["archetype_tagline"]}"</i>', tagline_style))
    
    elements.append(Spacer(1, 0.3 * inch))
    
    # Large Radar Chart
    radar_img = Image(fields['radar_chart_image'], width=4*inch, height=4*inch)
    elements.append(radar_img)
    
    elements.append(Spacer(1, 0.3 * inch))
    
    # Three Circular Gauges in a row
    gauge_data = [[
        Image(fields['nature_gauge'], width=1.8*inch, height=1.8*inch),
        Image(fields['nurture_gauge'], width=1.8*inch, height=1.8*inch),
        Image(fields['rhythm_gauge'], width=1.8*inch, height=1.8*inch)
    ]]
    
    gauge_labels = [['<b>Nature</b><br/>(Personality)', '<b>Nurture</b><br/>(Interests)', '<b>Rhythm</b><br/>(Energy)']]
    
    gauge_table = Table(gauge_data, colWidths=[2*inch, 2*inch, 2*inch])
    gauge_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(gauge_table)
    
    label_style = ParagraphStyle('GaugeLabel', fontSize=9, alignment=TA_CENTER, 
                                 fontName=get_font_name('bold'))
    label_table = Table([[Paragraph(label, label_style) for label in gauge_labels[0]]], 
                       colWidths=[2*inch, 2*inch, 2*inch])
    elements.append(label_table)
    
    elements.append(Spacer(1, 0.4 * inch))
    
    # Footer CTA
    footer_style = ParagraphStyle(
        'FooterCTA',
        fontSize=11,
        textColor=BRAND_TEXT,
        alignment=TA_CENTER,
        fontName=get_font_name('regular')
    )
    elements.append(Paragraph('Unlock your full simulation at <b>CaRhythm.com</b>', footer_style))
    
    elements.append(PageBreak())
    
    return elements


def create_science_page_v2(fields: Dict) -> List:
    """
    Create V2 Science Page (Page 2)
    - Title: "Decoding Your Coordinates"
    - Three cards: Brain (Aptitude), Fingerprint (Identity), Compass (Rhythm)
    - Sidebar: "Did you know?" stats
    """
    elements = []
    
    # Section Title
    title_style = ParagraphStyle(
        'ScienceTitle',
        fontSize=24,
        textColor=BRAND_PRIMARY,
        fontName=get_font_name('bold'),
        spaceAfter=0.4 * inch,
        alignment=TA_CENTER
    )
    elements.append(Paragraph('🧬 Decoding Your Coordinates', title_style))
    
    # Card style
    card_style = ParagraphStyle(
        'CardText',
        fontSize=10,
        textColor=BRAND_TEXT,
        fontName=get_font_name('regular'),
        alignment=TA_JUSTIFY,
        leading=14
    )
    
    card_title_style = ParagraphStyle(
        'CardTitle',
        fontSize=14,
        textColor=BRAND_PRIMARY,
        fontName=get_font_name('bold'),
        spaceAfter=0.1 * inch
    )
    
    # Card 1: Brain - Aptitude
    elements.append(Paragraph('🧠 Your Aptitude', card_title_style))
    aptitude_text = """
    <b>RIASEC (Holland Code)</b> measures your natural career interests across six dimensions. 
    Your code <b>{}</b> reveals where you'll find flow—careers that match your innate curiosity 
    and working style. This isn't about what you <i>can</i> do, but what you'll <i>love</i> doing.
    """.format(fields['holland_code'])
    elements.append(Paragraph(aptitude_text, card_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Card 2: Fingerprint - Identity
    elements.append(Paragraph('👤 Your Identity', card_title_style))
    identity_text = """
    <b>The Big Five</b> personality model maps who you are at your core: how you think, feel, 
    and interact with the world. Your strongest trait is <b>{}</b> ({}%), which shapes how you 
    approach challenges, collaborate with others, and find meaning in work.
    """.format(fields['top_big5_trait'], int(fields['top_big5_percentage']))
    elements.append(Paragraph(identity_text, card_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Card 3: Compass - Rhythm
    elements.append(Paragraph('🧭 Your Rhythm', card_title_style))
    rhythm_text = """
    <b>Behavioral Traits</b> measure your work habits, mindset, and energy patterns. These aren't 
    fixed—they're skills you can develop. Your current rhythm shows areas of strength and growth 
    opportunities, helping you optimize performance and avoid burnout.
    """
    elements.append(Paragraph(rhythm_text, card_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Sidebar "Did you know?" box
    didyouknow_style = ParagraphStyle(
        'DidYouKnow',
        fontSize=9,
        textColor=colors.white,
        fontName=get_font_name('italic'),
        alignment=TA_LEFT,
        leading=12
    )
    
    dyk_data = [[Paragraph('💡 <b>Did you know?</b><br/><br/>'
                          'People aligned with their career rhythm are <b>3x less likely</b> '
                          'to experience burnout and report <b>40% higher</b> job satisfaction.',
                          didyouknow_style)]]
    
    dyk_table = Table(dyk_data, colWidths=[5.5*inch])
    dyk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BRAND_SECONDARY),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(dyk_table)
    
    elements.append(PageBreak())
    
    return elements


def create_career_matches_page_v2(fields: Dict) -> List:
    """
    Create V2 Career Matches Page (Page 3)
    - Title: "Your Natural Habitat"
    - Top 3 career matches with scores
    - Blurred "Market Reality" upsell section
    """
    elements = []
    
    # Section Title
    title_style = ParagraphStyle(
        'CareerTitle',
        fontSize=24,
        textColor=BRAND_PRIMARY,
        fontName=get_font_name('bold'),
        spaceAfter=0.4 * inch,
        alignment=TA_CENTER
    )
    elements.append(Paragraph('🎯 Your Natural Habitat', title_style))
    
    intro_style = ParagraphStyle(
        'CareerIntro',
        fontSize=11,
        textColor=BRAND_TEXT,
        fontName=get_font_name('regular'),
        alignment=TA_CENTER,
        spaceAfter=0.3 * inch
    )
    elements.append(Paragraph('Based on your unique profile, these careers align with your strengths:', intro_style))
    
    # Career matches table
    career_data = [['Role', 'Match Score', 'Why It Fits']]
    
    for match in fields['career_matches']:
        career_data.append([
            match['title'],
            f"{match['score']}%",
            match['reason']
        ])
    
    career_table = Table(career_data, colWidths=[2*inch, 1.2*inch, 3*inch])
    career_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), get_font_name('bold')),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
    ]))
    
    elements.append(career_table)
    
    elements.append(Spacer(1, 0.5 * inch))
    
    # Market Reality Section (Blurred Upsell)
    market_title_style = ParagraphStyle(
        'MarketTitle',
        fontSize=18,
        textColor=BRAND_SECONDARY,
        fontName=get_font_name('bold'),
        spaceAfter=0.2 * inch
    )
    elements.append(Paragraph('📊 Market Reality', market_title_style))
    
    # Blurred data table
    blurred_data = [
        ['Career Path', 'Avg. Salary', 'Burnout Risk'],
        ['████████████', '██████', '████'],
        ['████████████', '██████', '████'],
        ['████████████', '██████', '████'],
    ]
    
    blurred_table = Table(blurred_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    blurred_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), get_font_name('bold')),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.lightgrey),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.9, 0.9, 0.9)),
    ]))
    
    elements.append(blurred_table)
    
    # Overlay message
    overlay_style = ParagraphStyle(
        'OverlayText',
        fontSize=14,
        textColor=BRAND_PRIMARY,
        fontName=get_font_name('bold'),
        alignment=TA_CENTER,
        spaceAfter=0.1 * inch,
        spaceBefore=0.2 * inch
    )
    elements.append(Paragraph('🔒 <b>Available in Premium Report</b>', overlay_style))
    
    premium_text_style = ParagraphStyle(
        'PremiumText',
        fontSize=10,
        textColor=BRAND_TEXT,
        fontName=get_font_name('regular'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph('Unlock salary ranges, growth projections, and burnout risk analysis', premium_text_style))
    
    elements.append(PageBreak())
    
    return elements


def create_friction_cta_page_v2(fields: Dict, checkout_url: str = 'https://carhythm.com/premium') -> List:
    """
    Create V2 Friction/CTA Page (Page 4)
    - Warning headline
    - Compass icon (visual friction indicator)
    - Dynamic friction text based on lowest trait
    - Large QR code with CTA
    """
    elements = []
    
    elements.append(Spacer(1, 0.5 * inch))
    
    # Compass icon (using emoji as placeholder)
    icon_style = ParagraphStyle(
        'CompassIcon',
        fontSize=72,
        alignment=TA_CENTER,
        textColor=colors.red,
        spaceAfter=0.3 * inch
    )
    elements.append(Paragraph('🧭', icon_style))
    
    # Warning Headline
    warning_style = ParagraphStyle(
        'WarningHeadline',
        fontSize=28,
        textColor=colors.red,
        fontName=get_font_name('bold'),
        alignment=TA_CENTER,
        spaceAfter=0.3 * inch,
        leading=34
    )
    elements.append(Paragraph('⚠️ Warning: Friction Detected', warning_style))
    
    # Dynamic friction text
    friction_style = ParagraphStyle(
        'FrictionText',
        fontSize=12,
        textColor=BRAND_TEXT,
        fontName=get_font_name('regular'),
        alignment=TA_CENTER,
        leading=18,
        spaceAfter=0.5 * inch
    )
    
    friction_text = f"""
    Your <b>Identity</b> matches your career suggestions, but your Behavioral Score in 
    <b>{fields['lowest_behavior_trait']}</b> indicates a potential blind spot.<br/><br/>
    
    Without addressing this, you may experience friction in:<br/>
    • Performance consistency<br/>
    • Work-life balance<br/>
    • Long-term satisfaction<br/>
    """
    
    elements.append(Paragraph(friction_text, friction_style))
    
    elements.append(Spacer(1, 0.3 * inch))
    
    # CTA Box
    cta_box_style = ParagraphStyle(
        'CTABox',
        fontSize=16,
        textColor=colors.white,
        fontName=get_font_name('bold'),
        alignment=TA_CENTER,
        leading=22
    )
    
    cta_data = [[Paragraph("Don't fly blind.<br/><br/>"
                          '<font size=14>Get the <b>50-Scenario Simulation</b></font><br/><br/>'
                          '<font size=11>Deep-dive personality insights • Career roadmap • Risk mitigation strategies</font>',
                          cta_box_style)]]
    
    cta_table = Table(cta_data, colWidths=[5*inch])
    cta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BRAND_PRIMARY),
        ('PADDING', (0, 0), (-1, -1), 20),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(cta_table)
    
    elements.append(Spacer(1, 0.4 * inch))
    
    # Generate QR code with UTM parameters
    utm_url = f"{checkout_url}?utm_source=pdf_report&utm_medium=qr_code&utm_campaign=friction_cta"
    qr_buffer = generate_qr_code(utm_url, size=400)
    qr_img = Image(qr_buffer, width=2.5*inch, height=2.5*inch)
    
    qr_data = [[qr_img]]
    qr_table = Table(qr_data, colWidths=[3*inch])
    qr_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    elements.append(qr_table)
    
    # QR instruction
    qr_text_style = ParagraphStyle(
        'QRText',
        fontSize=10,
        textColor=BRAND_TEXT,
        fontName=get_font_name('regular'),
        alignment=TA_CENTER,
        spaceAfter=0.3 * inch,
        spaceBefore=0.2 * inch
    )
    elements.append(Paragraph('📱 Scan to unlock your premium report', qr_text_style))
    
    elements.append(PageBreak())
    
    return elements


