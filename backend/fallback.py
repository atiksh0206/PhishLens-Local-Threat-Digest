"""
Deterministic fallback summarizer for PhishLens.

Used when AI is unavailable, unconfigured, or fails.
Groups incidents by category/neighborhood, detects categories via keywords,
and generates a template-based digest from playbooks.json.
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Keyword map for detecting category from free-text descriptions / titles
# ---------------------------------------------------------------------------
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "phishing_sms": [
        "sms", "text message", "text msg", "smishing", "fake text",
        "suspicious text", "bank text",
    ],
    "phishing_email": [
        "email", "e-mail", "inbox", "mail", "phish",
        "spoofed email", "fake email",
    ],
    "scam_call": [
        "call", "caller", "voicemail", "phone call", "robo",
        "scam call", "vishing",
    ],
    "account_compromise": [
        "account", "hacked", "password", "login", "credential",
        "unauthorized access", "compromised",
    ],
    "local_breach_alert": [
        "breach", "data leak", "exposed", "data breach",
    ],
    "fraud_report": [
        "fraud", "scam", "fake", "impersonat", "identity theft",
        "stolen", "counterfeit",
    ],
}

# Time window (days) for considering incidents as temporally related
TIME_PROXIMITY_DAYS = 7


def _load_playbooks() -> dict:
    """Load playbooks.json from the data directory."""
    path = os.path.join(os.path.dirname(__file__), "..", "data", "playbooks.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def detect_category(incident: dict) -> str:
    """Detect category from incident text using keyword matching.

    Uses the existing suspected_category if valid, otherwise scans
    title + description for keyword hits.
    """
    from schemas import ALLOWED_CATEGORIES

    existing = incident.get("suspected_category", "").strip().lower()
    if existing and existing in ALLOWED_CATEGORIES and existing != "unknown":
        return existing

    text = (
        f"{incident.get('title', '')} {incident.get('description', '')}"
    ).lower()

    scores: dict[str, int] = defaultdict(int)
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[category] += 1

    if scores:
        return max(scores, key=scores.get)  # type: ignore[arg-type]

    return "unknown"


def _group_incidents(incidents: list[dict]) -> dict[str, dict[str, list[dict]]]:
    """Group incidents by (detected_category, neighborhood).

    Returns nested dict: { category: { neighborhood: [incidents] } }
    """
    grouped: dict[str, dict[str, list[dict]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for inc in incidents:
        cat = detect_category(inc)
        hood = inc.get("neighborhood", "Unknown")
        grouped[cat][hood].append(inc)
    return grouped


def _within_time_window(incidents: list[dict], days: int = TIME_PROXIMITY_DAYS) -> bool:
    """Check whether all incidents fall within the given time window."""
    dates = []
    for inc in incidents:
        ts = inc.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            # Normalize to naive UTC so comparisons always work
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            dates.append(dt)
        except (ValueError, TypeError):
            continue

    if len(dates) < 2:
        return True

    span = max(dates) - min(dates)
    return span <= timedelta(days=days)


def fallback_summarize(incidents: list[dict]) -> dict:
    """Generate a deterministic digest for the given incidents.

    Returns a dict with: summary, explanation, actions, confidence_note.
    Always succeeds — no network calls.
    """
    if not incidents:
        return {
            "summary": "No incidents to summarize.",
            "explanation": "",
            "actions": [],
            "confidence_note": "No data provided.",
        }

    playbooks = _load_playbooks()
    grouped = _group_incidents(incidents)

    summaries: list[str] = []
    explanations: list[str] = []
    actions: list[str] = []
    seen_actions: set[str] = set()

    for category, hoods in grouped.items():
        playbook = playbooks.get(category, playbooks.get("unknown", {}))

        for neighborhood, incs in hoods.items():
            # Build summary line from template
            template = playbook.get(
                "summary_template",
                "{count} report(s) in {neighborhood}.",
            )
            summaries.append(
                template.format(count=len(incs), neighborhood=neighborhood)
            )

            # Explanation (one per category, not per neighborhood)
            exp = playbook.get("explanation", "")
            if exp and exp not in explanations:
                explanations.append(exp)

            # Actions (deduplicated across categories)
            for action in playbook.get("actions", []):
                if action not in seen_actions:
                    seen_actions.add(action)
                    actions.append(action)

    # Confidence note
    total = len(incidents)
    cats = list(grouped.keys())
    time_close = _within_time_window(incidents)

    if total == 1:
        confidence = (
            "Based on a single report. More data would increase confidence."
        )
    elif len(cats) == 1 and time_close:
        confidence = (
            f"Based on {total} reports in the same category within a "
            f"{TIME_PROXIMITY_DAYS}-day window. Pattern appears consistent."
        )
    elif time_close:
        confidence = (
            f"Based on {total} reports across {len(cats)} categories. "
            "Some reports may be unrelated."
        )
    else:
        confidence = (
            f"Based on {total} reports spanning more than "
            f"{TIME_PROXIMITY_DAYS} days. Temporal correlation is weak."
        )

    return {
        "summary": " ".join(summaries),
        "explanation": " ".join(explanations),
        "actions": actions,
        "confidence_note": confidence,
    }
