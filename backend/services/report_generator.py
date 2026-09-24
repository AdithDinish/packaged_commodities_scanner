import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable


def generate_compliance_report(inspection_data: dict, output_pdf_path: Path) -> str:
    """
    Generates an official digital PDF compliance report for Legal Metrology enforcement officers.
    """
    output_pdf_path = Path(output_pdf_path)
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#0F172A'),
        alignment=1,  # Centered
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        textColor=colors.HexColor('#334155'),
        leading=11
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        textColor=colors.white,
        leading=10
    )

    story = []

    # 1. Government & Department Header
    story.append(Paragraph("MINISTRY OF CONSUMER AFFAIRS, FOOD & PUBLIC DISTRIBUTION", subtitle_style))
    story.append(Paragraph("DEPARTMENT OF CONSUMER AFFAIRS (DoCA) - LEGAL METROLOGY DIVISION", title_style))
    story.append(Paragraph("<b>LEGAL METROLOGY (PACKAGED COMMODITIES) RULES, 2011 - COMPLIANCE INSPECTION REPORT</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceAfter=12))

    # 2. Inspection Metadata Box
    ref_no = inspection_data.get("scan_ref", "REF-2026-001")
    scan_date = inspection_data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    inspector = inspection_data.get("inspector_name", "Official Inspector (DoCA)")
    product_name = inspection_data.get("product_name", "Unknown Product")
    brand = inspection_data.get("brand", "Unknown Brand")
    status = inspection_data.get("overall_status", "UNKNOWN")
    score = inspection_data.get("compliance_score", 0.0)

    # Status color
    status_bg = colors.HexColor('#10B981') if status == "COMPLIANT" else (colors.HexColor('#EF4444') if status == "NON_COMPLIANT" else colors.HexColor('#F59E0B'))

    meta_table_data = [
        [
            Paragraph(f"<b>Inspection Ref:</b> {ref_no}", body_style),
            Paragraph(f"<b>Date & Time:</b> {scan_date}", body_style)
        ],
        [
            Paragraph(f"<b>Inspector:</b> {inspector}", body_style),
            Paragraph(f"<b>Product Title:</b> {brand} - {product_name}", body_style)
        ],
        [
            Paragraph(f"<b>Overall Compliance Status:</b> <font color='white'><b> {status} </b></font>", body_style),
            Paragraph(f"<b>Legal Metrology Score:</b> <b>{score}%</b> ({inspection_data.get('passed_rules', 0)}/9 Rules Passed)", body_style)
        ]
    ]

    meta_table = Table(meta_table_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 3. Rule Evaluation Matrix
    story.append(Paragraph("Mandatory Declaration Evaluation Matrix (Rules 6 & 7)", h2_style))

    rules_list = inspection_data.get("rules", [])
    rule_table_rows = [
        [
            Paragraph("Rule / Legal Provision", table_header_style),
            Paragraph("Declaration Field", table_header_style),
            Paragraph("Extracted Package Text", table_header_style),
            Paragraph("Compliance Result", table_header_style)
        ]
    ]

    for r in rules_list:
        sec = r.get("legal_section", "")
        name = r.get("rule_name", "")
        extracted = r.get("extracted_value", "-")
        r_status = r.get("status", "UNKNOWN")

        # Result badge style
        st_color = "#10B981" if r_status == "COMPLIANT" else ("#EF4444" if r_status == "NON_COMPLIANT" else "#F59E0B")
        st_text = f"<font color='{st_color}'><b>{r_status}</b></font>"

        rule_table_rows.append([
            Paragraph(f"<b>{sec}</b><br/>{name}", body_style),
            Paragraph(r.get("rule_code", ""), body_style),
            Paragraph(extracted[:80] + "..." if len(extracted) > 80 else extracted, body_style),
            Paragraph(st_text, body_style)
        ])

    rule_table = Table(rule_table_rows, colWidths=[140, 110, 200, 90])
    rule_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(rule_table)
    story.append(Spacer(1, 14))

    # 4. Offence & Enforcement Summary
    story.append(Paragraph("Legal Penalty & Offence Notice Summary", h2_style))
    violations = [r for r in rules_list if r.get("status") in ["NON_COMPLIANT", "WARNING"]]

    if violations:
        v_rows = [[Paragraph("Non-Compliant Provision", table_header_style), Paragraph("Identified Deficiency & Statutory Offence", table_header_style)]]
        for v in violations:
            msg = v.get("message", "")
            pen = v.get("legal_penalty", "")
            v_rows.append([
                Paragraph(f"<b>{v.get('legal_section')}</b><br/>{v.get('rule_name')}", body_style),
                Paragraph(f"{msg}<br/><font color='#B91C1C'><b>Statutory Action:</b> {pen}</font>", body_style)
            ])
        v_table = Table(v_rows, colWidths=[170, 370])
        v_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#991B1B')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#FCA5A5')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#FEE2E2')),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(v_table)
    else:
        story.append(Paragraph("<b>CONGRATULATIONS:</b> No statutory violations detected. Product packaging fully complies with the Legal Metrology (Packaged Commodities) Rules, 2011.", body_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#94A3B8'), spaceAfter=10))

    # 5. Official Verification Block
    verif_data = [
        [
            Paragraph("<b>Digitally Verified By:</b><br/>Legal Metrology Inspection Engine v2.0<br/>Department of Consumer Affairs (DoCA)", body_style),
            Paragraph("<b>Enforcement Officer Authorization:</b><br/>___________________________<br/>Seal & Signature", body_style)
        ]
    ]
    verif_table = Table(verif_data, colWidths=[300, 240])
    verif_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(verif_table)

    # Build document
    doc.build(story)
    return str(output_pdf_path)
