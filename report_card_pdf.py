"""
PDF Report Card Generator for School Management System
Generates professional report cards with student information, grades, and statistics.
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from models import Session, Student, Mark, Subject
from sqlalchemy import func


def calculate_class_position(student_id, class_name, term, session):
    """Calculate the student's position in their class for a given term."""
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
    """Return ordinal suffix for a number (1st, 2nd, 3rd, etc.)."""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


def generate_report_card(student_id, term, output_path):
    """
    Generate a PDF report card for a student.
    
    Args:
        student_id: Student database ID
        term: Term number (1, 2, or 3)
        output_path: Path where PDF should be saved
    
    Returns:
        True if successful, False otherwise
    """
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
        
        # Calculate average
        total_score = sum(mark.total for mark, _ in marks)
        average = total_score / len(marks) if marks else 0
        
        # Get class position
        position, total_students = calculate_class_position(
            student_id, student.class_name, term, session
        )
        
        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2a2a3e'),
            spaceAfter=12,
            alignment=TA_CENTER,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2a2a3e')
        )
        
        # Header
        story.append(Paragraph("SCHOOL MANAGEMENT SYSTEM", title_style))
        story.append(Paragraph("STUDENT REPORT CARD", heading_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Student Information
        student_info = [
            ["Student Name:", student.name, "Student ID:", student.student_id],
            ["Class:", student.class_name, "Term:", f"Term {term}"],
        ]
        
        info_table = Table(student_info, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0fe')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e8f0fe')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2a2a3e')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc1c6'))
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Grades Table
        story.append(Paragraph("Academic Performance", heading_style))
        
        # Table headers
        grades_data = [
            ["Subject", "CA (40)", "Exam (60)", "Total (100)", "Grade"]
        ]
        
        # Add marks
        for mark, subject in marks:
            grades_data.append([
                subject.subject_name,
                f"{mark.continuous_assessment:.1f}",
                f"{mark.exams:.1f}",
                f"{mark.total:.1f}",
                mark.grade or "N/A"
            ])
        
        grades_table = Table(grades_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
        grades_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2a2a3e')),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc1c6')),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(grades_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Summary Statistics
        summary_data = [
            ["Average Score:", f"{average:.2f}%"],
            ["Class Position:", f"{get_ordinal_suffix(position)} out of {total_students}" if position else "N/A"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0fe')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2a2a3e')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc1c6'))
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.6*inch))
        
        # Signature Section
        story.append(Paragraph("Administrative Approval", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        signature_data = [
            ["Admin Signature: _______________________", "Date: _______________________"]
        ]
        
        signature_table = Table(signature_data, colWidths=[3.5*inch, 3*inch])
        signature_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2a2a3e')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(signature_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Footer
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6c757d'),
            alignment=TA_CENTER
        )
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(footer_text, footer_style))
        
        # Build PDF
        doc.build(story)
        return True
        
    except Exception as e:
        print(f"Error generating report card: {e}")
        return False
    finally:
        session.close()
