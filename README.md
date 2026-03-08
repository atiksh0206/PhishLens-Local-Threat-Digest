# PhishLens — Local Threat Digest

A lightweight prototype that turns noisy, scattered local cyber-safety reports into a clear, calm, actionable digest. Built as a Palo Alto Networks case study.

## Problem

Phishing texts, scam calls, and local data breaches generate lots of fragmented reports. Residents — especially nontechnical users — need a single place to see what's happening in their neighborhood, understand the risk, and know what to do next.

## Features (planned)

- Submit local threat / scam / phishing reports
- Dashboard of incidents with search and filters
- Update report status (new → acknowledged → resolved …)
- AI-generated digest summaries with a deterministic fallback when AI is unavailable
- Synthetic data only — no live scraping

## Tech Stack

| Layer | Choice |
|-------|--------|
| Frontend | React + Vite |
| Backend | Flask (Python) |
| Storage | Local JSON files |
| AI | OpenAI API (optional) with rule-based fallback |
| Tests | pytest |

## Project Structure

```
├── backend/            # Flask API (coming soon)
│   └── requirements.txt
├── frontend/           # React app (coming soon)
│   └── package.json
├── data/               # Synthetic seed data
│   ├── incidents.json
│   ├── trusted_sources.json
│   └── playbooks.json
├── .env.example        # Environment variable template
└── README.md
```

## Setup (will be expanded)

```bash
# 1. Copy env template
cp .env.example .env

# 2. Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Frontend
cd ../frontend
npm install
```

## Data

All data is **synthetic**. No real incidents, users, or addresses are used. See the `data/` directory for seed files.

## AI + Fallback

- When an API key is configured, the app sends grouped reports to the AI for a digest summary.
- When AI is unavailable (no key, network error, malformed response), a **deterministic rule-based fallback** generates summaries from keyword detection + playbook templates.
- AI output is treated as assistive, never authoritative.

## Known Limitations

- Prototype scope — not production-ready
- No authentication or user accounts
- No real data ingestion or scraping
- AI summaries may be inaccurate; confidence language is always shown

## License

This project is a case study prototype and is not licensed for production use.
