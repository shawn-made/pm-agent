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
- **Status**: Open — substantially explored in Session 4 brainstorm, further validated in Phase 1A planning session (2026-02-25). Path A decision (D15) aligns with Use Case A (PM Interface Layer) for Stage 1 with plugin model evolution. Not formally closed — revisit after using VPMA with LPD against real project data.

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
- **Status**: Open — Phase 1A planning (D14, D15) doesn't close this but does affect it: the LPD concept and API-first design constraint would support workspace-based convergence (Option B) if chosen later. The "Log Session" bridge pattern could apply to PA sessions too. Revisit after LPD is built and tested.

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

## 2026-02-25 — Phase 1A Strategic Planning Questions

*Source: Strategic planning session analyzing PM Sandbox → VPMA transition path. See DECISIONS.md D14, D15 for the decisions made.*

### Q18: In-flight project intake — how should VPMA parse existing markdown files?
- **Context**: Phase 1A includes bulk import of existing PM files (PM Sandbox markdown, meeting notes, etc.) to seed the LPD. This is a one-time per-project operation.
- **Open questions**:
  - What's the parsing strategy? One LLM call per file, or batch?
  - What entities to extract: stakeholders, risks, decisions, action items, open questions, timeline milestones?
  - How to handle contradictions across files (e.g., different status for the same risk)?
  - Does import create a draft LPD for human review, or does it auto-populate sections?
- **Phase consideration**: Phase 1A — needed for the developer's own PM Sandbox cutover and for any PM adopting VPMA mid-project.
- **Status**: **Resolved** — See D18. One LLM call per file, draft for human review, contradictions flagged not auto-resolved. Extracts all 6 entity types.

### Q19: LPD section structure — fixed or emergent?
- **Context**: The LPD (QUESTIONS_LOG Q7) needs internal sections. Two approaches:
  - **Fixed template**: Predefined sections (Stakeholders, Timeline, Risks, Decisions, Open Questions, Recent Updates) that always exist
  - **Emergent**: LLM organizes sections organically based on content, new sections appear as needed
- **Architecture Insights connection**: Pattern 3 suggests separating Project Map (stable) from Session Log (temporal). The LPD could embody the Project Map, with a separate session log file.
- **Open questions**:
  - How does context injection work? Section-level relevance scoring? Token budget allocation?
  - Does the LLM get the full LPD or just relevant sections per query?
  - What's the max practical LPD size before context window limits bite?
- **Phase consideration**: Phase 1A design decision — must be answered before building.
- **Status**: **Resolved** — See D16. Fixed template with 7 sections. Section-based DB storage (not single file) for granular staleness + selective context injection. Token budget: ~4000 tokens max (Project Map ~2500 + Recent Context ~1500). Full Project Map always sent; Recent Context fills remaining budget.

### Q20: PM Sandbox cutover checklist — when is it actually done?
- **Context**: D15 defines cutover at end of Phase 1A. But what specifically must be true?
- **Candidate criteria**:
  - [ ] LPD exists and accumulates context across sessions
  - [ ] In-flight project intake has imported existing PM Sandbox files
  - [ ] Context injection works (LLM calls receive relevant LPD context)
  - [ ] "Log Session" bridge works (paste Claude Code conclusions → updates LPD)
  - [ ] One full week of daily PM work done entirely through VPMA + Claude Code hybrid
  - [ ] No information loss compared to PM Sandbox workflow (spot-check against recent sessions)
- **Status**: **Resolved** — Formalized as Task 30 acceptance criteria in TASKS.md. All 6 candidate criteria adopted.

---

## Phase 1A Planning Session Summary (2026-02-25)

*Dense strategic session analyzing the PM Sandbox → VPMA transition path. Four rounds of analysis with pressure-testing at each stage.*

### What Was Decided
1. **Phase 1 reframe**: Split into 1A (Context Foundation: LPD, return path, intake, context injection) and 1B (Feature Expansion: current Phase 1 PRD features). See D14.
2. **Path A chosen**: Strict LPD foundation + Claude Code hybrid for deep conversations. Rejected Path B (brain dump mode in VPMA) as a half-measure. See D15.
3. **Design constraint locked in**: LPD must be API-first — future chat plugs in without rearchitecting.
4. **Cutover point**: End of Phase 1A, not end of chat implementation.

### Key Analysis Produced
- **Two gaps**: Context gap (VPMA doesn't know project state) vs. Interaction model gap (VPMA is paste-and-process, PM Sandbox is conversational). Phase 1A closes context. Future chat closes interaction.
- **PM Sandbox workflow decomposition**: 4 categories — brain dumps/triage (→ 1A), strategic exploration (→ Claude Code), document drafting (→ Phase 0), cross-artifact synthesis (→ LPD).
- **Market validation of Path A**: Height's $18.3M failure → foundation first. Progression model Stage 1 focus. Chat as incremental addition. No workflow should depend on Claude Code long-term.
- **"Log Session" concept**: Bridge mechanism for deep Claude Code conversations back to VPMA. Paste conclusions → LLM extracts and updates LPD + artifacts.

### What Was NOT Decided
- LPD section structure (Q19)
- In-flight intake parsing strategy (Q18)
- PM Sandbox cutover criteria (Q20)
- Context injection implementation (section relevance scoring, token budgets)
- Phase 1A task breakdown (deferred to next implementation session)

---

## 2026-03-04 — Pre-Market Strategic Questions

*Source: Strategy session analyzing distribution, open-source, and go-to-market. Skeptical PM reviewed all four topics — two got MAYBE, two got USE IT.*

### Q21: How will other people run this tool? (Distribution model)
- **Context**: PRD says local-only through Phase 3, web app in Phase 4 (months 10-13). But velocity is 4x ahead of plan, and "marketable" is ~3-4 weeks away. The gap: no distribution path exists between "clone repo + run terminal commands" and "full SaaS with auth."
- **Options analyzed**:
  - **A. Clone + run locally** — zero effort, developers only
  - **B. Docker one-liner** — small effort (~1-2 days), still requires Docker (technical users)
  - **C. Electron/Tauri desktop app** — medium effort (~4-6 weeks realistically), anyone can install, preserves privacy story
  - **D. Hosted web app** — large effort (~3-4 weeks), anyone with browser, but **undermines privacy differentiator**
  - **E. Hybrid (local + optional cloud)** — large effort, serves both audiences
- **Skeptical PM verdict: MAYBE.** Key pushback:
  - Docker is "developer brain" — target PMs don't have Docker installed
  - Electron "1-2 weeks" is wildly optimistic for solo dev (code signing, auto-updates, OS-specific bugs = 4-6 weeks)
  - Distribution format doesn't matter if nobody knows the tool exists
  - Better approach: walk first 5-10 users through setup personally (screenshare). Their feedback tells you whether to package at all, and how.
  - If must pick: Mac-only `.app` via PyInstaller/py2app is cheapest path (skip Electron complexity)
- **Tension**: Privacy-first positioning favors local (Options A-C). Market reach favors web (Option D). Research market is more willing to install locally (they already run R/SPSS/NVivo).
- **Revisit trigger**: After 5 people have tried the tool (regardless of how they ran it). Their feedback determines the right packaging investment.
- **Status**: Open

### Q22: Should this go on GitHub? Public, private, or open-core?
- **Context**: Project has strong portfolio value (866 tests, 13 services, clean architecture, 46 documented decisions). Also has competitive value (prompt templates, market strategy, privacy implementation).
- **Options analyzed**:
  - **Full open source** — maximum portfolio exposure, minimum competitive moat
  - **Open-core** — public engine + private prompts/templates. Shows capability, protects secret sauce. Creates maintenance burden (two repos or careful .gitignore).
  - **Private repo, public demos** — protects everything, less verifiable to employers
  - **Delayed open source** — ship commercially first, open source later for marketing
- **Skeptical PM verdict: MAYBE.** Key pushback:
  - Open-core is a business model for companies with users. Zero external users = zero fork risk. Could publish everything and risk is near-zero because nobody's watching yet.
  - Open-core creates real maintenance overhead for one person (two configs, build scripts, CI for both).
  - "Shows capability to recruiters" is a different goal than "builds a business." Pick one — the answer changes everything.
  - If portfolio: publish it all, write great README, make demo video. If product: keep private, focus on users, open-source later as marketing play.
  - Moat is execution speed and domain expertise, not code secrecy. By the time someone clones and understands, you're two phases ahead.
- **Depends on Q23** (portfolio vs product intent).
- **Revisit trigger**: When Q23 is answered, or when preparing to share with first external users.
- **Status**: Open

### Q23: Is this a portfolio piece or a product? (Intent question)
- **Context**: The answer to this shapes distribution (Q21), open-source (Q22), and where to invest time. Both goals are valid but pull in different directions.
  - **Portfolio**: Publish everything, optimize README and demo video, explain architecture decisions. Goal is demonstrating capability to employers/collaborators.
  - **Product**: Keep private, focus on user experience and onboarding, find 5 paying users. Goal is revenue or market validation.
  - **Both**: Possible but creates tension — portfolio wants maximum visibility, product wants competitive protection.
- **Skeptical PM guidance**: "Finish Phase 2A, use it on a real project for a week, then show it to 5 people. Their reactions will answer this better than any planning session."
- **No marketing plan needed yet** — Skeptical PM verdict: USE IT. Capture strategic thinking in QUESTIONS_LOG (here) and DECISIONS.md. Formal marketing plan earns its keep when there's something to market.
- **Revisit trigger**: After Phase 2A complete and 1-2 weeks of daily use on a real project. The experience of using it (and showing it to others) will clarify intent.
- **Status**: Open

### Q24: Suite Vision — Modular Architecture for PA/VPMA/WAT/Future Apps
- **Context**: Vision is emerging for a suite of apps sharing one back-end with multiple front-ends differentiated by role/purpose (Personal Assistant, VPMA, WAT, future apps). Key architectural questions to brainstorm and document:
  - **Shared entry point**: Anonymization layer (VPN?) + profile-based view generation — what the user sees is shaped by their profile
  - **Modular frontends**: Can VPMA front-end be a reusable shell where the artifact layer swaps out per use case? Each front-end modular and stackable.
  - **Shared core infrastructure**: VPN layer, local LLM (Ollama), Proton file sync
  - **Device syncing**: How to handle device syncing across the suite
  - **Local LLM complexity progression**: Web app + Ollama is recommended starting point — calls local when on network, falls back to API when remote, abstract LLM client handles switching (pattern already proven in VPMA). VPN layer unlocks mobile viability. Progression: web app + local LLM (medium) → VPN layer (medium) → mobile + local LLM via VPN (medium-high, mostly already solved by VPN layer)
  - **Claude Code guardrails**: Define how Claude Code sessions coexist with the suite without conflicts — keep VPMA light enough given cost, processing power, and Ollama limitations
  - **Cost and resource management as design constraint**: Which LLMs for which tasks, when to switch to local, when to compress, how to manage token costs across the suite
- **Open questions**:
  - Does the "reusable shell" approach create more complexity than separate lightweight frontends?
  - What's the minimum viable shared backend (auth, anonymization, LLM routing)?
  - How does the VPN layer interact with Proton file sync?
- **Depends on**: Q17 (PA/VPMA convergence), Q23 (portfolio vs product intent)
- **Phase consideration**: Post-Phase 2A. This is strategic architecture — brainstorm now, build later.
- **Revisit trigger**: When starting any new frontend or when VPN/mobile becomes a priority.
- **Status**: Open
- **Source**: PA Brain Dump #4 (2026-03-05)

---

## 2026-03-12 — Design Questions & Feature Ideas

### Q25: Should VPMA have configurable workflow profiles?
- **Context**: As features accumulate (digest, KB, transcript watcher, export, stakeholder outreach), not every PM will use every feature. Without configuration, unused features become noise — exactly what the tool is supposed to reduce. Example: a PM who only uses VPMA for analysis doesn't need digest notifications or RAID log artifacts cluttering the UI.
- **Observation**: This is a design principle, not a single feature. It should influence how every new feature is built going forward.
- **Connections**:
  - D46 (multi-market strategy): PM users vs. Research users want fundamentally different feature sets from the same engine. Already noted: "keep artifact types data-driven, prompt templates parameterized."
  - Session 4 core insight: "We don't need all the jargon and endless views/interfaces for project data."
  - Daily Digest idea: only valuable if the user opted into the signals it surfaces
  - Artifact types are already somewhat configurable (choose which to generate per sync)
- **Design spectrum**:
  - Too granular: 30 individual toggles in Settings = Settings bloat, nobody configures
  - Too coarse: 3 preset profiles = doesn't fit anyone
  - Sweet spot: Preset workflow profiles with per-feature overrides (e.g., "Start with Analysis workflow, enable digest, disable RAID log artifacts")
- **Possible profiles**: "Full PM" (all features), "Analysis Only" (LPD + artifact sync, no outreach/digest), "Research Mode" (transcripts + theme coding + LPD, no PM artifacts), custom
- **Implementation could be simple**: A settings object that gates which tabs/features are visible and which artifact types appear in dropdowns. No architectural change — just a filter layer.
- **Design rule going forward**: Every new feature should have an enable/disable path. Don't hardwire features as always-on.
- **Phase consideration**: Design the profile concept during Phase 2B or 3. But apply the principle now — any feature built from here on should be togglable.
- **Status**: Open — design principle to apply immediately, formal profiles deferred to Phase 2B/3

---

## 2026-03-12 — Feature Ideas (Brain Dump)

### Idea: HTML Viewer for Formatted Content
- **Source**: Brain dump (2026-03-12)
- **Concept**: Render markdown artifacts/results as formatted HTML for preview and for high-fidelity copy-paste into external tools (Google Docs, Word, email, etc.). Toggle on existing result cards or a dedicated preview mode.
- **Value**: Standalone preview of how artifacts look when formatted. More importantly, copying formatted HTML into external docs preserves headings, tables, bold, lists — raw markdown paste does not.
- **Alignment**: Strong. Extends Phase 2A export story. Skeptical PM flagged export as table-stakes gap. Low implementation cost (react-markdown or similar). Solves 80% of the "get content into other tools" problem at 5% of the cost of API integrations.
- **Phase consideration**: Phase 2B or early Phase 3. Small enough to bundle with other work.
- **Status**: Open — approved for backlog

### Idea: Google Docs/Sheets/Email/Calendar Integration
- **Source**: Brain dump (2026-03-12)
- **Concept**: Programmatically edit Google Docs/Sheets, compose emails, or create calendar events from VPMA output.
- **Value**: High convenience if it worked — skip manual paste step entirely.
- **Alignment**: Poor for current phase. Contradicts privacy-first positioning (data goes through Google APIs). Session 4 strategic direction: "Don't replace Slack, Zoom, or email." Integration maintenance tax identified as a risk. Requires OAuth2 + Google Workspace API — significant complexity for solo dev.
- **Mitigated by**: HTML Viewer idea (above) solves most of the same user need with much less effort and no privacy tradeoff.
- **Better framing**: If revisited, the plugin model (VPMA accessed FROM other tools) is the strategic direction, not VPMA writing TO other tools.
- **Phase consideration**: Phase 4+ at earliest, per PRD roadmap. Only if users request it.
- **Status**: Open — deferred, revisit at Phase 4 or with user demand

### Idea: Configurable Daily Digest
- **Source**: Brain dump (2026-03-12)
- **Concept**: A proactive daily brief surfacing the top 3-5 things a PM should address. Goal: lower cognitive load, not add clutter. "Morning standup with yourself."
- **What it could surface**: Stale LPD sections (staleness tracking already built), unresolved open questions, overdue action items, artifact gaps ("no status report in 2 weeks"), upcoming milestones.
- **Value**: Shifts VPMA from reactive (paste input → get output) to proactive (here's what needs your attention). Aligns with "elite partnership" PRD pillar and Architecture Insights Pattern 5 (weekly cadence).
- **Design challenge**: Signal-to-noise ratio. Must be 3-5 items max, ranked by urgency, dismissable. If it surfaces 15 things daily it becomes noise. Needs configurable thresholds (staleness days, priority filters).
- **Implementation progression**:
  - **v1 (low effort)**: Staleness alerts + open item counts — data already in DB, just a query + summary view
  - **v2 (medium effort)**: LLM-powered daily brief — reads LPD state, generates prioritized narrative
  - **v3 (higher effort)**: Schedule-aware — flag upcoming milestones, slipped dates (requires timeline data in LPD)
- **Prerequisite**: LPD must be well-populated from real use first. A digest over empty data is useless.
- **Phase consideration**: Phase 3. v1 could be earlier if LPD has enough data.
- **Status**: Open — approved for backlog, needs design pass before implementation

### Idea: Stakeholder Input Requests (Email/Slack Outreach)
- **Source**: Brain dump (2026-03-12)
- **Concept**: PM identifies an input need → VPMA drafts and sends an email/Slack message to a stakeholder → stakeholder responds via reply or simple web form → response queues for PM review/approval → approved input enters the knowledge base.
- **Value**: High. Session 4 competitive finding #2: "Stakeholder access point is real and underserved. Most tools are PM-facing." This opens the project to non-PM contributors without requiring them to learn VPMA.
- **Alignment**: Fits the "stakeholder access" strategic theme. The approval workflow concept is valuable independently — a "pending input queue" could serve multiple intake paths (email, form, future integrations).
- **Complexity**: High. Email requires SMTP/API (moves away from local-only). Response capture needs either email parsing (unreliable) or hosted web form (requires external endpoint, contradicts local-first). Slack needs OAuth + webhooks. Privacy proxy must work bidirectionally.
- **Most viable path**: Unique-link web form — stakeholder fills in simple form, responses queue for PM review. But requires hosting something externally (Phase 4 architectural shift).
- **Near-term alternative**: HTML Viewer (backlog idea above) + well-structured request templates. VPMA drafts the ask, PM sends manually, pastes response back. Cheaper, preserves local-first, and may be sufficient for Phase 2-3.
- **Phase consideration**: Phase 4+ (requires hosted component). Approval workflow pattern could be designed earlier as a general concept.
- **Status**: Open — deferred, revisit at Phase 4. Near-term: template-based manual approach.

---

## Process Notes

- **Check QUESTIONS_LOG.md at key development milestones** — review backlog ideas when starting new phases or features, and log new questions as they arise during development.
