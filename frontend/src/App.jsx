import { useState, useEffect, useCallback } from "react";

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

  return (
    <div className="app">
      <header className="header">
        <h1>🛡️ PhishLens</h1>
        <p className="subtitle">Local Threat Digest</p>
      </header>

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

      {/* Results */}
      <p className="result-count">
        {loading ? "Loading…" : `${count} report${count !== 1 ? "s" : ""} found`}
      </p>

      {error && <p className="error-msg">Error: {error}</p>}

      <div className="card-grid">
        {incidents.map((inc) => (
          <div key={inc.id} className="card">
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
            <p className="card-desc">
              {inc.description.length > 140
                ? inc.description.slice(0, 140) + "…"
                : inc.description}
            </p>
            <div className="card-meta">
              <span>📍 {inc.neighborhood}</span>
              <span>🕐 {new Date(inc.timestamp).toLocaleDateString()}</span>
            </div>
          </div>
        ))}
      </div>

      {!loading && incidents.length === 0 && !error && (
        <p className="empty-msg">No reports match your filters.</p>
      )}
    </div>
  );
}
