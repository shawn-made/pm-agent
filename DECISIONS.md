# VPMA — Decisions Log

**Last Updated**: 2026-03-03
**Current As Of**: 2026-03-03 (D41-D44 added — Phase 1B design decisions)

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

### D16: LPD Section-Based Database Storage (Not Single File)
**Date**: 2026-02-25 (Phase 1A planning, resolves Q19) | **Status**: Active

**Decision**: Store LPD sections as individual database rows in `lpd_sections` table, not as a single Markdown file. Each section has independent `updated_at` and `verified_at` timestamps. A Markdown file is rendered as a write-through cache for human readability, but the database is the source of truth.

**Rationale**: Section-based storage enables: (1) independent staleness tracking per section (Pattern 2), (2) selective context injection — send only relevant sections to LLM within token budget, (3) granular updates without overwriting the full document, (4) future section-level versioning. This differs from Phase 0's artifact pattern (file as source of truth) because the LPD needs richer metadata per section.

**LPD sections (fixed template)**: Overview, Stakeholders, Timeline & Milestones, Risks, Decisions, Open Questions, Recent Context. First 6 form the stable "Project Map" (Pattern 3). Recent Context is temporal and bounded (~1500 tokens, auto-pruned).

### D17: LPD as Separate System from Artifacts
**Date**: 2026-02-25 (Phase 1A planning) | **Status**: Active

**Decision**: The LPD gets its own manager (`lpd_manager.py`), data model (`lpd_sections` table), and service layer — completely separate from the Phase 0 artifact system (`artifact_manager.py`, `artifacts` table). The LPD is NOT a new `ArtifactType`.

**Rationale**: The LPD and artifacts serve fundamentally different purposes. Artifacts (RAID Log, Status Report, Meeting Notes) are structured outputs for specific audiences — one per type per project. The LPD is a persistent knowledge base that accumulates across sessions and feeds context into all LLM calls. Conflating them would force the artifact system to support features it wasn't designed for (section-level staleness, context injection, session summaries). Keeping them separate maintains Phase 0's clean artifact system while adding the new capability.

### D18: Intake Strategy — Per-File Processing with Draft Review
**Date**: 2026-02-25 (Phase 1A planning, resolves Q18) | **Status**: Active

**Decision**: Process each intake file individually (one LLM call per file), present all extractions as a draft for human review before committing to the LPD. Contradictions across files are flagged, not silently resolved.

**Rationale**: Per-file processing is simpler, more reliable, and allows progress reporting per file. Draft review before commit prevents bad extractions from polluting the LPD. Flagging contradictions (rather than auto-resolving) respects the PM's judgment — the system surfaces conflicts, the human decides.

### D19: Context Injection Priority Order
**Date**: 2026-02-25 (Phase 1A, Task 23) | **Status**: Active

**Decision**: When assembling LPD context for injection into LLM prompts, sections are included in priority order: Overview → Recent Context → Risks → Decisions → Open Questions → Stakeholders → Timeline & Milestones. Sections with empty content are skipped. If the token budget is exceeded, content is truncated mid-section rather than dropping entire sections.

**Rationale**: Overview provides essential project identity. Recent Context is the most temporally relevant for current work. Risks and Decisions inform LLM judgment about project constraints. Stakeholders and Timeline are useful but lower priority for most prompts. Truncation over omission ensures the LLM always gets at least partial context for each priority section.

### D20: LPD Markdown as Write-Through Cache
**Date**: 2026-02-25 (Phase 1A, Task 23) | **Status**: Active

**Decision**: The LPD Markdown file (`data/artifacts/{project_id}_lpd.md`) is a write-through cache — it's regenerated from the database on every section update or append. The database is the source of truth, not the file. The file exists for human readability and for Claude Code's file-based workflows.

**Rationale**: D15 established that Claude Code reads LPD files for deep conversations during the hybrid workflow period. A write-through cache ensures the file is always current without requiring manual export. Database-as-truth preserves section-level metadata (staleness, verification) that a flat file can't capture. File regeneration is cheap (~1ms) and happens on every mutation anyway.

### D21: Rough Token Estimation (4 chars/token)
**Date**: 2026-02-25 (Phase 1A, Task 23) | **Status**: Active

**Decision**: Token budgets for context injection (~4000 tokens) and Recent Context pruning (~1500 tokens) use a rough estimate of 4 characters per token. No tokenizer library dependency.

**Rationale**: Exact token counting requires a provider-specific tokenizer (tiktoken for Claude, different for Gemini), adding complexity and a dependency for minimal accuracy gain. The 4 chars/token estimate is conservative for English text and consistent with the existing `estimate_tokens()` method on the LLM client. Over-estimating tokens (which this does slightly) is preferable to under-estimating, as it prevents context overflow. Can be refined later if real-world usage shows significant budget waste.

### D22: Structural Headings Outside Anonymization Boundary
**Date**: 2026-02-25 (Phase 1A, Task 24) | **Status**: Active

**Decision**: When injecting LPD context into LLM prompts, the structural heading `## Project Context` is added *after* anonymization, not passed through the privacy proxy. Only the context body (section headings and content) is anonymized.

**Rationale**: spaCy's `en_core_web_sm` model misclassifies "Project Context" as a PERSON entity, replacing it with `<PERSON_1>` and garbling the prompt structure. Since this heading is generated by VPMA (not user content), it contains no PII and should not be subject to NER detection. Separating structural headings from the anonymization boundary is a clean architectural fix — it prevents false positive mangling without modifying the NER stoplist or weakening PII detection. The same principle applies to `### Section` sub-headings, which pass through anonymization but are less likely to be misclassified.

### D23: Apply Endpoint Returns `lpd_updated` Flag
**Date**: 2026-02-25 (Phase 1A, Task 25) | **Status**: Active

**Decision**: The `apply_suggestion_by_type` endpoint response now includes an `lpd_updated: bool` field indicating whether the return path successfully updated the LPD. The apply always succeeds (artifact is written) even if the LPD update fails or is skipped.

**Rationale**: The frontend needs to know if the LPD was updated to show appropriate feedback. Decoupling artifact write success from LPD update success means the core apply flow is never blocked by LPD issues. When no LPD exists (backward compatibility), `lpd_updated` is `false` and the behavior is identical to pre-return-path.

### D24: Template-Based Session Summaries (No Extra LLM Call)
**Date**: 2026-02-25 (Phase 1A, Task 25) | **Status**: Active

**Decision**: Session summaries for the LPD Recent Context section are generated using a template (counting suggestions by artifact type) rather than making an additional LLM call. Format: `"Extracted from meeting notes: 3 RAID Log, 2 Status Report."` for extract mode, `"Analyzed status update: 4 observation(s) generated."` for analyze mode.

**Rationale**: An extra LLM call per session would add latency and cost with minimal value — the structured output already tells us what happened. Template summaries are instant, deterministic, and contain the key information (mode, input type, counts per artifact type). More sophisticated summarization (extracting key themes from the LLM output) can be explored in Phase 2 if the template approach proves too sparse for context injection.

### D25: Dedup Strategy — Prompt-Level for Sync, Service-Level for Intake
**Date**: 2026-02-25 (Phase 1A, Task 28) | **Status**: Active

**Decision**: Dedup is handled at two levels depending on the feature:
- **Artifact Sync (extract, analyze, log_session)**: Dedup instructions are in the system prompts. The LLM is told to check the injected `## Project Context` block and not re-suggest items that already exist. This works because context is injected into every LLM call.
- **Intake**: Dedup is handled in the service layer (`generate_intake_draft`). The function compares extracted content against existing LPD sections and flags conflicts. The intake prompt does NOT receive project context because it processes files in isolation (per-file LLM calls).

**Rationale**: The intake flow is fundamentally different from sync — it processes historical files that may predate the LPD. Conflict detection at the service layer is more reliable than asking the LLM to compare documents across separate calls. For sync modes, the LLM sees the current project state in every call, so prompt-level dedup is natural and effective. The two approaches complement each other: prompt-level handles real-time context awareness, service-level handles batch import conflicts.

### D26: QA Framework — Pre-Commit Hooks, Architecture Tests, Security Scanning
**Date**: 2026-02-25 (Quality infrastructure) | **Status**: Active

**Decision**: Implemented a three-gate quality framework:
1. **Pre-commit hooks** (`.pre-commit-config.yaml`): ruff lint+format, bandit security scan, smoke tests, file hygiene checks. Blocks commits that fail any check.
2. **Architecture enforcement tests** (`test_architecture.py`): AST-based import analysis validates layer boundaries on every commit — API can't import database directly, business logic can't import LLM SDKs directly, models/prompts are pure.
3. **Security scanning** (bandit + pip-audit + npm audit): Static analysis for Python vulnerabilities, dependency CVE auditing for both stacks.

Full plan documented in `QA_PLAN.md`. Rules integrated into `CLAUDE.md`.

**Rationale**: The project had 407 passing tests and 96% coverage but zero automation enforcing it — no git hooks, no architecture guards, no security scanning. For a project handling PII (privacy proxy), security scanning is non-negotiable. Architecture tests permanently prevent the most common drift patterns (bypassing the abstract LLM client, importing database from API, adding service dependencies to models). Pre-commit hooks make these checks friction-free rather than relying on developer memory.

**Resolved tech debt**: The `database.py → crud` circular import was fixed by moving `ensure_default_project()` to the `main.py` lifespan startup hook. Architecture test now passes cleanly (xfail removed).

### D27: Three-Tab Navigation with Intake as Sub-Route
**Date**: 2026-02-25 (Phase 1A, Task 29) | **Status**: Active

**Decision**: The app now has three navigation tabs: "Artifact Sync" (/), "Project Doc" (/project), and "Settings" (/settings). The Intake page (/intake) is NOT a tab — it's accessible from the Project Doc page via "Import Files" link. This follows Architecture Insights Pattern 3 (nav vs. session separation): the top-level nav represents persistent views (sync workflow, project knowledge, settings), while intake is a one-time action that flows back to the Project Doc page on completion.

**Rationale**: Adding intake as a fourth top-level tab would clutter navigation with a feature used infrequently (primarily during project setup or when importing new documents). Making it a sub-route of the Project Doc page groups related functionality — the Project Doc shows current LPD state, and intake is how you populate it. After applying intake, the user is navigated back to /project to see the results.

### D28: Doc-Freshness Pre-Commit Hook
**Date**: 2026-02-25 (Quality infrastructure) | **Status**: Active

**Decision**: Added `scripts/check_doc_freshness.py` as a pre-commit hook that compares actual codebase counts (endpoints, tables, services, components, pages) against claims in `docs/EXECUTIVE_SUMMARY.md`. Warns on mismatch but never blocks the commit (`verbose: true`, exit 0). Complements CLAUDE.md Session Close Protocol step 5 (manual checklist for AI sessions).

**Rationale**: A documentation quality audit found that stats drifted within hours as parallel sessions added tests, components, and pages without updating docs. The CLAUDE.md session close protocol is a "soft process" — it instructs the AI but nothing enforces it. The pre-commit hook is a "hard check" that catches structural drift automatically. It skips test counts (would require running the test suite, too slow for a hook) — those remain the session close protocol's responsibility. Two-layer approach: automated hook catches structural changes, AI protocol catches everything else.

### D31: Meeting Intelligence Strategy — PM Intelligence Layer, Not Transcription Tool
**Date**: 2026-02-26 (brainstorm session) | **Status**: Active

**Decision**: VPMA will accept transcripts from any source (file drop, paste, API) and transform them into PM-specific artifacts with persistent project context. VPMA will NOT compete on transcription, recording, or meeting capture. Phased approach: (1) File watcher + VTT parser in Phase 1B, (2) Zoom personal API in Phase 2-3, (3) evaluate Zoom Marketplace or local Whisper STT in Phase 3-4 based on demand. Multi-project routing uses a cascade architecture: explicit folder → filename pattern → LLM classification using LPD context → manual assignment.

**Rationale**: The transcription market is won (Otter $100M ARR, Fathom 90x growth, Granola $250M valuation) and being commoditized by platform giants (Microsoft Copilot, Google Gemini, Zoom AI Companion). However, no existing tool converts transcripts into structured PM artifacts (RAID logs, status reports, decision logs) with persistent project context — the gap is the last mile, not the pipeline. VPMA's LPD serves double duty: it's both the destination for transcript intelligence and the router for multi-project classification (no competitor has this). Privacy backlash against meeting bots (Otter class action Aug 2025, Fireflies BIPA lawsuit Dec 2025, university bans) makes a bot-free, local-processing approach a genuine differentiator. See `docs/MEETING_INTELLIGENCE_ANALYSIS.md` for full market analysis.

**Connects to**: D14 (Phase 1A/1B split), D15 (LPD foundation), D17 (LPD as separate system), Architecture Insights Pattern 7 (cross-tool orchestration)

### D30: Two-Persona Evaluation System (Not Eight)
**Date**: 2026-02-26 (Process decision) | **Status**: Active

**Decision**: Established a two-persona evaluation system for pressure-testing VPMA during development. Active now: (1) **Skeptical PM** — invoked at phase boundaries to gut-check whether features solve real PM problems, (2) **First Outside User** — invoked when evaluating market readiness to catch curse-of-knowledge gaps. Three additional personas (Solution Architect, Product Owner, First Enterprise Buyer) are deferred to specific future phases. Four personas (Sales, Marketing, Stakeholders, Sponsors) were explicitly rejected as premature.

**Rationale**: Eight simulated personas reviewing every milestone would be a productivity trap for a solo developer building for themselves first. Most feedback wouldn't be actionable. The two active personas target the highest-signal moments: phase boundaries (are we building the right thing?) and market readiness (can someone else actually use this?). Deferred personas are tied to concrete triggers (multi-user architecture, market fit evaluation, B2B consideration) rather than arbitrary timelines. The rejected personas optimize for concerns (sales positioning, marketing messaging, stakeholder reporting, budget alignment) that don't exist yet.

**Storage**: Persona definitions in `docs/personas/`, trigger rules in `CLAUDE.md`, expansion roadmap in `TASKS.md`.

**Connects to**: D14 (phase structure), D15 (hybrid workflow), Architecture Insights Pattern 3 (nav vs. session separation — personas follow the same principle: right tool at the right time)

### D32: Defer Model Cost/Benefit Analysis to Phase 2 Kickoff
**Date**: 2026-02-26 (Strategic planning) | **Status**: Active

**Decision**: Do not evaluate specific LLM models for cost/benefit or implement local LLM support until Phase 2 kickoff. The current abstract LLM client architecture (D1) is sufficient — no premature optimization or architectural changes needed. At Phase 2 kickoff, evaluate specific local models against real usage patterns from Phase 1A, not hypothetical workloads.

**Phase 2 design questions to resolve at that time**:
1. **Task-type routing**: Route routine artifact sync → local LLM, deep strategy → Claude. The abstract client supports this; it's a routing decision in the service layer, not an architecture change.
2. **Privacy Proxy bypass for local**: When running Ollama, anonymization is optional (data never leaves the machine). Decide whether to skip Privacy Proxy or still apply it for consistency.
3. **Provider-aware token budgets**: Local models often have smaller effective context windows. The token budget strategy (D21) may need a provider-aware mode where local models get compressed context injection.
4. **Hybrid/cascade pattern** (Phase 3+ consideration): Start with local, escalate to API if confidence is low. Don't design for this now, but the abstract client doesn't block it.

**Rationale**: Local model capabilities change rapidly — evaluations done now would be stale by Phase 2. Phase 1A's context injection and LPD work will reveal which LLM calls are "routine" (good Ollama candidates) vs. "deep reasoning" (need Claude/Gemini). The token budget work (D21) will inform which local models can handle VPMA's prompt sizes. Benchmarking real prompts against local models produces better decisions than hypothetical analysis.

**Connects to**: D1 (abstract LLM client), D21 (token estimation), D14 (phase structure)

### D29: Markdown Cache Sync After Session Summary
**Date**: 2026-02-25 (Phase 1A, Task 30 code review) | **Status**: Active

**Decision**: Added `_sync_markdown_from_db()` call to `_rebuild_recent_context()` in `lpd_manager.py`. Previously, session summary logging updated the DB but left the LPD Markdown cache file stale until the next explicit section update.

**Rationale**: Code review during Task 30 found that `_rebuild_recent_context()` updated the "Recent Context" section via the CRUD layer directly (`update_lpd_section_content`), bypassing the markdown sync. This meant the cached LPD file at `data/artifacts/{project_id}_lpd.md` was stale after every sync session. Since D15 established that Claude Code reads the LPD file for deep conversations during the hybrid workflow, a stale file breaks the workflow. The fix adds one `_sync_markdown_from_db()` call, which is cheap (~1ms) and ensures the file is always current.

### D33: LPD Content Quality Gate — Pre-Write Semantic Dedup
**Date**: 2026-02-26 (Phase 1A, E2E testing) | **Status**: Active

**Decision**: Added a pre-write content quality gate to the Log Session write path. Before auto-applying LPD updates, the system makes one batched LLM call comparing proposed content against existing section content, classifying each update as `new`, `duplicate`, `update`, or `contradiction`. Action rules: `new`/`update` → auto-apply; `duplicate` → skip (gray note in UI); `contradiction` → don't apply, show amber warning with "Apply Anyway" button. Graceful degradation: if the gate LLM call fails, all updates fall through as `new` (preserving previous behavior).

**Rationale**: E2E testing revealed that logging the same session twice produces duplicate LPD entries, and logging a session that reverses a prior decision creates contradictions with no warning. Existing dedup (prompt instructions, exact substring match in return path, intake conflict detection) was insufficient — prompt-based dedup is best-effort and substring matching doesn't catch semantic equivalence. An LLM-based semantic comparison catches "Chose PostgreSQL" vs "Database decision: PostgreSQL" as duplicates and "Switched to MySQL" vs "Chose PostgreSQL" as contradictions. Scoped to Log Session only (highest risk — auto-applies without user approval); other write paths can reuse the module later. One additional LLM call per session (~30-50% more cost per log session invocation).

**Key files**: `content_gate.py` (new service), `lpd_prompts.py` (CONTENT_GATE_SYSTEM_PROMPT), `artifact_sync.py` (integration), `LogSessionCard.jsx` (grouped display)

**E2E observation (2026-03-01)**: Live testing confirmed two-layer dedup behavior. Layer 1 (upstream): the Log Session prompt sees existing LPD context and avoids extracting duplicates at all — zero LPD updates returned. Layer 2 (downstream): content gate classifies any that slip through. In practice, Layer 1 handles exact repeats effectively; Layer 2 is the safety net for paraphrased or ambiguous duplicates. This is the ideal outcome — cheaper (no classification call when zero updates) and cleaner UX (no gray "skipped" noise). Acceptance criterion updated: "no duplicate LPD updates applied" rather than specifically requiring the gray skipped UI.

**Connects to**: D15 (LPD foundation), D17 (LPD as separate system), Architecture Insights Pattern 1 (return path)

### D34: Log Session Scope — Processed Outcomes, Not Raw Transcripts
**Date**: 2026-02-26 (Phase 1A) | **Status**: Active

**Decision**: Log Session stays scoped to processed/distilled input for Phase 1A. The intended workflow is: user has a deep session (Claude conversation, meeting, etc.), distills the key outcomes, and pastes the clean version into Log mode. Raw transcript ingestion (parsing full back-and-forth conversations) is deferred to a later phase.

**Rationale**: Raw transcript parsing is a meaningfully harder problem — handling exploratory tangents, rejected ideas, and conversational noise risks producing garbage LPD updates, which is worse than no updates. The current architecture creates no debt: adding a pre-processing step for transcripts later would slot in before the existing extraction pipeline without changes to the content gate, LPD auto-apply, or session summary machinery. The known risk is "write-up tax" friction — if manual summarization causes users to skip logging, the LPD goes stale. Mitigation: track skip rate during real usage; if friction is confirmed, that signals transcript handling should move up in priority.

**Connects to**: D15 (hybrid workflow bridge), D33 (content gate handles quality regardless of input polish)

### D36: Progressive Dual-Tool Architecture — Structured UI + Freeform Analysis
**Date**: 2026-02-27 (Backlog review session) | **Status**: Active

**Decision**: VPMA will evolve into a dual-mode tool: (1) the existing structured React UI for repeatable PM workflows (artifact sync, LPD, intake, settings), and (2) an embedded chat/analysis panel for freeform exploratory work (cross-document synthesis, ad hoc questions, brain dump triage). Progressive rollout: chat panel first (Phase 2-3), standalone CLI extraction later if validated.

**Architectural implication**: The backend needs a conversational API endpoint — session-aware, multi-turn interactions with LPD context injection. This API shape should be planned early (Phase 2 API design) even if the UI comes in Phase 3. Both interfaces share the same data layer (LPD, artifacts, privacy proxy).

**Rationale**: PMs do two fundamentally different types of work — structured (status updates, meeting prep, risk reviews) and exploratory (strategy analysis, cross-project synthesis, troubleshooting). The current roadmap is almost entirely structured-mode features. Backlog items V26 (NL query), V28/V33 (brain dump), V37 (cross-doc extraction), V23 (team chat), V25 (narrative output), V20 (adaptive model) all point toward exploratory-mode needs. The embedded panel is lower-friction to build (reuses React app and existing API), validates the concept, and doesn't require a whole new client. CLI extraction can happen later as an incremental feature.

**Connects to**: D15 (hybrid workflow — this is the path to retiring the Claude Code dependency), D14 (phase structure), VPMA_BACKLOG V23, V25, V26, V28, V33, V37

### D37: Backlog Consumption Protocol — Per-Phase Boundary Review
**Date**: 2026-02-27 (Backlog review session) | **Status**: Active

**Decision**: Run a structured backlog consumption review at every VPMA phase boundary (before starting a new phase). 5-step process: Harvest → Map → Score → Decide → Update. Scored on validation strength, roadmap fit, and differentiation (1-3 each). Dispositions: promote (7-9), slot (4-6), park (1-3), or merge. Added as Rule 17 to Process Playbook.

**Rationale**: VPMA_BACKLOG.md had 39 items captured from real PM work but zero consumption process (V39). Phase boundaries are natural planning moments — the review feeds directly into scope decisions for the upcoming phase. This session was the first instance of the protocol.

**Connects to**: VPMA_BACKLOG V39, Process Playbook Rule 17

### D35: Per-Session Artifact Type Toggle — Deferred
**Date**: 2026-02-27 (Phase 1A) | **Status**: Deferred to Phase 2+

**Decision**: Considered adding a toggle that lets users select which artifact types (RAID, Status Report, Meeting Notes) to generate suggestions for in a given session. Decided to defer — the feature doesn't earn its UI weight at 3 artifact types.

**Rationale**: The current design already handles this passively: suggestions are non-committal and can be dismissed with one click. The cost of dismissing 2-3 unwanted cards per session is lower than the cost of managing a toggle every session. More importantly, pre-filtering removes serendipity — the core value of Artifact Sync is that a messy input can surface relevant updates across artifacts the user didn't explicitly target (e.g., a standup note revealing a RAID item). If unwanted suggestions are noisy, the higher-leverage fix is better prompting, not a UI control.

**When to revisit**: (1) When artifact types grow beyond 3-4, dismissal cost rises and filtering becomes genuinely valuable. (2) If workflow presets emerge as a pattern (e.g., "Standup mode" = Status only, "Risk review mode" = RAID only) — bundling the toggle with other context like prompt tuning would earn its complexity. (3) If smart defaults become feasible (system learns session patterns and auto-prioritizes artifact types).

**Connects to**: D14 (phase structure), future artifact type expansion

### D38: Phase 1B UI/UX Improvements — Rename + Result Persistence
**Date**: 2026-03-01 (Phase 1A E2E testing) | **Status**: Deferred to Phase 1B

**Decision**: Two UX issues identified during E2E testing, deferred to Phase 1B:
1. **Rename "Project Hub" → "Project Knowledge Base"** — the subtitle already says "knowledge base"; "Hub" implies a dashboard/launcher which doesn't match the page's actual function (section-based KB viewer/editor).
2. **Result persistence across tab navigation** — Extract/Analyze/Log Session results vanish when switching tabs (stored in component state only). Recommended approach: localStorage with TTL as minimum viable fix; backend session table for durable history in Phase 2.

**Rationale**: Both are real UX issues but neither blocks Phase 1A cutover validation. The rename is trivial (2 lines); result persistence needs design thought (what to restore, TTL policy, clear triggers).

### D39: Cross-Section LPD Reconciliation — Phase 2 Candidate
**Date**: 2026-03-01 (Phase 1A E2E testing) | **Status**: Deferred to Phase 2

**Decision**: The content gate (D33) compares proposed content against the *same* LPD section's existing content. It does not analyze cross-section impact — e.g., whether a new Decision contradicts an existing Risk, or whether an Action Item resolves an Open Question. This cross-section reconciliation would require comparing each update against the full LPD (all 7 sections), not just the target section.

**Rationale**: Cross-section analysis adds significant value for PM workflows (a decision often resolves a risk, an action item may close an open question). However, it requires a more sophisticated prompt and increases token usage substantially (full LPD context per comparison vs. single-section). The content gate (D33) already adds ~30-50% LLM cost per log session; cross-section would roughly double that again. Better to validate the single-section gate works well in daily use first, then expand scope.

**Connects to**: D33 (content gate), V17 (data provenance), Phase 2 LLM cost evaluation (D32)

### D40: Semantic Dedup Gap on Return Path (Apply Button)
**Date**: 2026-03-01 (Phase 1A E2E testing) | **Status**: Deferred to Phase 1B

**Decision**: E2E testing found a duplicate risk entry in the LPD — same risk written in two different formats (narrative vs. pipe-delimited table). The return path (`update_lpd_from_suggestion()`) only uses exact substring matching (`proposed_text in section.content`), which can't detect semantic equivalence across formatting differences. The content gate (D33) already solves this for Log Session mode but isn't wired into the return path.

**Fix (Phase 1B)**: Call `classify_lpd_updates()` from `update_lpd_from_suggestion()` before appending, reusing the existing `content_gate.py` module. This adds one LLM call per Apply click that targets an LPD-mapped section (~5 of the artifact sections map to LPD). Cost is acceptable since Apply is user-initiated (not batched like Log Session).

**Connects to**: D33 (content gate), D39 (cross-section reconciliation)

### D41: localStorage for Result Persistence
**Date**: 2026-03-03 (Phase 1B planning) | **Status**: Active

**Decision**: Use localStorage with "clear on new sync" semantics for persisting artifact sync results across tab navigation. Each mode (extract/analyze/log_session) gets independent storage. Results are cleared when the user submits new text, not on a time-based TTL.

**Rationale**: The Skeptical PM review flagged TTL-based expiration as a source of silent failures. "Clear on new sync" is deterministic — the user controls when results refresh. Backend session storage was considered but rejected as over-engineering for a single-user local app. No distributed concerns, no multi-device sync needed.

**Connects to**: D38 (Phase 1B UI/UX improvements)

### D42: Graceful Degradation for Semantic Dedup on Return Path
**Date**: 2026-03-03 (Phase 1B planning) | **Status**: Active

**Decision**: When extending the content gate to the Apply return path (D40), LLM failure falls back to exact substring matching. Apply never fails due to content gate issues. Contradictions are applied with a warning log (user explicitly clicked Apply, so honor their intent).

**Rationale**: Matches the D33 pattern — the content gate on Log Session also degrades gracefully when LLM is unavailable. The Apply button is a user-initiated action; blocking it on a transient LLM failure would be a worse UX than allowing a potential duplicate.

**Connects to**: D33 (content gate), D40 (semantic dedup gap)

### D43: Transcript Watcher as Background Asyncio Task
**Date**: 2026-03-03 (Phase 1B planning) | **Status**: Active

**Decision**: The transcript file watcher runs as a background asyncio task inside the FastAPI process, not as a separate daemon or subprocess.

**Rationale**: Simpler deployment (one process to manage), simpler lifecycle (start/stop via API), and the watcher is I/O-bound (file system events) not CPU-bound, so sharing the event loop is appropriate. The `watchdog` library supports asyncio integration. If VPMA ever moves to multi-worker deployment, this would need revisiting.

**Connects to**: D31 (meeting intelligence strategy)

### D44: VTT Parser as Separate Module from Transcript Watcher
**Date**: 2026-03-03 (Phase 1B planning) | **Status**: Active

**Decision**: The VTT/SRT parser is a separate pure-function module (`vtt_parser.py`) from the file watcher service (`transcript_watcher.py`).

**Rationale**: Clean separation of concerns. The parser is a pure function (text in, text out) that can be tested independently with static fixtures. The watcher handles lifecycle, file detection, debouncing, and orchestration. This makes the parser reusable — the manual "process transcript file" endpoint uses the parser without the watcher.

**Connects to**: D31 (meeting intelligence strategy), D43 (watcher architecture)
