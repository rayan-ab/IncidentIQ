from datetime import datetime
from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def clean_text(value):
    """
    Convert any value to safe text that ReportLab can display.
    """
    if value is None:
        return "Not provided"

    return escape(str(value)).replace("\n", "<br/>")


def create_bullet_list(items, styles):
    """
    Create a PDF bullet list from a Python list.
    """
    if not items:
        return [
            Paragraph(
                "No information is available.",
                styles["BodyTextCustom"]
            )
        ]

    list_items = []

    for item in items:
        list_items.append(
            ListItem(
                Paragraph(
                    clean_text(item),
                    styles["BodyTextCustom"]
                ),
                leftIndent=12
            )
        )

    return [
        ListFlowable(
            list_items,
            bulletType="bullet",
            leftIndent=20,
            bulletFontName="Helvetica",
            bulletFontSize=8,
            spaceAfter=8
        )
    ]


def create_numbered_list(items, styles):
    """
    Create a numbered PDF list from a Python list.
    """
    if not items:
        return [
            Paragraph(
                "No actions were generated.",
                styles["BodyTextCustom"]
            )
        ]

    list_items = []

    for item in items:
        list_items.append(
            ListItem(
                Paragraph(
                    clean_text(item),
                    styles["BodyTextCustom"]
                ),
                leftIndent=12
            )
        )

    return [
        ListFlowable(
            list_items,
            bulletType="1",
            start="1",
            leftIndent=22,
            spaceAfter=8
        )
    ]


def add_page_number(canvas, document):
    """
    Add a footer and page number to every PDF page.
    """
    canvas.saveState()

    page_width, _ = A4

    canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas.line(
        1.5 * cm,
        1.4 * cm,
        page_width - 1.5 * cm,
        1.4 * cm
    )

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))

    canvas.drawString(
        1.5 * cm,
        0.9 * cm,
        "IncidentIQ - AI-Generated Incident Analysis"
    )

    canvas.drawRightString(
        page_width - 1.5 * cm,
        0.9 * cm,
        f"Page {document.page}"
    )

    canvas.restoreState()


def generate_pdf_report(analysis, incident="", logs="", notes=""):
    """
    Generate an IncidentIQ PDF report and return it as a BytesIO object.
    """
    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=1.7 * cm,
        leftMargin=1.7 * cm,
        topMargin=1.7 * cm,
        bottomMargin=2 * cm,
        title="IncidentIQ Incident Report",
        author="IncidentIQ"
    )

    default_styles = getSampleStyleSheet()

    styles = {
        "TitleCustom": ParagraphStyle(
            "TitleCustom",
            parent=default_styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=8
        ),

        "Subtitle": ParagraphStyle(
            "Subtitle",
            parent=default_styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=22
        ),

        "SectionTitle": ParagraphStyle(
            "SectionTitle",
            parent=default_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=colors.HexColor("#1D4ED8"),
            spaceBefore=14,
            spaceAfter=10
        ),

        "Subheading": ParagraphStyle(
            "Subheading",
            parent=default_styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=7,
            spaceAfter=5
        ),

        "BodyTextCustom": ParagraphStyle(
            "BodyTextCustom",
            parent=default_styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#334155"),
            spaceAfter=7,
            wordWrap="CJK"
        ),

        "SmallText": ParagraphStyle(
            "SmallText",
            parent=default_styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#475569"),
            wordWrap="CJK"
        ),

        "HypothesisTitle": ParagraphStyle(
            "HypothesisTitle",
            parent=default_styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#7C2D12"),
            spaceAfter=4
        )
    }

    story = []

    generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    story.append(
        Paragraph(
            "IncidentIQ",
            styles["TitleCustom"]
        )
    )

    story.append(
        Paragraph(
            "AI-Powered Incident Response and Root-Cause Analysis Report",
            styles["Subtitle"]
        )
    )

    metadata_table = Table(
        [
            ["Report Generated", generated_time],
            ["Analysis Type", "AI-Assisted Incident Response"],
            ["Report Status", "Generated"]
        ],
        colWidths=[4.2 * cm, 11.5 * cm]
    )

    metadata_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#EFF6FF")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#1E3A8A")
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold"
                ),
                (
                    "FONTNAME",
                    (1, 0),
                    (1, -1),
                    "Helvetica"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1")
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                )
            ]
        )
    )

    story.append(metadata_table)
    story.append(Spacer(1, 18))

    # Original incident input
    story.append(
        Paragraph(
            "Submitted Incident Information",
            styles["SectionTitle"]
        )
    )

    input_data = [
        [
            Paragraph("<b>Incident Description</b>", styles["SmallText"]),
            Paragraph(clean_text(incident), styles["SmallText"])
        ],
        [
            Paragraph("<b>Deployment Notes</b>", styles["SmallText"]),
            Paragraph(clean_text(notes), styles["SmallText"])
        ]
    ]

    input_table = Table(
        input_data,
        colWidths=[4.2 * cm, 11.5 * cm]
    )

    input_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#F8FAFC")
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1")
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ]
        )
    )

    story.append(input_table)
    story.append(Spacer(1, 8))

    if logs:
        log_excerpt = logs[:6000]

        if len(logs) > 6000:
            log_excerpt += (
                "\n\n[The log content was shortened in the PDF report.]"
            )

        story.append(
            Paragraph(
                "Application Logs",
                styles["Subheading"]
            )
        )

        story.append(
            Paragraph(
                clean_text(log_excerpt),
                styles["SmallText"]
            )
        )

    # Summary
    summary = analysis.get("incident_summary", {})

    story.append(
        Paragraph(
            "1. Incident Summary",
            styles["SectionTitle"]
        )
    )

    summary_data = [
        [
            Paragraph("<b>Description</b>", styles["SmallText"]),
            Paragraph(
                clean_text(summary.get("description", "Unknown")),
                styles["BodyTextCustom"]
            )
        ],
        [
            Paragraph("<b>Status</b>", styles["SmallText"]),
            Paragraph(
                clean_text(summary.get("status", "Unknown")),
                styles["BodyTextCustom"]
            )
        ],
        [
            Paragraph("<b>Likely Impact</b>", styles["SmallText"]),
            Paragraph(
                clean_text(summary.get("impact", "Unknown")),
                styles["BodyTextCustom"]
            )
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[4 * cm, 11.7 * cm]
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#EFF6FF")
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#BFDBFE")
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ]
        )
    )

    story.append(summary_table)

    # Timeline
    story.append(
        Paragraph(
            "2. Timeline",
            styles["SectionTitle"]
        )
    )

    timeline = analysis.get("timeline", [])

    if timeline:
        timeline_rows = [
            [
                Paragraph("<b>Timestamp</b>", styles["SmallText"]),
                Paragraph("<b>Event</b>", styles["SmallText"])
            ]
        ]

        for item in timeline:
            timeline_rows.append(
                [
                    Paragraph(
                        clean_text(item.get("timestamp", "Unknown")),
                        styles["SmallText"]
                    ),
                    Paragraph(
                        clean_text(item.get("event", "Unknown event")),
                        styles["SmallText"]
                    )
                ]
            )

        timeline_table = Table(
            timeline_rows,
            colWidths=[4.2 * cm, 11.5 * cm],
            repeatRows=1
        )

        timeline_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#DBEAFE")
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#1E3A8A")
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#CBD5E1")
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    )
                ]
            )
        )

        story.append(timeline_table)

    else:
        story.append(
            Paragraph(
                "No timeline information is available.",
                styles["BodyTextCustom"]
            )
        )

    # Root causes
    story.append(
        Paragraph(
            "3. Possible Root Causes",
            styles["SectionTitle"]
        )
    )

    root_causes = analysis.get("root_causes", [])

    if root_causes:
        for index, cause in enumerate(root_causes, start=1):
            cause_content = [
                Paragraph(
                    (
                        f"{index}. {clean_text(cause.get('title', 'Hypothesis'))}"
                    ),
                    styles["HypothesisTitle"]
                ),
                Paragraph(
                    (
                        "<b>Confidence:</b> "
                        f"{clean_text(cause.get('confidence', 'Unknown'))}"
                    ),
                    styles["BodyTextCustom"]
                ),
                Paragraph(
                    clean_text(cause.get("explanation", "")),
                    styles["BodyTextCustom"]
                ),
                Spacer(1, 7)
            ]

            story.append(KeepTogether(cause_content))

    else:
        story.append(
            Paragraph(
                "No root-cause hypotheses were generated.",
                styles["BodyTextCustom"]
            )
        )

    # Evidence
    story.append(
        Paragraph(
            "4. Evidence",
            styles["SectionTitle"]
        )
    )

    story.extend(
        create_bullet_list(
            analysis.get("evidence", []),
            styles
        )
    )

    # Assumptions
    story.append(
        Paragraph(
            "5. Assumptions",
            styles["SectionTitle"]
        )
    )

    story.extend(
        create_bullet_list(
            analysis.get("assumptions", []),
            styles
        )
    )

    # Uncertainties
    story.append(
        Paragraph(
            "6. Uncertainties",
            styles["SectionTitle"]
        )
    )

    story.extend(
        create_bullet_list(
            analysis.get("uncertainties", []),
            styles
        )
    )

    # Actions
    story.append(PageBreak())

    story.append(
        Paragraph(
            "7. Recommended Immediate Actions",
            styles["SectionTitle"]
        )
    )

    story.extend(
        create_numbered_list(
            analysis.get("immediate_actions", []),
            styles
        )
    )

    story.append(
        Paragraph(
            "8. Recommended Long-Term Actions",
            styles["SectionTitle"]
        )
    )

    story.extend(
        create_numbered_list(
            analysis.get("long_term_actions", []),
            styles
        )
    )

    story.append(Spacer(1, 20))

    disclaimer = Table(
        [
            [
                Paragraph(
                    (
                        "<b>Important:</b> This report contains an "
                        "AI-assisted analysis. Root-cause hypotheses and "
                        "recommended actions should be reviewed and verified "
                        "by qualified technical personnel before execution."
                    ),
                    styles["SmallText"]
                )
            ]
        ],
        colWidths=[15.7 * cm]
    )

    disclaimer.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#FFF7ED")
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    colors.HexColor("#FDBA74")
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                )
            ]
        )
    )

    story.append(disclaimer)

    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    pdf_buffer.seek(0)

    return pdf_buffer