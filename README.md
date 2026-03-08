# PhishLens — Local Threat Digest

A lightweight full-stack prototype that turns noisy, scattered local cyber-safety reports into a **clear, calm, actionable digest**. Built as a Palo Alto Networks case study.

---

## Submission Info

| Field | Details |
|-------|---------|
| **Candidate** | Atiksh Shah |
| **Scenario** | Case 3 — Community Safety & Digital Wellness |
| **Time Spent** | ~5 hours |

---

## Quick Start

### Prerequisites

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)
- **npm** (comes with Node.js)
- *(Optional)* An OpenAI API key — the app works without one via the deterministic fallback

### Run Commands

```bash
# 1. Clone and set up environment
git clone <repo-url> && cd PhishLens-Local-Threat-Digest
cp .env.example .env          # edit .env to add your API key (optional)

# 2. Backend (terminal 1)
cd backend
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py                  # → http://localhost:5000

# 3. Frontend (terminal 2)
cd frontend
npm install
npm run dev                    # → http://localhost:3000
```

Open **http://localhost:3000** in a browser. The frontend proxies `/api` requests to Flask automatically.

### Test Commands

```bash
cd backend
python -m pytest tests/ -v
```

Runs 20 tests in ~0.3 seconds — no network calls, no API key needed.

---

## AI Disclosure

- **Did you use an AI assistant?** Yes — GitHub Copilot (Claude) was used throughout development for code generation, debugging, and iteration.
- **How did you verify the suggestions?** Every generated file was reviewed for correctness before committing. Backend functions were smoke-tested in the terminal (Flask test client, direct function calls). The frontend was visually tested in the browser after each change. All 20 pytest tests pass and were reviewed line by line.
- **Example of a suggestion rejected or changed:** The AI initially attempted to use Google Gemini as the default AI provider and generated Gemini-specific SDK code. After hitting persistent free-tier rate limits (429 errors), I switched the implementation to use OpenAI's gpt-4o-mini as the default and restructured the adapter to use the OpenAI SDK for both providers (Gemini via its OpenAI-compatible endpoint). The original Gemini-only code was fully replaced. Additionally, the AI suggested building a separate dedicated incident detail page with React Router. I rejected this in favor of expandable cards that open in-place on the dashboard — this kept the codebase simpler (no routing library, single-component state) while still exposing full incident details and inline status updates.

---

## Tradeoffs & Prioritization

### What I cut to stay within the time limit

- **Authentication / user accounts** — not needed for a single-user demo; would add complexity without demonstrating the core flow.
- **Database (PostgreSQL/SQLite)** — JSON file storage is simpler and sufficient for prototype-scale data. Avoids setup friction for reviewers.
- **Dedicated incident detail page / routing** — instead, cards expand in-place on the dashboard with full details and status controls. This covers the same UX need with less code.
- **CSV export / PDF report generation** — nice-to-have but not part of the core CRUD + AI summarization flow.
- **Deployment config (Docker, CI/CD)** — kept the focus on local development and demo-ability.

### What I would build next with more time

- **React Router + dedicated detail page** — full incident view with related reports, AI digest scoped to that incident, and an action checklist with checkboxes.
- **SQLite or PostgreSQL backend** — proper concurrent storage, migrations, and query performance.
- **Batch digest scheduling** — generate daily/weekly neighborhood digests automatically.
- **Confidence scoring** — use report volume, time clustering, and source diversity to assign a numeric confidence level to each digest.
- **NLP-based category detection** — replace keyword matching with a lightweight classifier (e.g., scikit-learn or a small fine-tuned model) for better accuracy on novel phrasing.
- **User auth + roles** — let neighborhood admins triage reports and mark trusted sources.
- **Mobile-responsive polish** — the current CSS is functional but not optimized for small screens.

### Known limitations

- **Prototype scope** — not production-ready; no auth, no database, no deployment config.
- **JSON file storage** — simple but not concurrent-safe; acceptable for a single-user demo.
- **AI summaries may be inaccurate** — confidence language and the `source` field mitigate this. The fallback is always available.
- **Fallback is template-based** — produces correct but generic output; lacks the nuance of AI summaries.
- **No real data ingestion** — synthetic only; no scraping, no live feeds, no social media.
- **Keyword detection is basic** — covers common terms but won't catch novel phrasing.

---

## Problem Statement

Phishing texts, scam calls, and local data breaches generate fragmented reports across neighborhoods. Residents — especially nontechnical users, elderly community members, and remote workers — need a single place to see what's happening in their area, understand the risk in plain language, and know exactly what to do next.

Existing tools are either too technical, too alarmist, or don't aggregate local signals at all.

## Core Flow

1. **Submit** — Users file a local threat / scam / phishing report via a simple form (title, description, neighborhood, category, source type).
2. **View** — A dashboard displays incident cards with category, status, neighborhood, and a truncated summary. Search and filter controls narrow results by text, category, neighborhood, or status.
3. **Update** — Click a card to expand it, view full details, and update status inline (new → acknowledged → duplicate → resolved → needs_review).
4. **Digest** — Click "Generate Digest" to produce a summary of matching incidents, using AI when available and a deterministic fallback when not. A "Force fallback" checkbox lets you demo both paths.

## AI Summary + Deterministic Fallback

The app implements **one strong AI capability: summarization**.

| Path | When it runs | How it works |
|------|-------------|--------------|
| **AI** | API key is configured and the call succeeds | Sends grouped reports to OpenAI (gpt-4o-mini) or Gemini via the OpenAI-compatible SDK. Returns a structured JSON digest: summary, explanation, actions, confidence note. |
| **Fallback** | No key set, API error, timeout, or malformed response | Keyword-based category detection → grouping by category/neighborhood/time proximity → template-based summary and action checklist from `data/playbooks.json`. Zero network calls. |

The response always includes a `"source"` field (`"ai"`, `"fallback"`, or `"none"`) so the frontend knows which path produced the digest. AI output is treated as **assistive, never authoritative** — confidence language is always present.

The frontend shows a badge on the digest card: **"AI Summary"** (blue) or **"Rule-Based"** (amber) so the user always knows the source.

## .env Usage

Copy `.env.example` to `.env` in the project root. The backend reads it via `python-dotenv`.

| Variable | Purpose | Default |
|----------|---------|---------|
| `AI_PROVIDER` | `openai` or `gemini` | `openai` |
| `OPENAI_API_KEY` | OpenAI API key (required for AI path) | — |
| `GEMINI_API_KEY` | Gemini API key (only if provider is `gemini`) | — |
| `MODEL_NAME` | Override the model name | `gpt-4o-mini` / `gemini-2.0-flash-lite` |
| `PORT` | Flask server port | `5000` |

If no valid API key is set, the app runs entirely on the deterministic fallback — no errors, no degradation.

## Synthetic Data

All data is **synthetic**. No real incidents, users, or addresses are used. No live scraping or external data sources.

| File | Contents |
|------|----------|
| `data/incidents.json` | 10 seed incidents across 7 categories and 5 neighborhoods |
| `data/trusted_sources.json` | 5 verification sources (government, bank, FTC, ISP, nonprofit) |
| `data/playbooks.json` | Category-keyed templates with summary, explanation, and action checklists |

## Tests

20 pytest tests across 3 files, all run offline in ~0.3 seconds:

```bash
cd backend
python -m pytest tests/ -v
```

| File | Tests | Coverage |
|------|-------|----------|
| `test_fallback.py` | 5 | Fallback grouping, keyword detection, multi-category, empty input, vague reports |
| `test_validation.py` | 5 | Required fields, description length, invalid neighborhood/category, valid input |
| `test_api.py` | 10 | All CRUD endpoints, search/filter, digest with fallback, force_fallback, validation errors, 404s |

## Project Structure

```
├── backend/
│   ├── app.py              # Flask routes (CRUD + /api/digest)
│   ├── data_store.py       # JSON file store with in-memory cache
│   ├── schemas.py          # Validation constants and helpers
│   ├── summarizer.py       # AI summarization adapter (OpenAI / Gemini)
│   ├── fallback.py         # Deterministic fallback summarizer
│   ├── requirements.txt
│   └── tests/
│       ├── test_fallback.py
│       ├── test_validation.py
│       └── test_api.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Dashboard with search, filters, expandable cards
│   │   ├── ReportForm.jsx  # Submit-report form
│   │   ├── App.css
│   │   └── main.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── data/
│   ├── incidents.json
│   ├── trusted_sources.json
│   └── playbooks.json
├── .env.example
└── README.md
```

## License

This project is a case study prototype and is not licensed for production use.
