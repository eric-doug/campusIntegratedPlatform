import re


def validate_required(data, fields):
    """Validate that required fields are present and non-empty."""
    missing = []
    for field in fields:
        if field not in data or data[field] is None or data[field] == '':
            missing.append(field)
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, ""


def validate_phone(phone):
    """Validate Chinese phone number."""
    if not phone:
        return True
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_email(email):
    """Validate email address."""
    if not email:
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
