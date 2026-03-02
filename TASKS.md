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

**Status**: In progress — Tasks 21-29 complete (frontend done, integration remaining)
**Design decisions**: Q18 (one LLM call per file, draft for review), Q19 (fixed template, section-based DB), Q20 (formalized in Task 30)

Phase 1 reframed into 1A (Context Foundation) and 1B (Feature Expansion). Phase 1A is the prerequisite.

### Progress

| Group | Tasks | Done | Status |
|-------|-------|------|--------|
| Infrastructure | 21-22 | 2/2 | Complete |
| Core LPD Operations | 23-25 | 3/3 | Complete |
| Advanced Features | 26-28 | 3/3 | Complete |
| Frontend | 29 | 1/1 | Complete |
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

- [x] Add `lpd_sections` table (section_id, project_id, section_name, content, section_order, updated_at, verified_at)
- [x] Add `lpd_session_summaries` table (summary_id, project_id, session_id, summary_text, entities_extracted, created_at)
- [x] Add Pydantic models: LPDSection, LPDSectionCreate, LPDSessionSummary, LPDSessionSummaryCreate
- [x] Add LPD template file: `backend/app/prompts/templates/lpd.md`
- [x] Define LPD_SECTIONS constant (7 fixed sections with display order)
- [x] Tests: table creation, model validation, template loading (16 tests)
**Status**: Complete

### Task 22: LPD CRUD Operations
**Complexity**: S | **Sessions**: 1 | **Dependencies**: Task 21

- [x] `create_lpd_section()`, `get_lpd_sections()`, `get_lpd_section()`
- [x] `update_lpd_section_content()`, `verify_lpd_section()`, `lpd_exists()`
- [x] `create_lpd_session_summary()`, `get_recent_session_summaries()`, `get_session_summary_count()`
- [x] Tests: all CRUD operations, edge cases (22 tests)
- [x] Bug fix: `rowid DESC` tiebreaker on session summaries ordering (same-second inserts)
**Status**: Complete

---

### GROUP 2: CORE LPD OPERATIONS

### Task 23: LPD Manager Service
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: Tasks 21, 22

New file: `backend/app/services/lpd_manager.py`

- [x] `initialize_lpd(project_id)` — create all 7 sections from template (idempotent)
- [x] `get_full_lpd(project_id)` → dict of section_name → content
- [x] `render_lpd_markdown(project_id)` → full Markdown document
- [x] `update_section(project_id, section_name, content)` — replace section content
- [x] `append_to_section(project_id, section_name, text)` — add to existing content
- [x] `log_session_summary(project_id, session_id, summary, entities)` — record + rebuild Recent Context
- [x] `get_context_for_injection(project_id, max_tokens=4000)` — assemble context for LLM
- [x] `get_section_staleness(project_id)` — staleness info per section
- [x] Markdown file sync (write-through cache to `data/artifacts/{project_id}_lpd.md`)
- [x] Tests: initialize, get, render, update, append, session summary, context assembly, staleness (39 tests)
**Status**: Complete

### Task 24: Context Injection Engine
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: Task 23

- [x] Add context injection step to `run_artifact_sync()` pipeline
- [x] Fetch LPD context via `get_context_for_injection()`, anonymize through privacy proxy
- [x] Prepend anonymized LPD context to user prompt as `## Project Context`
- [x] Update system prompts: instruct LLM to use project context, avoid duplicates, flag contradictions
- [x] Backward compatible: no behavior change when LPD doesn't exist
- [x] Tests: with/without LPD, token budget, privacy proxy on LPD context (13 tests)
- [x] Bug fix: structural heading `## Project Context` was being mangled by spaCy NER — separated heading from anonymization boundary (D22)

**Files**: `artifact_sync.py`, `prompts/artifact_sync.py`
**Done when**: LLM calls receive project context, privacy proxy applied, backward compatible, tests pass.
**Status**: Complete

### Task 25: Return Path
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: Tasks 23, 24

- [x] Modify `apply_suggestion_by_type()`: after artifact write, call `update_lpd_from_suggestion()`
- [x] Section mapping: RAID/Risks→"Risks", Decisions→"Decisions", Action Items→"Open Questions", Accomplishments→"Overview", Blockers→"Risks"
- [x] Add session summary generation to `run_artifact_sync()` (template-based, no extra LLM call)
- [x] Recent Context pruning when section exceeds ~1500 tokens (already working from Task 23)
- [x] No behavior change when LPD doesn't exist
- [x] Tests: apply triggers LPD update, section mapping, session summaries, dedup guard, API integration (21 tests)
- [x] Apply endpoint response now includes `lpd_updated` boolean (D23)

**Files**: `routes.py`, `artifact_sync.py`, `lpd_manager.py`
**Done when**: Apply updates artifact AND LPD, session summaries accumulate, tests pass.
**Status**: Complete

---

### GROUP 3: ADVANCED FEATURES

### Task 26: In-Flight Project Intake
**Complexity**: L | **Sessions**: 2-3 | **Dependencies**: Task 23

New files: `backend/app/services/intake.py`, `backend/app/prompts/lpd_prompts.py`

- [x] `process_intake_file(content, filename, custom_terms, client)` — one LLM call per file
- [x] `generate_intake_draft(files, project_id)` → draft with proposed additions + conflicts
- [x] `apply_intake_draft(project_id, proposed_sections, approved_sections)` — commit to LPD
- [x] `INTAKE_EXTRACTION_PROMPT` — extract overview, stakeholders, risks, decisions, questions, timeline
- [x] API endpoints: `POST /lpd/{project_id}/intake/preview`, `POST /lpd/{project_id}/intake/apply`
- [x] Pydantic models: IntakeFile, IntakeExtraction, IntakeConflict, IntakeDraft, IntakePreviewRequest, IntakeApplyRequest, IntakeApplyResponse
- [x] `INTAKE_FIELD_TO_LPD_SECTION` constant mapping extraction fields to LPD sections
- [x] Privacy proxy applied to all content before LLM, PII reidentified in extractions
- [x] Conflict detection: flags when proposed content targets a section that already has content
- [x] Tests: parsing, single file, multi-file, conflict detection, draft apply, privacy, API endpoints, prompt (25 tests)

**Done when**: Upload/paste files → draft preview with conflicts → apply to LPD, tests pass.
**Status**: Complete

### Task 27: Log Session Bridge
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: Task 25

- [x] Add `mode="log_session"` to artifact sync pipeline (third mode alongside extract/analyze)
- [x] `LOG_SESSION_SYSTEM_PROMPT` in `lpd_prompts.py` — extract decisions, risks, actions, stakeholder changes, timeline updates
- [x] `_parse_log_session()` parser — returns session_summary + lpd_updates + artifact_suggestions
- [x] LPD updates applied directly via `append_to_section()`; artifact suggestions returned for review
- [x] `LPDUpdate` model added to schemas.py; `ArtifactSyncResponse` updated with `lpd_updates` and `session_summary` fields
- [x] LLM-generated session summary used for Recent Context (falls back to template if absent)
- [x] No behavior change when LPD doesn't exist (updates returned but not applied)
- [x] Tests: parsing, pipeline, LPD updates, privacy, backward compatibility, prompt verification (16 tests)
- [x] Bug fix: `log_session_summary` local variable shadowed imported function — renamed to `parsed_session_summary`

**Files**: `artifact_sync.py`, `lpd_prompts.py`, `schemas.py`
**Done when**: Paste session conclusions → LPD updated + artifact suggestions displayed, tests pass.
**Status**: Complete

### Task 28: Prompt Refinement
**Complexity**: S | **Sessions**: 1 | **Dependencies**: Tasks 24, 26, 27

- [x] Regression tests for all 5 prompts: extract, analyze, log_session, intake, input classification (25 tests)
- [x] Added dedup/context instructions to LOG_SESSION_SYSTEM_PROMPT (## Project Context section with avoid duplicates, enrichment, contradiction handling)
- [x] Extract prompt already had dedup instructions (from Phase 0); confirmed still present
- [x] Analyze prompt already had context awareness; confirmed still present
- [x] Intake prompt correctly handles dedup at service layer (conflict detection), not in prompt — by design
- [x] Prompt design decisions documented in D25

**Done when**: All prompt types produce useful results with real-world content.
**Status**: Complete

---

### GROUP 4: FRONTEND

### Task 29: Frontend Changes
**Complexity**: L | **Sessions**: 2-3 | **Dependencies**: Tasks 23, 25, 26, 27

- [x] ProjectContext provider (`ProjectContext.jsx`) — wraps app, provides `useProject().projectId`
- [x] Project Doc page (`pages/ProjectDoc.jsx`) — LPD viewer, staleness indicators, inline editing, verify, Copy All, initialize
- [x] Intake page (`pages/Intake.jsx`) — paste files, add/remove files, draft preview with conflicts, checkbox approval, apply to LPD
- [x] Log Session mode — third toggle ("Log") in TextInput, new `LogSessionCard` component displaying summary + LPD updates + artifact suggestions
- [x] Navigation — "Project Doc" tab added; Intake accessible from Project Doc page and as `/intake` route
- [x] API client — `initializeLPD()`, `getLPDSections()`, `updateLPDSection()`, `getLPDStaleness()`, `getLPDMarkdown()`, `verifyLPDSection()`, `intakePreview()`, `intakeApply()`
- [x] LPD API endpoints — `GET /lpd/{id}/sections`, `PUT /lpd/{id}/sections/{name}`, `POST /lpd/{id}/initialize`, `GET /lpd/{id}/staleness`, `GET /lpd/{id}/markdown`, `POST /lpd/{id}/sections/{name}/verify`
- [x] Tests: 51 new tests (38 frontend + 13 backend route tests)

**New files**: `ProjectContext.jsx`, `LogSessionCard.jsx`, `ProjectDoc.jsx`, `Intake.jsx`, `test_lpd_routes.py` + 4 test files
**Modified**: `App.jsx`, `api.js`, `TextInput.jsx`, `ArtifactSync.jsx`, `routes.py`
**Done when**: All pages functional, existing tests pass, new tests pass.
**Status**: Complete

---

### GROUP 5: INTEGRATION

### Task 30: E2E Integration & Cutover Validation
**Complexity**: L | **Sessions**: 2-3 | **Dependencies**: All

- [ ] E2E with real LLM: create project → init LPD → 3+ sessions → verify context accumulates
- [ ] Intake testing with sample PM files
- [ ] Regression: all Phase 0 tests still pass
- [ ] Performance: artifact sync with context injection < 60s
- [ ] Bug fixing (estimate 1-2 sessions)
- [ ] **Bug: Privacy proxy missed real names in artifact data** — `default_status-report.md` had 10+ real names that passed through spaCy NER undetected (common first names like Jenny, Jessica, Brian, Alex; non-Western names like Jaskaran Singh, Savitha Kandasamy, Nikhila). Manually fixed in data. Root cause: spaCy `en_core_web_sm` has weak recall on names outside training distribution + single first names without surname context. Investigate: confidence threshold tuning, supplemental name list, or fallback heuristics for short capitalized words in entity-dense text.
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

---

## Backlog-Sourced Additions (from Review 1, 2026-02-27)

Items promoted or slotted from VPMA_BACKLOG.md based on real PM workflow validation. See D36 (dual-tool architecture) and D37 (backlog consumption protocol) for strategic context. Full dispositions in `~/Projects/PM Sandbox/VPMA_BACKLOG.md` Review Log.

### Phase 1B Additions (Promoted)

| Item | Source | Description |
|------|--------|-------------|
| V15 | Sessions 1-4 | **Structured uncertainty tracking** — add "Questions" section to LPD with per-section question queue and resolution tracking. Natural LPD extension. |
| V25 | Brain dump | **Narrative-first output with commit/copy** — shift artifact sync output default to narrative with pop-up commit/copy action. UX improvement, minimal backend change. |
| D38a | E2E testing | **Rename "Project Hub" → "Project Knowledge Base"** — label doesn't match function. XS effort. |
| D38b | E2E testing | **Result persistence across tab navigation** — Extract/Analyze/Log Session results vanish on tab switch. localStorage with TTL as minimum fix. (D38) |
| D38c | E2E testing | **Surface `lpd_updated` feedback in UI** — Apply button returns `lpd_updated: true/false` but UI doesn't show it. Add toast or badge. |
| D40 | E2E testing | **Semantic dedup on return path (Apply)** — return path only does exact substring match; same risk in different formats (narrative vs table) passes through. Extend content gate to `update_lpd_from_suggestion()`. Reuse existing `content_gate.py` module. |

### Phase 2 Additions (Promoted/Slotted)

| Item | Source | Description |
|------|--------|-------------|
| V29 | PA Session 2+4 | **Import AI history** — generalize Gemini export pipeline into product feature. Users import conversation history from any AI assistant. Competitive differentiator. Intake pipeline (Phase 1A) is the foundation. |
| V5 | Session 3 | **Personal bottleneck detection** — track PM's action item aging and convergence points. Simpler than full HR capacity; moved earlier from Phase 4. |
| V17 | Sessions 1-4 | **Data provenance / source tracking** — every fact traces to input, timestamp, session. Add to LPD/artifact data model. Easier now than retrofit. |
| V7 | Session 3 | **Portfolio roll-up views** — extends multi-project with risk heat maps and cross-project dashboards. |
| V10 | Sessions 3+21 | **GitHub Projects sync** — validated twice, manual workaround exists. Automate the weekly cross-reference. |
| D39 | E2E testing | **Cross-section LPD reconciliation** — content gate (D33) compares within-section only. Extend to detect cross-section impacts (e.g., Decision resolves a Risk, Action Item closes an Open Question). Requires full-LPD context per comparison. |

### Phase 3 Additions (Promoted/Slotted)

| Item | Source | Description |
|------|--------|-------------|
| V28/V33 | PA + PM Sandbox | **Brain dump mode** — freeform capture → triage → route. MVP of the chat panel concept (D36). "Personal inbox zero." |
| V37 | Session 25 | **Cross-document synthesis** — "build alignment package for Topic X." Requires chat panel + good LPD context. |
| V31 | 3 projects | **Decision journal with pattern learning** — extend DECISIONS.md pattern into VPMA with temporal detection ("you delay X-type decisions by 2 weeks"). |
| V12 | Session 3 | **Meeting prep generation** — auto-generate agenda, talking points, data references from KB + meeting cadence. |

### Dual-Tool Architecture Placeholder (D36)

**Phase 2**: Design conversational API endpoint (session-aware, multi-turn, LPD context injection). API shape planned even if UI comes later.
**Phase 3**: Embedded chat panel in React app — freeform analysis mode alongside structured workflows. Brain dump (V28) is the entry point.
**Future**: Standalone CLI extraction for power users, if chat mode proves valuable.

---

## Transcript Integration (Phases 1B–3, tentative)

Strategic decision: D31. Full analysis: `docs/MEETING_INTELLIGENCE_ANALYSIS.md`.

- **Phase 1B**: File watcher (`watchdog`) for `.vtt/.txt/.srt` files + VTT parser + transcript-specific UX. ~1-2 days. $0.
- **Phase 2-3**: Zoom Server-to-Server OAuth for personal cloud transcript auto-fetch. Cascade routing (folder → filename → LLM classification → manual). ~3-5 days. $0.
- **Phase 3-4**: Evaluate Zoom Marketplace listing (if distributing) or local Whisper STT (if privacy angle resonating). Decision based on user demand signals.

---

## Phase 2 Checkpoint: LLM Model Evaluation

**Trigger**: Phase 2 kickoff (after Phase 1A/1B complete)

Before implementing Ollama adapter or choosing specific local models, complete this evaluation using real Phase 1A data:

1. **Audit LLM call patterns** — categorize all LLM calls by type (extract, analyze, log_session, intake, classification) and measure frequency, prompt size, and quality requirements
2. **Benchmark real prompts** — run actual VPMA prompts (with context injection) against candidate local models (Llama 3.x, Mistral, etc.) on target hardware and score output quality
3. **Define routing rules** — which task types can use local LLM without quality loss? Which require API models?
4. **Decide Privacy Proxy behavior** — skip anonymization for local-only calls, or apply uniformly for consistency?
5. **Evaluate provider-aware token budgets** — do local models need compressed context injection (D21)?

**Design decisions to log**: Task-type routing strategy, privacy proxy bypass policy, token budget per provider. See D32.

---

## Persona Expansion Roadmap

Active personas are defined in `docs/personas/`. Two are active now. Others should be considered at specific phase boundaries — not before.

### Active Now
| Persona | File | Trigger |
|---------|------|---------|
| Skeptical PM | `docs/personas/skeptical_pm.md` | Phase boundaries (automatic) + manual |
| First Outside User | `docs/personas/first_outside_user.md` | Market readiness discussions + manual |

### Consider Adding Later

| Persona | When to Consider | Why Not Now | What They'd Evaluate |
|---------|-----------------|-------------|---------------------|
| **Solution Architect** | Phase 2 (multi-project, chat interface) | Current architecture is simple enough that code review catches issues. No distributed systems, no auth, no multi-user. | Scalability decisions, database migration strategy, API design for multi-tenant, auth architecture |
| **Product Owner** | When evaluating market fit (post-daily-use validation) | You ARE the product owner. Adding this now would be arguing with yourself through a proxy. | Feature prioritization for external users, pricing model alignment, competitive positioning, backlog grooming |
| **First Enterprise Buyer** | Phase 3+ (if pursuing B2B) | No product to buy. Enterprise concerns (SSO, audit trails, compliance, on-prem) are irrelevant until you're considering B2B. | Security posture, deployment model, admin controls, compliance requirements, procurement friction |

### Personas Explicitly Rejected
| Persona | Why |
|---------|-----|
| Sales Team | No product to sell. Would pull toward premature positioning and feature bloat. |
| Marketing Team | Optimizes for messaging before there's a product worth messaging about. |
| End-User Stakeholders | Stakeholders consume PM outputs, not PM tools. Test output quality through the Skeptical PM instead. |
| Project Sponsors | You're the sponsor. You already know your constraints. |
