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
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from models import Session, Student, Mark, Subject

# A4 usable width with 0.6in margins each side
PAGE_W = A4[0]
MARGIN = 0.6 * inch
USABLE_W = PAGE_W - 2 * MARGIN   # ~6.27 inches

# Column widths for grades table
GRADE_COLS_T1 = [2.6*inch, 0.85*inch, 0.95*inch, 0.95*inch, 0.92*inch]
GRADE_COLS_T2 = [1.7*inch, 0.6*inch, 0.6*inch, 0.65*inch, 0.65*inch, 0.65*inch, 0.65*inch, 0.67*inch]
GRADE_COLS_T3 = [2.0*inch, 0.75*inch, 0.75*inch, 0.75*inch, 0.85*inch, 0.67*inch]
INFO_COLS = [1.3*inch, 2.0*inch, 1.3*inch, 1.67*inch]

BLUE  = colors.HexColor('#1a73e8')
LBLUE = colors.HexColor('#e8f0fe')
DARK  = colors.HexColor('#202124')
GREY  = colors.HexColor('#5f6368')
LGREY = colors.HexColor('#f8f9fa')
BORD  = colors.HexColor('#dadce0')
WHITE = colors.white

TERM_NAMES = {1: "First Term", 2: "Second Term", 3: "Third Term"}


def _grade(total):
    if total >= 70: return "A"
    if total >= 60: return "B"
    if total >= 50: return "C"
    if total >= 45: return "D"
    if total >= 40: return "E"
    return "F"


def calculate_class_position(student_id, class_name, term, db):
    students = db.query(Student).filter_by(class_name=class_name).all()
    averages = []
    for s in students:
        ms = db.query(Mark).filter_by(student_id=s.id, term=term).all()
        if ms:
            averages.append((s.id, sum(m.total for m in ms) / len(ms)))
    averages.sort(key=lambda x: x[1], reverse=True)
    for pos, (sid, _) in enumerate(averages, 1):
        if sid == student_id:
            return pos, len(averages)
    return None, len(averages)


def ordinal(n):
    if 10 <= n % 100 <= 20:
        sfx = 'th'
    else:
        sfx = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{sfx}"


def _base_styles():
    styles = getSampleStyleSheet()
    title = ParagraphStyle('GFATitle', parent=styles['Normal'],
        fontSize=18, fontName='Helvetica-Bold',
        textColor=BLUE, alignment=TA_CENTER, spaceAfter=4)
    section = ParagraphStyle('GFASection', parent=styles['Normal'],
        fontSize=11, fontName='Helvetica-Bold',
        textColor=BLUE, alignment=TA_LEFT, spaceBefore=8, spaceAfter=4)
    footer = ParagraphStyle('GFAFooter', parent=styles['Normal'],
        fontSize=8, textColor=GREY, alignment=TA_CENTER)
    return title, section, footer


def _header_block(usable_w):
    """School header image or placeholder."""
    img_h = usable_w * 2 / 5
    if os.path.exists("school_header.png"):
        return [Image("school_header.png", width=usable_w, height=img_h),
                Spacer(1, 0.15 * inch)]
    placeholder = Table(
        [["GFA Admin Panel — School Header Image Placeholder"]],
        colWidths=[usable_w], rowHeights=[img_h]
    )
    placeholder.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LBLUE),
        ('TEXTCOLOR', (0, 0), (-1, -1), BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 13),
        ('BOX', (0, 0), (-1, -1), 1, BORD),
    ]))
    return [placeholder, Spacer(1, 0.15 * inch)]


def _info_table(student, term):
    term_name = TERM_NAMES.get(term, f"Term {term}")
    sess_name = "—"
    if hasattr(student, 'academic_session') and student.academic_session:
        sess_name = student.academic_session.name
    data = [
        ["Student Name:", student.full_name, "Student ID:", student.student_id],
        ["Class:", student.class_name, "Term:", term_name],
        ["Sex:", student.sex, "Session:", sess_name],
    ]
    t = Table(data, colWidths=INFO_COLS)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LBLUE),
        ('BACKGROUND', (2, 0), (2, -1), LBLUE),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), DARK),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, BORD),
    ]))
    return t


def _apply_grade_style(table, num_rows, font_size=9):
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), font_size),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), font_size),
        ('TEXTCOLOR', (0, 1), (-1, -1), DARK),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, BORD),
    ]
    for i in range(1, num_rows + 1):
        bg = WHITE if i % 2 == 1 else LGREY
        style.append(('BACKGROUND', (0, i), (-1, i), bg))
    table.setStyle(TableStyle(style))


def _grades_table_t1(marks_data):
    header = [["Subject", "CA (30)", "Exam (70)", "Total (100)", "Grade"]]
    rows = [[n, f"{ca:.1f}", f"{ex:.1f}", f"{tot:.1f}", gr]
            for n, ca, ex, tot, gr in marks_data]
    t = Table(header + rows, colWidths=GRADE_COLS_T1)
    _apply_grade_style(t, len(rows))
    return t


def _grades_table_t2(marks_t1, marks_t2):
    header = [["Subject", "T1 CA", "T2 CA", "T1 Exam", "T2 Exam", "T1 Total", "T2 Total", "Grade"]]
    t1_map = {n: (ca, ex, tot) for n, ca, ex, tot, _ in marks_t1}
    rows = []
    for n, ca2, ex2, tot2, gr2 in marks_t2:
        ca1, ex1, tot1 = t1_map.get(n, (0, 0, 0))
        rows.append([n, f"{ca1:.1f}", f"{ca2:.1f}", f"{ex1:.1f}", f"{ex2:.1f}",
                     f"{tot1:.1f}", f"{tot2:.1f}", gr2])
    t = Table(header + rows, colWidths=GRADE_COLS_T2)
    _apply_grade_style(t, len(rows), font_size=8)
    return t


def _grades_table_t3(marks_t1, marks_t2, marks_t3):
    header = [["Subject", "1st Term", "2nd Term", "3rd Term", "Average", "Grade"]]
    t1_map = {n: tot for n, _, _, tot, _ in marks_t1}
    t2_map = {n: tot for n, _, _, tot, _ in marks_t2}
    rows = []
    for n, _, _, tot3, _ in marks_t3:
        t1 = t1_map.get(n, 0)
        t2 = t2_map.get(n, 0)
        avg = (t1 + t2 + tot3) / 3
        rows.append([n, f"{t1:.1f}", f"{t2:.1f}", f"{tot3:.1f}", f"{avg:.1f}", _grade(avg)])
    t = Table(header + rows, colWidths=GRADE_COLS_T3)
    _apply_grade_style(t, len(rows))
    return t


def _fetch_marks(db, student_id, term):
    rows = db.query(Mark, Subject).join(Subject).filter(
        Mark.student_id == student_id, Mark.term == term
    ).all()
    return [(s.subject_name, m.continuous_assessment, m.exams, m.total,
             m.grade or _grade(m.total)) for m, s in rows]


def generate_report_card(student_id, term, output_path):
    """
    Generate a PDF report card for a student.
    term: 1, 2, or 3
    Returns True on success, False on failure.
    """
    db = Session()
    try:
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            return False

        marks_current = _fetch_marks(db, student_id, term)
        if not marks_current:
            return False

        marks_t1 = _fetch_marks(db, student_id, 1)
        marks_t2 = _fetch_marks(db, student_id, 2)
        marks_t3 = _fetch_marks(db, student_id, 3)

        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            leftMargin=MARGIN, rightMargin=MARGIN,
            topMargin=0.5*inch, bottomMargin=0.5*inch
        )
        story = []
        title_style, section_style, footer_style = _base_styles()

        # Header image
        story.append(KeepTogether(_header_block(USABLE_W)))
        story.append(Spacer(1, 0.1*inch))

        # Student info
        story.append(KeepTogether([
            Paragraph("STUDENT REPORT CARD", title_style),
            Spacer(1, 0.1*inch),
            _info_table(student, term),
            Spacer(1, 0.2*inch),
        ]))

        # Grades
        if term == 1:
            grades_tbl = _grades_table_t1(marks_current)
        elif term == 2:
            grades_tbl = _grades_table_t2(marks_t1, marks_current)
        else:
            grades_tbl = _grades_table_t3(marks_t1, marks_t2, marks_current)

        story.append(KeepTogether([
            Paragraph("Academic Performance", section_style),
            grades_tbl,
        ]))
        story.append(Spacer(1, 0.25*inch))

        # Summary
        avg = sum(t for _, _, _, t, _ in marks_current) / len(marks_current)
        position, total_students = calculate_class_position(
            student_id, student.class_name, term, db
        )
        pos_str = f"{ordinal(position)} out of {total_students}" if position else "N/A"

        summary_tbl = Table(
            [["Average Score:", f"{avg:.1f}%", "Class Position:", pos_str]],
            colWidths=INFO_COLS
        )
        summary_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), LBLUE),
            ('BACKGROUND', (2, 0), (2, -1), LBLUE),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), DARK),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, BORD),
        ]))

        sig_tbl = Table(
            [["Class Teacher: _______________________",
              "Principal: _______________________",
              f"Date: {datetime.now().strftime('%d/%m/%Y')}"]],
            colWidths=[2.2*inch, 2.2*inch, 1.87*inch]
        )
        sig_tbl.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), DARK),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(KeepTogether([
            summary_tbl,
            Spacer(1, 0.3*inch),
            sig_tbl,
            Spacer(1, 0.2*inch),
            Paragraph(
                f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                footer_style
            ),
        ]))

        doc.build(story)
        return True

    except Exception as e:
        print(f"Error generating report card: {e}")
        return False
    finally:
        db.close()
