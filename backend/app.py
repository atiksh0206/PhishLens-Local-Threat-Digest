"""
PhishLens backend — Flask application.
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS

from data_store import get_incidents

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
