import { useState, useEffect, useCallback } from "react";
import ReportForm from "./ReportForm";

const CATEGORIES = [
  "",
  "phishing_sms",
  "phishing_email",
  "scam_call",
  "account_compromise",
  "local_breach_alert",
  "fraud_report",
  "unknown",
];

const NEIGHBORHOODS = [
  "",
  "Riverside",
  "Maple Heights",
  "Downtown",
  "Oak Park",
  "Lakeview",
];

const STATUSES = ["", "new", "acknowledged", "duplicate", "resolved", "needs_review"];

/** Human-friendly label for a category slug */
function formatLabel(slug) {
  if (!slug) return "—";
  return slug.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Color hint for status badges */
function statusColor(status) {
  const map = {
    new: "#2563eb",
    acknowledged: "#7c3aed",
    duplicate: "#6b7280",
    resolved: "#16a34a",
    needs_review: "#d97706",
  };
  return map[status] || "#6b7280";
}

export default function App() {
  const [incidents, setIncidents] = useState([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter state
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [neighborhood, setNeighborhood] = useState("");
  const [status, setStatus] = useState("");

  // Form visibility
  const [showForm, setShowForm] = useState(false);

  // Detail view state
  const [selectedId, setSelectedId] = useState(null);
  const [statusUpdating, setStatusUpdating] = useState(false);

  // Digest state
  const [digest, setDigest] = useState(null);
  const [digestLoading, setDigestLoading] = useState(false);
  const [digestError, setDigestError] = useState(null);
  const [forceFallback, setForceFallback] = useState(false);

  const fetchIncidents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (search) params.set("q", search);
      if (category) params.set("category", category);
      if (neighborhood) params.set("neighborhood", neighborhood);
      if (status) params.set("status", status);

      const res = await fetch(`/api/incidents?${params.toString()}`);
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      setIncidents(data.incidents);
      setCount(data.count);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [search, category, neighborhood, status]);

  useEffect(() => {
    fetchIncidents();
  }, [fetchIncidents]);

  const fetchDigest = async () => {
    setDigestLoading(true);
    setDigestError(null);
    setDigest(null);
    try {
      const params = new URLSearchParams();
      if (category) params.set("category", category);
      if (neighborhood) params.set("neighborhood", neighborhood);
      if (status) params.set("status", status);
      if (forceFallback) params.set("force_fallback", "1");
      const res = await fetch(`/api/digest?${params.toString()}`);
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      setDigest(await res.json());
    } catch (err) {
      setDigestError(err.message);
    } finally {
      setDigestLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🛡️ PhishLens</h1>
        <p className="subtitle">Local Threat Digest</p>
        <button
          className="btn-primary"
          style={{ marginTop: "0.75rem" }}
          onClick={() => setShowForm((v) => !v)}
        >
          {showForm ? "Back to dashboard" : "+ Submit a report"}
        </button>
      </header>

      {showForm && (
        <ReportForm
          onCreated={() => {
            setShowForm(false);
            fetchIncidents();
          }}
          onCancel={() => setShowForm(false)}
        />
      )}

      {!showForm && (
        <>
          {/* Search and filters */}
          <div className="controls">
            <input
              type="text"
              className="search-input"
              placeholder="Search reports…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <select value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="">All categories</option>
              {CATEGORIES.filter(Boolean).map((c) => (
                <option key={c} value={c}>
                  {formatLabel(c)}
                </option>
              ))}
            </select>
            <select value={neighborhood} onChange={(e) => setNeighborhood(e.target.value)}>
              <option value="">All neighborhoods</option>
              {NEIGHBORHOODS.filter(Boolean).map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
            <select value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="">All statuses</option>
              {STATUSES.filter(Boolean).map((s) => (
                <option key={s} value={s}>
                  {formatLabel(s)}
                </option>
              ))}
            </select>
          </div>

          {/* Digest controls */}
          <div className="digest-controls">
            <button className="btn-primary" onClick={fetchDigest} disabled={digestLoading}>
              {digestLoading ? "Generating…" : "Generate Digest"}
            </button>
            <label className="fallback-toggle">
              <input
                type="checkbox"
                checked={forceFallback}
                onChange={(e) => setForceFallback(e.target.checked)}
              />
              Force fallback (skip AI)
            </label>
          </div>

          {digestError && <p className="error-msg">Digest error: {digestError}</p>}

          {digest && (
            <div className="digest-card">
              <div className="digest-header">
                <h2>Threat Digest</h2>
                <span className={`digest-source ${digest.source}`}>
                  {digest.source === "ai" ? "AI Summary" : digest.source === "fallback" ? "Rule-Based" : "No Data"}
                </span>
              </div>
              <p className="digest-summary">{digest.digest.summary}</p>
              {digest.digest.explanation && (
                <p className="digest-explanation">{digest.digest.explanation}</p>
              )}
              {digest.digest.actions.length > 0 && (
                <>
                  <h4>Recommended Actions</h4>
                  <ul className="digest-actions">
                    {digest.digest.actions.map((a, i) => (
                      <li key={i}>{a}</li>
                    ))}
                  </ul>
                </>
              )}
              <p className="digest-confidence">{digest.digest.confidence_note}</p>
            </div>
          )}

          {/* Results */}
          <p className="result-count">
            {loading ? "Loading…" : `${count} report${count !== 1 ? "s" : ""} found`}
          </p>

          {error && <p className="error-msg">Error: {error}</p>}

          <div className="card-grid">
            {incidents.map((inc) => (
              <div
                key={inc.id}
                className={`card ${selectedId === inc.id ? "card-selected" : ""}`}
                onClick={() => setSelectedId(selectedId === inc.id ? null : inc.id)}
              >
                <div className="card-header">
                  <span className="card-category">{formatLabel(inc.suspected_category)}</span>
                  <span
                    className="card-status"
                    style={{ backgroundColor: statusColor(inc.status) }}
                  >
                    {formatLabel(inc.status)}
                  </span>
                </div>
                <h3 className="card-title">{inc.title}</h3>
                {selectedId !== inc.id && (
                  <p className="card-desc">
                    {inc.description.length > 140
                      ? inc.description.slice(0, 140) + "…"
                      : inc.description}
                  </p>
                )}
                {selectedId === inc.id && (
                  <div className="card-detail">
                    <p className="card-desc-full">{inc.description}</p>
                    <div className="detail-fields">
                      <div><strong>Category:</strong> {formatLabel(inc.suspected_category)}</div>
                      <div><strong>Neighborhood:</strong> {inc.neighborhood}</div>
                      <div><strong>Source:</strong> {formatLabel(inc.source_type)}</div>
                      <div><strong>Date:</strong> {new Date(inc.timestamp).toLocaleString()}</div>
                      <div><strong>ID:</strong> {inc.id}</div>
                    </div>
                    <div className="detail-status">
                      <strong>Update status:</strong>
                      <div className="status-buttons">
                        {STATUSES.filter(Boolean).map((s) => (
                          <button
                            key={s}
                            className={`status-btn ${inc.status === s ? "active" : ""}`}
                            style={inc.status === s ? { backgroundColor: statusColor(s), color: "#fff" } : {}}
                            disabled={inc.status === s || statusUpdating}
                            onClick={async (e) => {
                              e.stopPropagation();
                              setStatusUpdating(true);
                              try {
                                await fetch(`/api/incidents/${inc.id}/status`, {
                                  method: "PATCH",
                                  headers: { "Content-Type": "application/json" },
                                  body: JSON.stringify({ status: s }),
                                });
                                fetchIncidents();
                              } finally {
                                setStatusUpdating(false);
                              }
                            }}
                          >
                            {formatLabel(s)}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
                {selectedId !== inc.id && (
                  <div className="card-meta">
                    <span>📍 {inc.neighborhood}</span>
                    <span>🕐 {new Date(inc.timestamp).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {!loading && incidents.length === 0 && !error && (
            <p className="empty-msg">No reports match your filters.</p>
          )}
        </>
      )}
    </div>
  );
}
