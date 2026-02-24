# VPMA Architecture Insights — Patterns from Real PM Workflow

**Created**: 2026-02-18
**Source**: Observations from extended PM knowledge base sessions (7 sessions, 400K+ lines of source material)
**Constraint**: All patterns are project-agnostic. No project-specific details.

---

## Purpose

These are architectural patterns discovered by actually doing PM work with an LLM-assisted knowledge base system. They inform VPMA design decisions — not as theoretical requirements, but as validated needs from real workflow.

Each pattern describes: what was observed, why it matters for VPMA, and what it implies for the architecture.

---

## Pattern 1: The Core Loop Needs a Return Path

### What Was Observed
The productive PM workflow is a cycle: raw input (transcript, notes, screenshot) goes in, the LLM processes it, structured updates come out, and those updates get applied to a living knowledge base. The critical missing piece in a one-directional flow (input → suggestions → clipboard) is that **applied outputs need to feed back as system state**. Without the return path, the system forgets what it already knows — every session starts from zero.

### Why It Matters
VPMA's Phase 0 Artifact Sync is intentionally one-directional: paste text, get suggestions, copy to clipboard. That's fine for MVP validation. But the real value emerges when applied suggestions update the system's understanding of the project. The PM shouldn't have to re-explain project context every session.

### Architecture Implication
- VPMA needs a persistent project knowledge representation — not just individual artifacts, but a unified project state that accumulates over time
- The "Apply" action should update this state, not just write a markdown file
- Future LLM calls should receive relevant project context automatically, not require the PM to paste it
- **Connects to**: Living Project Document concept (QUESTIONS_LOG Q7), VPMA_BACKLOG V1 (paste-raw-input cycle), V14 (cross-artifact dependency cascade)

---

## Pattern 2: Staleness Detection as a First-Class Feature

### What Was Observed
PM artifacts go stale fast. A risk register from Monday may be inaccurate by Thursday. "Last modified" is insufficient — a file can be modified recently but still contain stale sections (e.g., updating one risk doesn't verify the other 12). What's needed is a separate concept: **"last verified accurate"** — distinguishing when content changed from when someone confirmed it's still correct.

In practice, a periodic "staleness sweep" (reading each artifact and confirming or updating it) was the most valuable maintenance activity. It caught 6 stale items in a single pass.

### Why It Matters
VPMA tracks artifact versions and timestamps, but doesn't have a concept of "verified freshness." As project knowledge accumulates, the system needs to know which parts are current vs. which parts might be stale — and surface that distinction to the PM.

### Architecture Implication
- Add a `verified_at` timestamp to artifact metadata, separate from `updated_at`
- Surface staleness signals in the UI: "This section hasn't been verified in X days" or "3 risks haven't been reviewed since last sprint"
- The staleness sweep itself is a VPMA workflow: present each artifact section, ask "still accurate?", bulk-update `verified_at` for confirmed items, flag items that need changes
- Consider section-level staleness, not just file-level — a 20-item risk register shouldn't show as "fresh" because one item was updated
- **Connects to**: New capability — not in current backlog. Closest: V15 (structured uncertainty tracking)

---

## Pattern 3: Navigation vs. Session Continuity Are Separate Concerns

### What Was Observed
A single index file was trying to serve two purposes: (1) "Where is everything in my project?" — a spatial map of all artifacts and their relationships, and (2) "What happened recently and what do I pick up next?" — temporal session history and handoff notes. These serve fundamentally different needs. The map is stable (changes when artifacts are added/removed). The session log grows every session. Combining them made the index increasingly bloated and hard to scan.

Splitting them — a lean navigation file and a separate session history file — immediately improved usability.

### Why It Matters
VPMA's UI already separates tabs (Artifact Sync, Settings), but the underlying data model should also separate project navigation (what exists, where it is, how it relates) from session continuity (what happened, what's pending, what to pick up).

### Architecture Implication
- Project state should have two distinct data structures:
  - **Project Map**: artifact inventory, relationships, current status of each — the "what exists" view
  - **Session Log**: chronological record of inputs, changes, decisions — the "what happened" view
- The LLM needs the Project Map for context in every session; it only needs recent Session Log entries for continuity
- This separation also helps with context window efficiency — load the full map (~stable size) plus only the last N sessions (~bounded) rather than an ever-growing combined blob
- **Connects to**: VPMA_BACKLOG V3 (session continuity overhead), V21 (context window scalability)

---

## Pattern 4: Action Items Need Routing AND Lifecycle

### What Was Observed
Action items aren't a flat to-do list. Every action item has two dimensions that matter:

**Routing** — where does this item actually live?
- PM's personal tracker (only the PM sees/tracks it)
- Team's ticket board (becomes a dev task)
- Governance/risk log (gets escalated to leadership)
- Existing ticket subtask (augments something already in flight)
- Internal-only note (tracked in PM's knowledge base, nowhere else)

**Lifecycle** — what's its current state?
- Open → In Progress → Blocked → Closed
- With blocking relationships: "A12 is blocked until A16 resolves"

Without both dimensions, action items pile up as an undifferentiated list where the PM can't distinguish "things I need to do" from "things I need to track that others are doing" from "things that should be tickets."

### Why It Matters
VPMA generates action items as part of artifact sync. But generating items without routing them creates a PM burden — now they have to manually figure out where each one goes. The routing decision is itself a PM skill that VPMA should support (suggest routing based on content, owner, and artifact type).

### Architecture Implication
- Action item model needs: `routing_destination` (enum: personal, team_board, governance, subtask, kb_only) and `lifecycle_state` (enum: open, in_progress, blocked, closed)
- Add `blocked_by` relationship between action items
- LLM prompts for action item extraction should include routing classification: "Based on the content and owner, where should this item be tracked?"
- UI should support drag-to-route or quick-tag routing, not just a flat list
- Export/sync adapters per routing destination (future: GitHub Issues, Smartsheets, etc.)
- **Connects to**: VPMA_BACKLOG V2 (action item categorization routing), V10 (GitHub sync), V11 (RAID log sync)

---

## Pattern 5: Weekly Is the Natural Planning Cadence

### What Was Observed
The PM's most productive planning unit is the week. Not the day (too granular — interrupts and meetings make daily plans unreliable), not the sprint (too abstract — two weeks of work needs to be broken into a weekly rhythm to be actionable). The natural workflow is:

- **Monday**: Plan the week — what meetings, what deliverables, what deadlines
- **Friday**: Review the week — what got done, what slipped, what carries over
- **Daily**: Quick check on today's items within the weekly frame

Weekly plans with day-by-day breakdowns and named deliverables were the most useful planning artifact produced. They became the PM's operating system for the week.

### Why It Matters
VPMA's Daily Planner tab (Phase 3) should actually be a **Weekly Planner** that generates daily views. The week is the atomic planning unit. Daily is a derived view.

### Architecture Implication
- Planning data model should be week-centric: `weekly_plan` with `daily_items[]` as children
- Weekly plan generation prompt: "Given current project state, meetings this week, and open action items, generate a week plan with daily breakdowns"
- End-of-week review prompt: "Given the weekly plan and what actually happened (session log), generate a weekly review: completed, slipped, carried forward"
- The weekly cadence also defines the natural staleness check interval — if something hasn't been touched in a week, flag it
- **Connects to**: VPMA_BACKLOG V12 (meeting prep generation). The weekly plan IS the meeting prep — each day's items include talking points for that day's meetings.

---

## Pattern 6: Same Data, Different Audiences

### What Was Observed
The same project information needs to appear in at least three different forms:

1. **PM Working View** — full context, raw observations, uncertainty flags, linked dependencies. This is messy and detailed because the PM needs all the nuance.
2. **Leadership/Governance View** — cleaned up, prioritized, action-oriented. Same risks, but framed for decision-makers. No uncertainty flags — just clear status and ask.
3. **Team View** — task-focused. What do I need to do? What's blocking me? No strategic context needed.

Maintaining these as separate documents creates drift. In practice, the PM writes the working view first, then manually rewrites for each audience. This is exactly the kind of "artifact tax" VPMA exists to eliminate.

### Why It Matters
VPMA should store information once (in the project knowledge base) and render it differently per audience. The LLM is perfectly suited for this — given raw project state, generate an executive summary, a team task list, or a governance report.

### Architecture Implication
- Artifact rendering should be audience-parameterized: `render(artifact, audience="executive")` vs `render(artifact, audience="team")`
- Audience profiles define: detail level, tone (formal vs. working), what to include/exclude, formatting conventions
- The PM's working view is the source of truth; audience views are derived
- This is a prompt engineering pattern, not a data model change — the same underlying data gets different system prompts
- Export formats should match audience expectations (governance wants formatted docs; team wants ticket-style lists)
- **Connects to**: VPMA_BACKLOG V16 (audience-aware views), V8 (stakeholder-facing interfaces)

---

## Pattern 7: Cross-Tool Orchestration, Not Replacement

### What Was Observed
The PM uses: GitHub Projects (dev tickets), RAID logs in shared spreadsheets (governance), a personal KB in markdown (working notes), Slack (communication), email (stakeholders), meeting transcripts (input), and at least two LLMs (Claude, Gemini). No single tool replaces the others. The value isn't in any one tool — it's in the PM's ability to synthesize across all of them.

The most productive sessions weren't "do everything in one tool" — they were "pull information from multiple sources, synthesize in the KB, then push decisions and actions back out to the right tools."

### Why It Matters
VPMA should be the **synthesis and coordination layer**, not a replacement for any specific tool. It's the hub in a hub-and-spoke model. Information flows in from various tools, gets synthesized and analyzed, and actions/outputs flow back out to the appropriate tools.

Trying to replace GitHub or Slack or email is a losing strategy. Becoming the intelligent middle layer that connects them is the winning one.

### Architecture Implication
- Integration architecture should be bidirectional adapters: `pull(source)` and `push(destination)`
- Phase 0-1: Manual pull (paste) and manual push (copy). This is fine.
- Phase 2+: Semi-automated adapters for key tools (GitHub API for ticket sync, calendar API for meeting context)
- The LLM's role is synthesis and generation, not tool replacement. Prompt design should assume multi-tool context: "Given updates from [standup transcript] and [GitHub board state] and [current risk register], what needs attention?"
- VPMA's unique value proposition is **cross-tool intelligence** — seeing patterns that no single tool surfaces because the information is spread across systems
- **Connects to**: VPMA_BACKLOG V10 (GitHub sync), V11 (RAID log sync), PRD Section 4 (Six-Tab System as synthesis hub)

---

## How These Patterns Connect

These aren't independent insights — they form a coherent architecture picture:

```
                    Pattern 7: Cross-Tool Orchestration
                    ┌──────────────────────────────────┐
                    │  GitHub  Slack  Email  Sheets ... │
                    └──────────┬───────────────────────┘
                               │ pull / push
                               ▼
┌─────────────────────────────────────────────────────────┐
│                    VPMA Core                            │
│                                                         │
│  Pattern 1: Return Path                                 │
│  ┌─────────┐    ┌─────────┐    ┌──────────────┐        │
│  │  Input   │───▶│  LLM    │───▶│  Suggestions │──┐     │
│  └─────────┘    └─────────┘    └──────────────┘  │     │
│       ▲                                          │     │
│       │         ┌──────────────┐                 │     │
│       └─────────│ Project KB   │◀────────────────┘     │
│                 │ (LPD)        │   "Apply"              │
│                 └──────┬───────┘                        │
│                        │                                │
│  Pattern 2: Staleness  │  Pattern 3: Nav vs. Session    │
│  ┌─verified_at─┐       │  ┌─Project Map─┐              │
│  │ per-section │       │  │ (stable)    │              │
│  └─────────────┘       │  ├─Session Log─┤              │
│                        │  │ (temporal)  │              │
│  Pattern 4: Routing    │  └─────────────┘              │
│  ┌─action items───┐    │                                │
│  │ route + state  │    │  Pattern 5: Weekly Cadence     │
│  │ blocked_by     │    │  ┌─week plan──────┐           │
│  └────────────────┘    │  │ ├─mon items    │           │
│                        │  │ ├─tue items    │           │
│  Pattern 6: Audiences  │  │ └─...          │           │
│  ┌─same data──────┐    │  └────────────────┘           │
│  │ → PM view      │    │                                │
│  │ → exec view    │    │                                │
│  │ → team view    │    │                                │
│  └────────────────┘    │                                │
└─────────────────────────────────────────────────────────┘
```

The **Living Project Document** (QUESTIONS_LOG Q7) is the unifying concept. It's the persistent project knowledge base (Pattern 1's return path), with staleness tracking (Pattern 2), separated into map and log (Pattern 3), containing action items with routing and lifecycle (Pattern 4), organized around weekly cadence (Pattern 5), renderable for different audiences (Pattern 6), and fed by / pushing to external tools (Pattern 7).

---

## Prioritization for VPMA Development

| Pattern | When to Build | Why |
|---------|--------------|-----|
| 1. Return Path | **Phase 1** — after MVP validation | This is the LPD. Without it, every session starts cold. It's the foundation for all other patterns. |
| 3. Nav vs. Session | **Phase 1** — with return path | Data model decision. Get it right early so session accumulation doesn't create scaling problems. |
| 2. Staleness Detection | **Phase 1-2** — after LPD exists | Requires a knowledge base to track staleness against. Low implementation cost, high value. |
| 4. Action Item Routing | **Phase 2** — with integrations | Routing is only valuable when there are destinations to route to. Start with manual routing, automate with integrations. |
| 5. Weekly Cadence | **Phase 3** — Daily Planner redesign | Reframe Daily Planner as Weekly Planner. Low risk to defer — the cadence insight informs the design, not the timeline. |
| 6. Audience Views | **Phase 2-3** — after multi-project | Most valuable when managing multiple stakeholder groups. Prompt engineering pattern — can be prototyped early. |
| 7. Cross-Tool Orchestration | **Phase 2-4** — progressive | Start with GitHub (Phase 2), add integrations progressively. The manual paste/copy flow (Phase 0-1) IS orchestration — just manual. |

---

## Cross-Reference: VPMA Backlog Items

| Pattern | Related Backlog Items |
|---------|----------------------|
| 1. Return Path | V1, V14, QUESTIONS_LOG Q7 (LPD) |
| 2. Staleness | V15 (adjacent — uncertainty tracking) |
| 3. Nav vs. Session | V3 (session continuity), V21 (context window) |
| 4. Action Routing | V2, V10, V11 |
| 5. Weekly Cadence | V12 (meeting prep) |
| 6. Audience Views | V16, V8 |
| 7. Orchestration | V10, V11 |

Items NOT covered by existing backlog: **Pattern 2 (staleness detection)** and **Pattern 5 (weekly cadence)** are genuinely new insights. Consider adding them as V22 and V23.
