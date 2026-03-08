"""
Focused tests for the deterministic fallback summarizer.
"""

from fallback import fallback_summarize, detect_category


def test_groups_similar_phishing_reports():
    """Happy path: two phishing SMS reports in the same neighborhood
    should produce a grouped summary with relevant actions."""
    incidents = [
        {
            "title": "Fake bank text",
            "description": "Got a suspicious text message asking me to click a link",
            "neighborhood": "Riverside",
            "suspected_category": "phishing_sms",
            "timestamp": "2026-03-01",
        },
        {
            "title": "Another SMS scam",
            "description": "Text claiming my account is locked, wants credentials",
            "neighborhood": "Riverside",
            "suspected_category": "phishing_sms",
            "timestamp": "2026-03-02",
        },
    ]

    result = fallback_summarize(incidents)

    # Structure is complete
    assert "summary" in result
    assert "explanation" in result
    assert "actions" in result
    assert "confidence_note" in result

    # Both reports grouped under one category + neighborhood
    assert "2 user(s) in Riverside" in result["summary"]
    assert "phishing" in result["summary"].lower() or "SMS" in result["summary"]

    # Actions come from the phishing_sms playbook
    assert any("7726" in a for a in result["actions"]), "Should include carrier-report action"
    assert len(result["actions"]) >= 3

    # Confidence reflects same-category, close-in-time reports
    assert "same category" in result["confidence_note"].lower()


def test_handles_low_information_report_with_safe_fallback():
    """Edge case: a single vague report with no category and minimal text
    should still return a valid digest without crashing."""
    incidents = [
        {
            "title": "Something weird",
            "description": "Not sure what happened but it seemed off",
            "neighborhood": "Downtown",
        },
    ]

    # Category detection should fall back to "unknown"
    assert detect_category(incidents[0]) == "unknown"

    result = fallback_summarize(incidents)

    # Structure is still complete
    assert isinstance(result["summary"], str) and len(result["summary"]) > 0
    assert isinstance(result["actions"], list)
    assert isinstance(result["confidence_note"], str)

    # Should mention limited data
    assert "single report" in result["confidence_note"].lower()

    # Should still provide some generic actions from the "unknown" playbook
    assert len(result["actions"]) >= 1
