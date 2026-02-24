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

6. **Architecture Insights from Real PM Workflow**: Read `docs/VPMA_ARCHITECTURE_INSIGHTS.md` for 7 validated design patterns (return path, staleness detection, nav vs. session separation, action item routing, weekly cadence, audience views, cross-tool orchestration). Consult when designing new features or planning future phases.

## Development Workflow

- Read `~/Projects/Cross Project Docs/PROCESS_PLAYBOOK.md` before starting — it contains cross-project process rules
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

## Generality & Privacy Rules

VPMA is a **general-purpose PM tool**. The shipped product (source code, prompts, tests, UI) must never contain references to the developer's personal projects, career history, or specific clients.

### Hard Rules (enforced now)
- **No personal references in code/app**: Never include real company names, client names, project names, or people's names in source code, prompts, test data, or UI. Use clearly fictional placeholders (Acme Corp, Project Falcon, etc.).
- **No industry-specific bias**: Features, examples, and prompts should work across all industries (tech, construction, healthcare, government, etc.). Avoid skewing toward any single domain.
- **Generic examples only**: All prompt examples, test fixtures, and UI placeholder text must use fictional names and scenarios that any PM could relate to.
- **No personal constraints in architecture**: When implementing features, design for general use. If a decision is being shaped by a personal constraint (specific hardware, budget tier, single-user assumption), flag it so it doesn't become baked-in technical debt. The question to ask: "Would this implementation work for someone with different hardware/budget/team size?"

### Personal Fingerprints (acceptable in planning docs, clean up before external release)
Planning docs (prd.md, QUESTIONS_LOG.md, TASKS.md, VPMA_ARCHITECTURE_INSIGHTS.md) contain references to the developer's hardware (M4 MacBook Air 24GB), skill level, subscription budget, and personal workflow patterns. These are practical for current development and acceptable in private planning artifacts. They should be generalized before any external sharing or open-sourcing.

## Session Close Protocol

Before ending any session that modified code or docs:

1. Update `TASKS.md` — mark completed tasks, note progress on in-flight tasks
2. If any non-obvious decisions were made, log them in `DECISIONS.md`
3. If new questions arose, add to `QUESTIONS_LOG.md`
4. Run tests and lint — confirm passing before closing
5. Note in a brief comment to the user: what was done, what's next, any blockers

---

## Quick Start

```bash
# Clone and install backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Configure environment
cp .env.example .env  # then add your API keys

# Run backend
uvicorn app.main:app --reload  # → http://localhost:8000

# Install and run frontend (separate terminal)
cd frontend
npm install
npm run dev  # → http://localhost:3000
```

## Debugging

```bash
# Run backend tests (174 tests)
cd backend && source venv/bin/activate && python -m pytest tests/ -v

# Run backend tests with coverage
cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Run frontend tests (57 tests)
cd frontend && npm test

# Lint backend
cd backend && ruff check .

# Lint frontend
cd frontend && npm run lint

# Check SQLite database
sqlite3 ~/VPMA/vpma.db ".tables"
sqlite3 ~/VPMA/vpma.db "SELECT * FROM settings;"

# Inspect PII vault
sqlite3 ~/VPMA/vpma.db "SELECT token, entity_type FROM pii_vault LIMIT 20;"

# Check audit log
cat ~/VPMA/privacy/audit_log.jsonl | tail -5

# View API docs
open http://localhost:8000/docs
```

## Testing Rules

- Always run tests after changes. Always lint. Always write tests for new features.
- Backend: `cd backend && python -m pytest tests/ -v`
- Frontend: `cd frontend && npm test`
- Lint backend: `cd backend && ruff check .`
- Lint frontend: `cd frontend && npm run lint`
- Fix lint issues: `cd backend && ruff check . --fix`
