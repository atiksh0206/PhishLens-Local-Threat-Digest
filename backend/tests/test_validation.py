"""
Tests for input validation (schemas.py).
"""

from schemas import validate_incident


def test_valid_incident_passes_validation():
    """A complete, well-formed incident should produce zero errors."""
    data = {
        "title": "Suspicious text from bank",
        "description": "Received a text claiming my account is locked and to click a link",
        "neighborhood": "Riverside",
        "suspected_category": "phishing_sms",
        "source_type": "sms",
    }
    errors = validate_incident(data)
    assert errors == []


def test_missing_required_fields():
    """Omitting title, description, and neighborhood should produce three errors."""
    errors = validate_incident({})
    assert len(errors) == 3
    assert any("Title" in e for e in errors)
    assert any("Description" in e for e in errors)
    assert any("neighborhood" in e.lower() for e in errors)


def test_short_description_rejected():
    """A description under 15 characters should be rejected."""
    data = {
        "title": "Test report",
        "description": "Too short",
        "neighborhood": "Downtown",
    }
    errors = validate_incident(data)
    assert any("15 characters" in e for e in errors)


def test_invalid_neighborhood_rejected():
    """A neighborhood not in the allowed list should be rejected."""
    data = {
        "title": "Test report",
        "description": "This is a long enough description for validation",
        "neighborhood": "Atlantis",
    }
    errors = validate_incident(data)
    assert any("Neighborhood" in e for e in errors)


def test_invalid_category_rejected():
    """An unknown category value should be rejected."""
    data = {
        "title": "Test report",
        "description": "This is a long enough description for validation",
        "neighborhood": "Oak Park",
        "suspected_category": "alien_invasion",
    }
    errors = validate_incident(data)
    assert any("Category" in e for e in errors)
