"""
Simple file-based data store for incidents.

Loads incidents from data/incidents.json into memory at startup.
Provides a get_incidents() function with search and filter support.
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
INCIDENTS_PATH = os.path.join(DATA_DIR, "incidents.json")

# In-memory list, loaded once at import time
_incidents: list[dict] = []


def _load_incidents() -> list[dict]:
    """Read incidents from the JSON seed file."""
    with open(INCIDENTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def reload():
    """(Re)load incidents from disk into memory."""
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


# Load seed data on first import
reload()
