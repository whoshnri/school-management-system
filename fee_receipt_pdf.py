"""
PDF School Fees Payment Receipt — GFA Admin Panel
"""
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from models import Session, Student, Fee
from app_paths import find_asset

PAGE_W = A4[0]
MARGIN = 0.55 * inch
USABLE_W = PAGE_W - 2 * MARGIN

BLUE = colors.HexColor('#1a73e8')
LBLUE = colors.HexColor('#e8f0fe')
DARK = colors.HexColor('#202124')
GREY = colors.HexColor('#5f6368')
GREEN = colors.HexColor('#34a853')
BORD = colors.HexColor('#dadce0')
WHITE = colors.white

PAD_V = 6
PAD_H = 8
SECTION_GAP = 0.16 * inch
BLOCK_GAP = 0.12 * inch
HEADER_IMG_H = 1.05 * inch

TERM_NAMES = {1: "First Term", 2: "Second Term", 3: "Third Term"}


def _widths(*weights):
    total = float(sum(weights))
    return [USABLE_W * (weight / total) for weight in weights]


def is_fee_fully_paid(fee):
    if not fee or fee.amount_due <= 0:
        return False
    return fee.amount_paid >= fee.amount_due


def _label_value_style(label_cols=(0, 2)):
    return TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), DARK),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), PAD_V + 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), PAD_V + 2),
        ('LEFTPADDING', (0, 0), (-1, -1), PAD_H),
        ('RIGHTPADDING', (0, 0), (-1, -1), PAD_H),
        ('GRID', (0, 0), (-1, -1), 0.5, BORD),
        *[
            ('BACKGROUND', (col, 0), (col, -1), LBLUE)
            for col in label_cols
        ],
        *[
            ('FONTNAME', (col, 0), (col, -1), 'Helvetica-Bold')
            for col in label_cols
        ],
    ])


def _header_block():
    header_path = find_asset(("assets/report-banner.png", "report-banner.png", "school_header.png"))
    if header_path and os.path.exists(header_path):
        return [
            Image(str(header_path), width=USABLE_W, height=HEADER_IMG_H),
            Spacer(1, SECTION_GAP),
        ]
    placeholder = Table(
        [["GFA Admin Panel — School Header"]],
        colWidths=[USABLE_W],
        rowHeights=[HEADER_IMG_H],
    )
    placeholder.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LBLUE),
        ('TEXTCOLOR', (0, 0), (-1, -1), BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 0.75, BORD),
        ('TOPPADDING', (0, 0), (-1, -1), PAD_V),
        ('BOTTOMPADDING', (0, 0), (-1, -1), PAD_V),
    ]))
    return [placeholder, Spacer(1, SECTION_GAP)]


def generate_fee_receipt(student_id, term, output_path):
    """Generate a PDF payment receipt for a fully paid fee record."""
    db = Session()
    try:
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            return False

        fee = db.query(Fee).filter_by(student_id=student_id, term=term).first()
        if not is_fee_fully_paid(fee):
            return False

        term_name = TERM_NAMES.get(term, f"Term {term}")
        session_name = "—"
        if hasattr(student, 'academic_session') and student.academic_session:
            session_name = student.academic_session.name

        receipt_no = f"GFA-{student.id:04d}-T{term}-{datetime.now().strftime('%Y%m%d')}"
        balance = max(fee.amount_due - fee.amount_paid, 0)
        issued_at = datetime.now()

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=0.45 * inch,
            bottomMargin=0.45 * inch,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReceiptTitle', parent=styles['Normal'],
            fontSize=16, fontName='Helvetica-Bold',
            textColor=BLUE, alignment=TA_CENTER, spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            'ReceiptSub', parent=styles['Normal'],
            fontSize=10, textColor=GREY, alignment=TA_CENTER, spaceAfter=10,
        )
        section_style = ParagraphStyle(
            'ReceiptSection', parent=styles['Normal'],
            fontSize=10, fontName='Helvetica-Bold',
            textColor=BLUE, alignment=TA_LEFT, spaceBefore=4, spaceAfter=6,
        )
        paid_style = ParagraphStyle(
            'PaidStamp', parent=styles['Normal'],
            fontSize=12, fontName='Helvetica-Bold',
            textColor=GREEN, alignment=TA_CENTER, spaceBefore=10, spaceAfter=10,
        )
        footer_style = ParagraphStyle(
            'ReceiptFooter', parent=styles['Normal'],
            fontSize=8, textColor=GREY, alignment=TA_CENTER, spaceBefore=10,
        )

        story = []
        story.extend(_header_block())
        
        pic_path = student.profile_picture_path
        if pic_path and os.path.exists(pic_path):
            try:
                img = Image(pic_path, width=1.2*inch, height=1.2*inch)
                img.hAlign = 'LEFT'
                story.append(img)
                story.append(Spacer(1, BLOCK_GAP))
            except Exception:
                pass
                
        story.append(Spacer(1, BLOCK_GAP))
        story.append(Paragraph("SCHOOL FEES PAYMENT RECEIPT", title_style))
        story.append(Paragraph(f"Receipt No: {receipt_no}", subtitle_style))
        story.append(Spacer(1, BLOCK_GAP))

        student_info = Table([
            ["Student Name:", student.full_name, "Student ID:", student.student_id],
            ["Class:", student.class_name, "Term:", term_name],
            ["Session:", session_name, "Date Issued:", issued_at.strftime("%d/%m/%Y")],
        ], colWidths=_widths(1.05, 1.55, 1.05, 1.55))
        student_info.setStyle(_label_value_style())
        story.append(student_info)
        story.append(Spacer(1, SECTION_GAP))

        story.append(Paragraph("Payment Summary", section_style))
        
        amt_style = ParagraphStyle(
            'AmtRight', parent=styles['Normal'],
            fontSize=9, textColor=DARK, alignment=TA_RIGHT,
        )
        amt_bold_style = ParagraphStyle(
            'AmtRightBold', parent=styles['Normal'],
            fontSize=9, fontName='Helvetica-Bold', textColor=DARK, alignment=TA_RIGHT,
        )
        
        payment_rows = [
            ["Description", "Amount"],
            ["Amount Due", Paragraph(f"<strike>N</strike>{fee.amount_due:,.2f}", amt_style)],
            ["Amount Paid", Paragraph(f"<strike>N</strike>{fee.amount_paid:,.2f}", amt_style)],
            ["Outstanding Balance", Paragraph(f"<strike>N</strike>{balance:,.2f}", amt_bold_style)],
        ]
        payment_table = Table(payment_rows, colWidths=_widths(2.2, 1.0))
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), DARK),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), PAD_V + 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), PAD_V + 2),
            ('LEFTPADDING', (0, 0), (-1, -1), PAD_H),
            ('RIGHTPADDING', (0, 0), (-1, -1), PAD_H),
            ('GRID', (0, 0), (-1, -1), 0.5, BORD),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), LBLUE),
        ]))
        story.append(payment_table)
        story.append(Spacer(1, SECTION_GAP))

        sig_col = USABLE_W / 2
        sig_table = Table(
            [["", ""], ["Received By", "Official Stamp"]],
            colWidths=[sig_col, sig_col],
            rowHeights=[0.34 * inch, 0.18 * inch],
        )
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('TEXTCOLOR', (0, 0), (-1, -1), DARK),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (-1, 0), 0.75, DARK),
            ('TOPPADDING', (0, 0), (-1, 0), 22),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 1), (-1, 1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 4),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ]))
        story.append(sig_table)
        story.append(Spacer(1, BLOCK_GAP))

        doc.build(story)
        return True

    except Exception as e:
        print(f"Error generating fee receipt: {e}")
        return False
    finally:
        db.close()
