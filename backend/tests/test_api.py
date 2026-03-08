"""
Tests for Flask API endpoints (app.py).
"""

import json
import os

# Ensure AI is disabled so digest tests hit fallback
os.environ["OPENAI_API_KEY"] = ""

from app import app


def client():
    return app.test_client()


# ── GET /api/incidents ──

def test_list_incidents_returns_array():
    resp = client().get("/api/incidents")
    data = json.loads(resp.data)
    assert resp.status_code == 200
    assert "incidents" in data
    assert isinstance(data["incidents"], list)
    assert data["count"] == len(data["incidents"])


def test_filter_by_category():
    resp = client().get("/api/incidents?category=phishing_sms")
    data = json.loads(resp.data)
    assert resp.status_code == 200
    for inc in data["incidents"]:
        assert inc["suspected_category"] == "phishing_sms"


def test_search_filters_by_text():
    resp = client().get("/api/incidents?q=bank")
    data = json.loads(resp.data)
    assert resp.status_code == 200
    for inc in data["incidents"]:
        combined = (inc["title"] + inc["description"]).lower()
        assert "bank" in combined


# ── POST /api/incidents ──

def test_create_incident_success():
    resp = client().post(
        "/api/incidents",
        data=json.dumps({
            "title": "Test phishing report",
            "description": "Got a suspicious email asking for my password and credentials",
            "neighborhood": "Downtown",
        }),
        content_type="application/json",
    )
    data = json.loads(resp.data)
    assert resp.status_code == 201
    assert data["incident"]["title"] == "Test phishing report"
    assert data["incident"]["status"] == "new"
    assert data["incident"]["id"].startswith("inc-")


def test_create_incident_validation_error():
    resp = client().post(
        "/api/incidents",
        data=json.dumps({"title": ""}),
        content_type="application/json",
    )
    data = json.loads(resp.data)
    assert resp.status_code == 400
    assert "errors" in data
    assert len(data["errors"]) > 0


# ── GET /api/incidents/<id> ──

def test_get_incident_not_found():
    resp = client().get("/api/incidents/inc-99999")
    assert resp.status_code == 404


# ── PATCH /api/incidents/<id>/status ──

def test_update_status_invalid():
    resp = client().patch(
        "/api/incidents/inc-001/status",
        data=json.dumps({"status": "bogus"}),
        content_type="application/json",
    )
    assert resp.status_code == 400


# ── GET /api/digest ──

def test_digest_returns_fallback_without_api_key():
    resp = client().get("/api/digest")
    data = json.loads(resp.data)
    assert resp.status_code == 200
    assert data["source"] == "fallback"
    assert "summary" in data["digest"]
    assert isinstance(data["digest"]["actions"], list)


def test_digest_force_fallback():
    resp = client().get("/api/digest?force_fallback=1")
    data = json.loads(resp.data)
    assert resp.status_code == 200
    assert data["source"] == "fallback"


def test_digest_empty_with_impossible_filter():
    resp = client().get("/api/digest?category=phishing_sms&neighborhood=Lakeview&status=resolved")
    data = json.loads(resp.data)
    assert resp.status_code == 200
    # May be "none" or "fallback" depending on seed data
    assert data["source"] in ("none", "fallback")
