# VPMA — Executive Technical Summary

**Version**: 0.4.0 — Phase 0 Complete, Phase 1A Complete, Phase 1B Complete, Phase 2A Complete
**Last Updated**: 2026-03-04

---

## What VPMA Does (The Elevator Pitch)

VPMA is a **local, privacy-first project management assistant**. A PM pastes in meeting notes, transcripts, or project updates. VPMA reads the text, strips out personally identifiable information (names, emails, phone numbers), sends the sanitized text to an AI model, and returns structured suggestions: "Here's a RAID Log entry to add," "Here's an updated Status Report," "Here are Meeting Notes to file."

The PM reviews the suggestions, copies what they want, and applies it to their project. No data leaves the machine unprotected. The AI never sees real names.

---

## Architecture Overview

VPMA is a **two-process local application**:

| Layer | Technology | Runs On | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | React + Tailwind CSS | localhost:3000 | User interface — text input, suggestion cards, settings |
| **Backend** | Python FastAPI | localhost:8000 | Business logic — privacy, AI calls, artifact management |
| **Database** | SQLite | ~/VPMA/vpma.db | Metadata storage — sessions, settings, PII vault |
| **File Storage** | Markdown files | ~/VPMA/artifacts/ | Artifact content — the actual RAID logs, reports, notes |
| **AI** | Claude, Gemini (cloud), or Ollama (local) | Remote or local | Text analysis and suggestion generation |

**Why two processes?** Separation of concerns. The frontend handles user interaction only. The backend handles all sensitive operations (privacy, AI, storage). They communicate over HTTP on localhost. This is the standard pattern for modern web applications and makes each piece independently testable.

**Why SQLite + Markdown?** SQLite handles structured metadata (who, when, what type, which session). Markdown files hold the actual artifact content — this makes artifacts human-readable, version-controllable with git, and editable outside the app. It's a deliberate architectural choice: metadata in the database, content in files.

---

## The Core Data Flow

This is the most important thing to understand — the end-to-end pipeline:

```
User pastes text
    │
    ▼
[Frontend] ──POST /api/artifact-sync──► [Backend API]
                                            │
                                            ▼
                                    [Input Type Classifier]
                                    "Is this meeting notes, a
                                     transcript, or general text?"
                                            │
                                            ▼
                                    [Privacy Proxy: ANONYMIZE]
                                    Step 1: Regex (emails, phones, URLs)
                                    Step 2: spaCy NER (names, companies)
                                    Step 3: Custom terms (user-defined)
                                    "John Smith" → <PERSON_1>
                                    "Acme Corp"  → <ORG_1>
                                            │
                                            ▼
                                    [LLM Client] ──API call──► Claude/Gemini
                                    Sends ONLY anonymized text.
                                    AI never sees real names.
                                            │
                                            ▼
                                    [Parse LLM Response]
                                    Extract structured suggestions:
                                    - artifact type (RAID, Status, Notes)
                                    - change type (add, update)
                                    - proposed text (still anonymized)
                                            │
                                            ▼
                                    [Privacy Proxy: RE-IDENTIFY]
                                    <PERSON_1> → "John Smith"
                                    <ORG_1>    → "Acme Corp"
                                            │
                                            ▼
[Frontend] ◄── JSON response ────── [Backend API]
    │
    ▼
User sees suggestion cards
with REAL names restored.
Copies or applies as needed.
```

**Key insight**: The AI model is powerful but untrusted with PII. The Privacy Proxy wraps every AI call — anonymize before, re-identify after. This is enforced architecturally (the code path makes it impossible to skip).

---

## Key Architectural Decisions

### 1. Abstract LLM Client (Provider Switching)

The app doesn't call Claude or Gemini directly. It calls an **abstract interface** (`LLMClient.call()`), and a factory creates the right provider. This means:
- Switching between Claude, Gemini, and Ollama is a settings toggle, not a code change
- Adding a new provider just means implementing one more adapter
- Business logic never knows or cares which AI provider is active

**Engineering term**: *Strategy pattern* / *dependency injection*

### 2. Privacy Proxy (Three-Layer PII Detection)

Three detection methods run in sequence, each catching what the others miss:

| Layer | Method | Catches | Reliability |
|-------|--------|---------|-------------|
| Regex | Pattern matching | Emails, phones, URLs | Very high (deterministic) |
| spaCy NER | Machine learning | Person names, company names, locations | High (context-aware) |
| Custom terms | User-defined list | Project-specific sensitive words | Exact match |

Overlapping detections are deduplicated (prefer longer, higher-confidence matches). This layered approach is standard in data privacy engineering.

### 3. Project-Scoped Schema (Future-Proofing)

Every database table has a `project_id` column. Phase 0 uses only one project, but the schema supports multiple projects from day one. This prevents a painful database migration later.

**Engineering term**: *Schema forward-compatibility*

### 4. Markdown Artifact Storage

Artifacts (RAID logs, status reports) are stored as Markdown files, not database blobs. Benefits:
- Human-readable without the app
- Can be version-controlled with git
- Editable in any text editor
- Easy to export or share

---

## Technology Choices Explained

| Choice | Why This | What It Means |
|--------|----------|---------------|
| **React** | Industry-standard UI framework | Component-based, huge ecosystem, easy to hire for |
| **Tailwind CSS** | Utility-first styling | Fast development, consistent design, no custom CSS files |
| **FastAPI** | Modern Python web framework | Auto-generates API docs, async support, type-safe |
| **SQLite** | File-based database | Zero setup, no database server, portable |
| **spaCy** | NLP library for entity detection | Industry standard for NER, lightweight model available |
| **Pydantic** | Data validation library | Ensures API inputs/outputs match expected shapes |
| **Vite** | Frontend build tool | Fast hot-reload during development |

---

## What's Built (Phase 0 Scope)

| Feature | Status | Files Involved |
|---------|--------|---------------|
| Text input with auto-resize | Complete | `TextInput.jsx` |
| Suggestion cards with copy/apply | Complete | `SuggestionCard.jsx` |
| Privacy anonymization pipeline | Complete | `privacy_proxy.py` |
| PII vault (persistent name mapping) | Complete | `crud.py`, SQLite |
| Claude adapter | Complete | `llm_claude.py` |
| Gemini adapter | Complete | `llm_gemini.py` |
| LLM provider toggle | Complete | Settings page |
| 3 artifact types | Complete | `artifact_manager.py` |
| System prompt templates | Complete | `prompts/templates/` |
| Toast notification system | Complete | `Toast.jsx`, `ToastContext.js` |
| Error handling & loading states | Complete | Throughout |
| Living Project Document (LPD) | Complete | `lpd_manager.py`, `ProjectDoc.jsx` |
| Context injection engine | Complete | `artifact_sync.py` |
| Return path (Apply → LPD) | Complete | `lpd_manager.py`, `routes.py` |
| Project intake (bulk file import) | Complete | `intake.py`, `Intake.jsx` |
| Log session bridge | Complete | `artifact_sync.py`, `LogSessionCard.jsx` |
| Content quality gate (dedup/contradiction) | Complete | `content_gate.py` |
| Semantic dedup on Apply (return path) | Complete | `lpd_manager.py`, `content_gate.py` |
| Result persistence across tabs | Complete | `usePersistedResults.js` |
| LPD update toast feedback | Complete | `ArtifactSync.jsx`, `LogSessionCard.jsx` |
| VTT/SRT transcript parser | Complete | `vtt_parser.py` |
| Transcript file watcher service | Complete | `transcript_watcher.py`, Settings page |
| Ollama local LLM adapter | Complete | `llm_ollama.py`, Settings page |
| Markdown/clipboard export | Complete | `ProjectDoc.jsx`, `ArtifactSync.jsx`, `routes.py` |
| LPD change summary on Apply | Complete | `lpd_manager.py`, suggestion cards |
| Transcript watcher results view | Complete | Settings page (expandable results) |
| Transcript drag-and-drop upload | Complete | Settings page (drop zone), `routes.py` |
| Conversational API design | Complete | `docs/conversational_api_design.md`, `schemas.py` |
| Deep Strategy 4-pass engine | Complete | `deep_strategy.py`, `DeepStrategy.jsx` |
| AI Risk Prediction | Complete | `risk_prediction.py`, `RiskPredictionPanel.jsx` |
| Cross-section LPD Reconciliation | Complete | `reconciliation.py`, `ReconciliationPanel.jsx` |
| Folder browser for Settings | Complete | `routes.py`, `FolderBrowser.jsx` |

---

## What's Next (Phase Roadmap)

| Phase | Focus | Key Additions |
|-------|-------|--------------|
| **Phase 1A** | Living Project Document | ~~LPD with section-based storage, context injection, return path, project intake~~ DONE |
| **Phase 1B** | Fit & Finish + Transcripts | ~~Semantic dedup, result persistence, transcript watcher, UX polish~~ DONE |
| **Phase 2A** | Workflow Completion | ~~Ollama adapter, export, change summary, results view, drag-drop, conv. API design~~ DONE |
| **Phase 2B** | Deep Analysis | ~~Deep strategy tab, folder browser, AI risk prediction, cross-section reconciliation~~ DONE |
| **Phase 3** | Proactive | Daily planner, project initiation wizard, history search |
| **Phase 4** | Commercial | Google auth, security hardening, integrations, HR planning |

---

## Codebase Statistics

- **Backend**: 17 service modules, 8 database tables, 30 API endpoints
- **Frontend**: 13 components, 5 pages, 1 hook, 1 API service module
- **Tests**: 1,199+ total (915+ backend + 284+ frontend)
- **Lines of code**: ~8,500 backend Python, ~3,200 frontend JavaScript (estimated)

---

## Glossary for PM Conversations

| Term | Plain English |
|------|--------------|
| **API endpoint** | A specific URL the frontend calls to ask the backend to do something (e.g., POST /api/artifact-sync) |
| **CORS** | Security rule that says "only my frontend at localhost:3000 can talk to my backend at localhost:8000" |
| **NER** | Named Entity Recognition — AI technique for finding names, companies, and places in text |
| **PII** | Personally Identifiable Information — names, emails, phones, anything that identifies a person |
| **Pydantic model** | A Python class that defines the exact shape of data (like a form template — must have these fields, of these types) |
| **SQLite** | A database that lives in a single file — no server needed, just a file on disk |
| **Token (privacy)** | A placeholder like `<PERSON_1>` that replaces a real name during anonymization |
| **Vault** | The database table that stores the mapping between tokens and real names |
| **Abstract interface** | A code contract that says "any LLM provider must implement these methods" — enables switching providers |
| **Factory pattern** | Code that creates the right object based on a setting ("give me a Claude client" or "give me a Gemini client") |
| **Middleware** | Code that runs on every request before it reaches the main logic (like a security checkpoint) |
| **Async** | Code that can wait for slow operations (API calls, database reads) without blocking other work |
| **Round-trip** | Anonymize then re-identify — the text should be identical to the original. Tests verify this. |
