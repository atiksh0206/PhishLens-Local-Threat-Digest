"""
Schemas and constants for PhishLens incident data.

Defines allowed values for categories, statuses, neighborhoods, and source types.
Provides a validate_incident() helper used by routes and tests.
"""

ALLOWED_CATEGORIES = [
    "phishing_sms",
    "phishing_email",
    "scam_call",
    "account_compromise",
    "local_breach_alert",
    "fraud_report",
    "unknown",
]

ALLOWED_STATUSES = [
    "new",
    "acknowledged",
    "duplicate",
    "resolved",
    "needs_review",
]

ALLOWED_NEIGHBORHOODS = [
    "Riverside",
    "Maple Heights",
    "Downtown",
    "Oak Park",
    "Lakeview",
]

ALLOWED_SOURCE_TYPES = [
    "sms",
    "email",
    "phone",
    "community_report",
    "in_person",
    "physical",
    "other",
]

# Required fields and their human-readable error messages
REQUIRED_FIELDS = {
    "title": "Title is required.",
    "description": "Description is required.",
    "neighborhood": "Please choose a neighborhood.",
}

MIN_DESCRIPTION_LENGTH = 15


def validate_incident(data: dict) -> list[str]:
    """Validate an incident dict and return a list of error messages (empty = valid)."""
    errors = []

    # --- required fields ---
    for field, message in REQUIRED_FIELDS.items():
        value = data.get(field)
        if not value or not str(value).strip():
            errors.append(message)

    # --- description length ---
    description = data.get("description", "")
    if description and len(description.strip()) < MIN_DESCRIPTION_LENGTH:
        errors.append(
            f"Description must be at least {MIN_DESCRIPTION_LENGTH} characters."
        )

    # --- neighborhood must be in allowed list ---
    neighborhood = data.get("neighborhood")
    if neighborhood and neighborhood not in ALLOWED_NEIGHBORHOODS:
        errors.append(
            f"Neighborhood must be one of: {', '.join(ALLOWED_NEIGHBORHOODS)}."
        )

    # --- category (optional, but must be valid when provided) ---
    category = data.get("suspected_category")
    if category and category not in ALLOWED_CATEGORIES:
        errors.append(
            f"Category must be one of: {', '.join(ALLOWED_CATEGORIES)}."
        )

    # --- status (optional on create, but must be valid when provided) ---
    status = data.get("status")
    if status and status not in ALLOWED_STATUSES:
        errors.append(
            f"Status must be one of: {', '.join(ALLOWED_STATUSES)}."
        )

    # --- source_type (optional, but must be valid when provided) ---
    source_type = data.get("source_type")
    if source_type and source_type not in ALLOWED_SOURCE_TYPES:
        errors.append(
            f"Source type must be one of: {', '.join(ALLOWED_SOURCE_TYPES)}."
        )

    return errors
