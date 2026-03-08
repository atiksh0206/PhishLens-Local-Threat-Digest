import { useState } from "react";

const NEIGHBORHOODS = [
  "Riverside",
  "Maple Heights",
  "Downtown",
  "Oak Park",
  "Lakeview",
];

const SOURCE_TYPES = [
  "sms",
  "email",
  "phone",
  "community_report",
  "in_person",
  "physical",
  "other",
];

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

function formatLabel(slug) {
  if (!slug) return "";
  return slug.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

const INITIAL = {
  title: "",
  description: "",
  neighborhood: "",
  source_type: "other",
  timestamp: "",
  suspected_category: "",
};

export default function ReportForm({ onCreated, onCancel }) {
  const [form, setForm] = useState({ ...INITIAL });
  const [errors, setErrors] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors([]); // clear errors on edit
    setSuccess(false);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setErrors([]);
    setSuccess(false);
    setSubmitting(true);

    // Build payload — omit empty optional fields
    const payload = {
      title: form.title,
      description: form.description,
      neighborhood: form.neighborhood,
      source_type: form.source_type,
    };
    if (form.timestamp) payload.timestamp = form.timestamp;
    if (form.suspected_category) payload.suspected_category = form.suspected_category;

    try {
      const res = await fetch("/api/incidents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (!res.ok) {
        setErrors(data.errors || ["Something went wrong."]);
        return;
      }

      setSuccess(true);
      setForm({ ...INITIAL });
      if (onCreated) onCreated(data.incident);
    } catch (err) {
      setErrors([err.message || "Network error. Is the backend running?"]);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="report-form" onSubmit={handleSubmit}>
      <h2>Submit a Report</h2>

      {errors.length > 0 && (
        <ul className="form-errors">
          {errors.map((err, i) => (
            <li key={i}>{err}</li>
          ))}
        </ul>
      )}

      {success && (
        <p className="form-success">Report submitted successfully.</p>
      )}

      {/* Title */}
      <label className="form-label">
        Title <span className="required">*</span>
        <input
          type="text"
          value={form.title}
          onChange={(e) => update("title", e.target.value)}
          placeholder="Brief title of the incident"
        />
      </label>

      {/* Description */}
      <label className="form-label">
        Description <span className="required">*</span>
        <textarea
          rows={4}
          value={form.description}
          onChange={(e) => update("description", e.target.value)}
          placeholder="Describe what happened (at least 15 characters)"
        />
      </label>

      {/* Neighborhood */}
      <label className="form-label">
        Neighborhood <span className="required">*</span>
        <select
          value={form.neighborhood}
          onChange={(e) => update("neighborhood", e.target.value)}
        >
          <option value="">Select neighborhood…</option>
          {NEIGHBORHOODS.map((n) => (
            <option key={n} value={n}>{n}</option>
          ))}
        </select>
      </label>

      {/* Source type */}
      <label className="form-label">
        Source type
        <select
          value={form.source_type}
          onChange={(e) => update("source_type", e.target.value)}
        >
          {SOURCE_TYPES.map((s) => (
            <option key={s} value={s}>{formatLabel(s)}</option>
          ))}
        </select>
      </label>

      {/* Timestamp */}
      <label className="form-label">
        Date / time (optional)
        <input
          type="datetime-local"
          value={form.timestamp}
          onChange={(e) => update("timestamp", e.target.value)}
        />
      </label>

      {/* Category */}
      <label className="form-label">
        Suspected category (optional)
        <select
          value={form.suspected_category}
          onChange={(e) => update("suspected_category", e.target.value)}
        >
          <option value="">Not sure</option>
          {CATEGORIES.filter(Boolean).map((c) => (
            <option key={c} value={c}>{formatLabel(c)}</option>
          ))}
        </select>
      </label>

      {/* Buttons */}
      <div className="form-actions">
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? "Submitting…" : "Submit report"}
        </button>
        {onCancel && (
          <button type="button" className="btn-secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
