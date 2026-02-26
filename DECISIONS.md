# VPMA — Decisions Log

**Last Updated**: 2026-02-25
**Current As Of**: 2026-02-25 (Phase 1A strategic planning session)

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

### D6: Section-Aware Artifact Insertion
**Date**: 2026-02-24 (Phase 0, Task 19 bug fix) | **Status**: Active

**Decision**: Apply endpoint now parses the artifact Markdown structure and inserts suggestions into the correct `## Section` heading instead of appending at end-of-file. Falls back to end-of-file append if the section heading isn't found.

**Rationale**: First live test revealed that end-of-file append produced artifacts with content dumped outside section boundaries (table rows outside tables, bullets outside lists). Section-aware insertion produces well-structured, human-readable artifacts that match the Markdown templates.

### D7: Dedup Guard on Artifact Apply
**Date**: 2026-02-24 (Phase 0, Task 19 bug fix) | **Status**: Active

**Decision**: Before appending a suggestion, the apply endpoint checks if `proposed_text` already exists in the artifact content. If found, returns `{"status": "duplicate"}` (200 OK) instead of appending again.

**Rationale**: First live test produced 55 suggestions; many had identical proposed_text (generic template content from the LLM). Applying all of them produced artifacts with 20-30x duplicate lines. Substring-based dedup is simple and effective for Phase 0. A more sophisticated approach (semantic similarity, content hashing) can be added later if needed.

### D8: Gemini 2.5 Flash Thinking Budget Cap
**Date**: 2026-02-24 (Phase 0, Task 19 bug fix) | **Status**: Active

**Decision**: Set `thinking_budget=2048` and `max_output_tokens=16384` for Gemini 2.5 Flash calls. Thinking tokens are explicitly capped rather than allowed to consume the full output budget.

**Rationale**: Gemini 2.5 Flash's thinking tokens count toward `max_output_tokens`. With the original 4096 limit, thinking consumed the entire budget, producing truncated (521-char) or empty responses. The 2048/16384 split reserves enough room for both reasoning and a full JSON response.

### D9: NER False Positive Filtering
**Date**: 2026-02-25 (Phase 0, Task 19 quality fix) | **Status**: Active

**Decision**: Added three filters to `detect_ner()`: (1) minimum confidence threshold of 0.75 (previously defined at 0.70 but never enforced), (2) minimum entity length of 2 characters, (3) stoplist of ~40 words that `en_core_web_sm` commonly misclassifies in conversational text (e.g., "Hmm" as PERSON, "SMS" as ORG, "Colleague" as GPE).

**Rationale**: Second live test showed 991 entity detections from 78 "unique" entities — most were false positives from conversational transcript text. Words like "Standup", "Congratulations", and "UI" were being tokenized, garbling the LLM input and producing unreidentified tokens in output. Filtering at the NER layer is the cleanest fix since regex and custom term detections are deterministic and accurate.

### D10: Self-Contained Suggestion Quality Standard
**Date**: 2026-02-25 (Phase 0, Task 19 quality fix) | **Status**: Active

**Decision**: Rewrote the artifact sync system prompt to prioritize self-contained, detailed suggestions over brevity. Key changes: (1) replaced "concise" with "self-contained" in proposed_text guidance, (2) redefined reasoning field from source attribution to project impact/urgency, (3) added "standalone test" anti-vagueness rules, (4) added Bad vs Good quality calibration examples, (5) enriched all prompt examples with richer proposed_text and impact-based reasoning, (6) expanded transcript-specific extraction guidance.

**Rationale**: Live testing showed suggestions like "Working on automation setup" that required going back to the source material. A PM document entry should be self-explanatory — the reader shouldn't need to research what it's referring to. The prompt's use of "concise" was the primary signal causing the LLM to compress too aggressively. The Bad vs Good examples calibrate the LLM on the target quality level.

### D11: Document Draft View for Meeting Notes & Status Report
**Date**: 2026-02-25 (Phase 0, Task 19 UX fix) | **Status**: Active

**Decision**: Meeting Notes and Status Report suggestions render as a single assembled document draft card (grouped by section, with "Copy All" / "Apply All"). RAID Log suggestions remain as individual item cards. New `DocumentDraftCard` component handles the assembled view; `ArtifactSync.jsx` conditionally renders based on artifact type.

**Rationale**: Meeting Notes and Status Reports are "document creation" workflows — you create a new document per meeting or per reporting period and want to review/copy it as a whole. RAID Log is an "item management" workflow — you append or update individual rows. The previous design rendered all artifact types as individual cards, forcing users to mentally assemble documents from fragments and click Apply 4-8 times. The new split matches how PMs actually use these artifacts.

### D12: Intent Mode Toggle (Extract vs. Analyze)
**Date**: 2026-02-25 (Phase 0, UX enhancement) | **Status**: Active

**Decision**: Added a mode toggle to Artifact Sync with two intents: "Extract & Route" (existing behavior — extract structured suggestions from input) and "Analyze & Advise" (new — provide feedback and observations on a document draft). Same endpoint with a `mode` parameter, separate system prompt, new `AnalysisItem` response model, and new `AnalysisCard` frontend component. Extract remains the default.

**Rationale**: User feedback identified that not all input is "data to extract from" — sometimes it's a draft document needing review. Same input (e.g., a Slack screenshot) can serve either purpose depending on user intent. This is a lightweight precursor to Phase 1's Feedback Box, reusing 80% of the existing pipeline (LLM client, privacy proxy, input classification, session logging). Weekly status synthesis across sessions was triaged and parked for Phase 3 as designed.

### D13: Weekly Status Synthesis Stays Phase 3
**Date**: 2026-02-25 (Phase 0 triage) | **Status**: Active

**Decision**: Deferred multi-session status report synthesis to Phase 3 (Weekly Planner). The current one-shot flow remains for Phase 0. Session logging infrastructure exists and `get_sessions_by_project()` is built but unused.

**Rationale**: Synthesis requires cross-session context accumulation, a "synthesize my week" UX action, and the return path (Phase 1). Architecture Insights Pattern 5 validates weekly cadence as the right granularity. Pulling this into Phase 0 would require premature architecture decisions about context assembly before the return path is built.

### D14: Phase 1 Reframe — Phase 1A (Context Foundation) Before 1B (Feature Expansion)
**Date**: 2026-02-25 (strategic planning session) | **Status**: Active

**Decision**: Split Phase 1 into two sub-phases:
- **Phase 1A — Context Foundation**: Living Project Document (LPD), return path (applied suggestions update LPD), context injection (LLM calls receive relevant LPD context automatically), in-flight project intake (bulk import existing PM markdown files to seed LPD)
- **Phase 1B — Feature Expansion**: Remaining Phase 1 PRD features (TypeScript migration, more artifact types, export engine, onboarding wizard, comms assistant, feedback box)

Phase 1A is the prerequisite. Phase 1B builds on it.

**Rationale**: Without the return path, every VPMA session starts from zero — the system has no memory of what it already knows about a project. The LPD is the unifying concept (QUESTIONS_LOG Q7, Architecture Insights Pattern 1) that makes dashboards, narrative output, cross-session synthesis, and intelligent questions all tractable. Building Phase 1B features without the LPD would produce features that can't reference project context, limiting their value. Architecture Insights Pattern 1 (return path) and Pattern 3 (nav vs. session separation) are explicitly tagged as Phase 1 priorities. In-flight project intake (new — not in current PRD) is included in 1A because the developer's own PM Sandbox files are the first import target, and the feature is needed for any PM adopting the tool mid-project.

**Connects to**: Architecture Insights Patterns 1, 3; QUESTIONS_LOG Q7 (LPD concept); VPMA_BACKLOG V1, V3, V14, V21

### D15: Path A — Strict LPD Foundation + Claude Code Hybrid Workflow
**Date**: 2026-02-25 (strategic planning session) | **Status**: Active

**Decision**: For the PM Sandbox → VPMA transition, chose Path A (strict LPD foundation, Claude Code for deep conversations) over Path B (lightweight brain dump/chat mode in VPMA during Phase 1A). The transition plan:

1. **Build Phase 1A**: LPD + return path + project intake + context injection
2. **Cutover from PM Sandbox**: At end of Phase 1A — once context accumulation works, not once chat is built
3. **Hybrid workflow during transition**: VPMA handles structured daily artifact work (extract, analyze, apply); Claude Code reads LPD files for deep strategic conversations
4. **Bridge mechanism**: "Log Session" intake feature — paste conclusions/decisions from deep Claude Code sessions into VPMA, LLM extracts entities and updates LPD + artifacts
5. **Future**: Native chat interface in VPMA replaces the Claude Code dependency (Phase 2+)

**Design constraint**: LPD must be fully usable through VPMA's own API — no workflow should require external file access. This ensures a future chat interface can plug in without rearchitecting.

**Rationale**: Two distinct gaps were identified between PM Sandbox and VPMA:
- **Context gap**: VPMA doesn't know project state (every session starts cold). *Phase 1A closes this.*
- **Interaction model gap**: VPMA is paste-and-process; PM Sandbox is conversational. *Future chat closes this.*

Path B (brain dump mode) was rejected because even with it, deep strategic conversations would still require Claude Code — the lightweight mode wouldn't replace the interaction gap, only partially bridge it. Better to build the foundation right than ship a half-measure that still has the same dependency.

**PM Sandbox workflow analysis** (from this session's research):
- Brain dumps + triage → Covered by Phase 1A intake + extract mode
- Strategic exploration → Stays in Claude Code until chat is built
- Document drafting/review → Already in Phase 0 (Analyze mode)
- Cross-artifact synthesis → Covered by LPD + context injection

**Market validation**: Height's $18.3M failure validates building foundation before full experience. The progression model (personal → expert PMs → orgs) means Stage 2 users won't have Claude Code, so the API-first LPD design ensures chat can be added later as an incremental feature, not an architectural rework. The cutover point (end of 1A, not end of chat) means PM Sandbox can be retired sooner than originally assumed.
