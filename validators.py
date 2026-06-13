"""Shared field validation helpers."""
import re

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def is_valid_email(value):
    text = (value or "").strip()
    if not text:
        return False
    return bool(EMAIL_PATTERN.match(text))


def validate_email(value, required=True):
    text = (value or "").strip()
    if not text:
        if required:
            return False, "Email is required."
        return True, ""
    if not is_valid_email(text):
        return False, "Enter a valid email address (e.g. name@school.com)."
    return True, ""


def validate_fee_payment(amount_str, amount_due, amount_paid):
    """Validate a fee payment amount against due and already paid."""
    text = (amount_str or "").strip()
    if not text:
        return None, "Please enter a payment amount."

    try:
        amount = float(text)
    except ValueError:
        return None, "Please enter a valid amount."

    if amount <= 0:
        return None, "Payment amount must be greater than zero."

    if amount_due <= 0:
        return None, "No fee is due for this student. Set the fee structure first."

    balance = amount_due - amount_paid
    if balance <= 0:
        return None, "This fee is already paid in full."

    if amount > balance:
        return None, f"Payment cannot exceed the remaining balance of ₦{balance:,.2f}."

    return amount, None
