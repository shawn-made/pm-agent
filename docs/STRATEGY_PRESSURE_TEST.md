# VPMA Strategy Pressure Test

*Captured: 2026-04-08 — from strategic product vision session*

---

## Context

This document captures a pressure test of VPMA's product positioning, target user, and product identity. The goal was to stress-test two strategic questions:

1. **Target user**: "Cross-functional PM" — is this the right frame?
2. **Product identity**: What IS this thing — notebook, document creator, agent, or something else?

---

## Pressure Test #1: "Cross-Functional PM" as Target User

### What's strong

- Artifact types (RAID logs, status reports, charters, meeting notes) are genuinely **domain-agnostic**. A RAID log in healthcare, construction, or fintech has the same structure.
- VPMA operates at the **process structure layer**, not the domain content layer. That's a legitimate universal.
- Privacy-first architecture plays universally. Healthcare PMs can't upload PHI. Defense PMs can't upload classified adjacents. Financial PMs can't upload deal terms. The "can't use ChatGPT at work" problem is not tech-specific.

### Where it breaks down

- **"Cross-functional PM" is not a market segment** — it's a job description. You can't buy a mailing list of them. You can't target them with ads. You can't find them at a conference (PMI? They're all cross-functional). The positioning is true but not actionable for go-to-market.
- Compare: *"Privacy-first PM tool for enterprise PMs who can't use ChatGPT"* — that's a targetable pain point. *"Cross-functional PM assistant"* is everyone and nobody.
- The **actual current user is more specific**: a PM with enough technical comfort to run uvicorn from a terminal and manage .env files. That's not "any PM" — that's a tech-adjacent PM managing complex multi-stakeholder projects.

### Domain Fluency — Reframed

The insight that "technical fluency" is one instance of a general pattern is correct. But the pattern isn't "domain fluency" — it's **stakeholder translation**. Every cross-functional PM's core skill is translating between groups that speak different languages:

| Domain | Translation axis |
|--------|-----------------|
| Tech | Engineering ↔ Business |
| Healthcare | Clinical ↔ IT ↔ Regulatory |
| Construction | Field ↔ Office ↔ Client |
| Government | Policy ↔ Implementation ↔ Procurement |

If built as a **pluggable translation layer** (prompt templates per domain), this becomes powerful: the PM process engine is universal, the translation layer is domain-specific. This could be a **prompt-pack model**, not a code-fork model.

**Recommendation**: Park domain packs for v2. v1 user is a tech-adjacent PM. Own the niche, expand later. The one exception: if "technical fluency" means helping PMs translate between engineering and business stakeholders, that's core to the current user base and should be a default capability.

---

## Pressure Test #2: What IS This Thing?

### What it's NOT

| Category | Why not |
|----------|---------|
| **Notebook** (Jupyter, Notion, Obsidian) | Nobody writes their status report inside VPMA. They paste input, get structured output, copy it elsewhere. VPMA is not the long-term home of artifacts. |
| **Document creator** (Jasper, Beautiful.ai) | VPMA started here (Phase 0: paste → suggestions → copy), but LPD, return path, staleness tracking, and briefings make it **stateful**. Document creators don't remember your project. |
| **Autonomous agent** (Devin-style) | VPMA explicitly keeps the human in the review loop — suggestion cards, apply buttons, pressure test reviews. Not delegating; augmenting. |

### What it IS: A Processing Engine with Persistent Project Memory

VPMA is a **PM's intelligent processing layer** — it sits between raw project chaos (transcripts, notes, conversations, brain dumps) and structured project artifacts (RAID logs, status reports, charters). It:

1. **Ingests** raw, unstructured input
2. **Processes** it through domain-aware AI with privacy protection
3. **Proposes** structured updates to specific artifacts
4. **Accumulates** project knowledge over time (LPD)
5. **Proactively surfaces** issues the PM might miss (staleness, contradictions, risks)
6. **Always defers** the final decision to the human

### The Primary Verb

Every product has one:
- Google → Search
- Slack → Message
- Figma → Design
- Notion → Write

**VPMA's verb: "Digest"** — it captures the raw→structured transformation AND the accumulation over time.

> *"VPMA digests your project chaos into structured artifacts and keeps them consistent."*

### Human-in-the-Loop: A Trust Gradient (Not a Binary)

| Interaction mode | Built? | Trust level |
|-----------------|--------|-------------|
| Paste → Review → Apply (artifact sync) | Yes | Low trust — human reviews every suggestion |
| Accumulate → Surface (LPD, staleness) | Yes | Medium trust — system decides what to flag |
| Monitor → Alert (briefings, risks) | Yes | Medium-high trust — system proactively tells you what to care about |
| Delegate → Report (transcript watcher) | Partial | High trust — system works independently |

This is a natural **adoption curve**, not a product identity crisis. Users start at paste-and-review (low trust), develop confidence, and gradually rely on proactive features (higher trust).

---

## Decisions Framework

### Tier 1: Identity (answer before anything else)

| Question | Options | Recommendation |
|----------|---------|---------------|
| Primary verb | Sync / Process / Digest / Manage | **"Digest"** — captures raw→structured + accumulation |
| Category | Assistant / Companion / Processing engine | **"PM Companion"** — relational (persistent memory, proactive nudges) not transactional |
| v1 user | Any PM / Tech-adjacent PM / Enterprise PM | **Tech-adjacent PM who can't use ChatGPT for project data**. Own the niche, expand later |

### Tier 2: Go-to-Market Positioning

| Angle | Strength | Weakness |
|-------|----------|----------|
| "Privacy-first PM tool" | Clear differentiator, targetable | Privacy is a qualifier, not a value prop. People buy productivity; accept privacy as bonus |
| "AI PM companion" | Warm, relational, accurate | Crowded — everyone is an "AI companion" now |
| "Project digest engine" | Unique, accurate to what it does | Unfamiliar category — requires education |
| "The PM tool for projects you can't talk about" | Provocative, immediately clear | Narrow, might scare some users |

**Recommended positioning**: Lead with workflow, qualify with privacy.

> *"VPMA turns raw project chaos into structured artifacts in 30 seconds — and your sensitive data never leaves your machine."*

Productivity first, privacy as the trust-builder.

### Tier 3: Domain Strategy

- **v1**: Universal PM process engine. No domain packs.
- **v2**: Prompt-pack model for domain-specific stakeholder translation.
- **Exception**: Engineering ↔ Business translation is core to v1 user base — include by default.

---

## Open Questions (for the developer to decide)

1. Does "digest" resonate as the primary verb, or is there something better?
2. Is "tech-adjacent PM who can't use ChatGPT" too narrow or just right for launch?
3. Should domain fluency (stakeholder translation packs) be part of the roadmap, or is it a distraction?
4. Is the trust gradient (low → high) the right way to frame the human-in-the-loop model for marketing?

---

## Status

- [ ] Developer reaction to pressure test
- [ ] Tier 1 identity decisions finalized
- [ ] Go-to-market angle selected
- [ ] Strategy integrated into PRD
