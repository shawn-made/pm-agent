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

## 2026-02-20 — Strategic Questions for Phase 1+ Planning

*Source: Personal Assistant brain dump (2026-02-20). These questions should be addressed in the next VPMA planning session.*

### Q8: Which of the three use cases is the primary target?
- **Options**: PM Interface Layer, Full Comms Platform, or Outsourcing-Only
- **Why it matters**: Determines scope, architecture complexity, and go-to-market strategy
- **Source**: Personal Assistant brain dump (2026-02-20)
- **Status**: Open — substantially explored in Session 4 brainstorm, not finalized

#### Session 4 Brainstorm Evolution (2026-02-23)
The original A/B/C framing evolved through iterative discussion and pressure testing:

1. **Reframe 1**: A (PM Interface Layer) and B (Full Comms Platform) are product choices. C (Outsourcing/Consulting) is a *business model* on top of either A or B — not a separate product. The "fully autonomous AI PM" is a stretch goal, not a near-term target.
2. **Reframe 2**: B removes integration complexity rather than adding it ("integration paradox" — replacing tools is simpler than connecting to them all).
3. **Reframe 3**: Evolved past A/B entirely into a **"project intelligence layer / plugin model"** — not replacing Slack, Zoom, or email, but sitting alongside them. A plugin or agent that connects to the project KB from within existing tools.
4. **Key principle**: "I need to take advantage of a more simple model that may be enabled by AI. We don't need all the jargon and endless views/interfaces for project data."
5. **What NOT to build**: Don't replace Slack, Zoom, or email. Don't try to beat incumbents adding AI on top of existing tools.
6. **What TO build**: Clean, easy plugin that connects people to project intelligence — maps questions to the right people, surfaces context, reduces the friction of "I don't know who to ask or what docs to look at."
7. **Progression model**: Personal tool → expert PMs on proprietary tool → tool integrates into orgs by itself over time.
8. **Decision**: Not finalized. User wants to log ideas, check in over time, and set overall course. More building and testing needed before committing. See Session 4 Brainstorm Summary below.

### Q9: Value proposition summary across use cases
- What's the concise value prop for each of the three use cases?
- **Source**: Personal Assistant brain dump (2026-02-20)
- **Status**: Substantially answered — Session 4 brainstorm (2026-02-23)

#### Articulated Value Props (Session 4)

**Use Case A — PM Interface Layer:**
- *For the PM*: Personal productivity multiplier. Paste unstructured input → get structured PM artifacts. Privacy-first, local-first. Sits between PM and existing tools.
- *Value*: "Your PM brain, externalized and accelerated."

**Use Case B — Full Comms/Project Platform:**
- *For the team*: Replace the fragmented stack (SharePoint + Slack + email + dashboards). One app where anyone can chat with each other and agents. Team members give unstructured input; agents structure it for the PM team.
- *Value*: "No more Jira jargon. No confusion about when to Slack vs email. Just talk."
- *Additional*: Opens the project to more stakeholders — they can ask questions and give feedback without friction. PM agent interprets and reduces misunderstanding friction.
- *Integration paradox*: Sounds bigger than A but actually reduces tech complexity by replacing tools rather than building connectors.

**Use Case C — Outsourcing/Consulting Enabler:**
- *For the client org*: Human PM still at center, but the tool enables rapid integration and high efficiency. PMs work on proprietary tool → deploy into client orgs quickly.
- *Value*: "Expert PM, day one."
- *Note*: Business model on top of A or B, not a separate product. Fully autonomous AI PM is a stretch goal.

**Core Pain Point (applies to all):**
> "People don't know who to go to or what docs to reference." A clean, easy plugin that maps things wherever possible, encourages interaction with stakeholders/team members who may be sitting on questions or feedback.

**Evolved Framing:**
The strongest value prop may be the *plugin model* — a project intelligence layer that sits alongside existing tools and gives anyone quick access to project/portfolio context, history, and the right people. Not replacing tools. Augmenting them.

### Q10: Competitive analysis — who's doing this already?
- Survey existing PM tools, AI-assisted PM platforms, and adjacent products
- **Source**: Personal Assistant brain dump (2026-02-20)
- **Status**: Substantially answered — Session 4 brainstorm (2026-02-23)

#### Competitive Landscape (Session 4 Research)

**Category A — AI add-ons to existing PM tools:** Atlassian Rovo, Microsoft Copilot+Planner, Wrike AI, Reclaim AI, Forecast, Teamwork.com

**Category B — Unified workspaces with AI:** ClickUp, Monday.com, Notion 3.0, Edworking, BridgeApp

**Hybrid approaches:** Asana Intelligence, Taskade, Dart

**Privacy/Local-first:** AppFlowy (open-source, local AI), BridgeApp (on-prem)

**Cautionary tale:** Height shut down Sept 2025 after $18.3M funding — attempted autonomous PM agent, couldn't sustain it.

#### Five Strategic Findings
1. **Nobody doing "unstructured team input → structured PM artifacts" well.** Tools accept structured input (Jira tickets, forms) or do simple NL→task conversion. The full pipeline of unstructured brain dump → categorized, prioritized, routed PM artifacts is an open lane.
2. **Stakeholder access point is real and underserved.** Most tools are PM-facing. Few make it easy for non-PM stakeholders to interact with project data naturally.
3. **Privacy gap is wide open.** Only AppFlowy and BridgeApp address data sovereignty. Enterprise PMs with sensitive data have almost no local-first AI options.
4. **Pricing complexity is a competitive vulnerability.** Per-seat pricing at $7-30/user creates friction for org-wide adoption. Simpler models could win.
5. **NL input is table stakes; what happens AFTER input is the differentiator.** Everyone claims "just type naturally." The value is in routing, structuring, cross-referencing, and surfacing patterns — not in accepting text.

### Q11: Adjacent markets not yet considered
- Beyond PM tooling — what other markets could VPMA serve?
- **Source**: Personal Assistant brain dump (2026-02-20)
- **Status**: Open — progression model added from Session 4

#### Progression Model (Session 4 Brainstorm)
User articulated a go-to-market progression:
1. **Personal tool** — keep using/building the engine, structure, app, AI agent model
2. **Expert PMs on proprietary tool** — build it out to where expert PMs work on this tool and can be deployed into client orgs
3. **Org integration** — tool becomes something integrated by itself into organizations

This progression naturally serves adjacent markets at each stage: personal productivity → consulting/services → enterprise SaaS.

### Q12: Architecture for local LLM integration
- How should Ollama/local models integrate at the architecture level? Phase 2 PRD covers the UI toggle, but what are the backend implications for context management, model switching, and quality tradeoffs?
- **Status**: Open

### Q13: Web app authentication approach
- Google SSO? Other options? What's the simplest path for a hosted version?
- **Status**: Open

### Q14: Token/time/effort estimates for MVP and later phases
- Rough estimates for Phase 1+ development effort, token costs at scale, and timeline
- **Status**: Open

### Q15: Can Ralph accelerate any of this?
- Evaluate whether Ralph (or other tools/resources) could speed up development
- **Status**: Open

### Q16: PM Agent deployability and tech stack complexity
- During next PM Agent review: evaluate how easy the tool is to hand off, maintain, or scale without heavy technical overhead
- Consider: deployment complexity, dependency footprint, documentation requirements for a non-developer to operate or extend
- **Source**: Personal Assistant brain dump (2026-02-22)
- **Status**: Open

### Q17: Should Personal Assistant and VPMA converge into one platform?
- **Context**: PA and VPMA share the same core pattern — markdown KB + LLM routing + domain expertise + brain dump + session handoff. PA has personal life domains; VPMA has PM work domains. Both use privacy-aware processing, staleness tracking, and cross-project routing.
- **Options**: (A) Keep them separate — PA as a personal tool, VPMA as a PM tool. (B) VPMA becomes a platform with "workspaces" — one for PM work, one for personal life. Same privacy proxy, brain dump engine, LPD concept. (C) PA stays markdown-only and feeds product insights to VPMA.
- **Why it matters**: If they converge, one codebase serves both. If they diverge, PA needs its own app architecture. Decision affects scope, timeline, and the "build PA into app" goal.
- **Source**: Personal Assistant Session 4 brainstorm (2026-02-23)
- **Status**: Open

---

## Session 4 Strategic Brainstorm Summary (2026-02-23)

*Captured for continuity. Read this section when resuming strategic brainstorming after more building/testing.*

### Vision Evolution
Started with three use cases (A: PM Interface Layer, B: Full Comms Platform, C: Outsourcing). Through pressure testing and iterative discussion, the framing evolved:

1. **A vs B is the product decision. C is the business model decision.** Don't conflate them.
2. **The "integration paradox"**: B (replacing tools) actually reduces tech complexity compared to A (connecting to many tools). Counter-intuitive but significant.
3. **Neither A nor B landed as the final answer.** Instead, the concept evolved into a **"project intelligence layer / plugin model"** — not replacing existing comms tools, but sitting alongside them. A plugin or agent that connects to the project KB from within Slack, email, etc.
4. **Core insight**: "I need to take advantage of a more simple model that may be enabled by AI. We don't need all the jargon and endless views/interfaces for project data."
5. **What NOT to build**: Don't replace Slack, Zoom, or email. Don't try to beat incumbents adding AI on top of existing tools.
6. **What TO build**: Clean, easy plugin that connects people to project intelligence — maps questions to the right people, surfaces context, reduces the friction of "I don't know who to ask or what docs to look at."

### Pressure Testing (10 Questions Raised and How They Were Addressed)

**On Use Case B (Full Platform):**
1. **Height died doing less** — AI PM agent startup, $18.3M funding, shut down Sept 2025. Building a full platform is high-risk. → *Plugin model sidesteps this — not building a full platform.*
2. **Cold-start adoption problem** — whole team must switch for B to work. → *Plugin model = nobody switches tools, just add a plugin. Lowest adoption friction.*
3. **ClickUp charges $7/seat with years of features** — hard to compete head-on. → *Not competing on features. Competing on simplicity and privacy. Different value prop.*
4. **Building comms is building infrastructure** (message delivery, search, notifications, permissions) — not PM work. → *Plugin model = don't build comms infrastructure. Augment existing comms.*
5. **NLP parsing of unstructured input is genuinely hard at scale** — misrouted items erode trust. → *Start with PM-only usage where misroutes are low-risk. Expand as quality improves.*

**On Use Case A (PM Interface Layer):**
6. **Most crowded AI lane** — every PM tool adding AI copilots. → *Differentiate on privacy-first, local-first, unstructured→structured pipeline (nobody does this well).*
7. **Hard to prove value before purchase** — demo-ability problem. → *Brain dump experience IS the demo (VP9). Let people try it.*
8. **Integration maintenance tax** — APIs break, each connector is ongoing work. → *Plugin model reduces this — fewer integrations needed if you're a layer, not a hub.*

**On Both:**
9. **PM building a dev product — do you have the technical capacity?** → *Claude Code does ~80% of implementation. User provides direction, review, and decisions. 15min define → 30-60min Claude implements → 15-30min review. Validated in Phase 0 (6,135 lines built).*
10. **Timing — are you building when you should still be using?** → *PM Sandbox has likely hit major pattern plateau. PM Agent is 95% Phase 0 complete. The next learning comes from USING the app against real data, not more markdown KB sessions.*

### Codebase Readiness (for context)
- PM Agent: 95% Phase 0 complete (19/20 tasks), 6,135 lines of working code
- Full pipeline works: paste text → anonymize → LLM → suggestions → apply
- Only Task 19 (live evaluation with real API key) remains
- Architecture: FastAPI + React + SQLite + abstract LLM client (Claude/Gemini) + 3-layer privacy proxy
- 40-hour roadmap: Week 1 (live eval + fix), Week 2 (multi-project), Week 3 (brain dump tab), Week 4 (polish + history)

### What to Do Next
1. Get an API key (Gemini free tier is fastest path)
2. Complete Task 19 — run PM Agent against real PM Sandbox data (= V32, PM Sandbox as live test harness)
3. Use the app for real PM work before brainstorming further
4. Resume strategic questions (Q8, Q11, Q17) after building/testing experience informs them

### User Note
> "I don't expect to make final decisions today but do like to work through all of this to log my ideas, check in on them over time, and set my overall course."

---

## Process Notes

- **Check QUESTIONS_LOG.md at key development milestones** — review backlog ideas when starting new phases or features, and log new questions as they arise during development.
