# VPMA Development Questions Log

Track questions, answers, and lessons learned throughout development.

---

## 2026-02-14 — Pre-Development Questions (Before Tasks 18-20)

### Q1: How do I get the API keys I need? (Accounts & costs)
- **Claude**: Sign up at console.anthropic.com → API Keys → Create. Pay-as-you-go, ~$3-15/M tokens. Expect $1-5/month for personal PM use.
- **Gemini**: Sign up at aistudio.google.com → Create API Key. ~50% cheaper than Claude, generous free tier. Expect $0-5/month.
- **Both accounts are free to create.** Store keys in `.env` as `ANTHROPIC_API_KEY` and `GOOGLE_AI_API_KEY`.

### Q2: Does my plan include choosing/loading different local LLMs?
- **Yes, in Phase 2.** Ollama integration with auto-detection of installed models, dropdown selector in Settings. Recommended: llama3.1:8b for daily syncs (free, ~5GB RAM, 40-60 tok/s on M4 MacBook Air).
- Phase 0 has the abstract `LLMClient` factory already scaffolded (Task 6) to support this.

### Q3: Does my plan support system-agnostic architecture?
- **Mostly yes.** Phase 0-3 is browser-based (localhost), works on macOS/Windows/Linux. SQLite + ~/VPMA/ uses platform-agnostic paths.
- **Gaps**: Electron wrapper (Phase 4) needs OS-specific features (Keychain vs. Credential Manager). No cloud/hosted deployment path — designed as local tool. Multi-user hosted service would need auth + Postgres (Phase 4+ effort).

### Q4: Did I include an LLM toggle?
- **Yes.** Phase 0: Claude/Gemini radio buttons in Settings (Task 16, built). Phase 2: "Triple-Brain Toggle" adds Ollama with model dropdown. Abstract client factory makes switching seamless.

### Q5: Can I log questions for process improvement?
- **This file!** Created `QUESTIONS_LOG.md` to track questions, answers, and lessons learned.

### Q6: Backlog items for consideration
- **Dashboard view**: PRD has partial coverage — Status Report artifact generates executive summaries, and Phase 2+ mentions exportable KPI/health data. But a dedicated visual "project dashboard" tab is not explicitly in scope. Added to backlog below.
- **Narrative-first output flow**: Currently the flow is artifact-centric (text → artifact suggestions). A "narrative contextual update → then suggest artifacts" flow would be a different UX paradigm. Added to backlog below.

---

## Backlog Ideas (From Questions)

### Idea: Project Dashboard View
- **Source**: Q6 (2026-02-14)
- **Concept**: A dashboard tab that intelligently summarizes project status from the most recent artifacts, sessions, and inputs.
- **What PRD covers**: Status Report artifact has executive summaries; Deep Strategy (Phase 2) has integration reports; KPI export mentioned.
- **What's missing**: A dedicated always-visible dashboard tab that aggregates across all artifact types and shows real-time project health.
- **Phase consideration**: Post-MVP (Phase 1 or 2). Requires multiple artifacts to exist before it adds value.

### Idea: Narrative-First Output (Context → Artifact Suggestions)
- **Source**: Q6 (2026-02-14)
- **Concept**: Instead of "paste text → artifact suggestions," offer a more natural narrative output that contextualizes the update for the PM first, THEN pops up artifact suggestions.
- **Example flow**: User pastes meeting notes → System generates a contextual narrative ("Here's what happened and what it means for your project...") → Then suggests specific artifact updates as secondary actions.
- **How it differs**: Current flow is artifact-centric. This would be PM-experience-centric.
- **Phase consideration**: Post-MVP. Could be an alternative "mode" or the default in Phase 1+.

### Idea: Living Project Document (LPD) — Master Project Knowledge Base
- **Source**: Q7 (2026-02-14)
- **Concept**: A continuously updated master Markdown file per project that VPMA builds and maintains from every input, conversation, and artifact update. The project's "single source of truth" — similar to how a PRD works, but auto-maintained.
- **Location**: `~/VPMA/projects/{project_id}/project.md`
- **What it enables**:
  - **Dashboards** become trivial — just render/summarize sections of the LPD
  - **Artifact reconciliation** — the LPD is canonical state; artifacts are *views* into it
  - **Intelligent questions** — compare new input against LPD, spot gaps/contradictions ("You mentioned a new vendor but no risk entry exists — should we add one?")
  - **Context accumulation** — each input enriches the LPD, so VPMA understands *your specific project* better over time
  - **Narrative output** — summarizing the LPD is more natural than stitching disparate artifacts
- **How it differs from artifacts**: Artifacts (RAID Log, Status Report) are structured outputs for specific audiences. The LPD is the unstructured knowledge base that feeds them all. LPD = project's brain, Artifacts = reports it produces.
- **Open Questions section**: VPMA maintains "Open Questions" in the LPD and surfaces them proactively ("3 sessions ago you mentioned a budget concern but never resolved it — still open?"). Similar to a planning tool driving clarifying questions.
- **Update mechanism**: Incremental — each Artifact Sync session triggers an LLM prompt: "Given the existing project document and this new input, produce an updated project document."
- **Relationship to other backlog ideas**: This is foundational — Dashboard View and Narrative-First Output both become much easier if the LPD exists.
- **Phase consideration**: Could start simple in Phase 1 (append-only log), mature in Phase 2 (LLM-reconciled document with sections that emerge organically: stakeholders, timeline, risks, decisions, open questions, recent updates).

---

## Process Notes

- **Check QUESTIONS_LOG.md at key development milestones** — review backlog ideas when starting new phases or features, and log new questions as they arise during development.
