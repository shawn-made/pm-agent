# VPMA Product Vision & Strategy — Pressure Test

**Created**: 2026-04-07
**Status**: Draft — awaiting founder reaction
**Purpose**: Pressure test two foundational product questions before they become baked-in assumptions

---

## Context

Two strategic questions surfaced during product vision planning:

1. **Target user**: Is "cross-functional PM" the right frame? Where does "domain fluency" (technical, business, healthcare, etc.) fit?
2. **Product category**: What IS this thing — notebook, document creator, assistant, agent? Where is the human in the loop?

Both questions have downstream implications for marketing, feature prioritization, and architecture.

---

## Question 1: "Cross-Functional PM" as Target User

### What's Strong

VPMA's artifact types — RAID logs, status reports, charters, meeting notes — are genuinely **domain-agnostic**. A RAID log in healthcare, construction, or fintech has the same structure: Risk, Action, Issue, Decision. The PM *process* is the same regardless of industry. VPMA operates at the **process structure layer**, not the domain content layer. That's a legitimate universal.

The privacy-first architecture also plays universally:
- Healthcare PMs can't upload PHI
- Defense PMs can't upload classified adjacents
- Financial PMs can't upload deal terms
- The "can't use ChatGPT at work" problem is not tech-specific

### Where It Breaks Down

**"Cross-functional PM" is not a market segment — it's a job description.** You can't buy a mailing list of "cross-functional PMs." You can't target them with ads. You can't find them at a conference (PMI? They're all cross-functional). The positioning is true but **it's not actionable for go-to-market**.

Compare: "Privacy-first PM tool for enterprise PMs who can't use ChatGPT" — that's a targetable pain point. "Cross-functional PM assistant" is... everyone? Nobody?

**The actual current user is more specific than admitted.** The PRD personas (Sarah, Marcus, Aisha) are all **tech-adjacent, terminal-comfortable, managing complex multi-stakeholder projects.** That's not "any PM" — that's a PM with enough technical comfort to run `uvicorn` from a terminal and manage `.env` files.

### The Domain Fluency Insight — Reframed

The original insight: "technical fluency" is one instance of a general pattern. The reframe: the pattern isn't "domain fluency" — it's **stakeholder translation**. Every cross-functional PM's core skill is translating between groups that speak different languages:

| Domain | Translation axis |
|--------|-----------------|
| Tech | Engineering ↔ Business |
| Healthcare | Clinical ↔ IT ↔ Regulatory |
| Construction | Field ↔ Office ↔ Client |
| Government | Policy ↔ Implementation ↔ Procurement |
| Financial | Regulatory/Compliance ↔ Engineering |

If built as a **pluggable translation layer** (prompt templates per domain), the PM process engine stays universal while the translation layer becomes domain-specific. This could be a prompt-pack model, not a code-fork model.

**But the hard question: is this needed for v1?** No. The v1 user is a tech-adjacent PM. Own that. Domain packs are a scaling strategy, not a launch strategy.

### Architecture Implication

The `prompts/templates/` directory already supports this extensibility. No architectural changes needed — just a future content strategy decision.

---

## Question 2: What IS This Thing?

### Options Eliminated

| Category | Example | Why VPMA is NOT this |
|----------|---------|---------------------|
| **Notebook** | Jupyter, Notion, Obsidian | Writing environments where the artifact IS the product. Nobody writes their status report *inside* VPMA. They paste input, get output, copy elsewhere. |
| **Document Creator** | Jasper, Beautiful.ai | One-shot generators. VPMA started here (Phase 0: paste → suggestions → copy) but has moved past it. The LPD, return path, staleness tracking, and briefings make it **stateful**. Document creators don't remember your project. |
| **Autonomous Agent** | Devin, autonomous systems | Work independently and come back with results. VPMA explicitly keeps the human in the review loop — suggestion cards, apply buttons, pressure test reviews. |

### What VPMA Actually Is

**VPMA is a PM's intelligent processing layer** — it sits between raw project chaos (transcripts, notes, conversations, brain dumps) and structured project artifacts (RAID logs, status reports, charters).

The operating model:

1. **Ingests** raw, unstructured input
2. **Processes** it through domain-aware AI with privacy protection
3. **Proposes** structured updates to specific artifacts
4. **Accumulates** project knowledge over time (LPD)
5. **Proactively surfaces** issues the PM might miss (staleness, contradictions, risks)
6. **Always defers** the final decision to the human

The human-in-the-loop model is **review-and-approve at the artifact level, delegate at the processing level.** The PM delegates the grunt work (parsing a 45-minute transcript into RAID entries) but retains judgment (which entries to actually apply).

### The Primary Verb Question

Every product has one verb:
- Google: **Search**
- Slack: **Message**
- Figma: **Design**
- Notion: **Write**

VPMA's current verb is "Sync" (artifact sync). But with LPD, briefings, brain dump, and dashboard, it's outgrowing sync.

**Proposed verb: "Digest"** — it captures both the raw→structured transformation AND the accumulation over time.

> "VPMA digests your project chaos into structured artifacts and keeps them consistent."

That's one sentence covering everything built so far.

### The Product Category

**"PM Companion"** — it's relational (persistent memory, proactive nudges) not transactional (one-shot generation).

The "companion" frame captures:
- It knows your project (LPD)
- It proactively flags things (staleness, risks, contradictions)
- It gets smarter over time (accumulated context)
- It defers to your judgment (review-and-approve)

---

## The Trust Gradient (Human-in-the-Loop Model)

VPMA already operates on a **trust gradient** — and this is the right model, not an identity crisis:

| Interaction mode | Already built? | Trust level | User behavior |
|-----------------|---------------|-------------|---------------|
| **Paste → Review → Apply** (artifact sync) | Yes | Low trust | Human reviews every suggestion |
| **Accumulate → Surface** (LPD, staleness) | Yes | Medium trust | System decides what to flag |
| **Monitor → Alert** (briefings, risks) | Yes | Medium-high trust | System proactively tells you what to care about |
| **Delegate → Report** (transcript watcher) | Partial | High trust | System works independently |

Users start at paste-and-review (low trust), develop confidence, and gradually rely on proactive features (higher trust). This is a natural adoption curve.

---

## Decisions Required

### Tier 1: Identity (answer before anything else)

| Question | Options | Recommendation |
|----------|---------|----------------|
| **Primary verb** | Sync / Process / Digest / Manage | "Digest" — captures raw→structured + accumulation |
| **Category** | Assistant / Companion / Processing engine | "PM Companion" — relational, not transactional |
| **v1 user** | Any PM / Tech-adjacent PM / Enterprise PM | Tech-adjacent PM who can't use ChatGPT for project data |

### Tier 2: Go-to-Market Positioning

| Angle | Strength | Weakness |
|-------|----------|----------|
| "Privacy-first PM tool" | Clear differentiator, targetable | Privacy is a qualifier, not a value prop |
| "AI PM companion" | Warm, relational, accurate | Crowded — everyone is an "AI companion" |
| "Project digest engine" | Unique, accurate to function | Unfamiliar category, requires education |
| "The PM tool for projects you can't talk about" | Provocative, immediately clear | Narrow, might scare some users |

**Recommended lead**: Workflow first, privacy as qualifier.

> "VPMA turns raw project chaos into structured artifacts in 30 seconds — and your sensitive data never leaves your machine."

### Tier 3: Domain Fluency

- Park for v1
- Build as prompt template architecture (already extensible via `prompts/templates/`)
- "Technical fluency" (engineering ↔ business translation) ships as a default capability, not a domain pack
- Domain packs become the year-2 expansion strategy

---

## Open Questions

1. Does "Digest" resonate as the primary verb, or does something else feel more natural?
2. Is "PM Companion" the right category, or is there a better frame?
3. Should the v1 target be even narrower (e.g., "PMs at companies with >500 employees where ChatGPT is blocked")?
4. Is stakeholder translation (the reframe of domain fluency) a v1 feature or a v2 feature?
5. How does the trust gradient map to the onboarding experience — do we explicitly guide users through it?
