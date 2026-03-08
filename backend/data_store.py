"""
Simple file-based data store for incidents.

Loads incidents from data/incidents.json into memory at startup.
Provides a get_incidents() function with search and filter support.
"""

import json
import os
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
INCIDENTS_PATH = os.path.join(DATA_DIR, "incidents.json")

# In-memory list, loaded once at import time
_incidents: list[dict] = []


def _load_incidents() -> list[dict]:
    with open(INCIDENTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def reload():
    global _incidents
    _incidents = _load_incidents()


def get_incidents(
    q: str | None = None,
    category: str | None = None,
    neighborhood: str | None = None,
    status: str | None = None,
) -> list[dict]:
    """Return incidents matching the given filters.

    Args:
        q: free-text search across title and description (case-insensitive)
        category: exact match on suspected_category
        neighborhood: exact match on neighborhood
        status: exact match on status

    Returns:
        Filtered list of incident dicts, newest first.
    """
    results = list(_incidents)

    if q:
        q_lower = q.lower()
        results = [
            inc for inc in results
            if q_lower in inc.get("title", "").lower()
            or q_lower in inc.get("description", "").lower()
        ]

    if category:
        results = [
            inc for inc in results
            if inc.get("suspected_category") == category
        ]

    if neighborhood:
        results = [
            inc for inc in results
            if inc.get("neighborhood") == neighborhood
        ]

    if status:
        results = [
            inc for inc in results
            if inc.get("status") == status
        ]

    # Newest first by timestamp
    results.sort(key=lambda inc: inc.get("timestamp", ""), reverse=True)

    return results


def _next_id() -> str:
    """Generate the next inc-NNN id based on existing incidents."""
    max_num = 0
    for inc in _incidents:
        inc_id = inc.get("id", "")
        if inc_id.startswith("inc-"):
            try:
                num = int(inc_id.split("-")[1])
                max_num = max(max_num, num)
            except (IndexError, ValueError):
                pass
    return f"inc-{max_num + 1:03d}"


def _save_incidents():
    """Persist the in-memory incidents list back to the JSON file."""
    with open(INCIDENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(_incidents, f, indent=2, ensure_ascii=False)
        f.write("\n")


def add_incident(data: dict) -> dict:
    """Create a new incident, append it to storage, and return it.

    Fills in defaults for id, status, and timestamp if not provided.
    Caller is responsible for validating data before calling this.
    """
    incident = {
        "id": _next_id(),
        "title": data["title"].strip(),
        "description": data["description"].strip(),
        "source_type": data.get("source_type", "other"),
        "neighborhood": data["neighborhood"],
        "timestamp": data.get("timestamp") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reporter_type": data.get("reporter_type", "resident"),
        "suspected_category": data.get("suspected_category", "unknown"),
        "status": data.get("status", "new"),
    }

    _incidents.append(incident)
    _save_incidents()
    return incident


# Load seed data on first import
reload()
