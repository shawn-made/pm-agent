# VPMA Phase 0: Foundation MVP — RALPH Tasks

**Target**: 4 weeks (~50-70 keyboard hours)
**Method**: Claude Code + RALPH loop (prompt → review → test → refine)

## Progress

| Group | Tasks | Done | Status |
|-------|-------|------|--------|
| Infrastructure | 1-4 | 4/4 | Complete |
| Privacy & LLM | 5-8 | 4/4 | Complete |
| Backend Logic | 9-12 | 4/4 | Complete |
| Frontend | 13-17 | 5/5 | Complete |
| Integration & Polish | 18-20 | 3/3 | Complete |

---

## Infrastructure (Tasks 1-4)

### Task 1: Project Scaffolding
- [x] React app (Create React App or Vite), Tailwind CSS setup
- [x] FastAPI skeleton with CORS middleware
- [x] Directory structure (backend/app/{api,models,services,prompts}, frontend/src/{components,pages,services})
- [x] .env loading in backend
- [x] ~/VPMA/ directory creation (artifacts/, privacy/, feedback/, analytics/)
**Status**: Complete

### Task 2: SQLite Database Setup
- [x] Schema with all tables: projects, artifacts, artifact_versions, sessions, pii_vault, settings
- [x] project_id on all tables (multi-project ready)
- [x] Connection module (async with aiosqlite)
- [x] Init script (create tables on first run)
- [x] Basic CRUD queries (25 functions in services/crud.py + Pydantic models in models/schemas.py)
**Status**: Complete

### Task 3: Privacy Proxy — Regex PII Detection
- [x] Email pattern detection
- [x] Phone number pattern detection
- [x] URL pattern detection
- [x] Custom sensitive terms matching (from settings)
- [x] Unit tests with sample text (21 tests)
**Status**: Complete

### Task 4: Privacy Proxy — spaCy NER Integration
- [x] Load en_core_web_sm model (lazy-loaded)
- [x] PERSON entity detection
- [x] ORG entity detection
- [x] GPE (location) entity detection
- [x] Confidence scoring (flag low confidence < 70%)
- [x] Unit tests (18 tests including combined pipeline)
**Status**: Complete

---

## Privacy & LLM (Tasks 5-8)

### Task 5: Privacy Proxy — Vault & Anonymize/Reidentify
- [x] Token vault (store/retrieve mappings in SQLite pii_vault table)
- [x] anonymize(text) function — combines regex + NER, replaces with tokens (<PERSON_1>, etc.)
- [x] reidentify(text) function — replaces tokens back to originals
- [x] Audit log writing (append to ~/VPMA/privacy/audit_log.jsonl)
- [x] Global vault scope (not project-specific)
- [x] Unit tests for round-trip anonymize → reidentify (18 tests)
**Status**: Complete

### Task 6: LLM Client — Base Abstract Interface
- [x] Base class with call() method (system_prompt, user_prompt, max_tokens) → str
- [x] Provider enum (CLAUDE, GEMINI, OLLAMA)
- [x] Client factory: create_client(provider) → LLMClient
- [x] Error handling (retry with exponential backoff, 3 attempts)
- [x] Token counting stub
**Status**: Complete

### Task 7: LLM Client — Claude Adapter
- [x] ClaudeClient implementing base interface
- [x] API key from .env (ANTHROPIC_API_KEY)
- [x] Model selection (default: claude-sonnet-4-5-20250929)
- [x] Error handling for API failures
- [x] Unit tests (mock API call, 8 tests)
**Status**: Complete

### Task 8: LLM Client — Gemini Adapter
- [x] GeminiClient implementing base interface
- [x] API key from .env (GOOGLE_AI_API_KEY)
- [x] Model selection (default: gemini-2.0-flash)
- [x] Error handling for API failures
- [x] Unit tests (mock API call, 7 tests)
**Status**: Complete

---

## Backend Logic (Tasks 9-12)

### Task 9: Artifact Manager — Types & Templates
- [x] Artifact type definitions (RAID Log, Status Report, Meeting Notes)
- [x] Markdown template for each type
- [x] Template loading from backend/app/prompts/templates/
- [x] Artifact CRUD (create, read, update via markdown files in ~/VPMA/artifacts/)
- [x] Metadata tracking in SQLite artifacts table
- [x] Unit tests (18 tests)
**Status**: Complete

### Task 10: Artifact Sync — Core Backend Logic
- [x] Input → Privacy Proxy anonymize → LLM call → parse response → suggestions
- [x] Input type classification (text vs transcript — extensible)
- [x] Delta extraction (what changed, what's new)
- [x] Suggestion model (artifact_type, change_type, proposed_text, confidence)
- [x] Session logging (write to SQLite sessions table)
**Status**: Complete

### Task 11: Artifact Sync — System Prompts
- [x] System prompt for artifact detection ("which artifacts need updates?")
- [x] System prompt for delta extraction ("what specific changes?")
- [x] Structured JSON output format for suggestions
- [x] Few-shot examples for each artifact type
- [x] Input type classification prompt
- [x] Unit tests for parsing and classification (15 tests)
**Status**: Complete

### Task 12: FastAPI Endpoints
- [x] POST /api/artifact-sync (main flow: text → suggestions)
- [x] GET /api/settings (retrieve current settings)
- [x] PUT /api/settings (update settings — API keys, LLM provider, sensitive terms)
- [x] GET /api/health (backend status check)
- [x] POST /api/artifacts/{id}/apply (apply a suggestion to local storage)
- [x] Request/response Pydantic models
- [x] CORS configuration for localhost:3000
- [x] API endpoint tests (9 tests)
**Status**: Complete

---

## Frontend (Tasks 13-17)

### Task 13: React App Shell
- [x] Two-tab navigation (Artifact Sync, Settings)
- [x] Layout component with header (VPMA branding)
- [x] React Router setup (/ → Artifact Sync, /settings → Settings)
- [x] Tailwind CSS base styles
- [x] API base URL from environment (Vite proxy to localhost:8000)
**Status**: Complete

### Task 14: Text Input Component
- [x] Large text area with placeholder ("Paste meeting notes, transcripts, or project updates...")
- [x] Submit button with loading state
- [x] Character count display
- [x] Clear button
- [x] Auto-resize text area
**Status**: Complete

### Task 15: Suggestion Cards Component
- [x] Card layout per suggestion (artifact name, change type, proposed text)
- [x] Expandable preview (click to show full text)
- [x] Copy-to-clipboard button (primary action)
- [x] Apply button (stores in VPMA database)
- [x] Visual feedback on copy/apply (toast or checkmark)
- [x] Empty state ("No suggestions yet")
**Status**: Complete

### Task 16: Basic Settings Page
- [x] API key inputs (Claude, Gemini) with show/hide toggle
- [x] LLM provider radio buttons (Claude / Gemini)
- [x] Custom sensitive terms textarea (comma-separated or newline-separated)
- [x] Save button with success feedback
- [x] Load current settings on page mount
**Status**: Complete

### Task 17: Error Handling & States
- [x] API error display (connection failed, LLM error, etc.)
- [x] Loading spinner during LLM calls
- [x] Empty states for each page
- [x] Toast/notification system for actions (copied, saved, error)
- [x] Backend health check on app load
**Status**: Complete

---

## Integration & Polish (Tasks 18-20)

### Task 18: End-to-End Integration Test
- [x] Full flow: paste text → anonymize → LLM → reidentify → display → copy
- [x] Test with 3+ real-world meeting notes samples (meeting notes, status update, transcript)
- [x] Verify PII anonymization (no real names in LLM requests)
- [x] Verify copy-to-clipboard works (frontend wired up)
- [x] Verify apply writes to ~/VPMA/artifacts/ (new /api/artifacts/apply endpoint)
- [x] Test Claude ⟷ Gemini toggle
- [x] 22 integration tests covering: full pipeline, PII round-trip, apply, provider toggle, error handling
- [x] Bug fix: phone regex missed opening parenthesis in (555) 123-4567
- [x] Bug fix: Apply button was not wired up — added convenience endpoint + frontend integration
**Status**: Complete

### Task 19: Prompt Quality Tuning
- [x] Refine system prompts based on analysis (section names, format rules, 3rd example)
- [x] Wire input_type classification into main LLM prompt (was classified but not used)
- [x] Create 7 diverse test samples with expected outputs (backend/tests/test_samples.py)
- [x] Add case-insensitive artifact type matching in apply endpoint
- [x] Code review: verified integration pipeline, no critical bugs found
- [x] First live test: 86K transcript → 55 suggestions → artifacts populated
- [x] Bug fix: Gemini 2.5 Flash thinking tokens consumed max_output_tokens → increased to 16384, capped thinking_budget at 2048
- [x] Bug fix: classify_input returned None with low max_tokens → increased to 256, added None guard
- [x] Bug fix: Apply endpoint had no dedup guard → added duplicate detection
- [x] Bug fix: Apply endpoint appended to end-of-file → now inserts into correct ## section
- [x] Artifacts reset for clean re-testing
- [x] Bug fix: spaCy NER false positives — added confidence threshold (0.75), min entity length (2), and stoplist of ~40 common misclassified words
- [x] PII vault cleared (136 stale false-positive entries removed)
- [x] Frontend: Suggestions now grouped by artifact type (RAID Log / Status Report / Meeting Notes)
- [x] Test isolation fix: conftest now patches ARTIFACTS_DIR to temp directory
- [x] Prompt rewrite: self-contained suggestions (replaced "concise" with standalone test, anti-vagueness rules, Bad vs Good examples, enriched all examples, reasoning → project impact)
- [x] Prompt fix: reasoning anti-pattern — added explicit anti-pattern for quality self-description ("specific next steps with named individuals"), Bad/Good reasoning examples, fixed 4 weak example reasoning values
- [x] UX: Document draft view — Meeting Notes and Status Report now render as assembled document drafts with "Copy All" / "Apply All"; RAID Log keeps individual cards (D11)
- [x] Intent mode toggle: Extract & Route + Analyze & Advise (D12)
  - Backend: `AnalysisItem` model, `ANALYZE_ADVISE_SYSTEM_PROMPT`, `_parse_analysis()`, mode branch in pipeline
  - Frontend: Mode toggle in TextInput, new AnalysisCard component, conditional rendering in ArtifactSync
  - Tests: 13 new backend tests (201 total), 10 new/updated frontend tests (76 total)
- [x] Bug fix: Mode-toggle crash — stale state not cleared on mode switch. Added `handleModeChange` handler + mode guards on render conditions (77 frontend tests)
- [x] Evaluate suggestion relevance with 3+ diverse samples (user testing)
- [x] Evaluate proposed text quality (user assessment)
**Status**: Complete — Phase 0 Go/No-Go passed (2026-02-25)

### Task 20: Styling & Polish
- [x] Consistent Tailwind styling across all components
- [x] Responsive layout (works on laptop screen)
- [x] Loading states feel smooth
- [x] Error messages are helpful
- [x] Overall UX feels clean (Google-minimalist philosophy)
- [x] Subtle gray-50 background with white cards for depth
- [x] Footer with version number
- [x] Meta bar: input type badge + green shield icon for PII count
- [x] Settings form wrapped in white card
- [x] Fix: replace() → replaceAll() for input type display
**Status**: Complete

---

## Go/No-Go Criteria (End of Phase 0)

- [x] Core flow works end-to-end without errors
- [x] Privacy Proxy: No PII leaks in manual audit
- [x] Artifact suggestions are relevant and useful (personal assessment)
- [x] Copy-to-clipboard works reliably
- [x] "This saves me time vs. doing it manually" (personal validation)

**Result**: GO — Phase 0 signed off 2026-02-25

---

## Phase 1A: Context Foundation

**Status**: Task breakdown complete, ready for implementation
**Plan file**: `.claude/plans/stateful-sparking-biscuit.md` (full implementation details)
**Design decisions**: Q18 (one LLM call per file, draft for review), Q19 (fixed template, section-based DB), Q20 (formalized in Task 30)

Phase 1 reframed into 1A (Context Foundation) and 1B (Feature Expansion). Phase 1A is the prerequisite.

### Progress

| Group | Tasks | Done | Status |
|-------|-------|------|--------|
| Infrastructure | 21-22 | 0/2 | Not started |
| Core LPD Operations | 23-25 | 0/3 | Not started |
| Advanced Features | 26-28 | 0/3 | Not started |
| Frontend | 29 | 0/1 | Not started |
| Integration | 30 | 0/1 | Not started |

### Dependency Graph
```
Task 21 → Task 22 → Task 23 → Task 24 → Task 25
                       ↓                    ↓
                     Task 26    Task 27    Task 28
                       ↓          ↓          ↓
                            Task 29
                              ↓
                           Task 30
```

---

### GROUP 1: INFRASTRUCTURE

### Task 21: LPD Data Model & Schema
**Complexity**: S | **Sessions**: 1 | **Dependencies**: None

- [ ] Add `lpd_sections` table (section_id, project_id, section_name, content, section_order, updated_at, verified_at)
- [ ] Add `lpd_session_summaries` table (summary_id, project_id, session_id, summary_text, entities_extracted, created_at)
- [ ] Add Pydantic models: LPDSection, LPDSectionCreate, LPDSessionSummary, LPDSessionSummaryCreate
- [ ] Add LPD template file: `backend/app/prompts/templates/lpd.md`
- [ ] Define LPD_SECTIONS constant (7 fixed sections with display order)
- [ ] Tests: table creation, model validation, template loading (~10 tests)

**Files**: `database.py`, `schemas.py`, `templates/lpd.md`
**Done when**: Tables created by `init_db()`, models validate, template loads, tests pass.

### Task 22: LPD CRUD Operations
**Complexity**: S | **Sessions**: 1 | **Dependencies**: Task 21

- [ ] `create_lpd_section()`, `get_lpd_sections()`, `get_lpd_section()`
- [ ] `update_lpd_section_content()`, `verify_lpd_section()`, `lpd_exists()`
- [ ] `create_lpd_session_summary()`, `get_recent_session_summaries()`, `get_session_summary_count()`
- [ ] Tests: all CRUD operations, edge cases (~15 tests)

**Files**: `crud.py`
**Done when**: All CRUD functions work, edge cases covered, tests pass.

---

### GROUP 2: CORE LPD OPERATIONS

### Task 23: LPD Manager Service
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: Tasks 21, 22

New file: `backend/app/services/lpd_manager.py`

- [ ] `initialize_lpd(project_id)` — create all 7 sections from template (idempotent)
- [ ] `get_full_lpd(project_id)` → dict of section_name → content
- [ ] `render_lpd_markdown(project_id)` → full Markdown document
- [ ] `update_section(project_id, section_name, content)` — replace section content
- [ ] `append_to_section(project_id, section_name, text)` — add to existing content
- [ ] `log_session_summary(project_id, session_id, summary, entities)` — record + rebuild Recent Context
- [ ] `get_context_for_injection(project_id, max_tokens=4000)` — assemble context for LLM
- [ ] `get_section_staleness(project_id)` — staleness info per section
- [ ] Markdown file sync (write-through cache to `data/artifacts/{project_id}_lpd.md`)
- [ ] Tests: initialize, get, render, update, append, session summary, context assembly, staleness (~20 tests)

**Design note**: LPD is NOT a new ArtifactType. Separate manager and data model.
**Done when**: All functions work, token budget enforced, Markdown rendering valid, tests pass.

### Task 24: Context Injection Engine
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: Task 23

- [ ] Add context injection step to `run_artifact_sync()` pipeline
- [ ] Fetch LPD context via `get_context_for_injection()`, anonymize through privacy proxy
- [ ] Prepend anonymized LPD context to user prompt as `## Project Context`
- [ ] Update system prompts: instruct LLM to use project context, avoid duplicates, flag contradictions
- [ ] Backward compatible: no behavior change when LPD doesn't exist
- [ ] Tests: with/without LPD, token budget, privacy proxy on LPD context (~12 tests)

**Files**: `artifact_sync.py`, `prompts/artifact_sync.py`
**Done when**: LLM calls receive project context, privacy proxy applied, backward compatible, tests pass.

### Task 25: Return Path
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: Tasks 23, 24

- [ ] Modify `apply_suggestion_by_type()`: after artifact write, call `update_lpd_from_suggestion()`
- [ ] Section mapping: RAID/Risks→"risks", Decisions→"decisions", Action Items→"open_questions", Accomplishments→"overview", Blockers→"risks"
- [ ] Add session summary generation to `run_artifact_sync()` (template-based, no extra LLM call)
- [ ] Recent Context pruning when section exceeds ~1500 tokens
- [ ] No behavior change when LPD doesn't exist
- [ ] Tests: apply triggers LPD update, section mapping, session summaries, pruning (~15 tests)

**Files**: `routes.py`, `artifact_sync.py`, `lpd_manager.py`
**Done when**: Apply updates artifact AND LPD, session summaries accumulate, tests pass.

---

### GROUP 3: ADVANCED FEATURES

### Task 26: In-Flight Project Intake
**Complexity**: L | **Sessions**: 2-3 | **Dependencies**: Task 23

New files: `backend/app/services/intake.py`, `backend/app/prompts/lpd_prompts.py`

- [ ] `process_intake_file(content, filename, project_id, client)` — one LLM call per file
- [ ] `generate_intake_draft(files, project_id)` → draft with proposed additions + conflicts
- [ ] `apply_intake_draft(project_id, draft, approved_sections)` — commit to LPD
- [ ] `INTAKE_EXTRACTION_PROMPT` — extract stakeholders, risks, decisions, actions, questions, timeline
- [ ] API endpoints: `POST /lpd/{project_id}/intake/preview`, `POST /lpd/{project_id}/intake/apply`
- [ ] Pydantic request/response models for intake
- [ ] Privacy proxy applied to all content before LLM
- [ ] Tests: single file, multi-file, conflict detection, draft apply, privacy (~20 tests)

**Done when**: Upload/paste files → draft preview with conflicts → apply to LPD, tests pass.

### Task 27: Log Session Bridge
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: Task 25

- [ ] Add `mode="log_session"` to artifact sync pipeline
- [ ] `LOG_SESSION_SYSTEM_PROMPT` in `lpd_prompts.py` — extract decisions, risks, actions, status changes
- [ ] `_parse_log_session()` parser — returns session_summary + lpd_updates + artifact_suggestions
- [ ] LPD updates applied directly; artifact suggestions shown for review
- [ ] Update ArtifactSyncResponse with `lpd_updates` and `session_summary` fields
- [ ] Tests: parsing, LPD updates, privacy proxy, backward compatibility (~15 tests)

**Files**: `artifact_sync.py`, `lpd_prompts.py`, `schemas.py`
**Done when**: Paste session conclusions → LPD updated + artifact suggestions displayed, tests pass.

### Task 28: Prompt Refinement
**Complexity**: S | **Sessions**: 1 | **Dependencies**: Tasks 24, 26, 27

- [ ] Create test samples for context injection, intake, and log session prompts
- [ ] Refine prompts based on testing with realistic content
- [ ] Add dedup instructions (don't re-suggest existing items when LPD context present)
- [ ] Document prompt design decisions
- [ ] Tests: ~5 regression test cases

**Done when**: All prompt types produce useful results with real-world content.

---

### GROUP 4: FRONTEND

### Task 29: Frontend Changes
**Complexity**: L | **Sessions**: 2-3 | **Dependencies**: Tasks 23, 25, 26, 27

- [ ] ProjectContext provider — replace hardcoded 'default' with `useProject().projectId`
- [ ] Project Doc page (`pages/ProjectDoc.jsx`) — LPD viewer, staleness indicators, inline editing, Copy All
- [ ] Intake page (`pages/Intake.jsx`) — paste/upload files, draft preview with conflicts, apply
- [ ] Log Session mode — third toggle in TextInput, display summary + LPD updates + suggestions
- [ ] Navigation — add "Project Doc" tab; Intake accessible from Project Doc page
- [ ] API client — `getLPDSections()`, `updateLPDSection()`, `getLPDStaleness()`, `intakePreview()`, `intakeApply()`
- [ ] LPD API endpoints — `GET/PUT /lpd/{project_id}/sections`, `POST /lpd/{project_id}/initialize`, `GET /lpd/{project_id}/staleness`
- [ ] Tests: ~35 new tests (frontend + backend route tests)

**New files**: `ProjectContext.js`, `ProjectDoc.jsx`, `Intake.jsx` + tests
**Modified**: `App.jsx`, `api.js`, `TextInput.jsx`, `ArtifactSync.jsx`, `routes.py`
**Done when**: All pages functional, existing tests pass, new tests pass.

---

### GROUP 5: INTEGRATION

### Task 30: E2E Integration & Cutover Validation
**Complexity**: L | **Sessions**: 2-3 | **Dependencies**: All

- [ ] E2E with real LLM: create project → init LPD → 3+ sessions → verify context accumulates
- [ ] Intake testing with sample PM files
- [ ] Regression: all Phase 0 tests still pass
- [ ] Performance: artifact sync with context injection < 60s
- [ ] Bug fixing (estimate 1-2 sessions)
- [ ] Version bump to 0.2.0

**Cutover criteria (Q20)**:
- [ ] LPD accumulates context across sessions
- [ ] Intake imports files successfully
- [ ] Context injection works (LLM references project context)
- [ ] Log Session bridge works
- [ ] One full week of daily PM work through VPMA + Claude Code hybrid
- [ ] No information loss vs. PM Sandbox workflow

**Done when**: All criteria met, version 0.2.0, docs updated.

---

### Phase 1A Summary

| Metric | Target |
|--------|--------|
| Tasks | 10 (Tasks 21-30) |
| Sessions | 13-20 |
| New tests | ~162 |
| Total tests | ~393 (231 existing + 162 new) |
| New files | 12 (6 backend, 6 frontend) |
| Modified files | 12 (8 backend, 4 frontend) |
| New API endpoints | 8 |
| New DB tables | 2 |
