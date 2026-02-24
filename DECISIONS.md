# VPMA — Decisions Log

**Last Updated**: 2026-02-23
**Current As Of**: 2026-02-23

---

## Purpose

Records non-obvious architectural and design decisions with rationale. Prevents relitigating decisions and provides context for future sessions.

**Note**: This file was created retroactively during a cross-project process audit (2026-02-23). Prior decisions are embedded in CLAUDE.md (Key Patterns), TASKS.md (implementation choices), and QUESTIONS_LOG.md (backlog ideas). Future decisions should be logged here as they're made.

---

## Decisions

### D1: Abstract LLM Client Interface
**Date**: 2026-02-14 (Phase 0, Task 6) | **Status**: Active

**Decision**: All LLM calls go through an abstract `LLMClient` base interface with provider-specific adapters (Claude, Gemini, Ollama). No direct API calls in business logic.

**Rationale**: Enables provider switching without code changes. Proved its value when adding Gemini adapter — one new file, zero changes to existing code. Matches Process Playbook Rule #5 (abstract interfaces pay off even for MVPs).

### D2: Privacy Proxy as Mandatory Pipeline Step
**Date**: 2026-02-14 (Phase 0, Tasks 3-5) | **Status**: Active

**Decision**: All user text must pass through the Privacy Proxy (regex + spaCy NER + custom terms) before reaching any LLM. Three detection layers with deduplication.

**Rationale**: Privacy is a core differentiator. Layered detection catches what single methods miss (Process Playbook Rule #6). Global vault scope (not project-specific) ensures consistent anonymization across sessions.

### D3: Project-Scoped Schema from Day One
**Date**: 2026-02-14 (Phase 0, Task 2) | **Status**: Active

**Decision**: Every database table includes `project_id` even though Phase 0 is single-project.

**Rationale**: Forward-compatible schema prevents painful migration when multi-project support arrives in Phase 2 (Process Playbook Rule #7).

### D4: Markdown Files for Artifact Content, SQLite for Metadata
**Date**: 2026-02-14 (Phase 0, Task 9) | **Status**: Active

**Decision**: Artifact content lives in `~/VPMA/artifacts/` as Markdown files. SQLite stores metadata only (timestamps, references, sessions, PII vault).

**Rationale**: Markdown files are human-readable, diffable, and portable. SQLite handles structured queries well but is the wrong format for long-form document content. This split optimizes for both use cases.

### D5: Generality and Privacy Rules for Source Code
**Date**: 2026-02-15 (Phase 0, Task 19) | **Status**: Active

**Decision**: VPMA source code, prompts, tests, and UI must never contain references to the developer's personal projects, career, or clients. Planning docs may contain personal context but must be cleaned before external release.

**Rationale**: The tool is designed to be general-purpose. Personal references in shipped code would limit adoption and expose private information. Planning docs are acceptable as private working artifacts.
