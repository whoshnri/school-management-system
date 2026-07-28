"""Helpers for class/term/department fee structures and student fee sync."""
import json
from datetime import datetime

from models import Student, Fee, FeeStructure, Department

CLASS_OPTIONS = ["SSS1", "SSS2", "SSS3"]
DEPT_OPTIONS = ["Science", "Art", "Commercial"]
TERM_OPTIONS = [
    (1, "First Term"),
    (2, "Second Term"),
    (3, "Third Term"),
]


def get_fee_structure(session, class_name, term, dept_name=None):
    """Get a fee structure, optionally filtered by department."""
    query = session.query(FeeStructure).filter_by(class_name=class_name, term=term)
    if dept_name:
        query = query.filter_by(dept_name=dept_name)
    else:
        query = query.filter(FeeStructure.dept_name.is_(None))
    return query.first()


def get_or_create_student_fee(session, student_id, term, amount_due=0):
    fee = session.query(Fee).filter_by(student_id=student_id, term=term).first()
    if fee:
        return fee
    fee = Fee(student_id=student_id, term=term, amount_due=amount_due, amount_paid=0)
    session.add(fee)
    return fee


def apply_fee_structure(session, class_name, term, amount_due, fee_items=None, dept_name=None):
    """Save global fee for a class/term/dept and sync all student fee records."""
    if amount_due < 0:
        raise ValueError("Amount cannot be negative.")

    structure = get_fee_structure(session, class_name, term, dept_name)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if structure:
        structure.amount_due = amount_due
        structure.fee_items = fee_items
        structure.updated_at = now
    else:
        structure = FeeStructure(
            class_name=class_name,
            term=term,
            dept_name=dept_name,
            amount_due=amount_due,
            fee_items=fee_items,
            updated_at=now,
        )
        session.add(structure)

    # Sync student fees — filter by department if specified
    query = session.query(Student).filter_by(class_name=class_name)
    if dept_name:
        dept = session.query(Department).filter_by(name=dept_name).first()
        if dept:
            query = query.filter_by(dept_id=dept.id)
    students = query.all()
    for student in students:
        fee = get_or_create_student_fee(session, student.id, term, amount_due)
        fee.amount_due = amount_due

    session.commit()
    return structure


def sync_fees_for_scope(session, class_name, term):
    """Ensure each student fee record matches the saved fee structure."""
    students = session.query(Student).filter_by(class_name=class_name).all()
    for student in students:
        dept_name = student.department.name if student.department else None
        structure = get_fee_structure(session, class_name, term, dept_name)
        # Fallback to class-level structure if dept-specific doesn't exist
        if not structure:
            structure = get_fee_structure(session, class_name, term, None)
        amount_due = structure.amount_due if structure else 0
        fee = get_or_create_student_fee(session, student.id, term, amount_due)
        fee.amount_due = amount_due
    session.commit()


def load_fee_structure_matrix(session):
    """Return {(class_name, term, dept_name): FeeStructure} for all saved structures."""
    rows = session.query(FeeStructure).all()
    return {(row.class_name, row.term, row.dept_name): row for row in rows}


def get_student_fee_breakdown(session, student_id, term):
    """Return the fee items list for a student based on their class + department for a given term."""
    student = session.query(Student).filter_by(id=student_id).first()
    if not student:
        return [], 0

    dept_name = student.department.name if student.department else None
    structure = get_fee_structure(session, student.class_name, term, dept_name)
    # Fallback to class-level if no department-specific structure
    if not structure and dept_name:
        structure = get_fee_structure(session, student.class_name, term, None)

    if not structure or not structure.fee_items:
        return [], structure.amount_due if structure else 0

    try:
        items = json.loads(structure.fee_items)
    except (json.JSONDecodeError, TypeError):
        items = []

    return items, structure.amount_due


def get_student_outstanding_fees(session, student_id, up_to_term):
    """Return list of (term, amount_due, amount_paid, balance) for terms with outstanding balance."""
    outstanding = []
    for t in range(1, up_to_term + 1):
        fee = session.query(Fee).filter_by(student_id=student_id, term=t).first()
        if fee:
            balance = fee.amount_due - fee.amount_paid
            if balance > 0:
                outstanding.append((t, fee.amount_due, fee.amount_paid, balance))
    return outstanding
