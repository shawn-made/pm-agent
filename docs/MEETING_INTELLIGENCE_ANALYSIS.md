# Meeting Intelligence Integration Analysis

**Date**: 2026-02-26
**Context**: Brainstorm session exploring whether video conferencing/recording tools should be built into VPMA, and how transcript ingestion could work with existing and future architecture.
**Decision**: See D30 in DECISIONS.md for the strategic conclusion.

---

## Why This Matters

The #1 pain point for PMs is post-meeting admin: updating RAID logs, writing status reports, capturing decisions, tracking action items. VPMA already solves this for manually-pasted text. The question is whether automating the transcript-to-artifact pipeline (and how) would meaningfully improve the product — and whether it's worth the cost and complexity.

---

## The Landscape (Brutally Honest)

### The Transcription Market Is Won

Transcription accuracy is commoditized. The major players:

| Tool | ARR/Revenue | Users | Funding | Free Tier |
|------|-------------|-------|---------|-----------|
| Otter.ai | $100M ARR | 25M+ | $70M+ | Yes (limited) |
| Fathom | $18.8M rev | Growing 90x/2yr | $21.7M | Yes (unlimited!) |
| Granola | — | — | $67.2M ($250M val) | Yes |
| Fireflies | — | — | — | Yes |

Meanwhile, Microsoft Copilot, Google Gemini, and Zoom AI Companion are all bundling meeting intelligence into their platforms at no extra cost. A solo developer cannot compete on transcription.

### But the PM Artifact Gap Is Real

**No existing tool converts meeting transcripts into structured PM artifacts** (RAID logs, status reports, decision logs, risk registers). This is confirmed across the research:

- Fellow.ai comes closest — pushes action items to Jira/Asana — but produces meeting summaries, not structured PM documents
- Notion AI creates transcript summaries inside Notion but doesn't generate PM-specific formats
- ClickUp Brain converts action items to tasks but doesn't produce RAID logs or status reports
- Otter/Fireflies/Fathom all stop at "summary + action items"

The typical PM workflow today: meeting tool creates transcript → PM manually extracts relevant items → PM manually updates their PM documents. **VPMA's value is in that last mile.**

### The Privacy Angle Is Differentiating But Not Unique

Several tools now target privacy-first meeting intelligence:
- **Meetily**: Open-source, self-hosted, 17K+ users, enterprise pricing
- **Hyprnote**: Free, open-source, all on-device
- **Jamie/Slipbox/Alter**: Bot-free, local processing

The privacy backlash against meeting bots is real — Otter.ai class action (Aug 2025), Fireflies BIPA lawsuit (Dec 2025), multiple universities banning bots, Washington Post reporting bots outnumbering humans in meetings. A tool that works with post-meeting transcripts rather than joining as a bot has a genuine story. But VPMA would not be the first to tell it.

### The DIY Threat

PMs pasting transcripts into ChatGPT/Claude is free, flexible, and takes 30 seconds. VPMA competes against a workflow that costs $0. The counter: ChatGPT doesn't maintain persistent project context, doesn't accumulate knowledge across meetings, and doesn't route suggestions to specific artifacts. VPMA's LPD is the differentiator.

---

## Integration Options (Ranked by Friction-to-Value Ratio)

### Option 1: "Drop Your Transcript" File Watcher
**Effort: 1-2 days | Cost: $0 | Maintenance: Near-zero**

A Python `watchdog` monitors a configurable folder. When a `.vtt`, `.txt`, or `.srt` file appears, VPMA parses it and runs it through the existing intake pipeline.

- Zoom saves `.vtt` files locally when you do local recording with captions enabled
- Users can export/download transcripts from ANY platform and drop them in the folder
- Works with Otter, Fireflies, Fathom, Teams, Meet — anything that exports text
- No OAuth, no API keys, no webhooks, no rate limits

**Pros:**
- Universal (works with every platform and tool)
- Zero infrastructure dependency
- Perfectly aligned with local-first/privacy-first positioning
- Already 80% built (VPMA's intake pipeline handles text files)

**Cons:**
- Still requires a manual step (download + drop file)
- Not a "wow moment" for demos
- Doesn't solve the project-routing problem automatically

**Honest take:** This is the 80/20 play. It covers the core value (transcript → PM artifacts) with almost no new complexity. It should be built regardless of what else you do.

### Option 2: Fireflies.ai GraphQL API
**Effort: 2-3 days | Cost: $120-228/year | Maintenance: Low**

Fireflies handles the hard parts (recording, transcription, speaker ID) across all platforms. VPMA pulls transcripts via their documented GraphQL API.

- Real, documented API with self-serve API key
- Works across Zoom, Meet, Teams
- Structured data: `speaker_name`, `start_time`, `text` per sentence
- Rate limits: 50/day on Pro ($10-18/mo), 60/min on Business ($19-29/mo)

**Pros:**
- Single integration covers all meeting platforms
- Structured transcript data (better than raw VTT parsing)
- Offloads the entire transcription problem
- Reduces multi-platform complexity from 3+ integrations to 1

**Cons:**
- Adds a cloud dependency (contradicts privacy-first positioning)
- Ongoing cost ($120-228/year minimum)
- Rate limits on lower tiers are very tight (50/day)
- You're building on someone else's API (they could change terms, raise prices, shut down)
- Users must also pay for Fireflies subscription
- Meeting data passes through Fireflies' cloud (PII exposure)

**Honest take:** Good for a "works today" integration if you're OK with the privacy tradeoff. But it stacks costs (user pays for Fireflies + any VPMA subscription) and undermines the privacy story.

### Option 3: Zoom Server-to-Server OAuth (Personal Use)
**Effort: 2-3 days | Cost: $0 | Maintenance: Low**

Access your own Zoom cloud recordings and transcripts via API. No marketplace listing needed. Poll recordings API every 15-30 minutes.

- Server-to-Server OAuth is straightforward (no redirect URI problem)
- VTT transcripts with speaker labels and timestamps
- Requires Zoom Pro+ for cloud recording ($13.33/mo, which most PMs already have)

**Pros:**
- Free API access (included in Zoom subscription)
- No marketplace review needed for internal/personal apps
- Polling avoids the webhook infrastructure problem
- Zoom has ~55% market share for video conferencing

**Cons:**
- Only works for YOUR Zoom account (not distributable without marketplace listing)
- English-only for Zoom's native transcription
- Transcript processing delay: 2x recording duration up to 24 hours
- Cloud recording required (local recordings produce lower-quality transcripts)
- Only covers Zoom (not Meet or Teams)
- To distribute to other users → requires Zoom Marketplace listing (4+ weeks review, security audit, privacy policy, TOS, domain verification)

**Honest take:** Good for personal use. Dead end for distribution without significant marketplace investment.

### Option 4: Local Whisper STT + Audio Capture
**Effort: 2-4 weeks | Cost: $0 | Maintenance: Medium**

Record meeting audio locally, transcribe with Whisper.cpp on-device. Full privacy — audio never leaves the machine.

- Whisper.cpp on M4 MacBook: Large model runs comfortably in near real-time
- 99 languages, 95-97% accuracy on clear audio
- WhisperX adds speaker diarization (who said what)

**Pros:**
- Maximum privacy alignment (zero cloud dependency)
- Zero per-transcript cost
- Works offline
- Aligns with Phase 2 local Ollama story
- Differentiating: "Your meeting audio never leaves your machine"

**Cons:**
- No built-in speaker diarization (need WhisperX, adds complexity)
- Audio capture across platforms is tricky (macOS requires virtual audio driver like BlackHole or loopback)
- CPU-intensive during transcription (fans, battery drain on laptop)
- User must manually start/stop recording
- No meeting metadata (attendees, title) — just raw audio
- Significant scope increase for a solo developer
- Quality depends heavily on audio quality (headset vs. laptop mic vs. conference room)

**Honest take:** Technically compelling and perfectly aligned with VPMA's philosophy, but a substantial engineering effort. The audio capture layer alone (especially cross-platform) is a multi-week project. Best deferred until core PM features are solid and there's user demand.

### Option 5: Multi-Platform OAuth (Zoom + Meet + Teams)
**Effort: 6-12 weeks | Cost: $10-100/year + significant time | Maintenance: 20-40 hrs/year**

Full API integration with all three major platforms. Webhooks or polling for auto-fetch.

**Platform-specific realities:**

| Platform | OAuth Difficulty | Distribution Barrier | Transcript Quality |
|----------|-----------------|---------------------|-------------------|
| Zoom | Medium | Marketplace review: 4+ weeks | VTT, English-only native |
| Google Meet | HIGH | Restricted scope verification: 4-7 weeks, potential $0-75K security assessment | JSON, 5-min timestamp granularity |
| Teams | Medium | Admin consent required per tenant | VTT, good quality, multi-language |

**The webhook problem for local apps:** All three platforms require a publicly accessible HTTPS endpoint for webhooks. For a local-first app, you'd need ngrok ($8/mo), Cloudflare Tunnel (free + domain), or polling instead. Polling works but adds latency (minutes to hours).

**Honest take:** This is a product-company-level effort, not a solo-developer feature. The ROI only makes sense if you're building a commercial product with paying users who specifically need auto-fetch.

### Option 6: Recall.ai Middleware
**Effort: 1-2 weeks | Cost: $0.65/hour per meeting | Maintenance: Low**

Recall.ai provides a single API across Zoom, Meet, Teams, Webex, GoTo, and Slack Huddles. They handle the meeting bots, platform integrations, and transcription.

**Honest take:** The "throw money at the problem" solution. Makes sense for a well-funded startup building a SaaS product. Doesn't fit VPMA's philosophy or economics ($0.65/hr = $52/month for a PM with 20 hrs/week of meetings).

---

## The Hardest Unsolved Problem: Project Routing

When a transcript arrives automatically, how does VPMA know which project it belongs to?

**Key finding: No existing meeting AI tool has solved automatic multi-project routing.** Fireflies, Otter, Fellow — they all use manual organization (folders, tags). This is a genuinely unsolved product problem.

### The Cascade Architecture (Recommended)

Route using the cheapest, most-deterministic signal first. Fall through to more expensive/intelligent signals only when needed.

```
Transcript arrives
  │
  ├─ Signal 1: EXPLICIT FOLDER                    [deterministic, $0]
  │  File in ~/VPMA/transcripts/project-alpha/ → route to Alpha
  │  If matched → DONE (auto-process)
  │
  ├─ Signal 2: FILENAME PATTERN                    [regex, $0]
  │  Filename matches "[Alpha] Sprint Review" → route to Alpha
  │  If matched → DONE (auto-process)
  │
  ├─ Signal 3: MEETING TITLE LOOKUP                [string match, $0]
  │  Zoom cloud: meeting topic field
  │  Teams: meeting subject
  │  Meet: transcript filename contains title
  │  Fuzzy match against project names → route if confident
  │
  ├─ Signal 4: ATTENDEE MATCHING                   [fuzzy match, $0]
  │  Parse speaker names from VTT → match against LPD stakeholder lists
  │  If >80% of non-PM speakers match one project → suggest with confirmation
  │
  ├─ Signal 5: LLM CONTENT CLASSIFICATION          [$0.002/call]
  │  Send transcript excerpt (first 1000 tokens + samples) +
  │  all project summaries from LPDs to LLM
  │  VPMA already has this infrastructure (LLM client, privacy proxy, LPD context)
  │  If confident → suggest with confirmation
  │
  └─ Signal 6: ASK THE USER                        [manual, $0]
     "Which project does this meeting belong to?"
     Show: meeting title, date, speakers, and project dropdown
```

### What to Build When

- **Phase 1B (with file watcher):** Signals 1 + 6 only. Folder-based + manual fallback.
- **Phase 2 (multi-project lands):** Add Signals 2 + 3 + 5. Filename, title match, LLM classification.
- **Phase 3+ (if needed):** Add Signal 4. Attendee matching once LPD stakeholders populated.

### VPMA's Unique Advantage

The LPD already contains rich per-project context (Overview, Stakeholders, Recent Context, Risks, Decisions). When the LLM classification call sends a transcript excerpt alongside all project summaries, it has exactly the context needed to route accurately. **The LPD isn't just the destination for transcripts — it's also the router.** No other consumer PM tool has this depth of per-project context readily available.

### The "Wrong Project" Problem

- **High-confidence routes (folder, filename):** Auto-process, show undo toast.
- **Medium-confidence routes (LLM, attendee match):** Show suggestion, wait for one-click confirm.
- **Low-confidence / uncertain:** Ask the user. No processing until assigned.
- **Multi-project meetings:** "Process for both?" with per-project scoped extraction.
- **Correction flow:** Move action → revert wrong-project LPD changes → reprocess for correct project.

---

## Financial Reality Check

### LLM Cost Per Transcript

A 1-hour meeting ≈ 15K tokens input:

| Model | Cost/Transcript | 100 Meetings/Month |
|-------|----------------|---------------------|
| Gemini Flash | $0.01-0.02 | $1-2 |
| Claude Sonnet | $0.05-0.10 | $5-10 |
| Claude Opus | $0.30-0.75 | $30-75 |
| Local Ollama | $0 | $0 |

### Cost Stacking Problem

If VPMA requires users to also pay for a meeting platform ($13/mo) + transcription service ($10-29/mo) + LLM credits ($5-20/mo) + VPMA itself ($10-20/mo), that's $38-82/month total. Individual PMs won't pay this. The more steps you can eliminate from this stack, the better the adoption story.

---

## Can Platforms Auto-Drop Transcripts Into a Folder?

### Native Auto-Save (Zero Config)

| Platform | Auto-saves transcript? | Where? | Format | Sync to local folder? |
|----------|----------------------|--------|--------|-----------------------|
| **Microsoft Teams** | YES | OneDrive `Recordings/` | .vtt | YES — OneDrive desktop sync. **Best zero-code path.** |
| **Google Meet** | YES | Google Drive `Meet Recordings/` | Google Doc (.gdoc) | PARTIAL — .gdoc stubs locally. Need Zapier to convert. |
| **Zoom (local)** | PARTIAL | `~/Documents/Zoom/` | .vtt (if captions active) | Already local, but no title in filename. |
| **Zoom (cloud)** | YES | Zoom web portal only | .vtt | NO native local save. Needs Zapier/API. |

### Zapier-Automated Path (Zero Code, ~$20/mo)

**Pattern:** Platform trigger (new transcript) → Create file in Google Drive/OneDrive → Desktop sync to local.

All major platforms and transcription tools (Zoom, Otter, Fireflies, Fathom, tl;dv) have well-tested Zapier integrations for this workflow.

**Simplest Zoom setup:** Enable cloud recording with auto-transcription → Zapier downloads to Google Drive folder → Drive for Desktop syncs locally → VPMA file watcher picks it up.

---

## Marketability Impact

### What Makes This a Killer Feature

The pitch: *"Finish your meeting. By the time you're back at your desk, your RAID log is updated, your status report has new bullets, and your decisions are captured."*

- Most tangible, demo-able "wow moment" for PMs
- Directly attacks the #1 PM pain point (post-meeting admin)
- Differentiated from every existing tool (none route to structured PM artifacts)

### What Makes This Dangerous

- **Scope creep**: Meeting intelligence is an entire product category
- **Competitive comparison**: Users might compare VPMA to Otter/Fathom (unfavorably) instead of PM tools
- **The Copilot threat**: Microsoft could add PM-specific artifact generation to Copilot at any time
- **Distribution**: Meeting intelligence space is incredibly noisy

### Subscription Tier Opportunity

- **Free**: Manual paste (what exists today)
- **Pro ($10-20/mo)**: File watcher + transcript-specific UX + one platform integration
- **Team ($30-50/mo)**: Multi-platform auto-fetch + team sharing

---

## STT Engine Comparison (If Building Custom)

| Engine | Price/Min | Diarization | Real-time | Languages |
|--------|-----------|-------------|-----------|-----------|
| GPT-4o Transcribe + Diarization | $0.006 | Included | No | 99 |
| GPT-4o Mini Transcribe | $0.003 | No | No | 99 |
| Deepgram Nova-3 | $0.0065-0.0077 | Included | Yes (<300ms) | 45+ |
| AssemblyAI Universal-2 | $0.0045 | +$0.0003 | Yes | 99 |
| Whisper.cpp (local) | Free | No (need WhisperX) | On-device | 99 |

**Best for VPMA's privacy model:** Whisper.cpp (local) for maximum privacy, or AssemblyAI for best speaker diarization accuracy.

---

## The Strategic Bottom Line

VPMA's strongest position is **not** as a meeting intelligence tool. It's as a **PM intelligence layer** that can ingest transcripts from any source and transform them into PM-specific deliverables with persistent project context.

**Don't compete on transcription. Compete on what happens after.**
- Accept transcripts from anywhere (file drop, paste, API pull)
- Add PM-specific intelligence (RAID extraction, risk detection, decision logging)
- Accumulate project context (the LPD is the real moat)
- Keep the privacy story clean (local processing, no bots)

The file watcher approach (Option 1) delivers 80% of the value at 1% of the complexity. Start there.

---

## Recommended Phasing

1. **Phase 1B**: File watcher + VTT parser + transcript UX. ~1-2 days. $0.
2. **Phase 2-3**: Zoom Server-to-Server OAuth for personal auto-fetch + cascade routing. ~3-5 days. $0.
3. **Phase 3-4**: Evaluate Zoom Marketplace listing OR local Whisper STT based on demand signals.
4. **Phase 4+**: Multi-platform OAuth only if building a commercial product.

---

## Competitive Landscape Reference

### Tools That Come Closest to VPMA's Niche

| Tool | What It Does | Where It Stops |
|------|-------------|----------------|
| Fellow.ai | Transcribes + pushes action items to Jira/Asana | No structured PM artifacts (RAID logs, status reports) |
| Notion AI | Transcribes + summarizes inside Notion | No PM-specific formats, no persistent project context |
| ClickUp Brain | Transcribes + converts to ClickUp tasks | No RAID logs, no cross-meeting context accumulation |
| Otter/Fireflies/Fathom | Transcribe + summarize + action items | All stop at "summary + action items" |
| Microsoft Copilot | Real-time summaries + action items in Teams | No structured PM artifacts, enterprise-only |
| Google Gemini in Meet | Meeting notes in Google Docs | No PM-specific routing, Workspace-only |

### Privacy-First Competitors

| Tool | Approach | Status |
|------|----------|--------|
| Meetily | Open-source, self-hosted | 17K+ users, enterprise pricing |
| Hyprnote | Free, open-source, on-device | Active development |
| Jamie | Bot-free, local processing | Commercial product |
| Slipbox | No bots, no cloud | Active |

### Market Context

- AI Meeting Assistants Market: $3.5B in 2025, projected $34.3B by 2035 (25.6% CAGR)
- Privacy backlash accelerating: Otter class-action (Aug 2025), Fireflies BIPA lawsuit (Dec 2025), universities banning bots
- 2026 trend: Market moving from "notetakers" to "AI agents" — value is in post-transcript intelligence, not transcription itself
