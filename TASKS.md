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
| Phase 1A: LPD Foundation | 21-30 | 10/10 | Complete |
| Phase 1B: Polish + Transcripts | 31-37 | 7/7 | Complete |
| Phase 2A: Workflow Completion | 38-44 | 7/7 | Complete |
| Phase 2B: Deep Analysis | 45-53 | 9/9 | Complete |
| **Phase 3A: UX + Infrastructure** | **54-58** | **4/5** | **In Progress** |
| Phase 3B: Chat + Brain Dump | 59-61 | 0/3 | Not Started |
| Phase 3C: Skeptical Reviewer | 62-63 | 0/2 | Not Started |

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

**Status**: Complete — Tasks 21-30 done, v0.2.0 shipped (2026-03-01)
**Design decisions**: Q18 (one LLM call per file, draft for review), Q19 (fixed template, section-based DB), Q20 (formalized in Task 30)

Phase 1 reframed into 1A (Context Foundation) and 1B (Feature Expansion). Phase 1A is the prerequisite.

### Progress

| Group | Tasks | Done | Status |
|-------|-------|------|--------|
| Infrastructure | 21-22 | 2/2 | Complete |
| Core LPD Operations | 23-25 | 3/3 | Complete |
| Advanced Features | 26-28 | 3/3 | Complete |
| Frontend | 29 | 1/1 | Complete |
| Integration | 30 | 1/1 | Complete |

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

- [x] E2E with real LLM: create project → init LPD → 3+ sessions → verify context accumulates
- [x] Intake testing with sample PM files
- [x] Regression: all Phase 0 tests still pass
- [x] Performance: artifact sync with context injection < 60s
- [x] Bug fixing (estimate 1-2 sessions)
- [x] **Bug: Privacy proxy missed real names in artifact data** — `default_status-report.md` had 10+ real names that passed through spaCy NER undetected (common first names like Jenny, Jessica, Brian, Alex; non-Western names like Jaskaran Singh, Savitha Kandasamy, Nikhila). Manually fixed in data. Root cause: spaCy `en_core_web_sm` has weak recall on names outside training distribution + single first names without surname context. Investigate: confidence threshold tuning, supplemental name list, or fallback heuristics for short capitalized words in entity-dense text.
- [x] Version bump to 0.2.0
- [x] Content quality gate (D33): semantic dedup + contradiction detection for Log Session LPD updates
- [x] Golden fixture test suite: 10 input fixtures, 10 golden responses, PII safety checks
- [x] Pre-commit hooks: ruff format, bandit, smoke tests, doc freshness check
- [x] QA plan and architecture tests
- [x] Skeptical PM review at phase boundary
- [x] Full test suite pass: 651 backend + 125 frontend = 776 total tests
- [x] Docs updated with final counts

**Cutover criteria (Q20)**:
- [x] LPD accumulates context across sessions
- [x] Intake imports files successfully
- [x] Context injection works (LLM references project context)
- [x] Log Session bridge works
- [x] Daily PM work through VPMA + Claude Code hybrid (decision: dropped one-week gate, start Phase 1B in parallel with daily use)
- [x] No information loss vs. PM Sandbox workflow

**Done when**: All criteria met, version 0.2.0, docs updated.
**Status**: Complete

---

### Phase 1A Summary

| Metric | Target | Actual |
|--------|--------|--------|
| Tasks | 10 (Tasks 21-30) | 10/10 complete |
| Sessions | 13-20 | ~15 |
| New tests | ~162 | 288 (163 backend + 125 existing frontend) |
| Total tests | ~393 | 776 (651 backend + 125 frontend) |
| New files | 12 | 55 (services, tests, fixtures, prompts, pages, components, infra) |
| Modified files | 12 | 27 |
| New API endpoints | 8 | 8 (14 total) |
| New DB tables | 2 | 2 (8 total) |

---

## Phase 1B: Fit-and-Finish + Transcript Integration

**Status**: Complete — v0.3.0 shipped (2026-03-03)
**Scope**: Lean phase focused on validated refinements + transcript watcher. Skeptical PM review endorsed this scope, deferring V25 (narrative-first) and V15 (question tracking) until beta feedback.
**Backlog Review 2**: V40 (concept refinement cascade) → Phase 3. No new promotions.
**Design decisions**: D41 (localStorage persistence), D42 (graceful dedup degradation), D43 (watcher as asyncio task), D44 (parser/watcher separation)

### Progress

| Group | Tasks | Done | Status |
|-------|-------|------|--------|
| UI/UX Polish | 31-33 | 3/3 | Complete |
| Content Quality | 34 | 1/1 | Complete |
| Transcript Integration | 35-36 | 2/2 | Complete |
| Integration | 37 | 1/1 | Complete |

### Dependency Graph
```
Task 31 (XS, rename)                    ─┐
Task 32 (S, lpd_updated toast)           ├─→ Task 37 (M, E2E)
Task 33 (S-M, result persistence)        │
Task 34 (M, semantic dedup on Apply)     │
Task 35 (M, VTT parser + watcher) → 36 ─┘
```

---

### GROUP 1: UI/UX POLISH

### Task 31: Rename "Project Hub" → "Project Knowledge Base"
**Complexity**: XS | **Sessions**: 0.5 | **Dependencies**: None

- [x] All user-visible "Project Hub" text replaced in frontend (App.jsx, ProjectDoc.jsx, ArtifactSync.jsx, Intake.jsx)
- [x] Frontend test assertions updated (ProjectDoc.test.jsx)
- [x] Backend reason strings updated (content_gate.py, artifact_sync.py)
- [x] Backend test assertions updated (test_content_gate.py)
- [x] `grep -ri "project hub"` returns zero results
**Status**: Complete

### Task 32: Surface `lpd_updated` Feedback in Apply Toast
**Complexity**: S | **Sessions**: 0.5 | **Dependencies**: None

- [x] ArtifactSync handleApply captures response, shows differentiated toast when `lpd_updated=true`
- [x] Handle `status: "duplicate"` → `toast.info("Already applied")`
- [x] LogSessionCard handleApplySuggestion shows same differentiated feedback
- [x] handleApplyAll shows aggregated feedback (e.g., "Applied 5 suggestions, 3 knowledge base updates")
- [x] Frontend tests updated (5 new tests)
**Status**: Complete

### Task 33: Result Persistence Across Tab Navigation
**Complexity**: S-M | **Sessions**: 1-2 | **Dependencies**: None

New file: `frontend/src/hooks/usePersistedResults.js`

- [x] Custom hook `usePersistedResults` wrapping localStorage
- [x] Independent storage per mode (`vpma_results_extract`, `vpma_results_analyze`, `vpma_results_log_session`)
- [x] Store results (suggestions, analysis, logSession, meta) as JSON after successful submit
- [x] Restore results on component mount for current mode
- [x] Clear on new submission (not TTL-based) — D41
- [x] Mode switch preserves other modes' storage
- [x] Hook unit tests + integration tests (8 tests)
**Status**: Complete

---

### GROUP 2: CONTENT QUALITY

### Task 34: Semantic Dedup on Return Path (Apply Button)
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: None

- [x] Add optional `client` param to `update_lpd_from_suggestion()` in lpd_manager.py
- [x] If client provided, call `classify_lpd_updates()` with single-item LPDUpdate before append
- [x] `duplicate` → skip, `contradiction` → apply with warning log, `new`/`update` → apply
- [x] Graceful fallback: LLM failure → exact substring match (D42)
- [x] Make `get_llm_client()` and `get_custom_terms()` public in artifact_sync.py
- [x] Wire client creation in routes.py apply endpoint
- [x] Architecture tests still pass
- [x] Tests: semantic dedup, fallback, contradiction logging (13 new tests)
**Status**: Complete

---

### GROUP 3: TRANSCRIPT INTEGRATION

### Task 35: VTT Parser + Transcript File Watcher Service
**Complexity**: M | **Sessions**: 2 | **Dependencies**: None

New files: `backend/app/services/vtt_parser.py`, `backend/app/services/transcript_watcher.py`

- [x] VTT parser: extract speaker-tagged text, strip timestamps/formatting, handle `<v>` tags, NOTE/STYLE blocks
- [x] SRT parser: similar to VTT with different header structure
- [x] Plain text pass-through
- [x] Adjacent duplicate line deduplication
- [x] `TranscriptWatcher` class with start/stop/status (polling-based, no watchdog dependency)
- [x] Watch configurable folder for `.vtt`/`.txt`/`.srt` files
- [x] Processed file manifest (`transcript_manifest.json`) to prevent re-processing
- [x] 2-second debounce for partially-written files
- [x] Background asyncio task in FastAPI process (D43)
- [x] API endpoints: GET status, POST start, POST stop, POST process (manual)
- [x] Settings: `transcript_watch_folder`, `transcript_auto_mode`
- [x] Both modules added to architecture test parametrize lists
- [x] Tests: VTT parsing (10), SRT parsing (6), TXT (4), watcher lifecycle (9), file processing (5), manifest (2), API smoke (4), dispatch (6) — 48 total
**Status**: Complete

### Task 36: Transcript Watcher Frontend UX
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: Task 35

- [x] Settings page: "Transcript Watcher" section with folder path input
- [x] Mode selector (Extract / Log Session)
- [x] Start/Stop toggle with green/gray status indicator
- [x] "Recent Files" list (last 5 processed transcripts)
- [x] API client functions: getStatus, start, stop, processFile
- [x] Frontend tests (9 new tests in Settings.test.jsx)
**Status**: Complete

---

### GROUP 4: INTEGRATION

### Task 37: Phase 1B E2E Integration & Polish
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: All

- [x] E2E validation of all features
- [x] Regression: all Phase 0 + 1A tests pass
- [x] Version bump → 0.3.0
- [x] CLAUDE.md updated (project structure, test counts, endpoint count)
- [x] docs/EXECUTIVE_SUMMARY.md updated
- [x] Architecture tests include transcript_watcher, vtt_parser
- [x] Smoke tests for new critical paths (3 new smoke tests)
- [x] Full test suite pass: 719 backend + 147 frontend = 866 total tests
**Status**: Complete

---

## Phase 2A: Workflow Completion

**Status**: Complete — v0.4.0
**Scope**: Export, Ollama adapter, watcher results view, LPD change summary, conversational API design, drag-drop
**Backlog Review 2**: V40 → Slot Phase 3. No promotions to 2A.
**Skeptical PM Review**: USE IT — simplified diffs to change summary, keep conv. API minimal, drag-drop is stretch
**Design decisions**: D47 (conversational API design)

### Progress

| Group | Tasks | Done | Status |
|-------|-------|------|--------|
| LLM & Infrastructure | 38, 42 | 2/2 | Complete |
| User-Facing Features | 39-41 | 3/3 | Complete |
| Stretch | 43 | 1/1 | Complete |
| Integration | 44 | 1/1 | Complete |

### Dependency Graph
```
Task 38 (Ollama, M)           ─┐
Task 39 (Export, S-M)          ├── Task 44 (E2E, M)
Task 40 (Change summary, S-M)  │
Task 41 (Watcher results, M)   │
Task 42 (Conv. API design, S)  │
Task 43 (Drag-drop, S/stretch)─┘
```

---

### Task 38: Ollama LLM Adapter
**Complexity**: M | **Sessions**: 2-3 | **Dependencies**: None

New file: `backend/app/services/llm_ollama.py`

- [x] `OllamaClient` inheriting from `LLMClient` — httpx async, configurable base_url/model
- [x] Update `create_client()` factory in `llm_client.py`
- [x] Settings DB: `ollama_base_url`, `ollama_model` keys
- [x] Settings API: add to `allowed_keys` in `routes.py`
- [x] Connection test endpoint: `GET /api/settings/ollama-status`
- [x] Frontend Settings: Ollama radio button, model input, base URL, connection indicator + auto-check on load
- [x] `.env.example` updated
- [x] Privacy Proxy stays ON for all providers (D32)
- [x] `get_llm_client()` in artifact_sync.py wired for Ollama provider
- [x] Architecture tests updated (llm_ollama.py in provider list)
- [x] Tests: 14 backend (adapter, factory, status check, env vars) + 7 frontend (Ollama settings UI)

**Files**: `llm_ollama.py` (new), `llm_client.py`, `routes.py`, `artifact_sync.py`, `Settings.jsx`, `api.js`, `.env.example`, `test_llm_client.py`, `Settings.test.jsx`
**Done when**: Select Ollama in Settings → artifact sync runs → results display. Graceful fallback when Ollama not running.
**Status**: Complete

### Task 39: Markdown/Clipboard Export
**Complexity**: S-M | **Sessions**: 1-2 | **Dependencies**: None

- [x] Backend: `GET /api/artifacts/{project_id}/export` → combined artifact markdown
- [x] ProjectDoc: "Download Markdown" button → LPD as .md file download
- [x] ArtifactSync: "Export Results" button → results as .md download + clipboard ("Copy Results" + "Export .md")
- [x] ProjectDoc: "Export Artifacts" button → calls backend endpoint
- [x] Auto-check Ollama status on settings load when Ollama is active provider
- [x] Frontend api: `exportArtifacts()` function
- [x] Results formatted as markdown per mode (extract: grouped by artifact, analyze: items, log_session: summary + updates)
- [x] Tests: 3 backend (export empty, with artifacts, nonexistent project) + 7 frontend Ollama tests

**Files**: `routes.py`, `ArtifactSync.jsx`, `ProjectDoc.jsx`, `api.js`, `test_integration.py`, `Settings.test.jsx`
**Done when**: Can download LPD as .md, download results as .md, copy aggregated results to clipboard.
**Status**: Complete

### Task 40: LPD Change Summary on Apply
**Complexity**: S-M | **Sessions**: 1-2 | **Dependencies**: None

- [x] `update_lpd_from_suggestion()` returns `{updated, section, content_added}` instead of `bool`
- [x] Apply response adds `lpd_change: {section, content_added}` when LPD updated
- [x] Apply toast shows section name (SuggestionCard, LogSessionCard)
- [x] DocumentDraftCard Apply All shows sections in aggregated toast
- [x] Content preview truncated to 120 chars with ellipsis
- [x] Tests: 3 new (change details, truncation, skip returns null) + all existing tests updated for dict return
- [ ] ~~LPDUpdate model adds `existing_snippet` field~~ (deferred — contradiction items rarely hit in practice)
- [ ] ~~Contradiction items show existing content for comparison~~ (deferred — same reason)

**Files**: `lpd_manager.py`, `routes.py`, `SuggestionCard.jsx`, `DocumentDraftCard.jsx`, `LogSessionCard.jsx`, `test_return_path.py`, `test_e2e_phase1a.py`
**Done when**: Apply shows what was added and where. PM understands what changed without navigating to ProjectDoc.
**Status**: Complete

### Task 41: Transcript Watcher Results View (V42)
**Complexity**: M | **Sessions**: 2 | **Dependencies**: None

- [x] Store full `ArtifactSyncResponse` in watcher `recent_files` (cap at 10)
- [x] `GET /api/transcript-watcher/results` → recent files with full data
- [x] Settings: clickable file entries → expandable panel with suggestions/updates
- [x] Apply button per suggestion (reuses `applySuggestionByType`)
- [x] Status badges: processed/failed/processing
- [x] Tests: results storage, API, frontend, apply flow (10 tests)

**Files**: `transcript_watcher.py`, `routes.py`, `Settings.jsx`, `api.js`, `Settings.test.jsx`, `test_transcript_watcher.py`
**Done when**: Watcher processes transcript → PM sees suggestions in Settings → can Apply directly.
**Status**: Complete

### Task 42: Conversational API Design (D36)
**Complexity**: S | **Sessions**: 1 | **Dependencies**: None

Design-only. No endpoint implementation, no UI.

- [x] Design doc: `docs/conversational_api_design.md`
- [x] Pydantic models: `ConversationMessage`, `ConversationSession`, `ChatRequest`, `ChatResponse`
- [x] DB table design: `conversations`, `conversation_messages`
- [x] Document decisions in `DECISIONS.md` (D47)

**Files**: `docs/conversational_api_design.md` (new), `schemas.py`, `DECISIONS.md`
**Done when**: Design doc complete, models defined, DB schema documented.
**Status**: Complete

### Task 43: Transcript File Drag-and-Drop (Stretch)
**Complexity**: S | **Sessions**: 0.5-1 | **Dependencies**: None

- [x] Drop zone component in Settings (accepts .vtt/.srt/.txt) with drag-over visual feedback
- [x] Upload file content to backend via `POST /api/transcript-watcher/upload`
- [x] Backend: validates file type, writes temp file, processes through watcher pipeline, cleans up
- [x] Show results inline (reuses Task 41 suggestion card display with Apply buttons)
- [x] Tests: 3 backend (upload success, empty content, unsupported type) + 4 frontend (render, process, reject, error)

**Files**: `Settings.jsx`, `routes.py`, `api.js`, `Settings.test.jsx`, `test_transcript_watcher.py`
**Done when**: Drag .vtt onto Settings → processes → shows results.
**Status**: Complete

### Task 44: Phase 2A E2E Integration & Polish
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: All

- [x] Regression: all prior tests pass (745 backend + 162 frontend = 907 total)
- [x] Version bump → 0.4.0 (pyproject.toml, main.py, routes.py, package.json)
- [x] CLAUDE.md updated (Phase 2A scope, test counts, project structure, service modules)
- [x] EXECUTIVE_SUMMARY.md updated (version, stats, features, roadmap)
- [x] Architecture tests include llm_ollama (done in Task 38)
- [x] Smoke tests for new critical paths (5 new: export, upload, results, Ollama client, conv. models)
- [x] Full test suite pass + lint clean + doc freshness check
- [x] TASKS.md updated with all task completions
- [ ] ~~E2E validation with real data~~ (requires live LLM — manual test outside automated suite)
- [ ] ~~Ollama live test~~ (requires Ollama installed — manual validation)
- [ ] ~~D32 LLM evaluation checkpoint~~ (requires real workload data — deferred to post-deploy)

**Done when**: All tests pass, v0.4.0, docs current.
**Status**: Complete

---

## Phase 2B: Deep Analysis

**Status**: Complete (v0.5.0, shipped 2026-03-12)
**Scope**: Deep Strategy multi-artifact analysis, AI Risk Prediction, Cross-Section LPD Reconciliation, Folder Browser
**Backlog Review 2**: V5 (bottleneck detection → feeds risk prediction), V14 (cross-artifact dependency → IS Deep Strategy), V40 (concept refinement cascade → cross-section reconciliation). V17 (provenance) deferred.
**Skeptical PM Review (pre-build)**: USE IT — Deep Strategy passes Tuesday afternoon test if quality is good. Risk Prediction + Reconciliation are lighter-weight wins. Folder Browser is friction fix. Caveats: context window limits at scale, priority ordering UX, simulated progress bar, risk prediction nudge.
**Skeptical PM Review (post-ship)**: USE IT — Deep Strategy confirmed as cross-document consistency checker (pre-steering-committee use case). UX polish (dismiss, auto-expiry, clear) prevents "tried it once, annoying" churn. Three actionable items: (1) do UX-3 naming/IA pass before Phase 3 features, (2) add empty-state coaching to Risk Prediction + Reconciliation, (3) move toward proactive nudges over manual buttons. See D54.
**Design decisions**: D48 (markdown + text only for DS input), D49 (synchronous endpoint with long timeout), D50 (Apply: VPMA artifacts → write, uploaded → clipboard), D51 (reconciliation + risk = manual triggers, not auto-run), D52 (DS standalone — no LPD requirement)

### Progress

| Group | Tasks | Done | Status |
|-------|-------|------|--------|
| DS Infrastructure | 45-46 | 2/2 | Complete |
| DS Engine + Frontend | 47-48 | 2/2 | Complete |
| Complementary Features | 49-52 | 4/4 | Complete |
| Integration | 53 | 0/1 | In Progress |

### Dependency Graph
```
Task 45 (S, models)           ──┐
Task 46 (M, prompts)          ──┤
                                 ↓
Task 47 (L, DS engine + API)  ──┤
                                 ↓
Task 48 (L, DS frontend)      ──┤
                                 │
Task 49 (M, risk prediction)  ──┤  (independent track)
                                 ├──→ Task 53 (M, E2E)
Task 50 (M, risk + recon FE)  ──┤
                                 │
Task 51 (M, cross-section)    ──┤  (independent track)
                                 │
Task 52 (S, folder browser)   ──┘  (independent track)
```

---

### GROUP 1: DEEP STRATEGY INFRASTRUCTURE (Tasks 45-46)

### Task 45: Deep Strategy Data Models
**Complexity**: S | **Sessions**: 1 | **Dependencies**: None

- [x] `DeepStrategyArtifact` — name, content, priority (input)
- [x] `DependencyEdge` — source, target, relationship
- [x] `DependencyGraph` — artifacts list, edges, summary (Pass 1 output)
- [x] `Inconsistency` — id, source/target artifacts, description, severity, excerpts (Pass 2 output)
- [x] `ProposedUpdate` — inconsistency_id, artifact_name, section, current_text, proposed_text, change_type, rationale (Pass 3 output)
- [x] `ValidationCheck` — artifact_name, check_description, passed, detail (Pass 4 output)
- [x] `DeepStrategySummary` — artifacts_analyzed, inconsistencies_found, updates_proposed, validation_passed, consistency_score
- [x] `DeepStrategyRequest` / `DeepStrategyResponse` — full request/response models
- [x] `DeepStrategyApplyRequest` / `DeepStrategyApplyResponse` — apply flow models
- [x] `PredictedRisk` — risk prediction output (for Task 49)
- [x] `RiskPredictionResponse` — predictions, project_health, pii_detected, session_id
- [x] `CrossSectionImpact` — source_section, target_section, impact_type, description, excerpts, suggested_action (for Task 51)
- [x] `ReconciliationResponse` — impacts, sections_analyzed, pii_detected, session_id
- [x] Architecture tests pass (no service imports in models)

**Files**: `backend/app/models/schemas.py`
**Status**: Complete

---

### Task 46: Deep Strategy + Risk + Reconciliation Prompts
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: None

- [x] `PASS1_DEPENDENCY_GRAPH` — build relationship map between artifacts
- [x] `PASS2_INCONSISTENCY_DETECTION` — cross-reference artifact pairs for conflicts
- [x] `PASS3_PROPOSED_UPDATES` — generate specific text fixes per inconsistency
- [x] `PASS4_CROSS_VALIDATION` — re-read artifacts with proposed changes, verify consistency
- [x] `RISK_PREDICTION_PROMPT` — identify missing/predicted risks from project health
- [x] `CROSS_SECTION_RECONCILIATION_PROMPT` — detect cross-section impacts in LPD
- [x] All prompts specify JSON output format matching Pydantic models
- [x] Anti-vagueness rules (D10 pattern) and few-shot examples included
- [x] Prompt structure regression tests

**Files**: `deep_strategy_prompts.py` (new), `risk_prediction_prompts.py` (new), `lpd_prompts.py` (extend)
**Status**: Complete

---

### GROUP 2: DEEP STRATEGY ENGINE + FRONTEND (Tasks 47-48)

### Task 47: Deep Strategy Engine Service + API
**Complexity**: L | **Sessions**: 2-3 | **Dependencies**: Tasks 45, 46

- [x] `run_deep_strategy()` — full 4-pass pipeline (dependency graph → inconsistency detection → proposed updates → cross-validation)
- [x] `apply_deep_strategy_updates()` — VPMA artifacts → write to file, uploaded → clipboard content
- [x] Privacy proxy on all 4 passes (anonymize → LLM → reidentify)
- [x] Session logging (`tab_used="deep_strategy"`)
- [x] Helper parsers for each pass output
- [x] `POST /api/deep-strategy/analyze` endpoint
- [x] `POST /api/deep-strategy/apply` endpoint
- [x] Architecture tests include `deep_strategy`
- [x] Tests: parsers, pipeline, privacy, session logging, apply logic, edge cases

**Files**: `deep_strategy.py` (new), `routes.py` (extend)
**Status**: Complete

---

### Task 48: Deep Strategy Frontend
**Complexity**: L | **Sessions**: 2-3 | **Dependencies**: Tasks 45, 47

- [x] `DeepStrategy.jsx` page — full workflow UI
- [x] `ArtifactUploader.jsx` — paste/upload text areas + name field + priority ordering
- [x] `DeepStrategyResults.jsx` — tabbed view per artifact with diff display + accept/reject
- [x] `PassProgressBar.jsx` — 4-step indicator with simulated progress
- [x] "Load from VPMA" feature — load existing VPMA artifacts directly
- [x] API client: `deepStrategyAnalyze()`, `deepStrategyApply()`
- [x] Navigation: "Deep Strategy" as 4th tab in App.jsx at `/deep-strategy`
- [x] Frontend tests

**Files**: `DeepStrategy.jsx`, `ArtifactUploader.jsx`, `DeepStrategyResults.jsx`, `PassProgressBar.jsx` (new), `App.jsx`, `api.js` (extend)
**Status**: Complete

---

### GROUP 3: COMPLEMENTARY FEATURES (Tasks 49-52)

### Task 49: AI Risk Prediction Engine + API
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: None

- [x] `predict_risks()` — LPD + staleness + RAID Log → LLM → predicted risks
- [x] Risk categories: timeline, stakeholder gaps, scope creep, stale sections, unresolved questions, missing deadlines
- [x] Privacy proxy applied to all content
- [x] Session logging
- [x] `POST /api/risk-prediction/{project_id}` endpoint
- [x] Tests: prediction parsing, pipeline, empty LPD, privacy integration

**Files**: `risk_prediction.py` (new), `risk_prediction_prompts.py` (from Task 46), `routes.py` (extend)
**Status**: Complete

---

### Task 50: Risk Prediction + Reconciliation Frontend
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: Tasks 49, 51

- [x] `RiskPredictionPanel.jsx` — loading spinner, predicted risk cards with severity/confidence, "Add to RAID Log" button
- [x] `ReconciliationPanel.jsx` — cross-section impacts grouped by type, color-coded (resolves/contradicts/requires_update)
- [x] "Predict Risks" and "Reconcile" buttons on ProjectDoc.jsx
- [x] API client: `predictRisks()`, `reconcileLPD()`
- [x] Frontend tests

**Files**: `RiskPredictionPanel.jsx`, `ReconciliationPanel.jsx` (new), `ProjectDoc.jsx`, `api.js` (extend)
**Status**: Complete

---

### Task 51: Cross-Section LPD Reconciliation Engine (D39)
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: None

- [x] `reconcile_lpd_sections()` — fetch all 7 LPD sections, anonymize, single LLM call, parse impacts
- [x] Impact types: resolves, contradicts, supersedes, requires_update
- [x] `POST /api/lpd/{project_id}/reconcile` endpoint
- [x] Reuses content gate pattern + LPD manager + privacy proxy
- [x] Tests: parsing, empty LPD, full reconciliation

**Files**: `reconciliation.py` (new), `lpd_prompts.py`, `routes.py` (extend)
**Status**: Complete

---

### Task 52: Folder Browser (V41)
**Complexity**: S | **Sessions**: 1 | **Dependencies**: None

- [x] `GET /api/settings/browse-folders` — directory listing endpoint
- [x] Security: restricted to home directory, no symlinks, hidden dirs filtered, path traversal blocked
- [x] `FolderBrowser.jsx` — modal with directory navigation + select
- [x] "Browse" button in Settings next to transcript watch folder input
- [x] Tests: backend security (path traversal, symlinks, hidden dirs) + frontend (browse modal, navigation, select)

**Files**: `routes.py` (extend), `FolderBrowser.jsx` (new), `Settings.jsx` (extend), `api.js` (extend)
**Status**: Complete

---

### GROUP 4: INTEGRATION

### Task 53: Phase 2B E2E Integration & Polish
**Complexity**: M | **Sessions**: 2-3 | **Dependencies**: All (45-52)

- [x] Frontend testing: all Phase 2B components pass test suite
- [x] E2E: Deep Strategy with real LLM (3+ artifact scenario)
- [x] E2E: Risk Prediction with populated LPD
- [x] E2E: Reconciliation with known cross-section relationships
- [x] E2E: Folder Browser with real filesystem
- [x] Regression: all Phase 0 + 1A + 1B + 2A tests pass
- [x] Architecture tests include `deep_strategy`, `risk_prediction`, `reconciliation`
- [x] Smoke tests for new critical paths
- [x] Security: folder browser path traversal verification
- [x] Nav: Deep Strategy tab + Project Doc action buttons work correctly
- [x] Version bump (coordinate with 2A merge)
- [x] CLAUDE.md updated (project structure, test counts, endpoint counts, new services)
- [x] docs/EXECUTIVE_SUMMARY.md updated
- [x] Full test suite pass (915 backend + 284 frontend = 1,199 total)
- [x] Skeptical PM review of shipped features (D54)

**Done when**: All features work E2E with real LLM, all tests pass, docs current.
**Status**: Complete

---

## Phase 3: Interactive Intelligence (Tasks 54-63)

**Theme**: Shift from paste-and-process to proactive, conversational, leave-and-return.
**Scoped**: 2026-03-13 (D56). Split into 3A/3B/3C per Rule 20.
**Skeptical PM verdict**: MAYBE → adjusted plan (V31 deferred to Phase 4, V41 quality gate added).

### Progress

| Sub-Phase | Tasks | Done | Status |
|-----------|-------|------|--------|
| 3A: UX Clarity + Infrastructure | 54-58 | 3/5 | In Progress |
| 3B: Chat + Brain Dump | 59-61 | 0/3 | Not Started |
| 3C: Skeptical Reviewer | 62-63 | 0/2 | Not Started |

---

### PHASE 3A: UX CLARITY + INFRASTRUCTURE (Tasks 54-58)

### Task 54: UX-3 — Naming & Information Architecture Pass
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: None

- [x] Audit all tab names, page titles, and section headers against actual function
- [x] Rename "Artifact Sync" → **"Process"** (covers Extract/Analyze/Log — "I have new info")
- [x] Rename "Deep Strategy" → **"Audit"** with internal label **"Document Consistency"** (no user-facing "Deep Strategy" remains)
- [x] Add subtitles or one-line descriptions under each tab/mode explaining what it does
- [x] Review "Project Knowledge Base" — kept as **"Knowledge Base"** (accurate, consistent)
- [x] Move Reconciliation from Knowledge Base → Audit page (audit intent, not insight intent)
- [x] Risk Prediction stays on Knowledge Base (insight intent, seed of future Interrogate experience)
- [x] Frontend tests updated for renamed components/labels (286 pass)
- [x] No broken navigation or references after rename

**Terminology lock (D57)**: Process / Audit / Knowledge Base / Settings. Intent model: new info → audit/sync → insights/reference.
**Done when**: A first-time user can read tab names and understand what each feature does without explanation.
**Status**: Complete

---

### Task 55: Empty-State Coaching (D54 #2)
**Complexity**: S | **Sessions**: 1 | **Dependencies**: None

- [x] Risk Prediction: when no risks returned, coaching hint about adding Knowledge Base content
- [x] Reconciliation: when no impacts found, reassurance + growth guidance
- [x] Deep Strategy: coaching hints on all 3 sub-tabs (inconsistencies, proposed updates, validation)
- [x] Artifact Sync: LPD context hint in initial empty state
- [x] Frontend tests for each empty state message (7 new tests)

**Done when**: Every feature that can return "nothing" explains why and tells the user what to do next. Feels helpful, not broken.
**Status**: Complete

---

### Task 56: Proactive Nudge Banner (D54 #3)
**Complexity**: S | **Sessions**: 1 | **Dependencies**: None

- [x] Query LPD section staleness on Project Doc page load
- [x] Display banner when ≥1 section hasn't been updated in 14+ days with section names and day counts
- [x] Banner is dismissable (per session via state, not permanent)
- [x] Clicking section name scrolls to and highlights that section (ring-2 amber, 2s fade)
- [x] No banner when all sections are fresh or LPD is empty
- [x] Frontend tests for banner display logic, dismiss, and edge cases
- [x] Moved Reconciliation panel from Knowledge Base to Audit page (consolidates audit features)

**Done when**: Project Doc proactively tells the PM what needs attention without requiring them to click "Predict Risks" or "Reconcile."
**Status**: Complete

---

### Task 57: Session-Based Polling — V42 Fire-and-Forget Processing
**Complexity**: L | **Sessions**: 2-3 | **Dependencies**: None

- [ ] Backend: `POST /api/jobs` — accepts any processing request (artifact sync, deep strategy, etc.), returns `job_id` immediately
- [ ] Backend: `GET /api/jobs/{job_id}` — returns status (pending/running/complete/failed) + result when complete
- [ ] Backend: job runner executes processing in background thread/task, stores result in DB or memory
- [ ] New DB table: `jobs` (job_id, project_id, job_type, status, request_json, result_json, created_at, completed_at)
- [ ] Frontend: on submit, save `job_id` to localStorage, show progress indicator
- [ ] Frontend: on page mount, check localStorage for pending jobs, poll `GET /api/jobs/{job_id}` until complete
- [ ] Frontend: when complete, render results normally (same UI as current inline results)
- [ ] Migrate Deep Strategy to use job-based processing (longest-running pipeline, biggest benefit)
- [ ] Migrate Artifact Sync to use job-based processing
- [ ] Architecture tests include job runner
- [ ] Tests: job lifecycle (create, poll, complete, expire), error handling, concurrent jobs

**Done when**: User can start Deep Strategy or Artifact Sync, switch tabs or close the page, come back, and see results. No lost processing.
**Status**: Not Started

---

### Task 58: ESLint Cleanup
**Complexity**: XS | **Sessions**: <1 | **Dependencies**: None

- [x] Fix `afterEach` not defined in `api.test.js` (add to ESLint globals or import)
- [x] Fix `ProjectContext.jsx` fast-refresh warning (split export into separate file)
- [x] ESLint passes with 0 errors, 0 warnings

**Done when**: `npx eslint src/` returns clean.
**Status**: Complete

---

### PHASE 3B: CHAT + BRAIN DUMP (Tasks 59-61)

### Task 59: Conversational API — Backend Implementation
**Complexity**: L | **Sessions**: 2-3 | **Dependencies**: Task 57 (job polling pattern)

- [ ] Create `conversations` and `conversation_messages` DB tables (from `docs/conversational_api_design.md`)
- [ ] `chat_service.py` — new service: create conversation, add message, build LLM prompt with conversation history + LPD context
- [ ] System prompt template for conversational PM assistant persona
- [ ] `POST /api/chat/{project_id}` — start or continue conversation
- [ ] `GET /api/chat/{project_id}/conversations` — list conversations
- [ ] `GET /api/chat/{project_id}/conversations/{conversation_id}` — full history
- [ ] `DELETE /api/chat/{project_id}/conversations/{conversation_id}` — delete conversation
- [ ] Privacy proxy on all messages (anonymize user input, reidentify responses)
- [ ] Context window management: last 10 messages in full, summary rollup for older messages
- [ ] Auto-title generation after first assistant response
- [ ] Suggestions in responses: LLM can propose artifact/LPD updates as structured side-effects
- [ ] Session logging (`tab_used="chat"`)
- [ ] Architecture tests include `chat_service`
- [ ] Tests: conversation lifecycle, context injection, privacy round-trip, suggestion extraction, history truncation

**Files**: `chat_service.py` (new), `chat_prompts.py` (new), `routes.py` (extend), `database.py` (extend), `schemas.py` (extend)
**Done when**: Full conversational API works via `/docs` — multi-turn conversation with LPD context, privacy, and suggestion extraction.
**Status**: Not Started

---

### Task 60: Chat Panel — Frontend Implementation
**Complexity**: L | **Sessions**: 2-3 | **Dependencies**: Task 59

- [ ] `ChatPanel.jsx` — message list, input box, send button, loading state
- [ ] `ConversationList.jsx` — sidebar or dropdown showing past conversations with timestamps
- [ ] `ChatMessage.jsx` — renders user and assistant messages, with suggestion cards inline for assistant messages
- [ ] Suggestion cards in chat reuse existing `SuggestionCard.jsx` component (Apply/Copy flow)
- [ ] Navigation: "Chat" as new tab in App.jsx
- [ ] Conversation persistence: selected conversation survives tab switch (localStorage conversation_id)
- [ ] New conversation button, delete conversation
- [ ] Auto-scroll to latest message
- [ ] API client: `sendChatMessage()`, `listConversations()`, `getConversation()`, `deleteConversation()`
- [ ] Frontend tests: message rendering, conversation switching, suggestion card integration, empty states

**Terminology lock (Rule 22)**: Tab name decided before coding. Candidates: "Chat", "Assistant", "Ask VPMA". Finalize here: ___
**Done when**: User can have a multi-turn conversation with VPMA in the browser, see suggestion cards inline, apply suggestions to LPD/artifacts.
**Status**: Not Started

---

### Task 61: Brain Dump Mode — V28/V33
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: Task 59, 60

- [ ] Brain dump system prompt: "User is dumping unstructured thoughts. Triage into: action items, risks, decisions, open questions, project updates, or noise. Route each to the appropriate LPD section or artifact type."
- [ ] Brain dump trigger: either a "Brain Dump" button in the chat panel or a dedicated input mode
- [ ] Triage response format: categorized items with proposed destinations (LPD section, artifact type, or "no action needed")
- [ ] Apply flow: each triaged item can be applied individually (reuses suggestion card pattern)
- [ ] Works with messy, incomplete, stream-of-consciousness input (test with realistic PM brain dumps)
- [ ] Tests: triage parsing, routing logic, messy input handling, empty input

**Done when**: PM can paste or type a messy brain dump, VPMA categorizes and routes each thought to the right place, PM reviews and applies.
**Status**: Not Started

---

### PHASE 3C: SKEPTICAL REVIEWER (Tasks 62-63)

### Task 62: V41 Quality Gate — Prompt Testing
**Complexity**: M | **Sessions**: 1-2 | **Dependencies**: None (can run in parallel with 3B)

- [ ] Write Skeptical Reviewer prompt template: "Given this project's LPD and artifacts, identify specific contradictions, underestimated risks, timeline inconsistencies, and blind spots. Every finding must cite specific evidence from the provided documents."
- [ ] Run prompt against real project data (PM Sandbox or test project with populated LPD)
- [ ] Evaluate output specificity: does it cite specific artifacts/sections, or give generic advice?
- [ ] Score: SPECIFIC (cites evidence, names sections) vs. GENERIC (vague "consider your risks" platitudes)
- [ ] **GO/NO-GO decision**: If output is consistently specific and evidence-backed → GO to Task 63. If generic → iterate on prompt or defer feature.
- [ ] Document findings and decision in DECISIONS.md

**Done when**: Clear GO/NO-GO decision with evidence. If GO, prompt template is proven. If NO-GO, document what's needed and defer.
**Status**: Not Started

---

### Task 63: V41 Skeptical Reviewer — Service + UI
**Complexity**: L | **Sessions**: 2-3 | **Dependencies**: Task 62 (GO decision required)

- [ ] `skeptical_reviewer.py` — new service: reads LPD + artifacts, builds review prompt, parses findings
- [ ] Finding model: `ReviewFinding` — category (contradiction, blind_spot, timeline_risk, underestimated_risk), severity, evidence (artifact/section citations), recommendation
- [ ] `POST /api/review/{project_id}` endpoint
- [ ] Privacy proxy on all content
- [ ] Session logging (`tab_used="review"`)
- [ ] Frontend: "Pressure Test" button on Project Doc (or dedicated tab — decide per Rule 22)
- [ ] `ReviewFindings.jsx` — findings cards grouped by category, severity-colored, with evidence citations
- [ ] Quality filter: suppress findings that don't cite specific evidence (enforce the quality bar from Task 62)
- [ ] Architecture tests include `skeptical_reviewer`
- [ ] Tests: finding parsing, evidence citation validation, empty LPD handling, quality filter

**Terminology lock (Rule 22)**: User-facing name decided before coding. Candidates: "Pressure Test", "Review My Work", "Critical Review". Finalize here: ___
**Done when**: PM clicks a button, VPMA cross-references all project documents and returns specific, evidence-backed findings about contradictions, risks, and blind spots.
**Status**: Not Started

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
| V41 | Phase 1B review | **Folder browser for transcript watcher** — backend-powered directory listing endpoint (`GET /api/settings/browse-folders`) + "Browse" button in Settings. Browser APIs (`showDirectoryPicker`, `webkitdirectory`) don't return filesystem path strings. ~4-5 hrs. |
| V42 | Phase 1B testing | **Transcript watcher results view** — when watcher processes a file, surface what was extracted (suggestion cards, KB updates) in the UI. Currently processes server-side with no frontend visibility beyond "1 file processed" count. PM needs to read and understand updates as they enter the KB. Options: notification panel, activity feed, or auto-navigate to results. ~4-6 hrs. |
| V29 | PA Session 2+4 | **Import AI history** — generalize Gemini export pipeline into product feature. Users import conversation history from any AI assistant. Competitive differentiator. Intake pipeline (Phase 1A) is the foundation. |
| V5 | Session 3 | **Personal bottleneck detection** — track PM's action item aging and convergence points. Simpler than full HR capacity; moved earlier from Phase 4. |
| V17 | Sessions 1-4 | **Data provenance / source tracking** — every fact traces to input, timestamp, session. Add to LPD/artifact data model. Easier now than retrofit. |
| V7 | Session 3 | **Portfolio roll-up views** — extends multi-project with risk heat maps and cross-project dashboards. |
| V10 | Sessions 3+21 | **GitHub Projects sync** — validated twice, manual workaround exists. Automate the weekly cross-reference. |
| D39 | E2E testing | **Cross-section LPD reconciliation** — content gate (D33) compares within-section only. Extend to detect cross-section impacts (e.g., Decision resolves a Risk, Action Item closes an Open Question). Requires full-LPD context per comparison. |

### Phase 3 Additions (Promoted/Slotted)

| Item | Source | Description |
|------|--------|-------------|
| V41 | Phase 2A brainstorm | **Skeptical Reviewer / pressure-test mode (user-facing)** — VPMA acts as critical reviewer of PM's own work. Cross-references artifacts to surface contradictions, underestimated risks, timeline inconsistencies. Differentiated by LPD context: specific evidence-based critique, not generic advice. Serves both PM and Research markets. Promoted Review 3 (score 9/9). |
| V28/V33 | PA + PM Sandbox | **Brain dump mode** — freeform capture → triage → route. MVP of the chat panel concept (D36). "Personal inbox zero." |
| V37 | Session 25 | **Cross-document synthesis** — "build alignment package for Topic X." Requires chat panel + good LPD context. |
| V31 | 3 projects | **Decision journal with pattern learning** — extend DECISIONS.md pattern into VPMA with temporal detection ("you delay X-type decisions by 2 weeks"). |
| V42 | Phase 2A testing | **Session-based polling** — server-tracked processing so users can leave and come back. Prevents lost processing on tab switch. Enables progress indicators. Slotted Review 3. |
| V45 | Brain dump #5 | **Local LLM vision/multimodal evaluation** — evaluate vision models (qwen3.5:27b) for screenshot/diagram analysis. Connects to V13 (multi-format input). Slotted Review 3. |
| V12 | Session 3 | **Meeting prep generation** — auto-generate agenda, talking points, data references from KB + meeting cadence. |

### UX & Intelligence Backlog (User Feedback, 2026-03-12)

| Item | Description | Priority |
|------|-------------|----------|
| UX-1 | **Intelligent model selection** — warn on poor model choice (e.g. large input for Ollama small model), auto-suggest appropriate model, token budget awareness | Medium |
| UX-2 | **AI Agent window** — scrolling feed of suggestions, auto-updates, autonomous agent-style recommendations without user prompting | Low (Phase 3+) |
| UX-3 | **Information architecture / naming clarity** — "Artifact Sync" title appears on all 3 modes but doesn't explain why Extract/Analyze/Log are siblings; "Deep Strategy" is unclear; first-time user can't tell if a mode is one-off review, ongoing sync, coaching, or KB update. Needs clear labels, subtitles, or onboarding hints that answer "what does this do?" at a glance. | High |

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
