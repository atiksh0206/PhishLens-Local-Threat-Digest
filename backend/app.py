"""
PhishLens backend — Flask application.
"""

import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from data_store import get_incidents, get_incident_by_id, add_incident, update_incident_status
from schemas import validate_incident, ALLOWED_STATUSES
from summarizer import summarize_incidents
from fallback import fallback_summarize

load_dotenv()

app = Flask(__name__)
CORS(app)


@app.route("/api/incidents", methods=["GET"])
def list_incidents():
    """List incidents with optional search and filters.

    Query params:
        q            – free-text search (title + description)
        category     – filter by suspected_category
        neighborhood – filter by neighborhood
        status       – filter by status
    """
    q = request.args.get("q")
    category = request.args.get("category")
    neighborhood = request.args.get("neighborhood")
    status = request.args.get("status")

    incidents = get_incidents(
        q=q,
        category=category,
        neighborhood=neighborhood,
        status=status,
    )

    return jsonify({"incidents": incidents, "count": len(incidents)})


@app.route("/api/incidents", methods=["POST"])
def create_incident():
    """Create a new incident report.

    Expects a JSON body with at minimum: title, description, neighborhood.
    Returns 201 with the created incident or 400 with validation errors.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"errors": ["Request body must be valid JSON."]}), 400

    errors = validate_incident(data)

    # Validate timestamp format when provided
    timestamp = data.get("timestamp")
    if timestamp:
        try:
            from datetime import datetime
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            errors.append("Timestamp is invalid.")

    if errors:
        return jsonify({"errors": errors}), 400

    incident = add_incident(data)
    return jsonify({"incident": incident}), 201


@app.route("/api/incidents/<incident_id>", methods=["GET"])
def get_incident(incident_id):
    """Get a single incident by id."""
    incident = get_incident_by_id(incident_id)
    if incident is None:
        return jsonify({"error": f"Incident '{incident_id}' not found."}), 404
    return jsonify({"incident": incident})


@app.route("/api/incidents/<incident_id>/status", methods=["PATCH"])
def patch_incident_status(incident_id):
    """Update the status of an incident.

    Expects JSON body: { "status": "acknowledged" }
    """
    # Check incident exists
    if get_incident_by_id(incident_id) is None:
        return jsonify({"error": f"Incident '{incident_id}' not found."}), 404

    data = request.get_json(silent=True)
    if not data or "status" not in data:
        return jsonify({"error": "Request body must include 'status'."}), 400

    new_status = data["status"]
    if new_status not in ALLOWED_STATUSES:
        return jsonify({
            "error": f"Status must be one of: {', '.join(ALLOWED_STATUSES)}."
        }), 400

    updated = update_incident_status(incident_id, new_status)
    return jsonify({"incident": updated})


@app.route("/api/digest", methods=["GET"])
def digest():
    """Generate a summary digest for current incidents.

    Tries AI summarization first; if it returns None (no key, failure,
    timeout), falls back to the deterministic template-based summarizer.

    Query params: same filters as GET /api/incidents.
    """
    incidents = get_incidents(
        q=request.args.get("q"),
        category=request.args.get("category"),
        neighborhood=request.args.get("neighborhood"),
        status=request.args.get("status"),
    )

    if not incidents:
        return jsonify({
            "source": "none",
            "digest": {
                "summary": "No incidents match the current filters.",
                "explanation": "",
                "actions": [],
                "confidence_note": "No data to analyze.",
            },
        })

    # Try AI first
    result = summarize_incidents(incidents)
    if result is not None:
        return jsonify({"source": "ai", "digest": result})

    # Deterministic fallback
    result = fallback_summarize(incidents)
    return jsonify({"source": "fallback", "digest": result})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
