"""
PDF Report Card Generator — GFA Admin Panel
Generates professional Nigerian-format report cards.
"""
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from models import Session, Student, Mark, Subject, ReportCard
from calculations import GradeCalculator
from app_paths import find_asset

PAGE_W = A4[0]
MARGIN = 0.55 * inch
USABLE_W = PAGE_W - 2 * MARGIN

BLUE = colors.HexColor('#1a73e8')
LBLUE = colors.HexColor('#e8f0fe')
DARK = colors.HexColor('#202124')
GREY = colors.HexColor('#5f6368')
LGREY = colors.HexColor('#f8f9fa')
BORD = colors.HexColor('#dadce0')
WHITE = colors.white

PAD_V = 3
PAD_H = 5
SECTION_GAP = 0.06 * inch
HEADER_IMG_H = 1.05 * inch

TERM_NAMES = {1: "First Term", 2: "Second Term", 3: "Third Term"}
PREV_TERM_LABELS = {2: "1st Term Total", 3: "2nd Term Total"}

BEHAVIOUR_TRAITS = [
    ("Punctuality", "punctuality"),
    ("Neatness", "neatness"),
    ("Discipline", "discipline"),
    ("Teamwork", "teamwork"),
]

BEHAVIOUR_SECTION_TITLE = "Behavioural Assessment"
BEHAVIOUR_TABLE_HEADER = "Trait"
TEACHER_COMMENT_LABEL = "Teacher's Comment"
PRINCIPAL_COMMENT_LABEL = "Principal's Comment"
TEACHER_SIGNATURE_LABEL = "Class Teacher"
PRINCIPAL_SIGNATURE_LABEL = "Principal"
PARENT_SIGNATURE_LABEL = "Parent/Guardian"


def _widths(*weights, total_w=None):
    if total_w is None:
        total_w = USABLE_W
    total = float(sum(weights))
    return [total_w * (weight / total) for weight in weights]


def calculate_class_position(student_id, class_name, term, db):
    students = db.query(Student).filter_by(class_name=class_name).all()
    averages = []
    for student in students:
        marks = db.query(Mark).filter_by(student_id=student.id, term=term).all()
        if marks:
            averages.append((student.id, sum(mark.total for mark in marks) / len(marks)))
    averages.sort(key=lambda x: x[1], reverse=True)
    for pos, (sid, _) in enumerate(averages, 1):
        if sid == student_id:
            return pos, len(averages)
    return None, len(averages)


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


def is_report_card_complete(report_card, student_id, term, db):
    if not report_card:
        return False
    ratings = [
        report_card.punctuality,
        report_card.neatness,
        report_card.discipline,
        report_card.teamwork,
    ]
    if not all(rating and 1 <= rating <= 5 for rating in ratings):
        return False
    text_fields = [
        report_card.teacher_comment,
        report_card.principal_comment,
        report_card.teacher_signature,
        report_card.principal_signature,
        report_card.parent_signature,
    ]
    if not all(field and str(field).strip() for field in text_fields):
        return False
    marks_count = db.query(Mark).filter_by(student_id=student_id, term=term).count()
    return marks_count > 0


def _base_styles():
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        'GFATitle', parent=styles['Normal'],
        fontSize=16, fontName='Helvetica-Bold',
        textColor=BLUE, alignment=TA_CENTER, spaceAfter=2,
    )
    section = ParagraphStyle(
        'GFASection', parent=styles['Normal'],
        fontSize=10, fontName='Helvetica-Bold',
        textColor=BLUE, alignment=TA_LEFT, spaceBefore=3, spaceAfter=2,
    )
    body = ParagraphStyle(
        'GFABody', parent=styles['Normal'],
        fontSize=8.5, textColor=DARK, alignment=TA_LEFT, leading=11,
    )
    footer = ParagraphStyle(
        'GFAFooter', parent=styles['Normal'],
        fontSize=7.5, textColor=GREY, alignment=TA_CENTER, spaceBefore=2,
    )
    return title, section, body, footer


def _grid_style(num_rows, font_size=8, center_from=1, label_cols=()):
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), font_size),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), font_size),
        ('TEXTCOLOR', (0, 1), (-1, -1), DARK),
        ('ALIGN', (center_from, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), PAD_V),
        ('BOTTOMPADDING', (0, 0), (-1, -1), PAD_V),
        ('LEFTPADDING', (0, 0), (-1, -1), PAD_H),
        ('RIGHTPADDING', (0, 0), (-1, -1), PAD_H),
        ('GRID', (0, 0), (-1, -1), 0.5, BORD),
    ]
    for col in label_cols:
        style.append(('FONTNAME', (col, 0), (col, -1), 'Helvetica-Bold'))
        style.append(('BACKGROUND', (col, 0), (col, -1), LBLUE))
    for row in range(1, num_rows + 1):
        bg = WHITE if row % 2 == 1 else LGREY
        style.append(('BACKGROUND', (0, row), (-1, row), bg))
        for col in label_cols:
            style.append(('BACKGROUND', (col, row), (col, row), LBLUE))
    return TableStyle(style)


def _header_block():
    header_path = find_asset(("assets/report-banner.png", "report-banner.png", "school_header.png"))
    if header_path:
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


def _label_value_style(label_cols=(0, 2), font_size=9):
    return TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), font_size),
        ('TEXTCOLOR', (0, 0), (-1, -1), DARK),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), PAD_V + 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), PAD_V + 1),
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


def _info_table(student, term):
    term_name = TERM_NAMES.get(term, f"Term {term}")
    session_name = "—"
    if hasattr(student, 'academic_session') and student.academic_session:
        session_name = student.academic_session.name
    data = [
        ["Student Name:", student.full_name, "Student ID:", student.student_id],
        ["Class:", student.class_name, "Term:", term_name],
        ["Sex:", student.sex, "Session:", session_name],
    ]
    pic_path = getattr(student, 'profile_picture_path', None)
    if pic_path:
        abs_pic = os.path.join(os.path.dirname(os.path.abspath(__file__)), pic_path)
        if os.path.exists(abs_pic):
            table = Table(data, colWidths=_widths(1.05, 1.55, 1.05, 1.55, total_w=USABLE_W - 1.2*inch))
            table.setStyle(_label_value_style())
            try:
                from PIL import Image as PILImage
                with PILImage.open(abs_pic) as pil_img:
                    w, h = pil_img.size
                    aspect = h / float(w)
                    target_w = 1.1 * inch
                    target_h = target_w * aspect
            except Exception:
                target_w = 1.1 * inch
                target_h = 1.1 * inch
            img = Image(abs_pic, width=target_w, height=target_h)
            outer_table = Table([[img, table]], colWidths=[1.2*inch, USABLE_W - 1.2*inch])
            outer_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (0,0), 'LEFT'),
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            return outer_table

    table = Table(data, colWidths=_widths(1.05, 1.55, 1.05, 1.55))
    table.setStyle(_label_value_style())
    return table


def _fetch_marks(db, student_id, term):
    rows = db.query(Mark, Subject).join(Subject).filter(
        Mark.student_id == student_id,
        Mark.term == term,
    ).all()
    
    student = db.query(Student).filter_by(id=student_id).first()
    class_name = student.class_name
    
    result = []
    for mark, subject in rows:
        grade = mark.grade or GradeCalculator.calculate_grade(mark.total)
        remark = GradeCalculator.get_remark(mark.total)
        
        class_marks = db.query(Mark).join(Student).filter(
            Student.class_name == class_name,
            Mark.subject_id == mark.subject_id,
            Mark.term == term
        ).all()
        class_marks.sort(key=lambda m: m.total, reverse=True)
        pos = next((i + 1 for i, m in enumerate(class_marks) if m.student_id == student_id), None)
        
        result.append((
            subject.subject_name,
            mark.continuous_assessment,
            mark.exams,
            mark.total,
            grade,
            remark,
            pos,
        ))
    return result


def _grades_table(marks_current, prev_marks=None, prev_label="Previous Total"):
    if prev_marks is not None:
        header = [[
            "Subject", "CA (30)", "Exam (70)", "Total (100)",
            prev_label, "Position", "Grade", "Remark",
        ]]
        col_widths = _widths(2.7, 0.75, 0.75, 0.85, 0.95, 0.75, 0.6, 1.3)
        prev_map = {name: total for name, _, _, total, _, _, _ in prev_marks}
    else:
        header = [["Subject", "CA (30)", "Exam (70)", "Total (100)", "Position", "Grade", "Remark"]]
        col_widths = _widths(3.0, 0.8, 0.8, 0.9, 0.8, 0.65, 1.65)
        prev_map = {}

    rows = []
    for name, ca, exam, total, grade, remark, pos in marks_current:
        row = [name, f"{ca:.1f}", f"{exam:.1f}", f"{total:.1f}"]
        if prev_marks is not None:
            prev_total = prev_map.get(name)
            row.append(f"{prev_total:.1f}" if prev_total is not None else "—")
        row.extend([ordinal(pos) if pos else "—", grade, remark])
        rows.append(row)

    table = Table(header + rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(_grid_style(len(rows), font_size=8))
    return table


def _summary_table(avg, position):
    pos_str = ordinal(position) if position else "N/A"
    table = Table(
        [["Average Score:", f"{avg:.1f}%", "Class Position:", pos_str]],
        colWidths=_widths(1.05, 1.55, 1.05, 1.55),
    )
    table.setStyle(_label_value_style())
    return table


def _behaviour_table(report_card):
    header = [[BEHAVIOUR_TABLE_HEADER, "5", "4", "3", "2", "1"]]
    rows = []
    for label, field in BEHAVIOUR_TRAITS:
        rating = getattr(report_card, field)
        row = [label]
        for score in (5, 4, 3, 2, 1):
            row.append("X" if rating == score else "")
        rows.append(row)
    table = Table(header + rows, colWidths=_widths(4.8, 0.55, 0.55, 0.55, 0.55, 0.55))
    table.setStyle(_grid_style(len(rows), font_size=8))
    return table


def _details_section(report_card, body_style):
    rows = [
        [Paragraph(f"<b>{TEACHER_COMMENT_LABEL}</b>", body_style)],
        [Paragraph(report_card.teacher_comment or "—", body_style)],
        [Paragraph(f"<b>{PRINCIPAL_COMMENT_LABEL}</b>", body_style)],
        [Paragraph(report_card.principal_comment or "—", body_style)],
    ]
    table = Table(rows, colWidths=[USABLE_W])
    table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, BORD),
        ('BACKGROUND', (0, 0), (-1, 0), LBLUE),
        ('BACKGROUND', (0, 2), (-1, 2), LBLUE),
        ('TOPPADDING', (0, 0), (-1, -1), PAD_V + 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), PAD_V + 1),
        ('LEFTPADDING', (0, 0), (-1, -1), PAD_H),
        ('RIGHTPADDING', (0, 0), (-1, -1), PAD_H),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return table


def _signatures_table(report_card):
    roles = [
        TEACHER_SIGNATURE_LABEL,
        PRINCIPAL_SIGNATURE_LABEL,
        PARENT_SIGNATURE_LABEL,
    ]
    names = [
        report_card.teacher_signature or "",
        report_card.principal_signature or "",
        report_card.parent_signature or "",
    ]
    col_w = USABLE_W / 3
    table = Table(
        [["", "", ""], roles, names],
        colWidths=[col_w, col_w, col_w],
        rowHeights=[0.28 * inch, 0.14 * inch, 0.14 * inch],
    )
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('TEXTCOLOR', (0, 0), (-1, -1), DARK),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, 0), 0.75, DARK),
        ('TOPPADDING', (0, 0), (-1, 0), 16),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
    ]))
    return table


def _grade_legend_table():
    header = [["Grade", "Score Range", "Remark"]]
    rows = [
        [grade, score_range, remark]
        for grade, score_range, remark in GradeCalculator.grading_legend_rows()
    ]
    table = Table(
        header + rows,
        colWidths=_widths(0.9, 1.4, 2.7),
    )
    table.setStyle(_grid_style(len(rows), font_size=8))
    return table


def _invoice_bio_table(student, term):
    """Student bio table for the invoice page."""
    term_name = TERM_NAMES.get(term, f"Term {term}")
    dept_name = student.department.name if getattr(student, 'department', None) else "N/A"
    session_name = "—"
    if hasattr(student, 'academic_session') and student.academic_session:
        session_name = student.academic_session.name
    data = [
        ["Student Name:", student.full_name, "Student ID:", student.student_id],
        ["Class:", student.class_name, "Department:", dept_name],
        ["Sex:", student.sex, "Term:", term_name],
    ]
    table = Table(data, colWidths=_widths(1.05, 1.55, 1.05, 1.55))
    table.setStyle(_label_value_style())
    return table


def _invoice_page(db, student, term):
    """Build story elements for the fees invoice page."""
    from reportlab.platypus import PageBreak
    from fee_helpers import get_student_fee_breakdown, get_student_outstanding_fees

    title_style, section_style, body_style, footer_style = _base_styles()
    invoice_title = ParagraphStyle(
        'InvoiceTitle', parent=title_style,
        fontSize=14, spaceAfter=4,
    )
    elements = []

    # Page break before invoice
    elements.append(PageBreak())

    # Banner header
    elements.extend(_header_block())
    elements.append(Paragraph("FEES INVOICE", title_style))
    elements.append(Spacer(1, 0.08 * inch))

    # Invoice date
    elements.append(Paragraph(
        f"Date: {datetime.now().strftime('%B %d, %Y')}",
        body_style,
    ))
    elements.append(Spacer(1, 0.08 * inch))

    # Student bio
    elements.append(_invoice_bio_table(student, term))
    elements.append(Spacer(1, SECTION_GAP))

    grand_total = 0.0

    # Outstanding fees from previous/current terms
    outstanding = get_student_outstanding_fees(db, student.id, term)
    if outstanding:
        elements.append(Paragraph("Outstanding Fees", section_style))

        header = [["Term", "Amount Due", "Amount Paid", "Balance"]]
        rows = []
        outstanding_total = 0.0
        for t, due, paid, balance in outstanding:
            t_name = TERM_NAMES.get(t, f"Term {t}")
            rows.append([t_name, f"₦{due:,.2f}", f"₦{paid:,.2f}", f"₦{balance:,.2f}"])
            outstanding_total += balance

        # Subtotal row
        rows.append(["", "", "Subtotal:", f"₦{outstanding_total:,.2f}"])

        table = Table(header + rows, colWidths=_widths(1.5, 1.5, 1.5, 1.5))
        style_cmds = _grid_style(len(rows), font_size=9)
        table.setStyle(style_cmds)
        elements.append(table)
        elements.append(Spacer(1, SECTION_GAP))
        grand_total += outstanding_total

    # Next term fee breakdown
    next_term = term + 1 if term < 3 else 3
    next_term_name = TERM_NAMES.get(next_term, f"Term {next_term}")

    # Only show "next term" section if it's actually a different term
    if next_term != term or term == 3:
        fee_items, next_amount_due = get_student_fee_breakdown(db, student.id, next_term)

        if fee_items:
            elements.append(Paragraph(f"Fee Breakdown — {next_term_name}", section_style))

            header = [["Description", "Amount (₦)"]]
            rows = []
            items_total = 0.0
            for item in fee_items:
                desc = item.get("description", "")
                amt = item.get("amount", 0)
                rows.append([desc, f"₦{amt:,.2f}"])
                items_total += amt

            rows.append(["Total", f"₦{items_total:,.2f}"])

            table = Table(header + rows, colWidths=_widths(3, 2))
            style_cmds = _grid_style(len(rows), font_size=9)
            table.setStyle(style_cmds)
            elements.append(table)
            elements.append(Spacer(1, SECTION_GAP))
            grand_total += items_total
        elif next_amount_due > 0:
            elements.append(Paragraph(f"Fee Breakdown — {next_term_name}", section_style))
            header = [["Description", "Amount (₦)"]]
            rows = [["School Fees", f"₦{next_amount_due:,.2f}"], ["Total", f"₦{next_amount_due:,.2f}"]]
            table = Table(header + rows, colWidths=_widths(3, 2))
            table.setStyle(_grid_style(len(rows), font_size=9))
            elements.append(table)
            elements.append(Spacer(1, SECTION_GAP))
            grand_total += next_amount_due

    # Grand total
    if grand_total > 0:
        grand_data = [["GRAND TOTAL", f"₦{grand_total:,.2f}"]]
        grand_table = Table(grand_data, colWidths=_widths(3, 2))
        grand_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BLUE),
            ('TEXTCOLOR', (0, 0), (-1, -1), WHITE),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), PAD_H),
            ('RIGHTPADDING', (0, 0), (-1, -1), PAD_H),
            ('BOX', (0, 0), (-1, -1), 0.75, BORD),
        ]))
        elements.append(grand_table)
        elements.append(Spacer(1, 0.15 * inch))

    # Payment instructions
    elements.append(Paragraph("Payment Instructions", section_style))
    instructions = Table(
        [
            ["Please make payment to the school account using any of the following methods:"],
            ["1. Bank Transfer — Contact the school bursar for account details."],
            ["2. Cash Payment — Pay directly at the school accounts office."],
            ["3. Online Payment — Visit the school portal for online payment options."],
            [""],
            ["Please retain this invoice as proof of fees due. Present your receipt upon payment."],
        ],
        colWidths=[USABLE_W],
    )
    instructions.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LGREY),
        ('TEXTCOLOR', (0, 0), (-1, -1), DARK),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 0.75, BORD),
    ]))
    elements.append(instructions)
    elements.append(Spacer(1, 0.1 * inch))

    return elements


def generate_report_card(student_id, term, output_path):
    """Generate a PDF report card for a student."""
    db = Session()
    try:
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            return False

        report_card = db.query(ReportCard).filter_by(student_id=student_id, term=term).first()
        if not is_report_card_complete(report_card, student_id, term, db):
            return False

        marks_current = _fetch_marks(db, student_id, term)
        if not marks_current:
            return False

        prev_marks = None
        prev_label = None
        if term > 1:
            prev_marks = _fetch_marks(db, student_id, term - 1)
            prev_label = PREV_TERM_LABELS.get(term, "Previous Total")

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=0.45 * inch,
            bottomMargin=0.45 * inch,
        )
        story = []
        title_style, section_style, body_style, footer_style = _base_styles()

        story.extend(_header_block())
        story.append(Paragraph("STUDENT REPORT CARD", title_style))
        story.append(Spacer(1, 0.12 * inch))
        story.append(_info_table(student, term))
        story.append(Spacer(1, SECTION_GAP))

        story.append(Paragraph("Academic Performance", section_style))
        story.append(_grades_table(marks_current, prev_marks, prev_label))

        avg = sum(total for _, _, _, total, _, _, _ in marks_current) / len(marks_current) if marks_current else 0.0
        position, _total_students = calculate_class_position(
            student_id, student.class_name, term, db
        )
        story.append(Spacer(1, SECTION_GAP))
        story.append(_summary_table(avg, position))
        story.append(Spacer(1, SECTION_GAP))

        story.append(Paragraph(BEHAVIOUR_SECTION_TITLE, section_style))
        story.append(_behaviour_table(report_card))
        story.append(Spacer(1, SECTION_GAP))

        story.append(Paragraph("Details", section_style))
        story.append(_details_section(report_card, body_style))
        story.append(Spacer(1, SECTION_GAP))
        story.append(_signatures_table(report_card))
        story.append(Spacer(1, SECTION_GAP))

        story.append(Paragraph("Grade Boundaries", section_style))
        story.append(_grade_legend_table())
        
        if getattr(report_card, 'next_term_resumption_date', None):
            resumption_style = ParagraphStyle(
                'Resumption', parent=styles['Normal'],
                fontSize=10, fontName='Helvetica-Bold', alignment=2, spaceBefore=20, textColor=DARK
            )
            story.append(Paragraph(f"Next Term Resumption Date: {report_card.next_term_resumption_date}", resumption_style))

        # Add invoice page
        story.extend(_invoice_page(db, student, term))

        doc.build(story)
        return True

    except Exception as e:
        print(f"Error generating report card: {e}")
        return False
    finally:
        db.close()

