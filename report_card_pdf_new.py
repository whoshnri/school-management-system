"""
PDF Report Card Generator for School Management System
Generates comprehensive Nigerian-style report cards with cognitive ability, 
psychomotor skills, and affective areas assessment.
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
import os


def calculate_class_position(student_id, class_name, term, session):
    """Calculate the student's position in their class for a given term."""
    students = session.query(Student).filter_by(class_name=class_name).all()
    student_averages = []
    for student in students:
        marks = session.query(Mark).filter_by(student_id=student.id, term=term).all()
        if marks:
            avg = sum(m.total for m in marks) / len(marks)
            student_averages.append((student.id, avg))
    student_averages.sort(key=lambda x: x[1], reverse=True)
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
