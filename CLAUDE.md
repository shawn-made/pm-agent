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
    services/           # Business logic
      artifact_sync.py  # Artifact sync orchestration
      artifact_manager.py # Artifact CRUD + templates
      privacy_proxy.py  # PII anonymize/reidentify
      llm_client.py     # Abstract LLM interface
      llm_claude.py     # Claude adapter
      llm_gemini.py     # Gemini adapter
      lpd_manager.py    # Living Project Document management (Phase 1A)
      intake.py         # Bulk project file intake (Phase 1A)
      content_gate.py   # LPD content quality gate — dedup/contradiction detection (Phase 1A)
      crud.py           # Database CRUD operations
      database.py       # SQLite init + schema
    prompts/            # System prompt templates
      templates/        # Markdown prompt templates (artifact_sync, lpd)
      lpd_prompts.py    # LPD-specific prompt builder (Phase 1A)
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
- Run frontend: `cd frontend && npm run dev`

## Phase 0 Scope (Complete)

Foundation MVP:
- Artifact Sync: text input → LLM → suggestion cards → copy-to-clipboard
- Privacy Proxy: regex + spaCy NER anonymization
- 3 artifact types: RAID Log, Status Report, Meeting Notes
- Basic Settings: API keys, LLM toggle, custom sensitive terms
- SQLite database with full schema (project-scoped)

## Phase 1A Scope (In Progress)

Living Project Document (LPD) — persistent project knowledge:
- LPD Manager: section-based DB storage with staleness tracking
- Context Injection Engine: prepends LPD context to LLM prompts
- Return Path: applied suggestions feed back into LPD state
- Project Intake: bulk import existing PM files into LPD
- New tables: `lpd_sections`, `lpd_session_summaries`
- New endpoints: 8 LPD endpoints under `/api/lpd/{project_id}/`

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

## Persona Evaluation System

Two evaluation personas exist in `docs/personas/`. These are development process tools, not app features.

### Automatic Triggers
- **Skeptical PM** (`docs/personas/skeptical_pm.md`): Invoke automatically at phase boundaries — before starting Phase 1B, Phase 2, or any major feature group. Read the persona file, adopt the perspective, and evaluate the upcoming phase plan against the criteria.
- **First Outside User** (`docs/personas/first_outside_user.md`): Invoke automatically when the conversation involves evaluating market readiness, external sharing, or "is this ready for other people to use?" discussions.

### Manual Triggers
- User says "run the skeptical PM review" → load and execute the Skeptical PM persona
- User says "run the first user review" or "outside user check" → load and execute the First Outside User persona
- User says "run both reviews" → execute both sequentially

### Rules
- Persona reviews evaluate features and plans, not individual code changes
- Output follows the format defined in each persona file
- Persona feedback is advisory — the user decides what to act on
- Keep reviews concise (under 500 words each)

### Future Personas (Deferred)
Additional personas may be warranted at later phases. See the "Persona Expansion Roadmap" section at the bottom of TASKS.md for when to consider adding: Solution Architect, Product Owner, First Enterprise Buyer.

## Session Close Protocol

Before ending any session that modified code or docs:

1. Update `TASKS.md` — mark completed tasks, note progress on in-flight tasks
2. If any non-obvious decisions were made, log them in `DECISIONS.md`
3. If new questions arose, add to `QUESTIONS_LOG.md`
4. Run tests and lint — confirm passing before closing
5. **Doc freshness check** — if the session changed any of the following, update the corresponding docs:
   - Added/removed tests → update test counts in `CLAUDE.md` (Debugging section), `docs/EXECUTIVE_SUMMARY.md`, `docs/PM_LEARNING_LOG.md`
   - Added/removed API endpoints → update endpoint count in `docs/EXECUTIVE_SUMMARY.md`, route list in `docs/architecture.mermaid`
   - Added/removed DB tables → update table count in `docs/EXECUTIVE_SUMMARY.md`, ERD in `docs/architecture.mermaid`
   - Added/removed service modules → update `CLAUDE.md` Project Structure section, module count in `docs/EXECUTIVE_SUMMARY.md`
   - Added/removed components/pages → update `docs/EXECUTIVE_SUMMARY.md`
   - Changed `.env` variables → update `backend/.env.example`
   - Changed setup/run commands → update `README.md` and `CLAUDE.md` Quick Start
6. Note in a brief comment to the user: what was done, what's next, any blockers

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
# Run backend tests (651+ tests)
cd backend && source venv/bin/activate && python -m pytest tests/ -v

# Run backend tests with coverage
cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Run frontend tests (125+ tests)
cd frontend && npm test

# Run smoke tests only (pre-commit gate)
cd backend && python -m pytest -m smoke --timeout=10 -q

# Security scan
cd backend && bandit -r app/ -c ../bandit.yaml && pip-audit
cd frontend && npm audit

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
- Smoke tests only: `cd backend && python -m pytest -m smoke --timeout=10 -q`

## Quality Assurance

See [QA_PLAN.md](QA_PLAN.md) for the full quality framework. Key rules for every session:

- **Pre-commit hooks are active**. They run ruff, bandit, and smoke tests on every commit. Do not bypass with `--no-verify`.
- **Architecture tests enforce layer boundaries**. If you add a new service module, add it to the parametrized lists in `test_architecture.py`.
- **Smoke tests cover critical paths**. If you add a new critical-path feature, add a `@pytest.mark.smoke` test for it.
- **Security scanning**: Run `pip-audit` and `npm audit` periodically (monthly minimum) or before any release.
- **New service checklist**: (1) Write unit tests, (2) Add to architecture test parametrize lists, (3) Add smoke test if critical path, (4) Run full suite.
