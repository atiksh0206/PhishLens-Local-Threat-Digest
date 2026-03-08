"""
PhishLens backend — Flask application.
"""

import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from data_store import get_incidents, add_incident
from schemas import validate_incident

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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
