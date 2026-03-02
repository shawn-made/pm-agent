# VPMA: Virtual Project Management Assistant

A local, privacy-centric Project Management agent that helps PMs maintain artifacts efficiently.

Paste meeting notes → get artifact update suggestions → copy to clipboard.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- An API key for Claude (Anthropic) or Gemini (Google AI)

### Setup

```bash
# Clone and enter project
cd "PM Agent"

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env  # Edit with your API keys

# Frontend
cd ../frontend
npm install
```

### Run

```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

Open http://localhost:3000

## How It Works

1. **Paste** meeting notes, transcripts, or project updates
2. **VPMA** anonymizes PII, sends to LLM, identifies which artifacts need updates
3. **Review** suggestion cards with proposed changes
4. **Copy** updates to clipboard and paste into your real artifacts

## Privacy

All text is anonymized (names, emails, orgs → tokens) before reaching any external LLM API. The Privacy Proxy uses regex patterns + spaCy NER. Original values stay in a local vault on your machine.

## Architecture

- **Frontend**: React + Tailwind CSS
- **Backend**: Python FastAPI
- **Database**: SQLite (metadata) + Markdown files (artifact content)
- **LLM**: Claude / Gemini (toggle in Settings)
- **Storage**: `~/VPMA/` directory

## Current Phase

**Phase 0: Foundation MVP** — Core Artifact Sync with Privacy Proxy, 3 artifact types (RAID Log, Status Report, Meeting Notes), basic Settings.

See [prd.md](prd.md) for full product vision and roadmap.
