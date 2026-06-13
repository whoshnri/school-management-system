"""Helpers for class/term fee structures and student fee sync."""
from datetime import datetime

from models import Student, Fee, FeeStructure

CLASS_OPTIONS = ["SSS1", "SSS2", "SSS3"]
TERM_OPTIONS = [
    (1, "First Term"),
    (2, "Second Term"),
    (3, "Third Term"),
]


def get_fee_structure(session, class_name, term):
    return session.query(FeeStructure).filter_by(class_name=class_name, term=term).first()


def get_or_create_student_fee(session, student_id, term, amount_due=0):
    fee = session.query(Fee).filter_by(student_id=student_id, term=term).first()
    if fee:
        return fee
    fee = Fee(student_id=student_id, term=term, amount_due=amount_due, amount_paid=0)
    session.add(fee)
    return fee


def apply_fee_structure(session, class_name, term, amount_due):
    """Save global fee for a class/term and sync all student fee records."""
    if amount_due < 0:
        raise ValueError("Amount cannot be negative.")

    structure = get_fee_structure(session, class_name, term)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if structure:
        structure.amount_due = amount_due
        structure.updated_at = now
    else:
        structure = FeeStructure(
            class_name=class_name,
            term=term,
            amount_due=amount_due,
            updated_at=now,
        )
        session.add(structure)

    students = session.query(Student).filter_by(class_name=class_name).all()
    for student in students:
        fee = get_or_create_student_fee(session, student.id, term, amount_due)
        fee.amount_due = amount_due

    session.commit()
    return structure


def sync_fees_for_scope(session, class_name, term):
    """Ensure each student fee record matches the saved fee structure."""
    structure = get_fee_structure(session, class_name, term)
    amount_due = structure.amount_due if structure else 0
    students = session.query(Student).filter_by(class_name=class_name).all()
    for student in students:
        fee = get_or_create_student_fee(session, student.id, term, amount_due)
        fee.amount_due = amount_due
    session.commit()


def load_fee_structure_matrix(session):
    """Return {(class_name, term): amount_due} for all saved structures."""
    rows = session.query(FeeStructure).all()
    return {(row.class_name, row.term): row.amount_due for row in rows}
