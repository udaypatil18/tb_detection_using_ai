"""
PDF Report Generator for Bone Cancer Detection Results
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from PIL import Image as PILImage

def create_report_pdf(
    original_image_path: str,
    segmentation_path: str = None,
    gradcam_path: str = None,
    detection_results: dict = None,
    llama_report: str = None,
    output_dir: str = "static/reports"
):
    """
    Create a PDF report containing the analysis results and images.
    
    Args:
        original_image_path: Path to the uploaded X-ray image
        segmentation_path: Optional path to the tumor segmentation image
        gradcam_path: Optional path to the GradCAM image
        detection_results: Dictionary containing multitask model results
        llama_report: Optional string containing the LLaMA generated report
    Returns:
        Path to the generated PDF file
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Styles and content elements (must be before any use)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, alignment=1, spaceAfter=12, fontName='Helvetica-Bold')
    subheading_style = ParagraphStyle('Subheading', parent=styles['Heading2'], fontSize=14, alignment=1, spaceAfter=8, fontName='Helvetica-Oblique')
    section_title = ParagraphStyle('SectionTitle', parent=styles['Heading2'], fontSize=13, spaceAfter=8, fontName='Helvetica-Bold')
    normal_style = styles['Normal']
    elements = []

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"bone_cancer_report_{timestamp}.pdf")

    # Header with logo (reduced spacing before logo)
    elements.append(Spacer(1, 6))
    logo_path = os.path.join('static', 'logo.png')
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=48, height=48))
        elements.append(Spacer(1, 4))
    elements.append(Paragraph("Bone Sense", title_style))
    elements.append(Paragraph("AI powered bone tumor detection system", subheading_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("Bone Tumor Detection Report", section_title))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 14))

    # --- Add X-ray images and GradCAM/Segmentation images ---
    from reportlab.platypus import Table, TableStyle
    img_headings_row = [
        Paragraph("Original X-ray", section_title),
        Spacer(0.25 * inch, 1),
        Paragraph("Tumor Segmentation", section_title)
    ]
    col_width = 2.7 * inch
    row_height = 2.7 * inch
    gradcam_heading = Paragraph("GradCAM Heatmap", section_title)
    gradcam_width = col_width
    gradcam_height = row_height

    def get_scaled_image(path, width, height, temp_name):
        if not path or not os.path.exists(path):
            return Spacer(1, height)
        try:
            img = PILImage.open(path)
            img.thumbnail((width, height))
            temp_path = f"temp_{temp_name}.jpg"
            img.save(temp_path)
            return Image(temp_path, width=width, height=height)
        except Exception:
            return Spacer(1, height)

    # Add space between original and segmentation images
    # Fix: Use two columns for headings/images, add space with Spacer row, not column
    spacer_width = 0.25 * inch
    img_table = Table([
        img_headings_row,
        [
            get_scaled_image(original_image_path, col_width, row_height, "original"),
            Spacer(spacer_width, row_height),
            get_scaled_image(segmentation_path, col_width, row_height, "segmentation")
        ],
        [Spacer(1, 8), '', Spacer(1, 8)],  # Add space between image rows
        [gradcam_heading, '', ''],
        [get_scaled_image(gradcam_path, gradcam_width, gradcam_height, "gradcam"), '', '']
    ], colWidths=[col_width, spacer_width, col_width], rowHeights=[None, row_height, 8, None, gradcam_height])
    img_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('SPAN', (0,3), (2,3)),  # GradCAM heading spans all columns
        ('SPAN', (0,4), (2,4)),  # GradCAM image spans all columns
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(img_table)
    elements.append(Spacer(1, 26))

    # --- Results Table ---
    if detection_results:
        elements.append(Paragraph("Analysis Results:", section_title))
        elements.append(Spacer(1, 8))
        data = []
        if detection_results.get('multiclass_label'):
            data.append(["Tumor Classification", str(detection_results['multiclass_label']).upper()])
        if detection_results.get('tumor_subtype'):
            data.append(["Probable Tumor Type Identified", str(detection_results['tumor_subtype']).upper()])
        if detection_results.get('confidence'):
            data.append(["Confidence", f"{detection_results['confidence']:.1%}"])
        if detection_results.get('pathology_scores'):
            scores = detection_results['pathology_scores'][:5]
            locs = [f"• {score['name'].replace('_',' ').title()} ({score['prob']:.1%})" for score in scores]
            locations_para = Paragraph("<br/>".join(locs), normal_style)
            data.append(["Probable Identified Locations", locations_para])
        if data:
            table = Table(data, colWidths=[2.5*inch, 3.5*inch])
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))

    # --- LLaMA Report ---
    if llama_report:
        elements.append(Paragraph("AI-Generated Medical Report:", section_title))
        elements.append(Spacer(1, 8))
        subsection_title = ParagraphStyle('SubsectionTitle', parent=styles['Heading3'], fontSize=11, fontName='Helvetica-Bold', spaceAfter=4)
        import re
        section_pattern = re.compile(r'^(\d+\.\s+.+)$', re.MULTILINE)
        splits = list(section_pattern.finditer(llama_report))
        section_spans = []
        for i, match in enumerate(splits):
            start = match.start()
            end = splits[i+1].start() if i+1 < len(splits) else len(llama_report)
            section_spans.append((match.group(1), llama_report[start+len(match.group(1)):end].strip()))
        for title, content in section_spans:
            elements.append(Paragraph(title, subsection_title))
            if 'Recommended Treatment Plan' in title:
                bullets = re.findall(r'^(?:\d+\.|-)\s*(.+)$', content, re.MULTILINE)
                if bullets:
                    from reportlab.platypus import ListFlowable, ListItem
                    bullet_items = [ListItem(Paragraph(b, normal_style)) for b in bullets]
                    elements.append(ListFlowable(bullet_items, bulletType='bullet', leftIndent=18))
                else:
                    elements.append(Paragraph(content, normal_style))
            else:
                for para in content.split('\n'):
                    if para.strip():
                        elements.append(Paragraph(para.strip(), normal_style))
            elements.append(Spacer(1, 8))

    # --- Disclaimer and Credits ---
    disclaimer = Paragraph(
        "<b>Disclaimer:</b> The results in this report are AI-generated and do not guarantee 100% accuracy. Please consult a qualified medical professional for final diagnosis and treatment decisions.",
        ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=9, alignment=1, textColor=colors.grey, spaceBefore=20, spaceAfter=2)
    )
    credits = Paragraph(
        "<font color='red'>♥</font> Made with love to fight with Bone Tumors by "
        "<a href='https://www.linkedin.com/in/narendra-patne/' color='blue'><u>Narendra</u></a>, "
        "<a href='' color='blue'><u>Niraj</u></a>, and "
        "<a href='' color='blue'><u>Rohit</u></a>",
        ParagraphStyle('Credits', parent=styles['Normal'], fontSize=9, alignment=1, textColor=colors.grey)
    )
    elements.append(Spacer(1, 30))
    elements.append(disclaimer)
    elements.append(credits)

    # --- Build PDF ---
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,  # 0.5 inch
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    doc.build(elements)
    return output_path