# Temporary script to create report_card_pdf.py

content = """\"\"\"
PDF Report Card Generator for School Management System
Generates comprehensive Nigerian-style report cards with cognitive ability, 
psychomotor skills, and affective areas assessment.
\"\"\"
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from models import Session, Student, Mark, Subject
from sqlalchemy import func
import os


def calculate_class_position(student_id, class_name, term, session):
    \"\"\"Calculate the student's position in their class for a given term.\"\"\"
    # Get all students in the same class
    students = session.query(Student).filter_by(class_name=class_name).all()
    
    # Calculate average for each student
    student_averages = []
    for student in students:
        marks = session.query(Mark).filter_by(student_id=student.id, term=term).all()
        if marks:
            avg = sum(m.total for m in marks) / len(marks)
            student_averages.append((student.id, avg))
    
    # Sort by average in descending order
    student_averages.sort(key=lambda x: x[1], reverse=True)
    
    # Find position
    for position, (sid, _) in enumerate(student_averages, start=1):
        if sid == student_id:
            return position, len(student_averages)
    
    return None, len(student_averages)


def get_ordinal_suffix(n):
    \"\"\"Return ordinal suffix for a number (1st, 2nd, 3rd, etc.).\"\"\"
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


def generate_report_card(student_id, term, output_path):
    \"\"\"
    Generate a comprehensive Nigerian-style PDF report card for a student.
    
    Args:
        student_id: Student database ID
        term: Term number (1, 2, or 3)
        output_path: Path where PDF should be saved
    
    Returns:
        True if successful, False otherwise
    \"\"\"
    session = Session()
    
    try:
        # Get student data
        student = session.query(Student).filter_by(id=student_id).first()
        if not student:
            return False
        
        # Get marks for the term
        marks = session.query(Mark, Subject).join(Subject).filter(
            Mark.student_id == student_id,
            Mark.term == term
        ).all()
        
        if not marks:
            return False
        
        # Calculate statistics
        total_score = sum(mark.total for mark, _ in marks)
        average = total_score / len(marks) if marks else 0
        position, total_students = calculate_class_position(
            student_id, student.class_name, term, session
        )
        
        # Get current academic year
        current_year = datetime.now().year
        next_year = current_year + 1
        session_year = f"{current_year}/{next_year}"
        
        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4, 
                               topMargin=0.3*inch, bottomMargin=0.5*inch,
                               leftMargin=0.5*inch, rightMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        section_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.HexColor('#2a2a3e'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # ===== HEADER IMAGE PLACEHOLDER =====
        # Try to load school logo/header image
        header_image_paths = ['school_header.png', 'school_header.jpg', 'header.png', 'header.jpg']
        header_added = False
        
        for img_path in header_image_paths:
            if os.path.exists(img_path):
                try:
                    # Image width = page width, height = 2/5 of width
                    page_width = A4[0] - 1*inch  # Account for margins
                    img_height = page_width * 0.4  # 2/5 ratio
                    
                    img = Image(img_path, width=page_width, height=img_height)
                    story.append(img)
                    story.append(Spacer(1, 0.15*inch))
                    header_added = True
                    break
                except:
                    pass
        
        # If no image found, add placeholder
        if not header_added:
            placeholder_data = [[
                "SCHOOL HEADER IMAGE PLACEHOLDER\\n(Place school_header.png in the application folder)"
            ]]
            placeholder_table = Table(placeholder_data, colWidths=[A4[0] - 1*inch])
            placeholder_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f0fe')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a73e8')),
                ('TOPPADDING', (0, 0), (-1, -1), 30),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 30),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a73e8')),
            ]))
            story.append(placeholder_table)
            story.append(Spacer(1, 0.15*inch))
        
        # ===== TITLE =====
        story.append(Paragraph(f"CONTINUOUS ASSESSMENT FOR TERM {term} {session_year} SESSION", title_style))
        story.append(Spacer(1, 0.15*inch))
        
        # ===== STUDENT INFO HEADER TABLE =====
        student_info_data = [
            ["NAME:", student.full_name, "STUDENT ID:", student.student_id],
            ["CLASS:", student.class_name, "SEX:", student.sex],
            ["TERM:", str(term), "SESSION:", session_year]
        ]
        
        student_info_table = Table(student_info_data, colWidths=[1.2*inch, 2.8*inch, 1.2*inch, 1.8*inch])
        student_info_table.setStyle(TableStyle([
            # Labels (columns 0 and 2)
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            # Values (columns 1 and 3)
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'LEFT'),
            # Borders and padding
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(student_info_table)
        story.append(Spacer(1, 0.2*inch))
"""

with open('report_card_pdf.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("File created successfully!")
