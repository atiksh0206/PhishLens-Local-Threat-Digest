# PhishLens — Local Threat Digest

A lightweight full-stack prototype that turns noisy, scattered local cyber-safety reports into a **clear, calm, actionable digest**. Built as a Palo Alto Networks case study.

## Problem Statement

Phishing texts, scam calls, and local data breaches generate fragmented reports across neighborhoods. Residents — especially nontechnical users, elderly community members, and remote workers — need a single place to see what's happening in their area, understand the risk in plain language, and know exactly what to do next.

Existing tools are either too technical, too alarmist, or don't aggregate local signals at all.

## Core Flow

1. **Submit** — Users file a local threat / scam / phishing report via a simple form (title, description, neighborhood, category, source type).
2. **View** — A dashboard displays incident cards with category, status, neighborhood, and a truncated summary. Search and filter controls narrow results by text, category, neighborhood, or status.
3. **Update** — Report status can be changed (new → acknowledged → duplicate → resolved → needs_review).
4. **Digest** — `GET /api/digest` generates a summary of matching incidents, using AI when available and a deterministic fallback when not.

## AI Summary + Deterministic Fallback

The app implements **one strong AI capability: summarization**.

| Path | When it runs | How it works |
|------|-------------|--------------|
| **AI** | API key is configured and the call succeeds | Sends grouped reports to OpenAI (gpt-4o-mini) or Gemini via the OpenAI-compatible SDK. Returns a structured JSON digest: summary, explanation, actions, confidence note. |
| **Fallback** | No key set, API error, timeout, or malformed response | Keyword-based category detection → grouping by category/neighborhood/time proximity → template-based summary and action checklist from `data/playbooks.json`. Zero network calls. |

The response always includes a `"source"` field (`"ai"`, `"fallback"`, or `"none"`) so the frontend knows which path produced the digest. AI output is treated as **assistive, never authoritative** — confidence language is always present.

## Setup

```bash
# 1. Clone and copy env template
git clone <repo-url> && cd PhishLens-Local-Threat-Digest
cp .env.example .env       # then edit .env with your API key (optional)

# 2. Backend
cd backend
python -m venv venv
venv\Scripts\activate       # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py               # runs on http://localhost:5000

# 3. Frontend (separate terminal)
cd frontend
npm install
npm run dev                 # runs on http://localhost:3000, proxies /api to Flask
```

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

All data is **synthetic**. No real incidents, users, or addresses are used.

| File | Contents |
|------|----------|
| `data/incidents.json` | 10 seed incidents across 7 categories and 5 neighborhoods |
| `data/trusted_sources.json` | 5 verification sources (government, bank, FTC, ISP, nonprofit) |
| `data/playbooks.json` | Category-keyed templates with summary, explanation, and action checklists |

## Tests

Two focused pytest tests covering the deterministic fallback:

```bash
cd backend
python -m pytest tests/test_fallback.py -v
```

| Test | What it verifies |
|------|-----------------|
| `test_groups_similar_phishing_reports` | Two phishing SMS reports in the same neighborhood are grouped correctly, produce a template summary, include carrier-report action, and note same-category confidence |
| `test_handles_low_information_report_with_safe_fallback` | A single vague report with no category detects as "unknown", returns a complete digest, and notes limited data |

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
│       └── test_fallback.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Dashboard with search, filters, cards
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

## Limitations and Tradeoffs

- **Prototype scope** — not production-ready; no auth, no database, no deployment config.
- **JSON file storage** — simple but not concurrent-safe; acceptable for a single-user demo.
- **AI summaries may be inaccurate** — confidence language and the `source` field mitigate this. The fallback is always available.
- **Fallback is template-based** — produces correct but generic output; lacks the nuance of AI summaries.
- **No real data ingestion** — synthetic only; no scraping, no live feeds, no social media.
- **Keyword detection is basic** — covers common terms but won't catch novel phrasing. A production system would use NLP or fine-tuned classifiers.
- **No incident detail page yet** — dashboard shows cards but there's no dedicated single-incident view with full digest.

## License

This project is a case study prototype and is not licensed for production use.
