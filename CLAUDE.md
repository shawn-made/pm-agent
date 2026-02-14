# VPMA Development Instructions

You're building **VPMA** (Virtual Project Management Assistant) — a local, privacy-centric PM agent.

## Architecture

- **Frontend**: JavaScript React + Tailwind CSS (localhost:3000)
- **Backend**: Python FastAPI (localhost:8000)
- **Database**: SQLite (metadata) + Markdown files (artifact content)
- **LLM**: Abstract client interface with Claude + Gemini adapters
- **Privacy**: Regex + spaCy NER anonymization with global vault

## Project Structure

```
backend/                # Python FastAPI application
  app/
    main.py             # FastAPI app entry point
    api/                # API route handlers
    models/             # Pydantic models + SQLite schemas
    services/           # Business logic (artifact sync, privacy proxy, LLM client)
    prompts/            # System prompt templates
frontend/               # React application
  src/
    components/         # React components
    pages/              # Page-level components (ArtifactSync, Settings)
    services/           # API client, utilities
    App.jsx             # Root component
prd.md                  # Vision PRD (source of truth)
TASKS.md                # RALPH task tracking
```

## Key Patterns

1. **Abstract LLM Client**: All LLM calls go through `services/llm_client.py` base interface. Never call APIs directly. This enables Claude ⟷ Gemini ⟷ Ollama switching.

2. **Privacy Proxy**: All user text must pass through `services/privacy_proxy.py` before reaching any LLM. Flow: `anonymize(text) → LLM call → reidentify(response)`.

3. **Project-Scoped Data**: Every database table includes `project_id`. MVP is single-project but the schema supports multi-project from day one.

4. **Environment Config**: All URLs, API keys, and paths come from `.env`. No hardcoded `localhost` in business logic.

5. **Input Type Detection**: Backend classifies input type (text, transcript) via pipeline. Extensible for images later.

## Development Workflow

- Use RALPH loop technique: prompt → review → test → refine
- Check `TASKS.md` for current task and progress
- Reference `prd.md` for detailed requirements (Section 7 Phase 0 for MVP scope)
- Run backend: `cd backend && uvicorn app.main:app --reload`
- Run frontend: `cd frontend && npm start`

## Phase 0 Scope (Current)

Building the Foundation MVP:
- Artifact Sync: text input → LLM → suggestion cards → copy-to-clipboard
- Privacy Proxy: regex + spaCy NER anonymization
- 3 artifact types: RAID Log, Status Report, Meeting Notes
- Basic Settings: API keys, LLM toggle, custom sensitive terms
- SQLite database with full schema (project-scoped)

## Rules

- Never bypass the Privacy Proxy for LLM calls
- Never hardcode API keys (always use .env)
- Keep the LLM client abstract (no provider-specific code in business logic)
- Artifact content lives in `~/VPMA/artifacts/` as Markdown files, not in SQLite
- SQLite stores metadata only (timestamps, references, sessions, PII vault)
