# VPMA Phase 0: Foundation MVP — RALPH Tasks

**Target**: 4 weeks (~50-70 keyboard hours)
**Method**: Claude Code + RALPH loop (prompt → review → test → refine)

## Progress

| Group | Tasks | Done | Status |
|-------|-------|------|--------|
| Infrastructure | 1-4 | 0/4 | Not started |
| Privacy & LLM | 5-8 | 0/4 | Not started |
| Backend Logic | 9-12 | 0/4 | Not started |
| Frontend | 13-17 | 0/5 | Not started |
| Integration & Polish | 18-20 | 0/3 | Not started |

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
- [ ] Schema with all tables: projects, artifacts, artifact_versions, sessions, pii_vault, settings
- [ ] project_id on all tables (multi-project ready)
- [ ] Connection module (async with aiosqlite)
- [ ] Init script (create tables on first run)
- [ ] Basic CRUD queries
**Status**: Not started

### Task 3: Privacy Proxy — Regex PII Detection
- [ ] Email pattern detection
- [ ] Phone number pattern detection
- [ ] URL pattern detection
- [ ] Custom sensitive terms matching (from settings)
- [ ] Unit tests with sample text
**Status**: Not started

### Task 4: Privacy Proxy — spaCy NER Integration
- [ ] Load en_core_web_sm model
- [ ] PERSON entity detection
- [ ] ORG entity detection
- [ ] GPE (location) entity detection
- [ ] Confidence scoring (flag low confidence < 70%)
- [ ] Unit tests
**Status**: Not started

---

## Privacy & LLM (Tasks 5-8)

### Task 5: Privacy Proxy — Vault & Anonymize/Reidentify
- [ ] Token vault (store/retrieve mappings in SQLite pii_vault table)
- [ ] anonymize(text) function — combines regex + NER, replaces with tokens (<PERSON_1>, etc.)
- [ ] reidentify(text) function — replaces tokens back to originals
- [ ] Audit log writing (append to ~/VPMA/privacy/audit_log.jsonl)
- [ ] Global vault scope (not project-specific)
- [ ] Unit tests for round-trip anonymize → reidentify
**Status**: Not started

### Task 6: LLM Client — Base Abstract Interface
- [ ] Base class with call() method (system_prompt, user_prompt, max_tokens) → str
- [ ] Provider enum (CLAUDE, GEMINI, OLLAMA)
- [ ] Client factory: create_client(provider) → LLMClient
- [ ] Error handling (retry with exponential backoff, 3 attempts)
- [ ] Token counting stub
**Status**: Not started

### Task 7: LLM Client — Claude Adapter
- [ ] AnthropicClient implementing base interface
- [ ] API key from .env (ANTHROPIC_API_KEY)
- [ ] Model selection (default: claude-sonnet-4-5-20250929)
- [ ] Error handling for API failures
- [ ] Unit test (mock API call)
**Status**: Not started

### Task 8: LLM Client — Gemini Adapter
- [ ] GeminiClient implementing base interface
- [ ] API key from .env (GOOGLE_AI_API_KEY)
- [ ] Model selection (default: gemini-2.0-flash)
- [ ] Error handling for API failures
- [ ] Unit test (mock API call)
**Status**: Not started

---

## Backend Logic (Tasks 9-12)

### Task 9: Artifact Manager — Types & Templates
- [ ] Artifact type definitions (RAID Log, Status Report, Meeting Notes)
- [ ] Markdown template for each type
- [ ] Template loading from backend/app/prompts/templates/
- [ ] Artifact CRUD (create, read, update via markdown files in ~/VPMA/artifacts/)
- [ ] Metadata tracking in SQLite artifacts table
**Status**: Not started

### Task 10: Artifact Sync — Core Backend Logic
- [ ] Input → Privacy Proxy anonymize → LLM call → parse response → suggestions
- [ ] Input type classification (text vs transcript — extensible)
- [ ] Delta extraction (what changed, what's new)
- [ ] Suggestion model (artifact_type, change_type, proposed_text, confidence)
- [ ] Session logging (write to SQLite sessions table)
**Status**: Not started

### Task 11: Artifact Sync — System Prompts
- [ ] System prompt for artifact detection ("which artifacts need updates?")
- [ ] System prompt for delta extraction ("what specific changes?")
- [ ] Structured JSON output format for suggestions
- [ ] Few-shot examples for each artifact type
- [ ] Prompt testing with sample meeting notes
**Status**: Not started

### Task 12: FastAPI Endpoints
- [ ] POST /api/artifact-sync (main flow: text → suggestions)
- [ ] GET /api/settings (retrieve current settings)
- [ ] PUT /api/settings (update settings — API keys, LLM provider, sensitive terms)
- [ ] GET /api/health (backend status check)
- [ ] POST /api/artifacts/{id}/apply (apply a suggestion to local storage)
- [ ] Request/response Pydantic models
- [ ] CORS configuration for localhost:3000
**Status**: Not started

---

## Frontend (Tasks 13-17)

### Task 13: React App Shell
- [ ] Two-tab navigation (Artifact Sync, Settings)
- [ ] Layout component with header (VPMA branding)
- [ ] React Router setup (/ → Artifact Sync, /settings → Settings)
- [ ] Tailwind CSS base styles
- [ ] API base URL from environment
**Status**: Not started

### Task 14: Text Input Component
- [ ] Large text area with placeholder ("Paste meeting notes, transcripts, or project updates...")
- [ ] Submit button with loading state
- [ ] Character count display
- [ ] Clear button
- [ ] Auto-resize text area
**Status**: Not started

### Task 15: Suggestion Cards Component
- [ ] Card layout per suggestion (artifact name, change type, proposed text)
- [ ] Expandable preview (click to show full text)
- [ ] Copy-to-clipboard button (primary action)
- [ ] Apply button (stores in VPMA database)
- [ ] Visual feedback on copy/apply (toast or checkmark)
- [ ] Empty state ("No suggestions yet")
**Status**: Not started

### Task 16: Basic Settings Page
- [ ] API key inputs (Claude, Gemini) with show/hide toggle
- [ ] LLM provider radio buttons (Claude / Gemini)
- [ ] Custom sensitive terms textarea (comma-separated or newline-separated)
- [ ] Save button with success feedback
- [ ] Load current settings on page mount
**Status**: Not started

### Task 17: Error Handling & States
- [ ] API error display (connection failed, LLM error, etc.)
- [ ] Loading spinner during LLM calls
- [ ] Empty states for each page
- [ ] Toast/notification system for actions (copied, saved, error)
- [ ] Backend health check on app load
**Status**: Not started

---

## Integration & Polish (Tasks 18-20)

### Task 18: End-to-End Integration Test
- [ ] Full flow: paste text → anonymize → LLM → reidentify → display → copy
- [ ] Test with 3+ real-world meeting notes samples
- [ ] Verify PII anonymization (no real names in LLM requests)
- [ ] Verify copy-to-clipboard works
- [ ] Verify apply writes to ~/VPMA/artifacts/
- [ ] Test Claude ⟷ Gemini toggle
**Status**: Not started

### Task 19: Prompt Quality Tuning
- [ ] Test with 5+ varied meeting note styles
- [ ] Evaluate suggestion relevance (are the right artifacts identified?)
- [ ] Evaluate proposed text quality (useful updates?)
- [ ] Refine system prompts based on results
- [ ] Document what works and what doesn't
**Status**: Not started

### Task 20: Styling & Polish
- [ ] Consistent Tailwind styling across all components
- [ ] Responsive layout (works on laptop screen)
- [ ] Loading states feel smooth
- [ ] Error messages are helpful
- [ ] Overall UX feels clean (Google-minimalist philosophy)
**Status**: Not started

---

## Go/No-Go Criteria (End of Phase 0)

- [ ] Core flow works end-to-end without errors
- [ ] Privacy Proxy: No PII leaks in manual audit
- [ ] Artifact suggestions are relevant and useful (personal assessment)
- [ ] Copy-to-clipboard works reliably
- [ ] "This saves me time vs. doing it manually" (personal validation)
