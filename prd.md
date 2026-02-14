# VPMA: Virtual Project Management Assistant
## Vision Product Requirements Document (PRD)

**Version**: 1.2 (Phase 0 MVP + Implementation Strategy)
**Date**: February 14, 2026
**Author**: Product Strategy Team
**Status**: Ready for Phase 0 Development

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Market Context](#2-problem-statement--market-context)
3. [Goals & Success Metrics](#3-goals--success-metrics)
4. [User Experience Design - The Six-Tab System](#4-user-experience-design---the-six-tab-system)
5. [Technical Architecture](#5-technical-architecture)
6. [Artifact Landscape & Content Model](#6-artifact-landscape--content-model)
7. [Roadmap & Phasing](#7-roadmap--phasing)
8. [Success Criteria & Measurement](#8-success-criteria--measurement)
9. [Risks & Mitigation](#9-risks--mitigation)
10. [Appendices](#10-appendices)

---

## 1. Executive Summary

### Vision Statement

**VPMA is a local, privacy-centric "Project Professional Agent" that functions as an elite-level cross-functional partner, capable of assuming the roles of Senior PM, Program Manager, Business Analyst, Product Owner, and Product Manager.**

In a world where project managers spend 60-70% of their time maintaining artifacts instead of driving strategy, VPMA reimagines the PM's daily workflow. It's not another task tracker or cloud-based AI assistant—it's a privacy-first, locally-run intelligent partner that lives entirely on your laptop, anonymizes sensitive data before it touches any external LLM, and adapts its professional expertise based on what you need in the moment.

### Target Users

**Primary**: Senior PMs managing 2-5 concurrent projects, privacy-conscious, tech-savvy, working with sensitive enterprise data they cannot upload to cloud services.

**Secondary**: Product Managers juggling roadmaps, PRDs, and stakeholder updates across multiple initiatives while navigating competing priorities.

**Tertiary**: Business Analysts coordinating requirements across multiple cross-functional teams, translating between technical and business stakeholders.

### Core Value Proposition

VPMA delivers on four pillars that existing solutions cannot match:

#### 1. Privacy-First Architecture
Unlike ChatGPT, Claude Web, or Microsoft Copilot, VPMA runs 100% locally with a **Privacy Proxy** that anonymizes PII (names, emails, organizations, proprietary terms) *before* data touches external LLM APIs. Sensitive project data never leaves your laptop in identifiable form.

#### 2. Frictionless Daily Use
"Artifact Sync" in under 30 seconds. Paste a meeting transcript, drop a Slack screenshot, or describe an update—VPMA identifies which artifacts need updating and generates structured changes. No manual context loading, no switching between 10 browser tabs. Google-minimalist interface means zero UI clutter between you and productivity.

#### 3. Elite Partnership
VPMA doesn't pretend to be a person—it operates as a **professional capability suite**. Need to draft a PRD? It becomes a Product Owner. Analyzing risks? It shifts to PM + Business Analyst mode. The intelligence adapts to the task, drawing from the combined expertise of senior PM, PO, BA, and Product Manager roles.

#### 4. Scales with Rigor
From 25-second daily syncs (paste meeting notes → update RAID log) to hour-long Deep Strategy sessions (propagate Charter changes across Schedule, RAID Log, Status Report with multi-pass consistency validation), VPMA meets you at your current need. Greenfield project initiation? Generate a baseline artifact package in minutes. Recurring weekly reporting? Copy talking points for tomorrow's steering committee.

### Key Differentiators

| Feature | VPMA | Jira/Asana/Monday | ChatGPT/Claude Web | Microsoft Copilot |
|---------|------|-------------------|-------------------|-------------------|
| **Local-First** | ✅ 100% laptop | ❌ Cloud only | ❌ Cloud only | ❌ Cloud only |
| **Privacy Proxy** | ✅ PII anonymization | N/A | ❌ Raw data upload | ⚠️ Enterprise-dependent |
| **Multi-Persona AI** | ✅ PM/PO/BA/Product | ❌ No AI | ⚠️ Generic assistant | ⚠️ Generic productivity |
| **Artifact Intelligence** | ✅ Specialized for PM artifacts | ❌ Task tracking only | ⚠️ Manual prompting | ⚠️ Document-focused |
| **Triple-Brain Toggle** | ✅ Claude ⟷ Gemini ⟷ Local (Ollama) | N/A | ❌ Single provider | ❌ Single provider |
| **PM Workflow Optimization** | ✅ 6 specialized tabs | ❌ One-size-fits-all | ❌ Chat interface | ⚠️ Office integration only |

### Development Approach

VPMA is built using **AI-assisted development** (Claude Code + RALPH loop technique) by a solo developer. The 5-phase rollout starts with a **lean Foundation MVP** (4 weeks, simplified tech stack) to validate the core hypothesis, then progressively adds features and complexity:

- **Phase 0** (Month 1): Foundation MVP — text in → suggestions → copy to clipboard
- **Phase 1** (Months 2-3): Full Artifact Sync + Settings + Cross-Tab features + Beta users
- **Phase 2** (Months 4-6): Deep Strategy + Local LLM (Ollama) + Multi-Project
- **Phase 3** (Months 7-9): Daily Planner + Project Initiation + History
- **Phase 4** (Months 10-13): Security, Web App + Auth, Integrations, HR Capacity Planning

See Section 10.6 for detailed implementation estimates (keyboard time, token usage, RALPH task decomposition).

### Success Snapshot: 12-Month Vision

**Adoption**: 50+ active PMs using VPMA daily, 5+ sessions per week per user, 90% retention after 3 months.

**Productivity**: 70% reduction in artifact maintenance time (from ~20 hrs/week → ~6 hrs/week), 90% faster status report generation (2 hours → 10 minutes).

**Quality**: 95%+ artifact completeness score, 90%+ change integration accuracy post-Deep Strategy, 98%+ PII anonymization accuracy in production.

**Satisfaction**: NPS 50+, CSAT 4.5/5, 2+ feature requests per user per month (signal of deep engagement).

---

## 2. Problem Statement & Market Context

### Current State: The PM Artifact Tax

Project Managers face a paradox: the artifacts meant to enable communication and decision-making consume 60-70% of their time. A typical PM managing 3 projects spends:

- **8 hours/week** updating RAID logs, status reports, and meeting notes
- **6 hours/week** preparing for meetings (finding latest versions, synthesizing updates, drafting agendas)
- **4 hours/week** reconciling inconsistencies when one artifact changes (Charter scope shifts → Schedule must update → RAID Log needs new risks → Status Report timeline section outdated)
- **2 hours/week** generating baseline artifacts for new initiatives

**Total artifact tax**: ~20 hours/week. This leaves barely 20 hours for the actual work: strategic planning, stakeholder management, risk mitigation, team coaching.

The tools that exist today fall into two categories, and neither solves the problem:

### Why Existing Solutions Fall Short

#### Task Management Tools (Jira, Asana, Monday)
**What they do well**: Track execution. Assign tasks, set deadlines, visualize backlogs.

**What they miss**: Zero intelligence. They're digital checklist managers, not strategic partners. They don't:
- Generate a Project Charter from a kickoff conversation
- Identify which artifacts need updates from a meeting transcript
- Propagate dependency changes when your timeline shifts
- Draft talking points for tomorrow's steering committee based on current project state

**Verdict**: Execution-focused, not intelligence-augmented. VPMA operates one layer higher—in the artifact generation and synchronization layer that Jira doesn't touch.

#### Generic AI Assistants (ChatGPT, Claude Web)
**What they do well**: Flexible, powerful language understanding. Can draft almost anything if you prompt it correctly.

**What they miss**:
1. **Privacy risk**: Cloud-based. You upload "Project Falcon's Q2 budget includes $3M for ClientCo integration" and hope for the best. Many enterprises forbid this.
2. **No PM-specific workflows**: Every session starts from scratch. No artifact memory, no understanding of your RAID Log vs. Status Report vs. Charter. You're constantly re-explaining context.
3. **Manual orchestration**: *You* must remember which artifacts to update when your Charter changes. *You* must copy/paste between 10 browser tabs to get consistency.

**Verdict**: Powerful but generic. Great for one-off tasks, exhausting for systematic artifact maintenance.

#### Microsoft Copilot
**What it does well**: Office integration. If you live in Word/Excel/PowerPoint, it can help draft and format.

**What it misses**:
1. **Enterprise-only**: Requires Microsoft 365 Business licenses, Azure AD, IT approval. Not accessible to solo PMs or consultants.
2. **Cloud-dependent**: Same privacy concerns as generic AI (data leaves your laptop).
3. **Not PM-specialized**: General productivity assistant, not a PM/PO/BA expert. No understanding of artifact interdependencies, no workflows for RAID logs or change propagation.

**Verdict**: Office-centric, not PM-centric. And still not local-first.

### The Gap: No Privacy-First, PM-Specialized, Local Intelligence Layer

The market has task trackers. It has cloud AI assistants. It has enterprise productivity suites. What it lacks:

- **Local-first architecture** that never uploads identifiable sensitive data
- **PM-specialized intelligence** that understands RAID logs, Charters, PRDs, and how they interconnect
- **Frictionless daily workflows** optimized for artifact sync, not generic chat
- **Multi-persona expertise** that shifts between PM, PO, BA, and Product Manager as needed
- **Proactive preparation** (daily planning scripts) not just reactive updates

VPMA fills this gap.

### Target User Personas (Detailed)

#### Primary Persona: Sarah, Senior Technical PM
- **Role**: Senior PM at mid-size SaaS company, managing 3 concurrent projects (infrastructure modernization, new product feature, vendor integration)
- **Pain**: Spends 15+ hours/week on artifact upkeep. Can't upload project details to ChatGPT (company policy). Jira tracks tasks but doesn't help her draft status reports or propagate Charter changes.
- **Privacy concerns**: Projects involve unreleased features, partner names under NDA, budget figures that are board-confidential
- **Tech-savviness**: Comfortable with terminal commands, runs local dev tools, understands API concepts
- **VPMA fit**: Perfect. Local-first architecture solves privacy, Artifact Sync saves 10 hours/week, Deep Strategy ensures consistency when scope shifts.

#### Secondary Persona: Marcus, Product Manager
- **Role**: PM at B2B startup, juggling roadmap prioritization, stakeholder feedback, engineering sprints, customer research
- **Pain**: Maintains 2 PRDs, 5 feature specs, weekly product updates to exec team, monthly board decks. Inconsistencies creep in (roadmap says "Q3" but PRD says "Q2"), embarrassing in front of stakeholders.
- **Privacy concerns**: Competitive analysis, pricing strategy, customer feedback with company names
- **Tech-savviness**: Moderate. Uses Git, comfortable with config files, prefers tools over manual work.
- **VPMA fit**: Strong. Project Initiation tab accelerates PRD creation, Deep Strategy catches cross-artifact inconsistencies, Communications Assistant helps draft exec updates.

#### Tertiary Persona: Aisha, Business Analyst
- **Role**: BA at financial services firm, coordinating requirements for regulatory compliance project across legal, engineering, operations
- **Pain**: Translates between stakeholders (legal speaks one language, engineers another). Manages 100+ requirements across 3 artifacts (BRD, FRD, Traceability Matrix). Changes ripple constantly.
- **Privacy concerns**: Regulatory details, customer PII in test data, internal audit findings
- **Tech-savviness**: High. Python scripting for data analysis, comfortable with CLIs.
- **VPMA fit**: Excellent. Multi-persona mode (BA + PM) for requirement analysis, Deep Strategy for propagating requirement changes, Technical Fluency Translation to bridge legal-technical gaps.

---

## 3. Goals & Success Metrics

### User Experience Goals

#### Frictionless Daily Use
**Goal**: < 30 seconds to sync all artifacts from raw inputs.

**Measurement**: Time from "paste meeting transcript" to "all bubbles displayed in Artifact Sync tab." Target: 25-second median, 30-second 95th percentile.

**Why it matters**: If syncing artifacts takes 5 minutes, users won't do it daily. Friction kills habits. VPMA must be faster than manual updates to change behavior.

#### Zero Context Switching
**Goal**: All PM artifacts managed in one unified interface.

**Measurement**: Number of external tools/tabs user opens during typical artifact sync session. Target: 0 (user never leaves VPMA during sync, only pastes results into final destinations like Google Docs or Jira).

**Why it matters**: Context switching destroys flow. Current workflow: Open Jira → Open Google Docs → Open ChatGPT → Copy/paste between all three → Format → Check consistency. VPMA collapses this into one interface.

#### Privacy Confidence
**Goal**: 100% local processing with visible anonymization.

**Measurement**:
- User survey: "On a scale of 1-10, how confident are you that sensitive data is protected?" Target: 9+ average.
- Privacy audit: Manual review of 100 random anonymized payloads. Target: 0 PII leaks detected.

**Why it matters**: Trust is binary. One PII leak destroys confidence. Users must *see* anonymization working (preview mode, audit log) to believe it.

#### Google-Minimalist Interface
**Goal**: Clean search bar entrance, zero UI clutter.

**Measurement**: Time to first action after launch. Target: < 3 seconds (user lands on Artifact Sync tab, search bar in focus, immediately starts typing).

**Benchmark**: Google.com. You arrive, you search. No distractions. VPMA's Artifact Sync tab must feel the same.

---

### Productivity Goals

#### 70% Reduction in Artifact Maintenance Time
**Baseline**: Typical PM spends ~20 hours/week on artifacts (status reports, RAID logs, meeting notes, charters, schedules).

**Target**: ~6 hours/week post-VPMA adoption.

**Breakdown**:
- Status reports: 2 hours → 10 minutes (90% reduction via Artifact Sync)
- RAID log updates: 3 hours → 30 minutes (83% reduction via meeting transcript processing)
- Meeting prep: 6 hours → 2 hours (67% reduction via Daily Planner talking points)
- Artifact consistency checks: 4 hours → 45 minutes (81% reduction via Deep Strategy multi-pass)
- Greenfield baselines: 8 hours → 20 minutes (96% reduction via Project Initiation tab)

**Measurement**: Before/after time tracking study with 10 beta users. Weekly self-reported hours on artifact tasks. Track for 4 weeks pre-VPMA, 4 weeks post-adoption.

#### 90% Faster Status Report Generation
**Baseline**: 2 hours (gather updates from 3 projects, synthesize into executive summary, format, cross-check with RAID log for consistency).

**Target**: 10 minutes (paste recent session notes into Artifact Sync, copy Status Report bubble, paste into template, light editing).

**Measurement**: Timed task with beta users. Provide realistic scenario (3 projects, 15 pages of raw notes), measure time to completion.

#### 85% Reduction in Change Integration Errors
**Problem**: When Charter scope changes, humans forget to update Schedule, RAID Log, Status Report. Inconsistencies surface in stakeholder meetings → credibility damage.

**Baseline**: Survey 20 PMs: "How often do you discover artifact inconsistencies after publishing?" Avg response: 30% of the time.

**Target**: 5% post-Deep Strategy use.

**Measurement**: Artifact audit. Give users Charter change scenario, ask them to update all downstream artifacts using Deep Strategy, then have third party review for consistency. Error rate: target < 5%.

---

### Technical Goals

#### 100% Local Operation
**Goal**: Zero cloud dependencies beyond LLM API calls.

**Verification**: Disconnect from internet (except for api.anthropic.com / Gemini endpoint), verify full VPMA functionality: artifact sync, deep strategy, project initiation, history review.

**Exception**: LLM API calls are inherently external, but all data sent is anonymized by Privacy Proxy.

#### < 3 Seconds Per Artifact Update in Artifact Sync Mode
**Goal**: Real-time feel. User pastes input, bubbles appear nearly instantly.

**Measurement**: Time from input submission to first bubble rendered. Target: 2.5-second median, 3-second 95th percentile.

**Note**: Excludes LLM API latency (external dependency). Measures VPMA's internal processing (Privacy Proxy, context assembly, bubble generation).

#### 99.5% PII Anonymization Accuracy
**Goal**: Catch essentially all PII before it reaches LLM APIs.

**Measurement**:
- Audit dataset: 1000 sample inputs (meeting transcripts, notes, emails) with labeled PII
- Run through Privacy Proxy, measure:
  - **True Positives**: Correctly anonymized PII (target: 995+/1000 = 99.5%+)
  - **False Negatives**: Missed PII (target: < 5/1000 = 0.5%)
  - **False Positives**: Non-PII incorrectly anonymized (acceptable up to 50/1000 = 5%, user reviews via preview mode)

**Risk tolerance**: False positives (over-anonymization) are acceptable. False negatives (PII leaks) are catastrophic.

#### Multi-Provider Parity
**Goal**: Feature parity across all LLM backends (Claude, Gemini, and Local/Ollama in Phase 2+).

**Verification**: Checklist of all features (Artifact Sync, Deep Strategy, Project Initiation, Communications Assistant, etc.) function identically regardless of which LLM provider is selected.

**Exception**: Quality and speed may differ across providers (Claude is highest quality, Ollama is free but slower), but *functionality* must be identical. Recommended usage patterns documented in Section 5.4.

---

### Key Performance Indicators (KPIs)

#### Adoption Metrics
- **DAU (Daily Active Users)**: Target 30+ after 3 months (from 50+ total users = 60% daily usage rate)
- **Artifacts Synced Per Session**: Target avg 3+ (signals regular, habitual use)
- **Session Frequency**: Target 5+ sessions per user per week

#### Efficiency Metrics
- **Hours Saved Per Week**: Self-reported + time tracking. Target avg 14 hours/week saved per user (from 20 → 6 hours on artifacts).
- **Time Per Artifact Update**: Target median 30 seconds (Artifact Sync), 45 minutes (Deep Strategy), 15 minutes (Project Initiation baseline)

#### Quality Metrics
- **Artifact Completeness Score**: Checklist-based (does Status Report include all required sections: Executive Summary, Progress, Risks, etc.?). Target 95%+ complete.
- **Change Integration Accuracy**: Post-Deep Strategy consistency audit. Target 90%+ error-free (no inconsistencies detected by third-party review).
- **Privacy Accuracy**: PII detection audit. Target 99.5%+ true positive rate, < 0.5% false negative rate.

#### Satisfaction Metrics
- **NPS (Net Promoter Score)**: "How likely are you to recommend VPMA to a fellow PM?" Target 50+ (strong promoter majority).
- **CSAT (Customer Satisfaction)**: "Overall, how satisfied are you with VPMA?" 1-5 scale. Target 4.5+ average.
- **Feature Request Rate**: Target 2+ requests per user per month (signal of engagement, not frustration—users care enough to suggest improvements).

---

## 4. User Experience Design - The Six-Tab System

### Overview

VPMA's UX is organized into six specialized tabs, each optimized for a distinct PM workflow. The interface philosophy is **"Google-minimalist"**: clean, fast, zero distraction. Every tab has a clear primary action with minimal UI chrome between the user and productivity.

**The Six Tabs**:
1. **Daily Planner** - Proactive preparation engine (meeting prep, talking points, project health gaps)
2. **Artifact Sync** - Reactive update engine (meeting transcripts → artifact updates in < 30 seconds)
3. **Deep Strategy** - Change integration management (multi-pass consistency validation)
4. **Project Initiation** - Greenfield baseline generation (describe project → full artifact package)
5. **History & Context** - Memory engine (session log, context slider)
6. **Settings & Landscape** - DNA configuration (Fixed Landscape, persona toggles, privacy settings)

**Cross-Tab Features** (always accessible):
- **Communications Assistant (💬 Compose)**: On-demand help drafting Slack messages and emails with automatic project context
- **Persistent Feedback Box (📝 Feedback)**: Ever-present bug/feature/UX feedback collection

**Default Landing**: Users arrive at **Artifact Sync** (Tab 2) - the reactive update flow is the most frequent daily workflow.

---

### 4.0 Cross-Tab Features (Always Available)

Two features are accessible from any tab at any time, providing on-demand assistance and continuous feedback collection.

#### 4.0.1 Communications Assistant (💬 Compose)

**Location**: Floating action button (FAB) in header or fixed position, always visible across all tabs.

**Purpose**: On-demand help drafting Slack messages, emails, or other team communications without leaving VPMA's workflow.

**Key Feature**: **AUTOMATIC CONTEXT SHARING** - Unlike a stateless chat assistant, the Communications Assistant reads your current project/session context (project name, active artifacts, recent session summary) to provide relevant, context-aware communication drafts.

**UX Flow**:
1. User clicks 💬 icon → Opens modal with chat-style interface
2. Communication type selector appears: Quick buttons [Slack Message] [Email] [General]
3. User describes communication need in text area
   - Example: "Draft a Slack message to engineering about tomorrow's sprint planning"
4. LLM generates draft WITH automatic context:
   - Reads current project name, active artifacts (e.g., Sprint Backlog, RAID Log)
   - Includes recent updates from last session (e.g., "We discussed 3 new risks yesterday")
   - Tailors tone to channel (Slack = casual + concise, Email = formal + structured)
5. User sees draft message in chat bubble
6. Iterative refinement: User provides feedback ("make it more casual", "add bullet points")
7. LLM regenerates, chat updates in real-time
8. User clicks [Copy to Clipboard] → Pastes into Slack/email client
9. **VPMA never actually sends** - only drafts for user control

**Privacy Integration**: Privacy Proxy applies to BOTH user input AND project context (anonymize → LLM → re-identify). Final draft has real names/orgs restored.

**Use Case Example**:
- User is working on "Project Falcon" with recent RAID log entry about vendor delay
- Clicks Communications Assistant → "Draft a Slack message to engineering about tomorrow's sprint planning"
- LLM generates: "Hey team, quick reminder about sprint planning tomorrow at 10am. We'll be prioritizing stories around the ClientCo integration (see latest RAID log for vendor delay context). Please review the backlog beforehand. See you there!"
- User refines: "Make it shorter"
- LLM regenerates: "Sprint planning tomorrow 10am - prioritizing ClientCo integration. Review backlog beforehand. 👍"
- User copies and pastes into Slack

**Technical Implementation**:
- **Context Assembly**: Loads current project name from SQLite, last 5 sessions' summaries, current artifact states (last updated timestamps)
- **LLM Call**: Simple prompt-response pattern (~500-1000 tokens), no multi-pass reasoning
- **System Prompt**: "You are a communications assistant helping a PM craft clear, professional messages. You have context about their current project: [project summary]. Focus on clarity, tone, and actionable content. Tailor to the communication channel."
- **Privacy**: Anonymize context + user input → LLM call → Re-identify output
- **Persistence**: Chat history stored in React component state (useState hook), cleared when modal closed
- **UI**: Material-UI Modal/Dialog component, chat-style message display, browser Clipboard API (`navigator.clipboard.writeText()`) for copy

**User Stories**:
- As a PM, I want to quickly draft a Slack message without switching contexts or manually copying project details
- As a PM, I want help crafting a sensitive email to a stakeholder with the right professional tone
- As a PM, I want to iterate on communication drafts until they're just right
- As a PM, I want the assistant to know what I'm currently working on without re-explaining

---

#### 4.0.2 Persistent Feedback Box (📝 Feedback)

**Location**: Small floating button fixed to bottom-right corner, always visible but unobtrusive.

**Purpose**: Capture user feedback on the app itself (bugs, feature requests, UX improvements) as they occur, independent of any project or session context.

**UX Flow**:
1. User encounters bug or has feature idea while working
2. Clicks 📝 Feedback button in bottom-right corner
3. Modal opens with simple form:
   - **Feedback Type**: Radio buttons [Bug] [Feature Request] [UX Improvement] [General]
   - **Description**: Large text area for details
   - **Include Context** (optional checkbox): Auto-capture current tab name, session ID, timestamp
4. User fills description, clicks [Submit]
5. Toast confirmation appears: "Feedback logged! Thank you."
6. Feedback appended to `~/VPMA/feedback/feedback_log.md` with intelligent categorization

**Feedback Storage Structure**:
```markdown
# VPMA Feedback Log

## Bugs

### [2026-02-12 14:32] - Tab 2 (Artifact Sync)
- **Type**: Bug
- **Description**: Bubble hover doesn't expand when input text exceeds 2000 characters
- **Context**: Session ID abc123, Tab 2 (Artifact Sync)
- **Status**: Open

---

## Feature Requests

### [2026-02-12 10:15] - General
- **Type**: Feature Request
- **Description**: Add support for MS Teams meeting transcripts (currently handles Zoom/Google Meet format only)
- **Context**: Session ID xyz789, Tab 2 (Artifact Sync)
- **Status**: Pending

---

## UX Improvements

### [2026-02-11 16:45] - Tab 6 (Settings)
- **Type**: UX Improvement
- **Description**: Landscape table hard to read with 20+ rows - add search/filter
- **Context**: Tab 6 (Settings & Landscape)
- **Status**: Under Review
```

**Organization**:
- Single consolidated file: `~/VPMA/feedback/feedback_log.md`
- Auto-categorization: New feedback auto-inserted under correct heading (## Bugs, ## Feature Requests, etc.)
- Chronological within category: Most recent first (reverse-chronological)
- Status tracking: Manually updatable (Open → Pending → Under Review → Resolved → Closed)

**Technical Implementation**:
- **File Operations**: Append to markdown file with timestamp and metadata
- **Auto-Categorization**: Optional LLM call if user doesn't select type (~100 tokens to analyze description)
- **Context Capture**: If checkbox enabled, log: current tab name, session ID, project ID, timestamp
- **No Session Tracking**: Feedback exists outside session history (not logged to `sessions` table)
- **Privacy**: Feedback NOT anonymized (stays local, never sent to external services except optional LLM categorization)
- **UI**: `st.dialog()` for modal, `st.radio()` for type selection, `st.text_area()` for description, `st.toast()` for confirmation

**Future Enhancement (Phase 2+)**:
- Feedback Dashboard in Settings tab: View/manage all feedback with filtering
- Export to CSV/JSON for analysis
- LLM-powered trend analysis: "3 users requested GitHub API integration this month"

**User Stories**:
- As a PM, I want to quickly log a bug I encounter without disrupting my workflow
- As a PM, I want to suggest feature ideas as they occur to me, knowing they'll be tracked
- As a PM, I want to see my feedback organized by type so I can review what I've suggested
- As a PM, I want to contribute to the app's improvement without complex reporting

---

### 4.1 Tab 1: Daily Planner (The Proactive Preparation Engine)

**Primary Use Case**: Daily or multi-day planning - generate personalized daily scripts with meeting prep, talking points, and project health suggestions.

**What Makes This Transformative**: Shifts VPMA from reactive artifact manager to proactive daily partner. Instead of "update artifacts after meetings," it's "prepare for meetings before they happen."

**UX Flow**:

1. **Entry**: User navigates to Daily Planner tab (first tab, primary morning routine entry point)

2. **Calendar Input**:
   - **UI**: Large text area with friendly prompt: "Paste your calendar (today or multiple days)"
   - User copies calendar from Google Calendar, Outlook, or any calendar tool
   - **Format**: Free-form text with meeting times, titles, attendees (LLM parses structure)
   - **Example Input**:
     ```
     Monday, Feb 12
     9:00-9:30 AM - Weekly Steering Committee (John, Sarah, Mike)
     11:00-12:00 PM - Technical Architecture Review (Engineering team)
     2:00-3:00 PM - 1:1 with Product Owner

     Tuesday, Feb 13
     10:00-11:00 AM - Sprint Planning (Dev team)
     3:00-4:00 PM - Customer Feedback Session (ClientCo stakeholders)
     ```

3. **Timeframe Selection**:
   - **UI**: Radio buttons: ⚪ Today (single day) ⚪ This Week ⚪ Custom Range
   - Default: Today
   - Multi-day capable: User can plan entire week at once

4. **Intelligence Processing** (< 60 seconds):
   - **Privacy Proxy**: Anonymizes calendar content (names, meeting titles with proprietary terms)
   - **LLM Analysis** for each meeting:
     - **Landscape Matching**: Fuzzy match meeting title to Fixed Landscape entries
       - Example: "Weekly Steering Committee" → Finds associated artifacts: Status Report, RAID Log
     - **Artifact Freshness Check**: Query SQLite for `artifacts.last_updated` timestamps
       - Example: RAID Log last updated 4 days ago → Flag as stale
     - **Project Health Gaps**: Identify pending items, unresolved risks, outdated artifacts
     - **Prep Package Generation**: Create personalized preparation for each meeting
   - **Context Assembly**: Load last 5 sessions + current artifact state for relevant artifacts
   - **Batch Efficiency**: Generate prep for ALL meetings in one LLM call (reduce API overhead)

5. **Output - The Daily Script**:

   **UI**: Structured document with collapsible sections per day, then per meeting

   **Day Header Example**:
   ```
   📅 Monday, Feb 12 - 3 meetings, 2 recommended work blocks
   ```

   **Per Meeting Section**:

   **Meeting Title & Time**: "9:00-9:30 AM - Weekly Steering Committee"

   **Suggested Agenda** (with [Copy] button):
   - Pre-populated from recurring meeting agenda artifact (if exists in Fixed Landscape)
   - Or generated based on meeting title + current project context
   - Example Output:
     ```
     1. Review last week's progress (5 min)
     2. Discuss new RAID log risks (10 min) - especially vendor delay impacting timeline
     3. Budget update request (10 min) - need approval for additional resource
     4. Next week priorities (5 min)
     ```

   **Talking Points** (with [Copy] button):
   - Context-aware bullets based on current project state
   - Example Output:
     ```
     - ✅ Highlight: Completed Phase 1 milestone (2 days ahead of schedule)
     - ⚠️ Concern: Vendor delay (RAID#R3) may push Phase 2 by 1 week - mitigation plan ready
     - 💰 Ask: Budget approval for additional QA resource ($15K) - justification in Status Report
     - 📊 FYI: Customer feedback session scheduled for Tuesday with ClientCo
     ```

   **Personal Context Notes** (with [Copy] button):
   - Follow-ups from previous meetings or action items
   - Example Output:
     ```
     - Follow up with John on risk mitigation plan from last week's meeting
     - Confirm Sarah received updated timeline (sent Friday)
     - Mike requested cost breakdown - bring budget spreadsheet
     ```

   **Artifacts to Bring**:
   - Visual list with icons: 📋 [RAID Log] 📊 [Status Report] 💰 [Budget Spreadsheet]
   - Click artifact name → Opens quick preview modal (shows current version without leaving Daily Planner)

   **Recommended Work Blocks** (between meetings):
   - **UI**: Suggested time slots for project health maintenance
   - Example Output:
     ```
     🕙 10:00-11:00 AM: Update RAID log
        - Last updated 4 days ago
        - 2 new risks identified from Slack thread (vendor delay, resource gap)
        - Estimated time: 15 minutes
        [Copy to Calendar]

     🕐 1:00-2:00 PM: Prepare Architecture Review talking points
        - Review technical design doc (uploaded yesterday)
        - Align with current project timeline
        - Estimated time: 30 minutes
        [Copy to Calendar]
     ```

6. **Iterative Refinement**:
   - User can provide feedback in conversational style
   - Example: "Add more technical detail to Architecture Review talking points"
   - LLM regenerates specific section, UI updates in real-time

7. **Export/Copy Options**:
   - **[Copy Full Script]**: Copies entire daily script to clipboard (markdown format)
   - **[Export to PDF]**: Generates formatted PDF for printing or annotating
   - **[Export to Markdown]**: Saves as .md file for import into note-taking apps
   - **Individual Section Copy**: Each meeting section and work block has own [Copy] button

**Technical Implementation**:
- **Calendar Parsing**: LLM extracts structured data (times, titles, attendees) from free-form text
- **Landscape Matching**: String similarity algorithm (Levenshtein distance) to match meeting titles to Fixed Landscape entries
- **Artifact Freshness Query**: SQL: `SELECT artifact_type, last_updated FROM artifacts WHERE project_id = ? ORDER BY last_updated ASC`
- **Context Assembly**: For each relevant artifact, load last 5 session summaries + current content preview (first 500 characters)
- **Multi-Meeting Orchestration**: Single LLM call with structured JSON output:
  ```json
  {
    "days": [
      {
        "date": "Monday, Feb 12",
        "meetings": [
          {
            "time": "9:00-9:30 AM",
            "title": "Weekly Steering Committee",
            "agenda": ["Review progress", "Discuss risks", ...],
            "talking_points": ["Completed Phase 1", "Vendor delay concern", ...],
            "personal_notes": ["Follow up with John", ...],
            "artifacts_to_bring": ["RAID Log", "Status Report"]
          }
        ],
        "work_blocks": [
          {
            "time": "10:00-11:00 AM",
            "task": "Update RAID log",
            "reason": "Last updated 4 days ago...",
            "estimated_time": "15 minutes"
          }
        ]
      }
    ]
  }
  ```
- **Export Engine**: `python-docx` for PDF generation, native markdown for .md export
- **Performance Target**: < 60 seconds from paste to full daily script display

**User Stories**:
- As a PM, I want to paste my calendar and get a complete daily script in under 60 seconds
- As a PM, I want suggested agendas for recurring meetings based on current project state, not generic templates
- As a PM, I want to know which artifacts to bring to each meeting without manually checking
- As a PM, I want talking points that reflect recent project developments so I'm always prepared
- As a PM, I want project health suggestions (stale artifacts, pending tasks) proactively identified with time blocks to address them

---

### 4.2 Tab 2: Artifact Sync (The Reactive Update Engine)

**Primary Use Case**: Daily artifact maintenance from raw inputs - meeting transcripts, meeting notes, Slack threads, email updates, screenshots.

**What Makes This Core**: This is the most frequent daily workflow (hence default landing tab). Designed for speed and frictionlessness.

**Copy-to-Clipboard Rationale**: User's live artifacts (Google Docs, Excel, Confluence, etc.) may not be accessible to VPMA. Copy-to-clipboard allows manual paste into actual artifact locations while maintaining privacy and user control.

**UX Flow**:

1. **Entry**: User lands on clean, branded search bar (Google-style minimalism)
   - **UI**: Large text area in focus with hint text: "Paste meeting notes, transcript, or describe updates..."
   - **Alternative Inputs**: File upload button (for screenshots), microphone icon (future: voice memo transcription)

2. **Input Types** (LLM auto-detects):
   - **Meeting Transcript** (PRIMARY - most common input):
     - Contains speaker labels ("John:", "Sarah:"), timestamps ("[00:15:23]"), conversational format
     - Triggers comprehensive processing: Meeting Notes artifact + Artifact updates + GitHub task suggestions
   - **Meeting Notes** (manual summaries):
     - Prose description of meeting outcomes
     - Triggers artifact updates only
   - **Slack Thread Screenshot**:
     - Image file with OCR via pytesseract
     - Extracted text processed as general update
   - **Email Update**:
     - Copy/paste from email client
     - Processed as general update
   - **Free-Form Update**:
     - User types quick note ("Vendor confirmed delivery date pushed to March 15")
     - Processed as general update

3. **Intelligence Processing** (< 30 seconds target):

   **Step 1: Input Classification**
   - First LLM pass detects input type (transcript vs. notes vs. general)
   - Transcript detection signals: speaker labels, timestamps, back-and-forth conversation

   **Step 2: Persona Determination**
   - LLM analyzes content to determine required professional roles
   - Example: Risk identification → PM + BA personas
   - Example: Feature discussion → PO + Product Manager personas
   - Uses enabled personas from Settings (all enabled by default)

   **Step 3: Artifact Pattern Matching**
   - LLM identifies which artifacts need updates
   - Matches content to artifact types:
     - New risks mentioned → RAID Log update
     - Progress discussed → Status Report update
     - Decisions made → Decision Log update
     - Tasks assigned → Action Item Log + GitHub task suggestions

   **Step 4: Delta Extraction**
   - Compare current artifact state vs. new information
   - Extract only what's new or changed
   - Example: RAID Log has 5 existing risks, input mentions 2 new ones → Extract only the 2 new risks

   **Step 5: Special Processing for Meeting Transcripts**:
   - **Meeting Notes Generation**: Extract attendees, discussion summary, decisions, action items, follow-up topics
   - **GitHub Task Suggestions**:
     - Identify action items that should become GitHub issues
     - Format: Title, Description, Suggested Labels, Assignee (if mentioned in transcript)
     - Distinguish: New tasks vs. notes for existing tasks (if issue number mentioned)
   - **Technical Fluency Translation** (if toggle enabled):
     - Flag technical jargon or architecture discussions
     - Generate PM-friendly explanations in separate section

4. **Output - The Interactive Pulse**:

   **UI**: Clean list of collapsible bubbles, prioritized by expert judgment (critical → important → FYI)

   **Bubble Structure**: `[Artifact Name] • [Change Type] • [Confidence Score]`

   **Example Bubbles**:
   ```
   🔴 RAID Log • 3 New Risks • High Confidence
   🟡 Status Report • Progress Update • High Confidence
   🟢 Meeting Notes • Complete Summary • High Confidence
   🟡 Project Plan • Budget Update • High Confidence
   🟡 Tasks • 3 New Tasks + 2 Updates • High Confidence
   🟡 GitHub Tasks • 4 New Suggestions • Medium Confidence
   🟢 Action Items • 5 New Items • High Confidence
   ```

   **Confidence Display Philosophy**: Only show confidence score when LOW (<70%) to avoid UI clutter
   - High confidence (≥70%): Don't show score, just artifact name and change type
   - Low confidence (<70%): Show "⚠️ Low Confidence" warning

   **Bubble Interaction**:
   - **Hover**: Bubble expands to show preview of updated text
   - **Click**: Opens with TWO action buttons:
     - **[Copy]**: Copies full update text to clipboard (for manual paste into external artifacts like Google Docs)
     - **[Apply]**: Shows preview modal → User reviews change → Confirms → Updates VPMA's SQLite database

   **Visual Hierarchy**:
   - Color-coded by urgency: 🔴 Red = Critical, 🟡 Yellow = Important, 🟢 Green = FYI
   - Sorted by priority (critical first, FYI last)

   **Discrepancy Warning**:
   - If LLM output deviates from user request, show subtle footer below bubbles:
   - "⚠️ Note: This update may deviate from your original request. Review carefully before applying."

   **Special Bubble - GitHub Tasks** (when transcript detected):
   - Expands to show two subsections:
     - **New Task Suggestions**:
       ```
       **Task 1: Implement user authentication refactor**
       - Description: Refactor auth to support OAuth2 and JWT tokens as discussed
       - Labels: enhancement, backend
       - Assignee: @john (mentioned as owner)

       **Task 2: Fix database connection pool issue**
       - Description: Investigate connection pool exhaustion under load
       - Labels: bug, database, high-priority
       - Assignee: @sarah
       ```
     - **Notes for Existing Tasks**:
       ```
       **Issue #234 (API migration)**: Mike mentioned 60% complete, on track for Friday deadline
       ```
   - [Copy All Tasks] button: Copies markdown-formatted task list to clipboard
   - **MVP**: Manual copy/paste to GitHub
   - **Phase 2+**: Direct GitHub API integration for one-click issue creation

   **Special Bubble - Tasks / Work Items**:
   - Expands to show three subsections:
     - **New Tasks Suggested**:
       ```
       **Task: Complete API documentation**
       - Owner: Sarah
       - Due: Feb 20, 2026
       - Priority: P1-High
       - Estimated Effort: 8 hours
       - Dependencies: API finalization (Task #45)

       **Task: Set up staging environment**
       - Owner: DevOps Team
       - Due: Feb 15, 2026
       - Priority: P0-Critical
       - Estimated Effort: 2 days
       - Notes: Requires AWS account provisioning
       ```
     - **Updates to Existing Tasks**:
       ```
       **Task #12 (Database migration)**: 60% complete, on track for delivery
       **Task #18 (Security audit)**: BLOCKED - awaiting vendor response, due date at risk
       **Task JIRA-456 (Performance optimization)**: Completed ahead of schedule
       ```
     - **Refinements**:
       ```
       **Task #22**: Increase priority from P2 to P1 (critical path dependency identified)
       **Task #35**: Reassign from John to Mike (John on PTO next week)
       ```
   - [Copy All Tasks] button: Copies markdown/CSV-formatted task list to clipboard
   - **MVP**: Manual paste into Jira, Asana, Monday, Linear, Trello, or spreadsheets
   - **Phase 2+**: Direct API integrations for one-click task creation/updates across platforms

5. **Technical Fluency Translation** (if toggle enabled):
   - Additional collapsible section below bubbles: "🎓 Technical Translation"
   - **Purpose**: Help PMs build technical fluency by explaining technical jargon in PM-friendly language
   - **Example Content**:
     ```
     🎓 Technical Translation

     "Refactor the monolith into microservices"
     → The team wants to break our single large application into smaller, independent services.
       This will slow initial development but make future changes faster and more reliable.

     "Implement JWT-based authentication"
     → Switch to a token-based login system that's more secure and works better for mobile apps.
       Users will stay logged in longer without compromising security.

     "Database connection pool exhaustion"
     → The app is running out of database connections under heavy load, causing slowdowns.
       We need to optimize how we manage database access.
     ```
   - [Copy] button to save translations for personal learning notes
   - Session-level toggle in app header (quick on/off without going to Settings)

6. **Iterative Refinement**:
   - User can provide conversational feedback below bubbles
   - Example: "Make the status report more executive-focused, less technical detail"
   - LLM regenerates that specific bubble, UI refreshes in real-time
   - Other bubbles remain unchanged (targeted refinement)

7. **Commit** - "Log Session" Button:
   - Finalizes all applied changes:
     - Updates SQLite `artifacts` table (last_updated timestamps)
     - Updates markdown artifact files in `~/VPMA/artifacts/*.md`
     - Creates new `sessions` record with summary, inputs, outputs
   - Archives session to History tab (accessible via Tab 5)
   - Clears input area for next sync
   - Toast confirmation: "Session logged! 4 artifacts updated."

**Technical Implementation**:

**Input Classification** (First LLM Pass):
```python
# Detect input type
prompt = """
Analyze this input and classify:
1. Type: [transcript|notes|general_update]
2. Has_speaker_labels: [true|false]
3. Has_timestamps: [true|false]

Input: {user_input}

Return JSON: {"type": "...", "has_speaker_labels": ..., "has_timestamps": ...}
"""
```

**Pattern Matching** (Second LLM Pass):
```python
# Identify artifacts needing updates
system_prompt = """
You are a PM assistant. Given this input, identify which PM artifacts need updates.
Available artifacts: RAID Log, Status Report, Project Charter, Meeting Notes, Decision Log, Action Items, PRD, User Stories.

Return JSON list: [{"artifact_type": "RAID Log", "change_type": "3 New Risks", "confidence": 0.95, "preview": "..."}]
"""
```

**Delta Extraction**:
- Load current artifact content from `~/VPMA/artifacts/{artifact_type}.md`
- LLM compares current vs. new information, extracts only deltas
- Example: Current RAID Log has risks R1-R5, input mentions 2 new risks → Output: R6, R7 only

**Confidence Scoring**:
- Based on clarity of input and specificity of artifact updates
- High (≥0.7): Clear, unambiguous extraction
- Medium (0.5-0.7): Some interpretation required
- Low (<0.5): Ambiguous, may need user review

**Real-Time Streaming**:
- Use Server-Sent Events (SSE) or WebSocket for live bubble updates as LLM generates
- React: useState hook with incremental updates, display spinner while loading
- Shows "Processing..." spinner → Bubbles appear one-by-one as LLM returns each update

**Meeting Transcript Processing** (when detected):
```python
# Extract structured data
meeting_data = {
    "attendees": ["John", "Sarah", "Mike"],
    "discussion_topics": ["Budget review", "Risk assessment", "Timeline update"],
    "decisions": ["Approved $15K budget increase", "Postponed vendor selection to March"],
    "action_items": [
        {"task": "Update RAID log", "owner": "Sarah", "due": "Friday"},
        {"task": "Draft vendor RFP", "owner": "Mike", "due": "Next week"}
    ],
    "technical_discussions": [
        {"topic": "Database migration", "context": "Move from monolith to microservices"}
    ]
}

# Generate outputs
outputs = {
    "meeting_notes": generate_meeting_notes(meeting_data),
    "artifact_updates": extract_artifact_deltas(meeting_data),
    "github_tasks": extract_github_tasks(meeting_data),
    "tech_fluency": translate_technical_jargon(meeting_data["technical_discussions"])  # if enabled
}
```

**Performance Optimization**:
- Target: < 30 seconds from input submission to bubbles displayed
- Parallel LLM calls where possible (input classification + pattern matching can run concurrently)
- Cache system prompts (don't re-send identical prompt structure each time)
- Token counting: `tiktoken` library for accurate cost estimation

**User Stories**:
- As a PM, I want to paste my meeting transcript and see which artifacts need updates in < 30 seconds
- As a PM, I want to get structured meeting notes automatically without manual summarization
- As a PM, I want to see GitHub task suggestions based on what was discussed
- As a PM, I want to hover over updates to quickly review before committing to database
- As a PM, I want to iteratively refine updates with conversational feedback
- As a PM, I want to understand technical discussions by enabling Technical Fluency Translation
- As a PM, I want to copy updates to clipboard for manual paste into Google Docs/Confluence while maintaining privacy

---

### 4.3 Tab 3: Deep Strategy (Change Integration Management)

**Primary Use Case**: High-rigor change propagation across interconnected artifacts - when Charter scope changes, ensure Schedule, RAID Log, Status Report, Communications Plan all reflect that change with absolute consistency.

**What Makes This Critical**: Humans forget. When you update the Project Charter to add a new deliverable, you might forget to update the Schedule, which means the RAID Log doesn't reflect new timeline risks, which means the Status Report shows outdated scope. VPMA's Deep Strategy catches all downstream impacts.

**UI Inversion**: High-contrast color shift (dark mode or inverted palette) to signal "Deep Thinking" mode - user knows this is slower, more rigorous processing.

**UX Flow**:

1. **UI Inversion**: Tab background shifts to dark mode or inverted color scheme
   - Visual signal: "You're entering Deep Strategy mode - this will take longer but ensure perfect consistency"
   - Optional toggle: "Fast Mode" (single-pass, 30 seconds) vs. "Deep Mode" (multi-pass, 2-10 minutes)

2. **Artifact Upload**:
   - **Prompt**: "Upload the latest versions of all relevant artifacts"
   - **UI**: Drag-and-drop zone + file browser
   - **Supported Formats**: DOCX, PDF, Markdown, Excel/CSV, Google Sheets export
   - **Typical Upload Set**:
     - Project Charter (docx or md)
     - Project Schedule (Excel or CSV)
     - RAID Log (Excel or CSV)
     - Status Report (docx or md)
     - PRD (if product project)
     - Communications Plan (docx or md)
   - **Privacy**: All uploaded files processed locally, content anonymized before LLM analysis

3. **Priority Sequencing**:
   - **Prompt**: "Define the review order (changes flow downward)"
   - **UI**: Drag-and-drop list to reorder artifacts
   - **Default Order**: Charter → Schedule → RAID Log → Status Report → PRD → User Stories
   - **Purpose**: Defines propagation hierarchy
     - Example: If Charter comes first, its changes are "truth" and downstream artifacts must align
     - Example: If Schedule updated first, then Charter, LLM will flag inconsistencies both ways
   - **User Control**: Allows PM to set priority based on what changed
     - Scenario 1: Charter scope expanded → Put Charter first, others adapt
     - Scenario 2: Timeline slipped in Schedule → Put Schedule first, Charter/RAID reflect timeline impact

4. **Multi-Pass Reasoning** (Progress Bar Visible):

   **Pass 1: Dependency Graph Construction** (~30 seconds)
   - LLM reads all artifacts (anonymized content)
   - Builds relationship map:
     ```
     Charter (Scope: 5 deliverables, Timeline: 6 months, Budget: $500K)
       ↓ influences
     Schedule (6 phases, 24 milestones, 18 dependencies)
       ↓ influences
     RAID Log (12 risks, 8 assumptions, 3 issues)
       ↓ influences
     Status Report (Executive summary, Progress, Risks, Timeline)
     ```
   - Progress indicator: "Pass 1/4: Building dependency graph..."

   **Pass 2: Inconsistency Detection** (~1-2 minutes)
   - LLM cross-references all artifact pairs
   - Flags conflicts:
     - ⚠️ Charter says "6 deliverables" but Schedule only has 5 → Missing deliverable in Schedule
     - ⚠️ Schedule milestone "Phase 2 complete" dated June 30 but Status Report says "Phase 2 complete by end of Q2" (Q2 ends June 30) → Consistent, no flag
     - ⚠️ RAID Log risk R3 "Budget overrun" but Charter shows $50K buffer → Inconsistent risk severity
   - Progress indicator: "Pass 2/4: Detecting inconsistencies... (15 found)"

   **Pass 3: Proposed Updates Generation** (~2-4 minutes)
   - For each inconsistency, LLM generates specific fix
   - Uses priority order to determine which artifact changes:
     - Example: Charter is priority 1, Schedule is priority 2 → Charter scope is "truth", Schedule must add 6th deliverable
   - Generates diff-style updates:
     ```
     SCHEDULE UPDATE:

     Section: Deliverables

     CURRENT:
     - Deliverable 1: User Authentication
     - Deliverable 2: Payment Gateway
     - Deliverable 3: Admin Dashboard
     - Deliverable 4: Reporting Module
     - Deliverable 5: Mobile App

     PROPOSED (add):
     - Deliverable 6: API Integration Layer  [NEW - from Charter]
     ```
   - Progress indicator: "Pass 3/4: Generating proposed updates... (8 artifacts affected)"

   **Pass 4: Cross-Validation** (~1-2 minutes)
   - LLM re-reads all artifacts WITH proposed changes applied
   - Verifies absolute consistency:
     - ✅ Charter scope matches Schedule deliverables
     - ✅ Schedule milestones align with RAID Log timeline risks
     - ✅ Status Report timeline section matches Schedule phases
   - If any inconsistency remains → Flag for manual review (rare, indicates complex conflict)
   - Progress indicator: "Pass 4/4: Cross-validating consistency... (100% consistent)"

5. **Output - Integration Report**:

   **UI**: Tabbed view with one tab per artifact

   **Tab Per Artifact**:
   - **Tab Label**: "📋 RAID Log (3 updates)" (shows number of proposed changes)
   - **Tab Content**:

     **Section 1: Detected Changes from Upstream**
     ```
     Changes from Charter (Priority 1):
     - Scope expanded: Added "API Integration Layer" deliverable
     - Budget increased: $500K → $550K

     Changes from Schedule (Priority 2):
     - Phase 2 completion pushed: June 30 → July 15
     ```

     **Section 2: Proposed Updates** (Diff-Style Highlighting)
     ```
     SECTION: Risks

     CURRENT:
     R3 | Budget Overrun | Medium | $50K buffer may be insufficient | Monitor monthly

     PROPOSED:
     R3 | Budget Overrun | Low | $100K buffer (increased from $50K) | Monitor monthly  [UPDATED]

     NEW:
     R7 | API Integration Complexity | Medium | New deliverable adds integration risk | Conduct vendor assessment by March 1  [NEW RISK]
     ```
     - **Color Coding**: Red strikethrough = removed, Green highlight = added, Yellow = modified

     **Section 3: Consistency Checks**
     ```
     ✅ Aligned with Charter scope (6 deliverables)
     ✅ Aligned with Schedule timeline (Phase 2 now July 15)
     ⚠️ RAID Log has 12 risks, recommended 15+ for project of this complexity (suggestion: add resource risk)
     ```

     **Section 4: Accept/Reject Controls**
     - [ ] Accept All (checkbox)
     - Individual update checkboxes (user can cherry-pick which changes to apply)

   **Summary Tab** (First Tab):
   - **Integration Overview**:
     ```
     📊 Deep Strategy Results

     Artifacts Analyzed: 6
     Inconsistencies Found: 15
     Proposed Updates: 23 (across 4 artifacts)
     Consistency After Updates: 100%

     Affected Artifacts:
     - Schedule: 8 updates (6 new milestones, 2 dependency changes)
     - RAID Log: 3 updates (1 modified risk, 2 new risks)
     - Status Report: 7 updates (executive summary, timeline section, risks)
     - Communications Plan: 5 updates (stakeholder matrix, meeting cadence)

     Unaffected Artifacts:
     - Charter: 0 updates (this was priority 1, source of truth)
     - PRD: 0 updates (no scope changes affecting product requirements)
     ```
   - **[Integrate All Changes]** button (applies all accepted updates across all artifacts)
   - **[Export Integration Report]** button (generates PDF summary for stakeholder review)

6. **Commit - "Integrate Changes" Button**:
   - Applies all accepted updates to artifact markdown files
   - Updates SQLite `artifacts` table (last_updated timestamps, version increments)
   - Generates updated artifact files in `~/VPMA/artifacts/`
   - Optional: Export updated artifacts to DOCX/PDF for distribution
   - Logs integration session to History tab:
     ```
     SESSION: Deep Strategy Integration
     Date: Feb 12, 2026 3:42 PM
     Duration: 8 minutes
     Artifacts Analyzed: 6
     Changes Applied: 23
     Consistency: 100%
     ```
   - Toast confirmation: "Integration complete! 4 artifacts updated with 23 changes."

**Technical Implementation**:

**Document Parsing**:
```python
def parse_artifact(file_path):
    if file_path.endswith('.docx'):
        return parse_docx(file_path)  # python-docx
    elif file_path.endswith('.pdf'):
        return parse_pdf(file_path)   # PyPDF2
    elif file_path.endswith(('.xlsx', '.csv')):
        return parse_excel(file_path)  # pandas
    elif file_path.endswith('.md'):
        return read_markdown(file_path)
    else:
        raise ValueError(f"Unsupported format: {file_path}")
```

**Dependency Graph**:
```python
# Simplified structure
dependency_graph = {
    "Charter": {
        "content": {...},
        "influences": ["Schedule", "RAID Log", "Communications Plan", "PRD"]
    },
    "Schedule": {
        "content": {...},
        "influences": ["RAID Log", "Status Report"],
        "influenced_by": ["Charter"]
    },
    # ...
}
```

**Multi-Pass LLM Calls**:
```python
# Pass 1: Dependency graph
graph = llm_call(
    system="Build a dependency graph from these artifacts",
    input=anonymized_artifacts,
    output_format="json"
)

# Pass 2: Inconsistency detection
inconsistencies = llm_call(
    system="Identify all inconsistencies based on this dependency graph",
    input={"graph": graph, "priority_order": user_defined_order},
    output_format="json_list"
)

# Pass 3: Proposed updates
updates = llm_call(
    system="Generate specific text updates to resolve each inconsistency",
    input={"inconsistencies": inconsistencies, "priority_order": user_defined_order},
    output_format="json_per_artifact"
)

# Pass 4: Cross-validation
validation = llm_call(
    system="Verify 100% consistency after applying proposed updates",
    input={"original_artifacts": anonymized_artifacts, "proposed_updates": updates},
    output_format="json_validation_report"
)
```

**Diff Generation**:
- Use Python `difflib` library for side-by-side text comparison
- Highlight: `<span style="color: red; text-decoration: line-through;">removed text</span>`
- Highlight: `<span style="background-color: lightgreen;">added text</span>`

**Performance**:
- **No Strict Target**: Deep Strategy is intentionally slower (2-10 minutes depending on complexity)
- **Progress Bar**: Show "Pass 1/4... Pass 2/4..." to manage user expectations
- **Async Processing**: FastAPI natively supports async/await, LLM calls run asynchronously without blocking the server, React displays progress updates via API polling or WebSocket

**User Stories**:
- As a PM, I want to update my Project Charter and see exactly how it affects my Schedule, RAID Log, and Status Report
- As a PM, I want to ensure absolute consistency across all artifacts before stakeholder reviews
- As a PM, I want to see specific text changes (diffs) before committing updates
- As a PM, I want to choose which artifacts are "source of truth" via priority sequencing
- As a PM, I want confidence that no inconsistencies slip through (100% cross-validation)

---

### 4.4 Tab 4: Project Initiation (The Greenfield Engine)

**Primary Use Case**: Starting a new project from scratch - generate a complete baseline artifact package in minutes instead of hours.

**What Makes This Valuable**: The hardest part of any project is the beginning. Blank page paralysis. VPMA's Project Initiation tab gives you 80% of your baseline artifacts in 15 minutes, freeing you to focus on the 20% that requires human judgment.

**UX Flow**:

1. **Entry**: User clicks "New Project" button in header or navigates to Tab 4

2. **Project Description**:
   - **Prompt**: "Describe your new initiative (1 paragraph to several pages)"
   - **UI**: Large text area (expandable, supports markdown formatting)
   - **Optional Upload**: Attach requirements doc, proposal, RFP, or stakeholder brief
   - **Example Input**:
     ```
     We're launching a B2B SaaS platform for inventory management targeting
     mid-size retail companies. The platform will integrate with existing POS
     systems (Square, Shopify, Clover), provide real-time inventory tracking
     across multiple locations, and offer predictive analytics for demand
     forecasting. Target launch: Q3 2026. Budget: $750K. Team: 2 engineers,
     1 designer, 1 PM (me), 1 QA. Key stakeholders: VP Product, CFO, Head of Sales.
     ```

3. **Intelligent Analysis** (~30 seconds):
   - **Project Type Classification**: LLM analyzes description to categorize
     - Example: "B2B SaaS platform" → Software Development Project
     - Other types: Hardware, Marketing Campaign, Infrastructure, Process Improvement
   - **Artifact Recommendations**: Based on project type, suggest artifact set
     - Software Project → Charter, Schedule, PRD, RAID Log, Communications Plan, User Stories, Feature Specs
     - Marketing Campaign → Charter, Timeline, Budget, Stakeholder Register, Creative Brief, Metrics Dashboard
   - **Stakeholder Meeting Suggestions**: Recommend kickoff meetings with agenda templates
     - Example: "Kickoff with VP Product and CFO (agenda: project scope, budget approval, success criteria)"
   - **Risk Category Scaffolding**: Preliminary RAID Log structure based on project domain
     - Software → Risks: Technical complexity, Resource availability, Vendor dependencies
     - Marketing → Risks: Budget overrun, Timeline delays, Audience targeting accuracy

4. **Artifact Selection**:
   - **UI**: Checklist of recommended artifacts (all checked by default)
   - **Example Display**:
     ```
     ✅ Project Charter (1 page)
     ✅ Project Schedule (6 phases, ~24 milestones)
     ✅ RAID Log (template with 5 common risk categories)
     ✅ PRD - Product Requirements Document (5-8 pages)
     ✅ User Stories / Backlog (15-20 stories)
     ✅ Communications Plan (stakeholder matrix, meeting cadence)
     ⬜ Feature Specifications (optional, can generate later)
     ⬜ Technical Design Doc (optional, for engineering team)
     ```
   - User can uncheck artifacts they don't need
   - Estimated generation time displayed: "~5 minutes for 6 artifacts"

5. **Baseline Generation** (~5 minutes with progress indicator):

   **LLM Processing**:
   - Load project-type-specific templates from `templates/{project_type}/`
   - Fill templates with project-specific content from description
   - Single LLM call with structured JSON output:
     ```json
     {
       "charter": {
         "objective": "Launch B2B SaaS inventory platform by Q3 2026",
         "scope_in": ["POS integration", "Multi-location tracking", "Predictive analytics"],
         "scope_out": ["Direct POS sales", "Hardware inventory devices"],
         "success_criteria": ["50 beta customers", "95% uptime", "<2s page load"],
         "stakeholders": ["VP Product", "CFO", "Head of Sales"],
         "timeline": "Q3 2026",
         "budget": "$750K"
       },
       "schedule": {
         "phases": [
           {"name": "Discovery & Planning", "duration": "4 weeks", "milestones": [...]},
           {"name": "Design & Prototyping", "duration": "6 weeks", "milestones": [...]},
           // ...
         ]
       },
       "raid_log": {
         "risks": [
           {"id": "R1", "description": "POS integration complexity", "probability": "Medium", "impact": "High", "mitigation": "Conduct vendor API assessment in Week 1"},
           // ...
         ],
         "assumptions": [
           {"id": "A1", "description": "Square/Shopify APIs remain stable", "validation": "Monitor API changelog weekly"}
         ]
       },
       // ... PRD, User Stories, Communications Plan
     }
     ```

   **Progress Indicator**:
   ```
   Generating baseline artifacts...
   ✅ Project Charter complete (1 page)
   ✅ Project Schedule complete (6 phases, 22 milestones)
   🔄 RAID Log in progress... (3/5 risk categories)
   ⏳ PRD queued...
   ⏳ User Stories queued...
   ⏳ Communications Plan queued...
   ```

6. **Output - Baseline Package**:

   **UI**: Accordion view with one expandable section per artifact

   **Per Artifact Section**:
   - **Header**: "📋 Project Charter (1 page)" [Expand ▼]
   - **Expanded View**:
     - **Generated Content** (editable text area with markdown formatting):
       ```markdown
       # Inventory SaaS Platform - Project Charter

       ## Objective
       Launch a B2B SaaS platform for inventory management targeting mid-size
       retail companies by Q3 2026.

       ## Scope
       ### In Scope
       - POS system integration (Square, Shopify, Clover)
       - Real-time inventory tracking across multiple locations
       - Predictive analytics for demand forecasting
       - Web-based dashboard (desktop + mobile responsive)

       ### Out of Scope
       - Direct POS sales functionality (focus on inventory only)
       - Hardware inventory scanning devices (software-only solution)
       - International markets (US only for MVP)

       ## Success Criteria
       - 50 beta customers onboarded by Q3 2026
       - 95%+ platform uptime SLA
       - < 2 second page load time for dashboards
       - Positive NPS (>30) from beta cohort

       ## Stakeholders
       - **Sponsor**: VP Product (Sarah Johnson)
       - **Budget Approver**: CFO (Michael Chen)
       - **Go-to-Market Partner**: Head of Sales (Alex Rodriguez)
       - **Project Manager**: [Your Name]

       ## Constraints
       - **Timeline**: 6 months (Q3 2026 launch)
       - **Budget**: $750K (includes team, infrastructure, tools)
       - **Team**: 2 engineers, 1 designer, 1 PM, 1 QA (5 FTEs)
       ```
     - **Action Buttons**:
       - **[Copy to Clipboard]**: Copies markdown content
       - **[Export as DOCX]**: Downloads formatted Word document
       - **[Export as PDF]**: Downloads formatted PDF
       - **[Edit Inline]**: Makes text area editable for refinement

7. **Iterative Refinement**:
   - User can provide feedback per artifact or globally
   - **Per-Artifact Refinement**: Below each section, small text input:
     - Example: "Make the Charter more technical, add acceptance criteria for each deliverable"
     - LLM regenerates just that artifact, accordion updates
   - **Global Refinement**: Below all artifacts:
     - Example: "Reduce timeline from 6 months to 4 months across all artifacts"
     - LLM regenerates ALL artifacts with adjusted timelines, schedules, risk mitigations

8. **Commit - "Save Baseline" Button**:
   - Creates new project in SQLite `projects` table:
     ```sql
     INSERT INTO projects (project_id, project_name, created_at, landscape_config)
     VALUES (uuid(), "Inventory SaaS Platform", "2026-02-12 15:30:00", {...})
     ```
   - Saves all artifacts as markdown files:
     ```
     ~/VPMA/artifacts/inventory_saas_platform/
       ├── project_charter.md
       ├── project_schedule.md
       ├── raid_log.md
       ├── prd.md
       ├── user_stories.md
       └── communications_plan.md
     ```
   - Inserts artifact metadata into `artifacts` table (artifact_type, last_updated, version)
   - Initializes History for this project (empty session log)
   - Initializes Fixed Landscape with default artifact/meeting mappings
   - Toast confirmation: "Baseline saved! 6 artifacts created for Inventory SaaS Platform."
   - Redirects user to Artifact Sync tab (Tab 2) to start daily workflow

**Technical Implementation**:

**Project Type Classification**:
```python
# LLM call
project_type = llm_call(
    system="Classify this project description into one category: [software, hardware, marketing, infrastructure, process_improvement, other]",
    input=user_description,
    output_format="json"
)
# Returns: {"type": "software", "confidence": 0.92}
```

**Template Library**:
```
templates/
  ├── software_project/
  │   ├── project_charter.md
  │   ├── prd.md
  │   ├── raid_log.json
  │   └── user_stories.md
  ├── marketing_campaign/
  │   ├── project_charter.md
  │   ├── creative_brief.md
  │   └── stakeholder_register.md
  └── ...
```

**Template Metadata** (JSON):
```json
{
  "artifact_type": "Project Charter",
  "project_types": ["software", "hardware", "marketing"],
  "sections": ["Objective", "Scope", "Deliverables", "Success Criteria", "Stakeholders", "Constraints"],
  "placeholders": {
    "PROJECT_NAME": "string",
    "OBJECTIVE": "string",
    "SCOPE_IN": "list",
    "SCOPE_OUT": "list",
    "SUCCESS_CRITERIA": "list",
    "STAKEHOLDERS": "list",
    "TIMELINE": "string",
    "BUDGET": "string"
  }
}
```

**Generative Expansion**:
```python
# Load template
template = load_template(project_type="software", artifact_type="Project Charter")

# Fill with LLM
filled_content = llm_call(
    system=f"Fill this template with specific content from the project description. Template: {template}",
    input={"description": user_description, "template_structure": template["sections"]},
    output_format="markdown"
)
```

**Export Engine**:
- **Markdown**: Native format, just save to file
- **DOCX**: Use `python-docx` library to convert markdown → formatted Word doc with styles
- **PDF**: Use `reportlab` or `weasyprint` to convert markdown → PDF

**Performance Target**: ~5 minutes for 6 artifacts (includes LLM call time, template loading, export generation)

**User Stories**:
- As a PM, I want to describe a new project and get a complete baseline of artifacts in under 10 minutes
- As a PM, I want artifact suggestions tailored to my project type (software vs. marketing vs. infrastructure)
- As a PM, I want editable drafts that I can refine with conversational feedback before finalizing
- As a PM, I want to export artifacts to DOCX/PDF immediately for stakeholder review
- As a PM, I want the baseline to include common risk categories and stakeholder matrices so I'm not starting from zero

---

### 4.5 Tab 5: History & Context (The Memory Engine)

**Primary Use Case**: Managing session history and controlling how much past context the LLM remembers for better continuity vs. privacy control.

**What Makes This Powerful**: Unlike cloud AI assistants where context is opaque, VPMA gives you full transparency and control. You decide how much history to include in each session.

**UX Flow**:

1. **Context Depth Slider**:
   - **UI**: Horizontal slider at top of tab
   - **Label**: "Context Depth: 0 sessions (None) ←→ 50 sessions (Maximum)"
   - **Default**: 10 sessions (balance between continuity and token cost)
   - **Visual Indicator** below slider:
     ```
     📊 Currently loaded: 10 sessions • 45,382 tokens • Est. cost: $0.12 (Claude Sonnet)
     ```
   - **Real-Time Update**: As user drags slider, token count and cost estimate update immediately
   - **Purpose**: Controls how many past sessions are included in LLM context for current session
     - 0 sessions: LLM has NO memory (fresh start, useful for sensitive sessions)
     - 50 sessions: LLM has full project history (maximum continuity, higher cost)

2. **Session Log**:

   **UI**: Reverse-chronological list (newest first), paginated (20 per page)

   **List Entry Format**:
   ```
   📅 Feb 12, 2026 • 3:42 PM
   📝 Updated RAID log with 3 risks from stakeholder meeting
   🏷️ [RAID Log] [Status Report] [Meeting Notes]
   [+] Expand
   ```

   **Entry Components**:
   - **Date/Time**: "Feb 12, 2026 • 3:42 PM"
   - **Auto-Generated Summary**: One-liner describing session (generated by LLM during session log)
   - **Artifact Tags**: Visual tags showing which artifacts were touched
   - **Expand Button**: [+] reveals full session details

3. **Expanded Session View** (when [+] clicked):

   **Section 1: Input**
   - **Truncated Preview**: First 500 characters of user input
   - **[View Full Input]** button: Opens modal with complete input text
   - **Example**:
     ```
     Input (truncated):
     "Meeting transcript from weekly steering committee. Attendees: John (VP Product),
     Sarah (CFO), Mike (Engineering Lead). Discussion covered budget increase request,
     vendor delay impact on timeline, new risk identified around API integration..."
     [View Full Input - 2,450 characters]
     ```

   **Section 2: Pulse Output**
   - List of artifact updates from that session (the bubbles that were generated)
   - **Example**:
     ```
     Artifact Updates:
     ✅ RAID Log: 3 New Risks (Applied)
     ✅ Status Report: Executive Summary Update (Applied)
     ✅ Meeting Notes: Complete Summary (Applied)
     ⬜ GitHub Tasks: 4 Suggestions (Not Applied)
     ```
   - Shows which updates were applied vs. skipped

   **Section 3: Persona Used**
   - Which professional roles the agent assumed
   - **Example**: "Personas: PM + Business Analyst"
   - **Learning Transparency**: User can see which skills were leveraged

   **Section 4: Include in Context Override**
   - **Checkbox**: "✅ Include in Context (overrides slider)"
   - **Purpose**: Manual override for slider setting
     - Example: Slider set to 10 sessions, but user wants to include session from 20 sessions ago that's particularly relevant
   - **Visual Indicator**: If checked and outside slider range, entry shows blue highlight border

4. **Search & Filter**:

   **Search Bar**:
   - **UI**: Text input above session log with magnifying glass icon
   - **Placeholder**: "Search sessions (e.g., 'risk assessment', 'vendor delay', 'ClientCo')"
   - **Functionality**: Full-text search across session inputs, outputs, summaries
   - **Example**: Search "vendor delay" → Returns 3 sessions mentioning vendor issues

   **Filter Dropdowns**:
   - **By Date Range**: [Last 7 Days] [Last 30 Days] [Last 90 Days] [Custom Range]
   - **By Artifact Type**: [All] [RAID Log] [Status Report] [Meeting Notes] [Charter] [PRD] ...
   - **By Persona Used**: [All] [PM] [PO] [BA] [Product Manager] [Multi-Persona]

   **Combined Filtering**:
   - Example: "Show me RAID Log sessions from last 30 days where PM persona was used"
   - Filters AND search work together (search within filtered results)

5. **Context Preview Panel**:

   **UI**: Bottom panel (collapsible), labeled "LLM Context Summary"

   **Content**:
   ```
   📊 LLM Context Summary (for next Artifact Sync session)

   Sessions Included: 10 (based on slider setting)
   Date Range: Jan 15 - Feb 12, 2026

   Session List:
   1. Feb 12, 3:42 PM - Updated RAID log with 3 risks
   2. Feb 11, 10:15 AM - Generated PRD for new feature
   3. Feb 9, 2:30 PM - Status report for weekly steering committee
   ...
   10. Jan 15, 4:00 PM - Initial project charter baseline

   Total Tokens: 45,382
   Estimated Cost (Claude Sonnet): $0.12 per session
   ```

   **Purpose**: Transparency. User knows exactly what the LLM "remembers" before starting next session.

   **[Clear All Context]** Button:
   - Emergency reset: Clears all sessions from context (sets slider to 0)
   - Confirmation dialog: "This will clear all LLM memory for this project. Continue?"
   - Use case: Starting sensitive session where prior context shouldn't influence

6. **Session Export**:
   - **Per-Session Export**: Each expanded session has **[Export]** button
     - Exports session to markdown file with input, output, metadata
   - **Bulk Export**: **[Export All Sessions]** button at top of tab
     - Generates timestamped ZIP file: `~/VPMA/exports/project_name_sessions_2026-02-12.zip`
     - Contains all sessions as individual markdown files

**Technical Implementation**:

**Session Storage** (SQLite):
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    project_id TEXT,
    timestamp DATETIME,
    tab_used TEXT,  -- "Artifact Sync", "Deep Strategy", etc.
    user_input TEXT,
    agent_output JSON,  -- List of bubbles/updates
    persona_used TEXT,  -- "PM,BA" (comma-separated)
    tokens_used INTEGER,
    llm_model TEXT,     -- "claude-3-5-sonnet", "gemini-pro"
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

**Context Assembly** (when slider = 10):
```python
# Load last 10 sessions
sessions = db.execute("""
    SELECT user_input, agent_output, timestamp, persona_used
    FROM sessions
    WHERE project_id = ?
    ORDER BY timestamp DESC
    LIMIT ?
""", (project_id, slider_value))

# Concatenate for LLM context
context_summary = "Previous session summaries:\n"
for session in reversed(sessions):  # Chronological order for LLM
    context_summary += f"- {session['timestamp']}: {session['agent_output']['summary']}\n"

# Include in next Artifact Sync LLM call
system_prompt = f"""
You are a PM assistant. Here is the project context from previous sessions:

{context_summary}

Use this context to provide continuity in your responses.
"""
```

**Search Implementation**:
- SQLite Full-Text Search (FTS5):
  ```sql
  CREATE VIRTUAL TABLE sessions_fts USING fts5(
      session_id, user_input, agent_output, summary
  );

  -- Search query
  SELECT * FROM sessions_fts WHERE sessions_fts MATCH 'vendor delay';
  ```

**Token Counting**:
- Use `tiktoken` library (for Claude) or Gemini's token counter API
- Count tokens in all sessions within slider range
- Display real-time: "45,382 tokens • $0.12 estimated cost"

**User Stories**:
- As a PM, I want to control how much history the agent remembers to balance continuity and privacy
- As a PM, I want to search past sessions to understand when a decision was made or a risk was identified
- As a PM, I want to manually include/exclude specific sessions from context (override slider setting)
- As a PM, I want transparency into what the LLM "knows" before starting a new session (context preview)
- As a PM, I want to export session history for compliance or handoff to another PM

---

### 4.6 Tab 6: Settings & Landscape (The DNA Configuration)

**Primary Use Case**: Configuring the "Fixed Landscape" (meetings, artifacts, timing), professional role toggles, privacy settings, and LLM preferences.

**What Makes This the Foundation**: Settings define VPMA's "DNA" - how it understands your project rhythm, which skills it uses, and how it protects your data.

**UX Flow**:

1. **Role Toggles** (Professional Persona Controls):

   **UI**: Row of toggle switches with labels and descriptions

   **Toggles**:
   ```
   ✅ PM (Project Manager)
      "Risk management, stakeholder coordination, timeline planning"

   ✅ Program Manager
      "Multi-project orchestration, portfolio management, resource allocation"

   ✅ Product Owner
      "Backlog prioritization, user story creation, sprint planning"

   ✅ Product Manager
      "Product strategy, roadmap planning, feature prioritization"

   ✅ Business Analyst
      "Requirements gathering, process mapping, stakeholder translation"
   ```

   **Default**: All ON (agent auto-determines which to use based on task)

   **User Control**: Disable roles not relevant to your work
   - Example: If you're purely a PM (not product-focused), turn off PO and Product Manager
   - Agent will only use PM + BA skills for artifact tasks

   **Learning Ledger Link**: "📊 View Learning Ledger" (shows historical persona usage)

2. **Fixed Landscape Table** (Project Rhythm Configuration):

   **UI**: Editable table with 4 columns

   **Columns**:
   - **Artifact Type** (dropdown): "Status Report", "RAID Log", "PRD", "Meeting Agenda", etc.
   - **Associated Meeting** (text): "Weekly Steering Committee", "Daily Standup", "Sprint Planning"
   - **Timing** (text): "Every Monday 9am", "Daily 9:30am", "Bi-weekly Thursdays 2pm"
   - **Update Frequency** (dropdown): "After every meeting", "Weekly", "Bi-weekly", "Monthly", "On-demand"

   **Example Rows** (Pre-populated defaults for new projects):
   ```
   | Artifact Type       | Associated Meeting         | Timing                    | Update Frequency      |
   |---------------------|----------------------------|---------------------------|-----------------------|
   | Status Report       | Weekly Steering Committee  | Every Monday 9am          | Weekly                |
   | RAID Log            | Daily Standup              | Daily 9:30am              | After every meeting   |
   | PRD                 | Product Planning Meeting   | Bi-weekly Thursdays 2pm   | Bi-weekly             |
   | Meeting Agenda      | Weekly Steering Committee  | Every Monday 9am          | Weekly (pre-meeting)  |
   | Action Item Log     | All Meetings               | N/A                       | After every meeting   |
   ```

   **Actions**:
   - **[+ Add Row]**: Creates new blank row for custom artifact/meeting pairing
   - **[Delete]** button per row: Removes mapping
   - **Inline Editing**: Click any cell to edit directly
   - **Drag to Reorder**: Reorder rows by priority (top = highest priority for Daily Planner)

3. **Natural Language Landscape Configurator** (Alternative to Table Editing):

   **UI**: Text area below table with AI parsing

   **Label**: "Or describe your landscape in plain English:"

   **Example Input**:
   ```
   Add a new artifact type: Technical Design Doc, updated monthly,
   presented at Architecture Review meeting every last Friday of the month.
   ```

   **Processing**:
   - LLM parses natural language input
   - Extracts: artifact_type="Technical Design Doc", meeting="Architecture Review", timing="Last Friday monthly", frequency="Monthly"
   - Auto-inserts row into table above
   - Toast confirmation: "Added 'Technical Design Doc' to landscape!"

   **Use Case**: Faster for users who prefer typing over clicking

4. **Learning Ledger** (Hidden/Expandable Section):

   **UI**: Collapsible section (collapsed by default), labeled "📊 Learning Ledger (Advanced)"

   **Purpose**: Transparency into agent decision-making - shows which skills/expertise were used for each task

   **Content** (when expanded):
   ```
   Learning Ledger - Last 30 Days

   📅 Feb 12, 3:42 PM
   Task: Risk identification from meeting transcript
   Personas Used: PM + Business Analyst
   Reason: Risk assessment (PM) + stakeholder requirement extraction (BA)

   📅 Feb 11, 10:15 AM
   Task: PRD generation for new feature
   Personas Used: Product Owner + Product Manager
   Reason: User story creation (PO) + product strategy alignment (PM)

   📅 Feb 9, 2:30 PM
   Task: Status report update
   Personas Used: PM
   Reason: Stakeholder communication, project health summary

   [View Full Ledger - 127 entries]
   ```

   **Data Use**: Continuous improvement - track which persona combinations are most effective

   **User Benefit**: Understand *why* agent made certain decisions (transparency builds trust)

5. **LLM Toggle**:

   **UI**: Radio buttons with model details

   **Options**:
   ```
   ⚪ Claude Pro (claude-3-5-sonnet-20241022)
      API Status: ✅ Connected
      Avg Latency: 1.2s
      Cost: ~$0.015 per 1K tokens (input/output blended)

   ⚪ Gemini (gemini-1.5-pro)
      API Status: ✅ Connected
      Avg Latency: 0.8s
      Cost: ~$0.007 per 1K tokens (input/output blended)
   ```

   **Default**: Claude Pro (higher quality for artifact generation)

   **User Control**: Switch to Gemini for:
   - Cost savings (roughly half the price)
   - Faster responses (lower latency)
   - Preference testing (compare quality)

   **API Key Configuration**: **[Edit API Keys]** button → Opens .env file editor or secure input modal

6. **Privacy Settings**:

   **UI**: Checkboxes and controls with explanations

   **Setting 1: Enable PII Anonymization**
   ```
   ✅ Enable PII anonymization (Privacy Proxy)

   "Anonymize names, emails, organizations, and proprietary terms before sending data to LLM APIs.
   Highly recommended - disable only for non-sensitive projects."

   Default: ON
   ```

   **Setting 2: Show Anonymization Preview**
   ```
   ⬜ Show anonymization preview when confidence is uncertain

   "When PII detection confidence is below 70%, show you the anonymized text before sending.
   Adds 5-10 seconds per session but increases privacy assurance."

   Default: OFF (users can enable for extra caution)
   ```

   **Setting 3: Privacy Audit Log**
   ```
   📋 Privacy Audit Log

   "Review all anonymized payloads sent to LLM APIs (post-hoc verification)."

   [View Audit Log] button → Opens viewer:

   Audit Log Viewer
   ----------------
   📅 Feb 12, 3:42 PM - Artifact Sync Session
   Anonymized Payload (sent to Claude API):
   "Meeting with <PERSON_1> and <PERSON_2> at <ORG_1>. Discussed <PROJECT_1> timeline..."

   Original Payload (local only, never sent):
   "Meeting with John Smith and Sarah Johnson at ACME Corp. Discussed Project Falcon timeline..."

   [Export Audit Log]
   ```

   **Setting 4: Anonymization Vault Scope**
   ```
   ℹ️ Anonymization Vault: Global across all projects

   "Token mappings (e.g., <PERSON_1> → John Smith) are shared across all projects for consistency.
   [View Vault - 47 entities] [Clear Vault - Reset All Tokens]"
   ```

7. **Technical Fluency Translation**:

   **UI**: Toggle switch with description

   **Setting**:
   ```
   ⬜ Enable Technical Fluency Translation (globally)

   "Get PM-friendly explanations of technical concepts in all sessions (Daily Planner, Artifact Sync, Deep Strategy).
   Helps build technical vocabulary over time. Can also be toggled per-session via app header."

   Default: OFF
   ```

   **Note**: This is global default. User can override per-session with header toggle.

8. **Data Management**:

   **Setting 1: Data Retention**
   ```
   🗓️ Data Retention

   "Keep last _____ days of sessions"
   [Input: 90] days

   "Automatically delete sessions older than this threshold. Artifact content is preserved, only session history is removed."

   Default: 90 days
   ```

   **Setting 2: Manual Backup**
   ```
   💾 Manual Backup

   "Export full project state (database + artifacts + settings) for manual backup."

   [Export Project] button → Generates timestamped ZIP:
   `~/VPMA/backups/project_name_2026-02-12.zip`

   Contains:
   - SQLite database (vpma.db)
   - All markdown artifacts (~/VPMA/artifacts/*.md)
   - Settings JSON (landscape config, preferences)

   "No automatic daily backups - you control when to backup."
   ```

9. **Analytics & Logs**:

   **UI**: Checkbox with folder link

   **Setting**:
   ```
   ✅ Enable anonymous usage analytics

   "Track feature usage, session duration, error rates locally in ~/VPMA/analytics/.
   No external sending - data stays on your laptop for your own analysis."

   [View Analytics Folder] → Opens Finder/Explorer to ~/VPMA/analytics/

   Contents:
   - feature_usage.json (Tab usage counts, button clicks)
   - session_durations.json (Time per tab, time per artifact type)
   - error_log.json (LLM API failures, parsing errors)

   Default: ON
   ```

10. **Export/Import Landscape Configuration**:

    **UI**: Buttons for portability

    **Buttons**:
    ```
    [Export Landscape] → Saves landscape config as JSON file
    ~/VPMA/exports/landscape_config_2026-02-12.json

    [Import Landscape] → Load landscape from JSON file
    (Useful for sharing config across projects or with other VPMA users)
    ```

    **Example JSON**:
    ```json
    {
      "artifacts": [
        {
          "type": "Status Report",
          "associated_meeting": "Weekly Steering Committee",
          "timing": "Every Monday 9am",
          "update_frequency": "Weekly"
        },
        // ...
      ],
      "custom_sensitive_terms": ["Project Falcon", "ACME Corp", "ClientCo"]
    }
    ```

**Technical Implementation**:

**Landscape Storage** (SQLite):
```sql
CREATE TABLE landscape_config (
    config_id TEXT PRIMARY KEY,
    project_id TEXT,
    artifact_type TEXT,
    associated_meeting TEXT,
    timing TEXT,
    update_frequency TEXT,
    active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

**Natural Language Parsing**:
```python
# LLM call to parse user input
parsed = llm_call(
    system="Extract landscape configuration from natural language input. Return JSON.",
    input=user_nl_input,
    output_format="json"
)
# Returns: {"artifact_type": "Technical Design Doc", "meeting": "Architecture Review", ...}

# Insert into database
db.execute("""
    INSERT INTO landscape_config (config_id, project_id, artifact_type, associated_meeting, timing, update_frequency)
    VALUES (?, ?, ?, ?, ?, ?)
""", (uuid(), project_id, parsed["artifact_type"], parsed["meeting"], parsed["timing"], parsed["frequency"]))
```

**Learning Ledger Storage**:
```sql
CREATE TABLE learning_ledger (
    ledger_id TEXT PRIMARY KEY,
    session_id TEXT,
    task_description TEXT,
    personas_used TEXT,  -- "PM,BA" (comma-separated)
    reason TEXT,
    timestamp DATETIME,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

**Privacy Audit Log**:
- Append to `~/VPMA/privacy/audit_log.jsonl` (JSON Lines format):
  ```json
  {"timestamp": "2026-02-12T15:42:00", "session_id": "abc123", "anonymized": "Meeting with <PERSON_1>...", "original": "Meeting with John Smith..."}
  ```
- Viewer in Settings tab reads and displays with side-by-side comparison

**Manual Backup**:
```python
import shutil
from datetime import datetime

def export_project(project_id):
    timestamp = datetime.now().strftime("%Y-%m-%d")
    zip_path = f"~/VPMA/backups/{project_name}_{timestamp}.zip"

    with ZipFile(zip_path, 'w') as zipf:
        # Add SQLite database
        zipf.write("~/VPMA/vpma.db", "vpma.db")

        # Add all artifact markdown files
        artifact_dir = f"~/VPMA/artifacts/{project_name}/"
        for md_file in os.listdir(artifact_dir):
            zipf.write(f"{artifact_dir}/{md_file}", f"artifacts/{md_file}")

        # Add settings JSON
        settings = export_landscape_config(project_id)
        zipf.writestr("settings.json", json.dumps(settings))

    return zip_path
```

**User Stories**:
- As a PM, I want to configure which artifacts I manage so the agent knows my "landscape"
- As a PM, I want to toggle between Claude and Gemini to compare quality and speed
- As a PM, I want to see which professional skills the agent used for each task (Learning Ledger)
- As a PM, I want to control PII anonymization settings and review what's being sent to LLMs
- As a PM, I want to export my landscape configuration to share with teammates or reuse across projects
- As a PM, I want to manually backup my project data without relying on automatic schedules

---

## 5. Technical Architecture

### 5.1 System Architecture Overview

**Deployment Model**: 100% local desktop application with zero cloud dependencies beyond LLM API calls.

**Core Technology Stack**:
```
┌─────────────────────────────────────────────────────────────┐
│                     USER (Web Browser)                       │
│                   http://localhost:3000                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              FRONTEND LAYER (React)                          │
│  Phase 0: JS React + Tailwind CSS + useState/useContext     │
│  Phase 1+: TypeScript migration, component library upgrade  │
│  Phase 4+: Electron wrapper for desktop features            │
│  - 6 Tab Navigation  - Cross-Tab Features  - UI Components  │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API (HTTP/JSON)
┌──────────────────────────▼──────────────────────────────────┐
│              BACKEND LAYER (Python FastAPI)                  │
│  - API Routes  - Business Logic  - Session Management       │
│  - Artifact Manager  - Deep Strategy Multi-Pass Engine      │
│  - Project Initiation Generator  - Export Engine            │
└──────────┬────────────────────────────────────┬─────────────┘
           │                                    │
┌──────────▼────────────┐          ┌───────────▼─────────────┐
│   PRIVACY PROXY       │          │  LLM INTEGRATION LAYER  │
│  - PII Detection      │◄────────►│  - Claude API Client    │
│  - Anonymization      │          │  - Gemini API Client    │
│  - Re-identification  │          │  - Ollama Client (Ph2)  │
│  - Vault Management   │          │  - Unified Interface    │
│                       │          └───────────┬─────────────┘
└──────────┬────────────┘                      │
           │                          ┌────────▼────────────────┐
           │                          │  LLM PROVIDERS          │
           │                          │  - Anthropic (HTTPS)    │
           │                          │  - Google AI (HTTPS)    │
           │                          │  - Ollama (localhost)   │
           │                          │  (HTTPS Only)   │
           │                          │  - Anthropic    │
           │                          │  - Google AI    │
           │                          └─────────────────┘
           │
┌──────────▼──────────────────────────────────────────────────┐
│                   DATA STORAGE LAYER                         │
│  - SQLite DB (metadata, sessions, config)                   │
│  - Markdown Files (artifact content in ~/VPMA/artifacts/)   │
│  - File System (exports, backups, logs, feedback)           │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow - Typical Artifact Sync Session**:
```
1. User Input (meeting transcript)
   ↓
2. Privacy Proxy: Anonymize PII
   "John Smith at ACME Corp" → "<PERSON_1> at <ORG_1>"
   ↓
3. LLM API Call (Claude/Gemini)
   Anonymized input → LLM generates artifact updates
   ↓
4. Privacy Proxy: Re-identify PII
   "<PERSON_1> at <ORG_1>" → "John Smith at ACME Corp"
   ↓
5. Business Logic: Generate bubbles, format output
   ↓
6. User Reviews & Confirms
   ↓
7. Local Storage: Update SQLite + Markdown files
   ↓
8. UI Update: Display confirmation, clear input
```

**Key Architectural Decisions**:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Deployment** | Local web app (localhost:3000) | Privacy guarantee, no server costs, instant startup. Phase 4: optional cloud deployment |
| **Frontend Framework** | React (JS in Phase 0 → TypeScript in Phase 1 → Electron in Phase 4) | Progressive complexity: validate fast, then harden. Avoids premature over-engineering |
| **UI Styling** | Tailwind CSS (Phase 0-1), evaluate Material-UI (Phase 2+) | Tailwind is simpler, AI generates it fluently, lower config overhead for novice developer |
| **State Management** | useState + useContext (Phase 0-1), Redux if needed (Phase 2+) | Minimal state for 5-7 components; add Redux only when complexity demands it |
| **Backend Framework** | Python FastAPI | Fast, modern, async-capable, keeps Python for LLM/Privacy Proxy/document parsing |
| **API Architecture** | REST (HTTP/JSON) | Simple, stateless, well-understood, easy to debug |
| **LLM Strategy** | Dual-brain toggle (Phase 0-1), Triple toggle with Ollama (Phase 2+) | Provider independence, local option for cost/privacy, fallback resilience |
| **Artifact Storage** | Markdown files only | Human-readable, version control friendly, portable, no lock-in |
| **Metadata Storage** | SQLite | Lightweight, serverless, reliable, excellent for single-user local apps |
| **Anonymization Vault** | Global across projects | Consistent token mappings (same person → same token in all projects) |
| **Backups** | Manual export only | User control, no automated background processes, explicit action |
| **Collaboration** | Single-user only (Phase 0-3), web users (Phase 4+) | Simplifies architecture initially, no auth/permissions/sync conflicts until commercial phase |

---

### 5.2 Privacy Proxy Architecture

**Purpose**: Ensure sensitive PII (names, emails, institutions, proprietary terms) never reaches external LLM APIs in identifiable form.

**Approach**: Simple regex + NER (Named Entity Recognition) replacement with local vault storage.

#### Component 1: Anonymization (Outbound)

**Step 1: PII Detection**

Three detection layers:

1. **Regex Patterns** (deterministic, fast):
   ```python
   patterns = {
       'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
       'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
       'url': r'https?://[^\s]+',
       # Company-specific domains
       'company_url': r'@(acme|clientco|partnerorg)\.com'
   }
   ```

2. **spaCy NER** (ML-based, context-aware):
   ```python
   import spacy
   nlp = spacy.load("en_core_web_sm")  # Lightweight model, ~15MB

   doc = nlp(user_input)
   entities = [
       (ent.text, ent.label_) for ent in doc.ents
       if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT']
   ]
   # Example: [("John Smith", "PERSON"), ("ACME Corp", "ORG"), ("Project Falcon", "PRODUCT")]
   ```

3. **Custom Dictionary** (user-defined sensitive terms):
   ```python
   # Loaded from Settings → Privacy Settings → Custom Sensitive Terms
   custom_sensitive = ["Project Falcon", "ClientCo", "Q4 Roadmap"]
   ```

**Step 2: Tokenization**

Replace detected entities with anonymized tokens:

```python
vault = {}  # In-memory dict, persisted to SQLite

def anonymize(text):
    # Sort entities by length (longest first) to avoid partial replacements
    entities = detect_pii(text)
    entities.sort(key=lambda x: len(x[0]), reverse=True)

    anonymized_text = text
    for entity, entity_type in entities:
        # Check if entity already in vault (consistency)
        if entity in vault:
            token = vault[entity]
        else:
            # Generate new token
            token_count = len([v for v in vault.values() if v.startswith(f"<{entity_type}_")])
            token = f"<{entity_type}_{token_count + 1}>"
            vault[entity] = token

        anonymized_text = anonymized_text.replace(entity, token)

    return anonymized_text

# Example:
input_text = "Meeting with John Smith from ACME Corp about Project Falcon timeline."
output = anonymize(input_text)
# → "Meeting with <PERSON_1> from <ORG_1> about <PRODUCT_1> timeline."
```

**Step 3: Validation & Preview**

If **Settings → Show anonymization preview** is enabled OR confidence is low (<70%):
```python
if show_preview or confidence < 0.7:
    # Display side-by-side comparison in modal
    ui.show_preview_modal(original=text, anonymized=anonymized_text)
    user_confirms = ui.wait_for_confirmation()
    if not user_confirms:
        return  # Abort session
```

**Confidence Scoring**:
```python
def calculate_confidence(entities):
    # High confidence: All entities detected by multiple methods (regex + NER)
    # Medium confidence: Mixed detection (some regex-only, some NER-only)
    # Low confidence: Ambiguous entities (NER flagged common words like "Apple" - company or fruit?)

    multi_method_count = count_entities_detected_by_multiple_methods(entities)
    total_count = len(entities)

    confidence = multi_method_count / total_count if total_count > 0 else 1.0
    return confidence
```

#### Component 2: Re-identification (Inbound)

**Step 1: Token Replacement**

After LLM returns response with anonymized tokens:

```python
def re_identify(anonymized_text, vault):
    # Reverse vault lookup
    reverse_vault = {token: original for original, token in vault.items()}

    re_identified_text = anonymized_text
    for token, original in reverse_vault.items():
        re_identified_text = re_identified_text.replace(token, original)

    return re_identified_text

# Example:
llm_output = "Updated RAID log: <PERSON_1> identified new risk about <PRODUCT_1> timeline delay."
output = re_identify(llm_output, vault)
# → "Updated RAID log: John Smith identified new risk about Project Falcon timeline delay."
```

**Step 2: Context Preservation**

Vault persists across sessions for consistency:

```python
# Save to SQLite after each session
db.execute("""
    INSERT OR REPLACE INTO pii_vault (token, original_value, entity_type, first_seen)
    VALUES (?, ?, ?, ?)
""", ("<PERSON_1>", "John Smith", "PERSON", datetime.now()))
```

**Vault Schema**:
```sql
CREATE TABLE pii_vault (
    token TEXT PRIMARY KEY,           -- "<PERSON_1>"
    original_value TEXT NOT NULL,     -- "John Smith"
    entity_type TEXT NOT NULL,        -- "PERSON", "ORG", "EMAIL", etc.
    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Global Vault Scope**: Vault is shared across ALL projects on the laptop for consistent mappings.

#### Privacy Guarantee

**What is sent to LLM APIs**:
```
"Meeting with <PERSON_1> from <ORG_1> discussed <PRODUCT_1> timeline. Budget concerns raised by <PERSON_2>."
```

**What stays local only**:
```
"Meeting with John Smith from ACME Corp discussed Project Falcon timeline. Budget concerns raised by Sarah Johnson."
```

**Audit Trail**: All anonymized payloads logged to `~/VPMA/privacy/audit_log.jsonl`:
```json
{"timestamp": "2026-02-12T15:42:00", "session_id": "abc123", "anonymized": "Meeting with <PERSON_1>...", "llm_model": "claude-3-5-sonnet"}
```
User can review this log in **Settings → Privacy Settings → Privacy Audit Log**.

**Performance Target**: < 200ms for anonymization of typical meeting transcript (2000 words).

**Accuracy Target**: 99.5% PII detection rate (measured via labeled test dataset of 1000 sample inputs).

---

### 5.3 Data Storage & Project State

**Storage Philosophy**: SQLite for metadata and relationships, Markdown files for human-readable artifact content.

#### File System Structure

```
~/VPMA/
  ├── vpma.db                          # SQLite database (all metadata)
  ├── artifacts/                       # Artifact content (markdown only)
  │   ├── project_alpha/
  │   │   ├── project_charter.md
  │   │   ├── raid_log.md
  │   │   ├── status_report.md
  │   │   └── prd.md
  │   └── project_beta/
  │       └── ...
  ├── exports/                         # User-initiated exports
  │   ├── project_alpha_2026-02-12.zip
  │   └── landscape_config_2026-02-12.json
  ├── backups/                         # Manual project backups
  │   └── project_alpha_2026-02-12.zip
  ├── privacy/                         # Privacy audit logs
  │   └── audit_log.jsonl
  ├── analytics/                       # Anonymous usage logs
  │   ├── feature_usage.json
  │   ├── session_durations.json
  │   └── error_log.json
  ├── feedback/                        # User feedback
  │   └── feedback_log.md
  └── .env                             # API keys (gitignored)
```

#### SQLite Database Schema

**Table 1: projects**
```sql
CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,        -- UUID
    project_name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    landscape_config JSON,              -- Fixed Landscape (serialized JSON)
    last_accessed DATETIME
);
```

**Table 2: artifacts**
```sql
CREATE TABLE artifacts (
    artifact_id TEXT PRIMARY KEY,       -- UUID
    project_id TEXT NOT NULL,
    artifact_type TEXT NOT NULL,        -- "Charter", "RAID Log", "PRD", etc.
    file_path TEXT NOT NULL,            -- "~/VPMA/artifacts/project_alpha/raid_log.md"
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    version_number INTEGER DEFAULT 1,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```
*Note*: **No content storage in SQLite** - all artifact text lives in markdown files. SQLite only stores metadata.

**Table 3: sessions**
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,        -- UUID
    project_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    tab_used TEXT NOT NULL,             -- "Artifact Sync", "Deep Strategy", etc.
    user_input TEXT,                    -- Original user input (for history review)
    agent_output JSON,                  -- Bubbles/updates generated (serialized JSON)
    persona_used TEXT,                  -- "PM,BA" (comma-separated)
    tokens_used INTEGER,
    llm_model TEXT,                     -- "claude-3-5-sonnet", "gemini-pro"
    session_summary TEXT,               -- Auto-generated one-liner for history log
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

**Table 4: pii_vault** (Privacy Proxy mappings)
```sql
CREATE TABLE pii_vault (
    token TEXT PRIMARY KEY,             -- "<PERSON_1>"
    original_value TEXT NOT NULL,       -- "John Smith"
    entity_type TEXT NOT NULL,          -- "PERSON", "ORG", "EMAIL"
    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
*Note*: **Global vault** - not tied to any specific project (consistent across all projects).

**Table 5: landscape_config** (Fixed Landscape entries)
```sql
CREATE TABLE landscape_config (
    config_id TEXT PRIMARY KEY,         -- UUID
    project_id TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    associated_meeting TEXT,
    timing TEXT,                        -- "Every Monday 9am"
    update_frequency TEXT,              -- "Weekly", "After every meeting"
    active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

**Table 6: learning_ledger** (Persona usage tracking)
```sql
CREATE TABLE learning_ledger (
    ledger_id TEXT PRIMARY KEY,         -- UUID
    session_id TEXT NOT NULL,
    task_description TEXT,
    personas_used TEXT,                 -- "PM,BA"
    reason TEXT,                        -- Why these personas were chosen
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

#### Artifact Content Storage (Markdown Files)

**Why Markdown**:
- Human-readable (no proprietary format lock-in)
- Version control friendly (Git can diff markdown)
- Portable (works with any text editor, note-taking app)
- Simple (no complex parsing, just read/write text files)

**Example Artifact File** (`~/VPMA/artifacts/project_alpha/raid_log.md`):
```markdown
# RAID Log - Project Alpha

## Risks

| ID | Description | Probability | Impact | Mitigation | Owner | Status |
|----|-------------|-------------|--------|------------|-------|--------|
| R1 | Vendor delay may push timeline by 2 weeks | Medium | High | Conduct weekly vendor check-ins, prepare contingency plan | Sarah Johnson | Open |
| R2 | Budget overrun on infrastructure costs | Low | Medium | Monitor AWS spending weekly, set billing alerts | Mike Chen | Open |

## Assumptions

| ID | Description | Validation Date | Status |
|----|-------------|-----------------|--------|
| A1 | API endpoints remain stable during integration | 2026-03-01 | Valid |
| A2 | Team availability: 2 engineers full-time through Q2 | 2026-02-15 | Valid |

## Issues

| ID | Description | Severity | Resolution | Owner | Status |
|----|-------------|----------|------------|-------|--------|
| I1 | Database migration failed on staging | High | Re-run migration with fixed schema | Alex Rodriguez | In Progress |

## Dependencies

| ID | Description | Dependency On | Status |
|----|-------------|---------------|--------|
| D1 | Frontend release blocked on API completion | Backend Team | Pending |
```

**Update Mechanism**:
1. User confirms artifact update in Artifact Sync → **[Apply]** button
2. VPMA reads current markdown file: `with open(file_path, 'r') as f: content = f.read()`
3. LLM generates updated markdown (or VPMA uses structured editing for tables)
4. VPMA writes updated content: `with open(file_path, 'w') as f: f.write(updated_content)`
5. Update metadata: `UPDATE artifacts SET last_updated = CURRENT_TIMESTAMP, version_number = version_number + 1 WHERE artifact_id = ?`

**Versioning (MVP)**: Simple "Undo" button per artifact (one-level rollback only):
```python
# Before writing update, save current version to temp
backup_content = read_artifact(file_path)
session_state['undo_backup'][artifact_id] = backup_content

# User clicks [Undo] → Restore from backup
write_artifact(file_path, session_state['undo_backup'][artifact_id])
```
**Phase 2**: Full version history (store all versions in `artifact_versions` table).

---

### 5.4 LLM Integration Layer

**Design Goal**: Unified interface for multiple LLM providers (Claude, Gemini, and local models via Ollama) with seamless switching. The abstract interface is implemented from Phase 0 to prevent technical debt when adding providers.

#### Abstraction Layer

**Interface**:
```python
class LLMClient(ABC):
    @abstractmethod
    def call(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
        """Send prompt to LLM, return response text."""
        pass

    @abstractmethod
    def call_structured(self, system_prompt: str, user_prompt: str, output_schema: dict) -> dict:
        """Send prompt to LLM with JSON schema, return parsed JSON."""
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens for cost estimation."""
        pass
```

**Claude Implementation**:
```python
import anthropic

class ClaudeClient(LLMClient):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def call(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return message.content[0].text

    def call_structured(self, system_prompt: str, user_prompt: str, output_schema: dict) -> dict:
        # Use Claude's JSON mode
        response = self.call(
            system_prompt=system_prompt + "\n\nReturn valid JSON only.",
            user_prompt=user_prompt
        )
        return json.loads(response)

    def count_tokens(self, text: str) -> int:
        import tiktoken
        enc = tiktoken.encoding_for_model("claude-3-5-sonnet-20241022")
        return len(enc.encode(text))
```

**Gemini Implementation**:
```python
import google.generativeai as genai

class GeminiClient(LLMClient):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def call(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
        # Gemini combines system + user prompts
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = self.model.generate_content(
            full_prompt,
            generation_config={"max_output_tokens": max_tokens}
        )
        return response.text

    def call_structured(self, system_prompt: str, user_prompt: str, output_schema: dict) -> dict:
        response = self.call(
            system_prompt=system_prompt + "\n\nReturn valid JSON only.",
            user_prompt=user_prompt
        )
        return json.loads(response)

    def count_tokens(self, text: str) -> int:
        # Use Gemini's token counter
        return self.model.count_tokens(text).total_tokens
```

**Ollama Implementation** (Phase 2 — Local LLM):
```python
import httpx

class OllamaClient(LLMClient):
    """Local LLM via Ollama REST API (localhost:11434).

    Prerequisites: brew install ollama && ollama pull llama3.1:8b
    Runs entirely on user's machine — zero API costs, zero data egress.

    Recommended models for M4 MacBook Air (24GB RAM):
    - llama3.1:8b     ~5GB RAM, 40-60 tok/s, best quality/speed balance
    - mistral:7b      ~5GB RAM, 40-50 tok/s, good for structured output
    - mistral-nemo    ~8GB RAM, 25-40 tok/s, better at longer context
    - phi3:mini       ~2GB RAM, 60-80 tok/s, fast but less nuanced
    """
    def __init__(self, model: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)  # Local models can be slow

    def call(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {"num_predict": max_tokens}
            }
        )
        return response.json()["message"]["content"]

    def call_structured(self, system_prompt: str, user_prompt: str, output_schema: dict) -> dict:
        response = self.call(
            system_prompt=system_prompt + "\n\nReturn valid JSON only. No markdown formatting.",
            user_prompt=user_prompt
        )
        return json.loads(response)

    def count_tokens(self, text: str) -> int:
        # Approximate: ~4 characters per token for most models
        return len(text) // 4

    @staticmethod
    def list_installed_models(base_url: str = "http://localhost:11434") -> list:
        """Auto-detect installed Ollama models for Settings UI dropdown."""
        try:
            response = httpx.get(f"{base_url}/api/tags")
            return [m["name"] for m in response.json().get("models", [])]
        except Exception:
            return []

    @staticmethod
    def is_available(base_url: str = "http://localhost:11434") -> bool:
        """Check if Ollama is running (for Settings UI status indicator)."""
        try:
            httpx.get(f"{base_url}/api/tags", timeout=2.0)
            return True
        except Exception:
            return False
```

**Local LLM Quality/Speed/Cost Tradeoffs**:

| Provider | Quality (PM Tasks) | Speed | Cost | Privacy |
|----------|-------------------|-------|------|---------|
| **Claude Pro** | Excellent | Fast (API) | ~$3-15/M tokens | PII anonymized before sending |
| **Gemini** | Very Good | Fast (API) | ~$1-7/M tokens | PII anonymized before sending |
| **Ollama (Llama 3.1 8B)** | Good | 40-60 tok/s | Free | 100% local, no anonymization needed |
| **Ollama (Mistral Nemo 12B)** | Good+ | 25-40 tok/s | Free | 100% local |

**Recommended Usage Pattern**:
- **Daily Artifact Sync** (routine): Local LLM (good enough, free, instant privacy)
- **Deep Strategy** (multi-pass reasoning): Claude Pro (highest quality for complex analysis)
- **Communications Assistant** (drafting): Either (local is fine for casual messages, API for formal emails)

**Client Factory**:
```python
def get_llm_client(provider: str) -> LLMClient:
    """Factory to return correct LLM client based on Settings toggle."""
    config = load_config()  # From .env file or keychain (Phase 4)

    if provider == "claude":
        return ClaudeClient(api_key=config['ANTHROPIC_API_KEY'])
    elif provider == "gemini":
        return GeminiClient(api_key=config['GOOGLE_API_KEY'])
    elif provider == "ollama":
        return OllamaClient(
            model=config.get('OLLAMA_MODEL', 'llama3.1:8b'),
            base_url=config.get('OLLAMA_URL', 'http://localhost:11434')
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
```

#### Prompt Engineering Strategy

**System Prompts** (Role-specific templates):

```python
SYSTEM_PROMPTS = {
    "PM": """
You are an expert Project Manager with 10+ years experience.
You excel at risk identification, stakeholder communication, and timeline planning.
When analyzing inputs, prioritize: risks, timeline impacts, and stakeholder concerns.
""",

    "PO": """
You are an expert Product Owner with deep understanding of agile methodologies.
You excel at user story creation, backlog prioritization, and acceptance criteria definition.
When analyzing inputs, prioritize: user needs, feature value, and sprint planning.
""",

    "BA": """
You are an expert Business Analyst skilled in requirements gathering and stakeholder translation.
You excel at process mapping, requirement elicitation, and bridging technical/business gaps.
When analyzing inputs, prioritize: requirement clarity, stakeholder alignment, and traceability.
"""
}

# Multi-persona prompts combine skills
def build_system_prompt(personas: List[str]) -> str:
    base = "You are a cross-functional PM assistant with the following expertise:\n\n"
    for persona in personas:
        base += SYSTEM_PROMPTS[persona] + "\n\n"
    return base
```

**Few-Shot Examples** (embedded in prompts for quality):

```python
FEW_SHOT_EXAMPLES = {
    "raid_log_extraction": """
Example Input:
"Meeting discussed vendor timeline concerns. John mentioned API integration might slip 2 weeks."

Example Output:
{
  "risks": [
    {
      "id": "R_NEW_1",
      "description": "API integration timeline may slip by 2 weeks due to vendor delays",
      "probability": "Medium",
      "impact": "High",
      "mitigation": "Conduct vendor check-in to confirm timeline, prepare contingency plan",
      "owner": "John",
      "status": "Open"
    }
  ]
}
"""
}
```

#### Cost Management

**Token Counting**:
```python
def estimate_cost(prompt: str, model: str) -> float:
    """Estimate LLM API cost before call."""
    token_count = llm_client.count_tokens(prompt)

    # Pricing (as of Feb 2026, approximate)
    pricing = {
        "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},  # per 1K tokens
        "gemini-1.5-pro": {"input": 0.00125, "output": 0.005}
    }

    # Assume avg input:output ratio of 1:2 for artifact generation
    input_cost = (token_count / 1000) * pricing[model]["input"]
    output_cost = (token_count * 2 / 1000) * pricing[model]["output"]  # 2x output tokens

    return input_cost + output_cost
```

**Cost Preview** (for expensive operations like Deep Strategy):
```python
if tab == "Deep Strategy":
    estimated_cost = estimate_cost(multi_pass_prompts, current_llm_model)
    if estimated_cost > 0.50:  # Threshold: warn if > $0.50
        ui.show_cost_warning(
            f"This Deep Strategy session will cost approximately ${estimated_cost:.2f}. Continue?"
        )
        if not user_confirms:
            return  # Abort
```

**User-Configurable Limits** (in Settings):
```python
# Settings → LLM Toggle → [Set Spending Limit]
max_cost_per_session = user_settings.get('max_cost_per_session', 5.00)  # Default: $5

if estimated_cost > max_cost_per_session:
    ui.show_error(f"Session would exceed spending limit (${max_cost_per_session:.2f}). Reduce scope or increase limit in Settings.")
    return
```

#### Error Handling & Retry Logic

**Retry with Exponential Backoff**:
```python
import time

def call_with_retry(llm_client, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = llm_client.call(system_prompt, user_prompt)
            return response
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                ui.show_toast(f"API temporarily unavailable, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                # Max retries exhausted
                ui.show_error(f"API call failed after {max_retries} attempts: {e}")
                raise
```

**Fallback to Alternative LLM**:
```python
def call_with_fallback(primary_provider, fallback_provider, prompt):
    try:
        primary_client = get_llm_client(primary_provider)
        return call_with_retry(primary_client, prompt)
    except Exception as primary_error:
        # Offer to switch to fallback
        user_confirms = ui.ask_user(
            f"{primary_provider} API failed. Switch to {fallback_provider}?",
            options=["Yes", "No"]
        )
        if user_confirms == "Yes":
            fallback_client = get_llm_client(fallback_provider)
            return call_with_retry(fallback_client, prompt)
        else:
            raise primary_error
```

---

### 5.5 Artifact Processing Pipeline

**End-to-End Flow** for Artifact Sync (Tab 2):

```
1. USER INPUT
   ↓
2. INPUT CLASSIFICATION (LLM Pass 1)
   - Detect type: transcript vs. notes vs. general
   - Extract metadata: speakers, dates, meeting title (if transcript)
   ↓
3. PRIVACY PROXY: ANONYMIZE
   - Detect PII via regex + NER
   - Replace with tokens (<PERSON_1>, <ORG_1>)
   - Store mappings in vault
   ↓
4. PERSONA DETERMINATION (LLM Pass 2)
   - Analyze content to select required roles (PM/PO/BA/Product)
   - Build combined system prompt
   ↓
5. ARTIFACT PATTERN MATCHING (LLM Pass 3)
   - Identify which artifacts need updates (RAID, Status Report, etc.)
   - Extract confidence scores per artifact
   ↓
6. DELTA EXTRACTION (LLM Pass 4)
   - Load current artifact content from markdown files
   - Compare current vs. new information
   - Generate only deltas (new risks, updated statuses)
   ↓
7. SPECIAL PROCESSING (if transcript detected)
   - Meeting Notes generation
   - GitHub task extraction
   - Technical Fluency Translation (if enabled)
   ↓
8. PRIVACY PROXY: RE-IDENTIFY
   - Replace tokens with original PII
   - Final output has real names restored
   ↓
9. BUBBLE GENERATION
   - Format updates as interactive bubbles
   - Color-code by urgency, sort by priority
   - Display in UI with [Copy] and [Apply] buttons
   ↓
10. USER REVIEW & REFINEMENT
    - User can provide feedback ("make more concise")
    - LLM regenerates specific bubbles
    ↓
11. COMMIT (when user clicks "Log Session")
    - Update markdown artifact files
    - Update SQLite metadata (last_updated, version)
    - Log session to history
    - Clear UI for next sync
```

**Performance Optimization**:
- **Parallel LLM Calls** where possible (input classification + persona determination can run concurrently)
- **Caching**: System prompts cached (don't re-send identical prompt structure)
- **Streaming**: Use Server-Sent Events (SSE) for real-time bubble updates as LLM generates

---

### 5.6 React Frontend & FastAPI Backend Implementation

**Technology Stack — Progressive Complexity**:

| Component | Phase 0 (MVP) | Phase 1 | Phase 2+ | Phase 4 |
|-----------|--------------|---------|----------|---------|
| **Language** | JavaScript React 18+ | TypeScript migration | TypeScript | TypeScript |
| **Styling** | Tailwind CSS | Tailwind CSS | Evaluate Material-UI | Final UI framework |
| **State** | useState + useContext | useState + useContext | Add Redux if needed | Redux |
| **Desktop** | Browser tab only | Browser tab | Browser tab | Electron wrapper |
| **Backend** | Python 3.10+ FastAPI | FastAPI | FastAPI | FastAPI (cloud option) |
| **Validation** | Pydantic | Pydantic | Pydantic | Pydantic |
| **HTTP Client** | fetch or Axios | Axios | Axios | Axios |
| **Real-time** | Polling | Polling | SSE for streaming | WebSocket (optional) |

**Rationale for Progressive Approach**: A novice developer using AI-assisted coding (Claude Code + RALPH) can build and validate the core flow faster with JavaScript + Tailwind than with TypeScript + Material-UI + Redux + Electron. Each technology layer is added only when the codebase complexity justifies it, avoiding premature over-engineering while maintaining upgrade paths.

---

#### **Frontend: React Component Structure**

**Main Application Shell**:
```tsx
// App.tsx
import React, { useState } from 'react';
import { Tabs, Tab, Box, AppBar } from '@mui/material';
import DailyPlanner from './tabs/DailyPlanner';
import ArtifactSync from './tabs/ArtifactSync';
import DeepStrategy from './tabs/DeepStrategy';
import ProjectInitiation from './tabs/ProjectInitiation';
import HistoryContext from './tabs/HistoryContext';
import Settings from './tabs/Settings';
import CommunicationsAssistant from './components/CommunicationsAssistant';
import FeedbackBox from './components/FeedbackBox';

function App() {
  const [activeTab, setActiveTab] = useState(1); // Default: Artifact Sync (Tab 2)

  return (
    <>
      <AppBar position="static">
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Daily Planner" />
          <Tab label="Artifact Sync" />
          <Tab label="Deep Strategy" />
          <Tab label="Project Initiation" />
          <Tab label="History & Context" />
          <Tab label="Settings & Landscape" />
        </Tabs>
      </AppBar>

      <Box sx={{ p: 3 }}>
        {activeTab === 0 && <DailyPlanner />}
        {activeTab === 1 && <ArtifactSync />}
        {activeTab === 2 && <DeepStrategy />}
        {activeTab === 3 && <ProjectInitiation />}
        {activeTab === 4 && <HistoryContext />}
        {activeTab === 5 && <Settings />}
      </Box>

      {/* Cross-Tab Features */}
      <CommunicationsAssistant />
      <FeedbackBox />
    </>
  );
}

export default App;
```

**Tab 2: Artifact Sync Component** (Primary Tab):
```tsx
// tabs/ArtifactSync.tsx
import React, { useState } from 'react';
import { TextField, Button, Box, CircularProgress } from '@mui/material';
import axios from 'axios';
import BubbleList from '../components/BubbleList';

const ArtifactSync: React.FC = () => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [bubbles, setBubbles] = useState([]);

  const handleSync = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/artifact-sync', {
        input: input,
        project_id: localStorage.getItem('current_project_id')
      });
      setBubbles(response.data.bubbles);
    } catch (error) {
      console.error('Artifact sync failed:', error);
      alert('Error processing input. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <TextField
        fullWidth
        multiline
        rows={8}
        placeholder="Paste meeting notes, transcript, or describe updates..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        variant="outlined"
        sx={{ mb: 2 }}
      />

      <Button
        variant="contained"
        onClick={handleSync}
        disabled={loading || !input.trim()}
      >
        {loading ? <CircularProgress size={24} /> : 'Sync Artifacts'}
      </Button>

      {bubbles.length > 0 && (
        <BubbleList bubbles={bubbles} onApply={(bubble) => {
          // Handle apply to database
          axios.post(`http://localhost:8000/api/apply-bubble`, bubble);
        }} />
      )}
    </Box>
  );
};

export default ArtifactSync;
```

**Bubble Component** (Expandable, Copy-to-Clipboard):
```tsx
// components/BubbleList.tsx
import React, { useState } from 'react';
import { Card, CardContent, Typography, Button, Collapse } from '@mui/material';

interface Bubble {
  id: string;
  artifact_type: string;
  change_type: string;
  preview: string;
  content: string;
  priority: 'critical' | 'important' | 'fyi';
  confidence: number;
}

const BubbleList: React.FC<{ bubbles: Bubble[], onApply: (bubble: Bubble) => void }> = ({ bubbles, onApply }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return '#ff4444';
      case 'important': return '#ffaa00';
      case 'fyi': return '#44ff44';
      default: return '#888888';
    }
  };

  return (
    <>
      {bubbles.map((bubble) => (
        <Card
          key={bubble.id}
          sx={{ mb: 2, borderLeft: `4px solid ${getPriorityColor(bubble.priority)}` }}
          onClick={() => setExpandedId(expandedId === bubble.id ? null : bubble.id)}
        >
          <CardContent>
            <Typography variant="h6">
              {bubble.artifact_type} • {bubble.change_type}
              {bubble.confidence < 0.7 && ' ⚠️ Low Confidence'}
            </Typography>

            <Collapse in={expandedId === bubble.id}>
              <Typography variant="body2" sx={{ mt: 2, whiteSpace: 'pre-wrap' }}>
                {bubble.preview}
              </Typography>

              <Box sx={{ mt: 2 }}>
                <Button
                  variant="outlined"
                  onClick={(e) => {
                    e.stopPropagation();
                    navigator.clipboard.writeText(bubble.content);
                    alert('Copied to clipboard!');
                  }}
                  sx={{ mr: 1 }}
                >
                  📋 Copy
                </Button>
                <Button
                  variant="contained"
                  onClick={(e) => {
                    e.stopPropagation();
                    onApply(bubble);
                    alert(`${bubble.artifact_type} updated!`);
                  }}
                >
                  ✅ Apply
                </Button>
              </Box>
            </Collapse>
          </CardContent>
        </Card>
      ))}
    </>
  );
};

export default BubbleList;
```

---

#### **Backend: FastAPI Routes**

**Main API Server**:
```python
# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from privacy_proxy import anonymize, re_identify
from llm_client import LLMClient
from artifact_manager import ArtifactManager
from session_manager import SessionManager

app = FastAPI(title="VPMA Backend API")

# CORS for local React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ArtifactSyncRequest(BaseModel):
    input: str
    project_id: str

class Bubble(BaseModel):
    id: str
    artifact_type: str
    change_type: str
    preview: str
    content: str
    priority: str
    confidence: float

class ArtifactSyncResponse(BaseModel):
    bubbles: List[Bubble]
    session_id: str

# Initialize services
llm_client = LLMClient(provider="claude")  # or "gemini"
artifact_manager = ArtifactManager()
session_manager = SessionManager()

@app.post("/api/artifact-sync", response_model=ArtifactSyncResponse)
async def artifact_sync(request: ArtifactSyncRequest):
    """
    Process user input, generate artifact update suggestions (bubbles).
    """
    try:
        # Step 1: Anonymize PII
        anonymized_input, vault = anonymize(request.input)

        # Step 2: Call LLM
        prompt = f"""
        Analyze this input and identify which PM artifacts need updates.
        Return JSON array of updates with: artifact_type, change_type, proposed_text, confidence.

        Input: {anonymized_input}
        """
        llm_response = await llm_client.call(prompt, max_tokens=2000)

        # Step 3: Re-identify PII
        re_identified_response = re_identify(llm_response, vault)

        # Step 4: Parse LLM response into bubbles
        bubbles = artifact_manager.parse_llm_response_to_bubbles(re_identified_response)

        # Step 5: Create session record
        session_id = session_manager.create_session(
            project_id=request.project_id,
            input=request.input,
            bubbles=bubbles
        )

        return ArtifactSyncResponse(bubbles=bubbles, session_id=session_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/apply-bubble")
async def apply_bubble(bubble: Bubble):
    """
    Apply bubble update to artifact markdown file and update SQLite metadata.
    """
    try:
        artifact_manager.apply_bubble_update(bubble)
        return {"status": "success", "message": f"{bubble.artifact_type} updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects")
async def list_projects():
    """Return list of all projects."""
    projects = artifact_manager.get_all_projects()
    return {"projects": projects}

@app.post("/api/privacy-proxy/preview")
async def preview_anonymization(request: dict):
    """
    Show user what will be anonymized before sending to LLM.
    """
    anonymized, vault = anonymize(request['input'])
    return {
        "original": request['input'],
        "anonymized": anonymized,
        "entities_detected": len(vault)
    }

# Run server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**LLM Client Module**:
```python
# llm_client.py
from anthropic import Anthropic
import google.generativeai as genai
from typing import Literal
import os

class LLMClient:
    def __init__(self, provider: Literal["claude", "gemini"]):
        self.provider = provider

        if provider == "claude":
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = "claude-3-5-sonnet-20241022"
        elif provider == "gemini":
            genai.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))
            self.client = genai.GenerativeModel("gemini-1.5-pro")
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def call(self, prompt: str, system_prompt: str = "", max_tokens: int = 4000) -> str:
        """Unified interface for LLM calls."""
        if self.provider == "claude":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        elif self.provider == "gemini":
            response = self.client.generate_content(prompt)
            return response.text

    def switch_provider(self, new_provider: Literal["claude", "gemini"]):
        """Switch between Claude and Gemini."""
        self.__init__(new_provider)
```

---

#### **Electron Integration** (Optional, for desktop features):

```javascript
// main.js (Electron main process)
const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // Load React app
  win.loadURL('http://localhost:3000'); // Dev mode
  // win.loadFile(path.join(__dirname, '../build/index.html')); // Production
}

app.whenReady().then(createWindow);
```

**Running the Application**:
```bash
# Terminal 1: Start FastAPI backend
cd backend
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn anthropic google-generativeai spacy python-dotenv
python main.py  # Runs on http://localhost:8000

# Terminal 2: Start React frontend
cd frontend
npm install
npm start  # Runs on http://localhost:3000

# Optional Terminal 3: Start Electron wrapper
npm run electron
```

---

### 5.7 Error Handling & Reliability

**LLM API Failures**:
- **Retry Logic**: Exponential backoff (1s → 2s → 4s), 3 attempts
- **Fallback**: Offer to switch LLM (Claude ↔ Gemini) on repeated failures
- **User Notification**: Toast message "API temporarily unavailable, retrying..." with progress indicator

**PII Detection Failures**:
- **Conservative Approach**: If unsure, anonymize (false positives acceptable, false negatives catastrophic)
- **User Review**: If confidence < 70%, show preview before sending (Settings toggle)
- **Audit Trail**: Log all anonymized payloads for post-hoc review

**Document Parsing Failures**:
- **Format Pre-Check**: Warn user if document has unsupported elements (complex tables, embedded images in PDFs)
- **Plain Text Fallback**: If parsing fails, ask user to copy/paste plain text version
- **Error Message**: "Unable to parse {file}. Please try plain text version or contact support."

**Data Corruption**:
- **SQLite WAL Mode**: Write-Ahead Logging for crash resilience
  ```python
  conn = sqlite3.connect('vpma.db')
  conn.execute('PRAGMA journal_mode=WAL')
  ```
- **Automatic Integrity Check** on startup:
  ```python
  result = conn.execute('PRAGMA integrity_check').fetchone()
  if result[0] != 'ok':
      ui.show_error("Database corruption detected. Restore from backup.")
  ```

**LLM Hallucinations**:
- **Confidence Scoring**: Show "⚠️ Low Confidence" when LLM is uncertain
- **User Review Required**: Never auto-save updates (user must review and confirm)
- **Discrepancy Disclaimer**: If LLM output deviates from input, show warning footer
- **Version History**: Allow rollback (MVP: 1-level Undo, Phase 2: full version history)

---

## 6. Artifact Landscape & Content Model

### 6.1 Supported Artifact Types (Complete Catalog)

VPMA supports **15 artifact types** across 4 categories, covering the complete PM artifact lifecycle.

#### Category 1: Core PM Artifacts

**1. Project Charter**
- **Purpose**: Foundational document defining project objectives, scope, success criteria, and constraints
- **Content Model**:
  - Objective (1-2 sentences: what and why)
  - Scope (In-Scope list, Out-of-Scope list)
  - Deliverables (numbered list with acceptance criteria)
  - Success Criteria (measurable outcomes)
  - Stakeholders (Sponsor, PM, Key Stakeholders with roles)
  - Constraints (Timeline, Budget, Resources)
  - Assumptions (foundational beliefs requiring validation)
- **Format**: Markdown or DOCX
- **Update Triggers**: Project initiation, major scope changes, stakeholder requests
- **Template Variables**: `{PROJECT_NAME}`, `{OBJECTIVE}`, `{DELIVERABLES}`, `{TIMELINE}`, `{BUDGET}`

**2. Project Schedule / Timeline**
- **Purpose**: Phased timeline with milestones, dependencies, and resource allocation
- **Content Model**:
  - Phases (name, duration, start/end dates)
  - Milestones (name, target date, acceptance criteria, owner)
  - Dependencies (task relationships, blocking items)
  - Resource Allocation (who's assigned to what, FTE %)
  - Critical Path (tasks that determine project duration)
- **Format**: Markdown table, Excel/CSV, or text-based Gantt representation
- **Update Triggers**: After planning sessions, weekly reviews, when scope/timeline shifts
- **Interdependencies**: Influenced by Charter (scope defines phases), influences RAID Log (date-based risks), Status Report (progress tracking)

**3. RAID Log (Risks, Assumptions, Issues, Dependencies)**
- **Purpose**: Centralized tracking of project uncertainties and blockers
- **Content Model**:
  - **Risks**: ID, Description, Probability (Low/Medium/High), Impact (Low/Medium/High), Mitigation Plan, Owner, Status (Open/Mitigated/Closed)
  - **Assumptions**: ID, Description, Validation Date, Status (Valid/Invalid/Pending)
  - **Issues**: ID, Description, Severity (Low/Medium/High/Critical), Resolution Plan, Owner, Status (Open/In Progress/Resolved)
  - **Dependencies**: ID, Description, Dependency On (team/vendor/external), Status (Pending/Confirmed/Delivered)
- **Format**: Markdown table or JSON for structured data
- **Update Triggers**: After every meeting, weekly reviews, when new risks/issues identified
- **Interdependencies**: Influenced by Charter (scope risks), Schedule (timeline risks), Meeting Notes (new risks surfaced)

---

#### Category 2: Status & Reporting

**4. Status Report**
- **Purpose**: Executive-level summary of project health for stakeholder communication
- **Content Model**:
  - Executive Summary (3-5 bullet points: highlights, concerns, asks)
  - Progress Since Last Report (completed milestones, key achievements)
  - Upcoming Work (next 2 weeks priorities)
  - Risks & Issues (top 3 from RAID Log with status)
  - Timeline Update (on track / at risk / delayed with explanation)
  - Budget Update (spend to date, forecast, variances)
  - Metrics / KPIs (if applicable: velocity, quality, customer satisfaction)
- **Format**: Markdown or DOCX
- **Update Triggers**: Weekly (or configurable cadence via Fixed Landscape), before steering committee meetings
- **Interdependencies**: Influenced by RAID Log (risks), Schedule (timeline), Action Items (progress)

**5. Project Dashboard (Text-Based or Data Export)**
- **Purpose**: Real-time project health metrics for at-a-glance visibility
- **Content Model**:
  - KPIs (burndown, velocity, budget utilization, quality metrics)
  - Health Score (overall project health: green/yellow/red with rationale)
  - Milestone Progress (% complete per phase)
  - Risk Heatmap (count of risks by probability/impact quadrant)
- **Format**: JSON or CSV (for import to visualization tools like Tableau, Google Sheets)
- **Update Triggers**: Daily or on-demand (auto-calculated from other artifacts)
- **Interdependencies**: Aggregates data from Schedule, RAID Log, Budget

---

#### Category 3: Requirements & Product

**6. PRD (Product Requirements Document)**
- **Purpose**: Detailed product vision, user needs, and feature specifications
- **Content Model**:
  - Problem Statement (what problem are we solving, for whom)
  - User Personas (target users with needs, goals, pain points)
  - Feature List (prioritized features with descriptions)
  - User Stories (high-level: "As a [role], I want [feature], so that [benefit]")
  - Acceptance Criteria (per feature: how we know it's done)
  - Non-Functional Requirements (performance, security, scalability)
  - Success Metrics (how we measure product success)
  - Out of Scope (explicitly excluded features to manage expectations)
- **Format**: Markdown or DOCX (5-15 pages typical)
- **Update Triggers**: Feature planning sessions, stakeholder feedback, roadmap changes
- **Interdependencies**: Influenced by Charter (project goals), influences User Stories, Feature Specs, Schedule (feature timeline)

**7. User Stories / Backlog**
- **Purpose**: Granular, actionable user-centric feature descriptions for development
- **Content Model** (per story):
  - User Story Format: "As a [role], I want [feature], so that [benefit]"
  - Priority (High/Medium/Low or MoSCoW: Must/Should/Could/Won't)
  - Effort Estimate (story points, t-shirt sizes, or hours)
  - Acceptance Criteria (bulleted checklist of "done" conditions)
  - Dependencies (other stories that must complete first)
  - Status (Backlog / In Progress / Done)
- **Format**: Markdown list or CSV (for import to Jira, Linear, etc.)
- **Update Triggers**: Sprint planning, backlog grooming sessions
- **Interdependencies**: Influenced by PRD (features), influences Schedule (sprint planning)

**8. Feature Specifications**
- **Purpose**: Detailed technical and UX specifications for individual features
- **Content Model**:
  - Feature Name & Overview
  - User Flow (step-by-step interaction)
  - Technical Approach (architecture, APIs, data models)
  - UI/UX Notes (wireframes, design decisions)
  - Dependencies (external services, internal components)
  - Edge Cases (error handling, boundary conditions)
- **Format**: Markdown (2-5 pages per feature)
- **Update Triggers**: Design sessions, technical reviews
- **Interdependencies**: Influenced by PRD (high-level feature), influences Schedule (implementation timeline)

---

#### Category 4: Meeting & Communications

**9. Meeting Notes**
- **Purpose**: Structured record of meeting discussions, decisions, and action items
- **Content Model**:
  - Meeting Metadata (Date, Time, Attendees, Meeting Title)
  - Agenda (planned topics)
  - Discussion Summary (key points discussed per agenda item)
  - Decisions Made (numbered list with context and rationale)
  - Action Items (task, owner, due date)
  - Topics for Follow-Up (items tabled or requiring further discussion)
- **Format**: Markdown
- **Update Triggers**: After every meeting (auto-generated from transcripts in Artifact Sync)
- **Interdependencies**: Influences Action Item Log, Decision Log, RAID Log (new risks mentioned)

**10. Action Item Log**
- **Purpose**: Centralized tracking of all action items across all meetings
- **Content Model**:
  - Item ID, Description, Owner, Due Date, Status (Pending/In Progress/Done), Source (which meeting/session)
- **Format**: Markdown table or JSON
- **Update Triggers**: After every meeting, weekly reviews
- **Interdependencies**: Influenced by Meeting Notes (new action items), influences Status Report (progress tracking)

**11. Decision Log**
- **Purpose**: Permanent record of key decisions for traceability and alignment
- **Content Model**:
  - Decision ID, Date, Decision (clear statement), Context (why this came up), Rationale (why this choice), Alternatives Considered, Decider(s) (who made the call)
- **Format**: Markdown table
- **Update Triggers**: After key decisions in meetings or strategy sessions
- **Interdependencies**: Influenced by Meeting Notes (decisions surfaced), influences Charter/PRD (scope decisions)

**12. Communications Plan**
- **Purpose**: Defines stakeholder communication rhythm and channels
- **Content Model**:
  - Stakeholder Matrix (Name, Role, Interest Level, Preferred Channel)
  - Meeting Cadence (recurring meetings: title, frequency, attendees, purpose)
  - Reporting Structure (what reports go to whom, how often)
  - Escalation Path (how to escalate issues, to whom, when)
  - Communication Channels (Slack, email, meetings, dashboards)
- **Format**: Markdown or DOCX
- **Update Triggers**: Project initiation, stakeholder changes
- **Interdependencies**: Influenced by Charter (stakeholders), influences Fixed Landscape (meeting rhythm)

**13. Meeting Agenda (Recurring Meetings)**
- **Purpose**: Pre-populated agenda templates for recurring meetings, updated based on current project state
- **Content Model**:
  - Meeting Title
  - Date/Time
  - Attendees (expected participants)
  - Agenda Items (numbered topics with time allocations)
  - Expected Outcomes (what should be decided/reviewed)
  - Pre-Reading Materials (artifacts to review beforehand: RAID Log, Status Report)
- **Format**: Markdown
- **Update Triggers**: Before each meeting (generated/updated by Daily Planner tab)
- **Interdependencies**: Linked to Fixed Landscape (recurring meeting configuration), uses current RAID Log/Status Report state
- **Special Note**: Daily Planner tab auto-updates agendas based on artifact freshness and project health

**14. Project Plan**
- **Purpose**: Comprehensive planning document that goes beyond timeline to include resource allocation, budget, dependencies, risk mitigation, and quality gates
- **Content Model**:
  - Phases (name, objectives, duration, deliverables)
  - Resource Allocation (team members, FTE %, roles, skills needed)
  - Budget Plan (cost breakdown by phase, contingency reserves, spend forecast)
  - Dependencies (internal team dependencies, external vendor/partner dependencies)
  - Critical Path Analysis (tasks that determine overall project duration)
  - Risk Mitigation Strategy (proactive mitigation plans from RAID Log)
  - Quality Gates (checkpoints, acceptance criteria, sign-off requirements)
  - Communication Strategy (how/when stakeholders are updated per phase)
- **Format**: Markdown or DOCX (8-15 pages typical)
- **Update Triggers**: Project initiation, major scope/resource changes, phase transitions, quarterly reviews
- **Interdependencies**: Influenced by Charter (objectives, constraints), Schedule (phases, milestones), RAID Log (risk mitigation), Communications Plan (stakeholder strategy)
- **Distinction from Schedule**: Schedule is timeline-focused (Gantt, dates, dependencies); Project Plan is holistic (resources, budget, quality, communication)
- **Output Types**:
  - **New Project Plan**: Generated during Project Initiation or when starting new planning cycle
  - **Refinements to Existing Plan**: Updates based on meeting notes, status reviews, resource changes (e.g., "Budget increased by 15%, add Phase 4 contingency")

**15. Tasks / Work Items**
- **Purpose**: Project task tracking broader than GitHub Issues - supports Jira, Asana, Monday, spreadsheets, or any task management system
- **Content Model**:
  - Task ID (if linked to external system: "JIRA-1234" or "Task #42")
  - Task Description (what needs to be done)
  - Owner (person responsible)
  - Due Date (target completion date)
  - Status (Backlog / To Do / In Progress / Blocked / Done)
  - Priority (P0-Critical / P1-High / P2-Medium / P3-Low)
  - Dependencies (other tasks that must complete first, or external blockers)
  - Notes (updates, blockers, progress notes - appended over time)
  - Estimated Effort (hours, days, or story points)
  - Actual Effort (time spent so far)
- **Format**: Markdown table, JSON, or CSV (for import to task management tools)
- **Update Triggers**: After meetings (new tasks identified), daily standups, sprint planning, weekly reviews
- **Interdependencies**: Influenced by Meeting Notes (action items → tasks), PRD/User Stories (features → implementation tasks), RAID Log (mitigation actions → tasks)
- **Output Types**:
  - **New Tasks Suggested**: Items mentioned in meetings/sessions that should become tracked tasks
    - Example: "Task: Complete API documentation (Owner: Sarah, Due: Feb 20, Priority: P1)"
  - **Updates to Existing Tasks**: Progress notes, status changes, blocker identification
    - Example: "Task #12 (Database migration): 60% complete, on track for Friday delivery"
    - Example: "Task JIRA-456 (Security audit): Blocked - waiting on vendor response, due date at risk"
  - **Refinements**: Changes to priority, ownership, due dates based on new information
    - Example: "Task #18: Increase priority to P0 (critical path dependency identified)"
- **Special Note**: Works with any task system (Jira, Asana, Monday, Linear, Trello, spreadsheets) - MVP output is markdown-formatted task list for copy/paste, Phase 2+ adds direct API integrations

---

### 6.2 Artifact Interdependencies

**Dependency Graph** (what influences what):

```
Project Charter (source of truth for scope, goals, timeline)
  ↓ influences
  ├── Project Plan (objectives, constraints, stakeholder strategy)
  ├── Project Schedule (phases, milestones based on Charter deliverables)
  ├── RAID Log (scope risks, constraint risks)
  ├── Communications Plan (stakeholders from Charter)
  └── PRD (product goals aligned with project objectives)

Project Plan
  ↓ influences
  ├── Project Schedule (phases inform timeline, budget informs resource allocation)
  ├── RAID Log (risk mitigation strategies, quality gates)
  ├── Tasks (resource allocation creates work breakdown)
  └── Status Report (budget tracking, resource utilization)

Project Schedule
  ↓ influences
  ├── Status Report (timeline section, progress tracking)
  ├── RAID Log (date-based risks: "Phase 2 delay risk")
  └── Tasks (schedule defines task deadlines and dependencies)

PRD (Product Requirements Document)
  ↓ influences
  ├── User Stories (granular breakdown of features)
  ├── Feature Specifications (detailed design per feature)
  ├── Project Schedule (feature implementation timeline)
  └── Tasks (features → implementation tasks)

Meeting Notes
  ↓ influences
  ├── Action Item Log (extract action items)
  ├── Decision Log (record decisions)
  ├── RAID Log (new risks/issues mentioned in meetings)
  └── Tasks (action items → tracked tasks, new work identified)

Action Item Log
  ↓ influences
  ├── Status Report (progress on action items tracked)
  └── Tasks (action items become tasks)

RAID Log
  ↓ influences
  ├── Status Report (top risks/issues highlighted)
  ├── Project Plan (risk mitigation strategies)
  └── Tasks (mitigation actions → tasks)

Tasks / Work Items
  ↓ influences
  └── Status Report (task completion progress, blockers, velocity)

Communications Plan
  ↓ influences
  └── Fixed Landscape (defines recurring meeting rhythm)
```

**Change Propagation Rules** (for Deep Strategy tab):

| If this artifact changes | Then these artifacts need review | Reason |
|-------------------------|-----------------------------------|---------|
| **Charter** scope expands | Project Plan, Schedule, RAID Log, Status Report, PRD | New deliverables → planning, phases, risks, timeline |
| **Project Plan** budget increases | Schedule, Tasks, Status Report | Budget impacts resource allocation, work breakdown, reporting |
| **Project Plan** resource changes | Tasks, Schedule, RAID Log | Resource shifts affect task assignments, timeline, capacity risks |
| **Schedule** milestone delays | RAID Log, Status Report, Tasks | Timeline risk, stakeholder communication, task deadline impacts |
| **PRD** adds feature | User Stories, Feature Specs, Schedule, Tasks | Feature breakdown, implementation timeline, development work |
| **RAID Log** critical risk added | Status Report, Project Plan, Charter (if scope impact) | Stakeholder awareness, mitigation planning, potential scope change |
| **Meeting Notes** surface decision | Decision Log, Charter/PRD/RAID (depending on decision type), Tasks (if action items) | Permanent record, potential artifact updates, new work identified |
| **Tasks** major blocker identified | RAID Log (new issue), Status Report, Schedule (if timeline impact) | Blocker becomes tracked issue, stakeholder awareness, timeline risk |

---

### 6.3 Artifact Templates

**Template Library Structure**:
```
templates/
  ├── software_project/
  │   ├── project_charter.md
  │   ├── prd.md
  │   ├── raid_log.md
  │   ├── user_stories.md
  │   └── feature_spec.md
  ├── marketing_campaign/
  │   ├── project_charter.md
  │   ├── creative_brief.md
  │   ├── stakeholder_register.md
  │   └── budget_tracker.md
  ├── infrastructure_project/
  │   ├── project_charter.md
  │   ├── technical_design_doc.md
  │   └── risk_assessment.md
  └── ...
```

**Example Template: Project Charter** (`templates/software_project/project_charter.md`):

```markdown
# {PROJECT_NAME} - Project Charter

## Objective
{OBJECTIVE}

## Scope

### In Scope
{SCOPE_IN_LIST}

### Out of Scope
{SCOPE_OUT_LIST}

## Deliverables
{DELIVERABLES_LIST}

## Success Criteria
{SUCCESS_CRITERIA_LIST}

## Stakeholders
- **Sponsor**: {SPONSOR_NAME}
- **Project Manager**: {PM_NAME}
- **Key Stakeholders**: {STAKEHOLDERS_LIST}

## Constraints
- **Timeline**: {TIMELINE}
- **Budget**: {BUDGET}
- **Resources**: {RESOURCES}

## Assumptions
{ASSUMPTIONS_LIST}

---

*Generated by VPMA on {DATE}*
```

**Template Metadata** (`templates/software_project/project_charter.json`):

```json
{
  "artifact_type": "Project Charter",
  "project_types": ["software", "hardware", "infrastructure"],
  "sections": [
    "Objective",
    "Scope",
    "Deliverables",
    "Success Criteria",
    "Stakeholders",
    "Constraints",
    "Assumptions"
  ],
  "placeholders": {
    "PROJECT_NAME": {"type": "string", "required": true},
    "OBJECTIVE": {"type": "string", "required": true, "max_length": 500},
    "SCOPE_IN_LIST": {"type": "list", "required": true},
    "SCOPE_OUT_LIST": {"type": "list", "required": false},
    "DELIVERABLES_LIST": {"type": "list", "required": true},
    "SUCCESS_CRITERIA_LIST": {"type": "list", "required": true},
    "SPONSOR_NAME": {"type": "string", "required": true},
    "PM_NAME": {"type": "string", "required": false},
    "STAKEHOLDERS_LIST": {"type": "list", "required": false},
    "TIMELINE": {"type": "string", "required": true},
    "BUDGET": {"type": "string", "required": false},
    "RESOURCES": {"type": "string", "required": false},
    "ASSUMPTIONS_LIST": {"type": "list", "required": false}
  },
  "estimated_length_pages": 1,
  "typical_generation_time_seconds": 45
}
```

**Example Template: RAID Log** (`templates/software_project/raid_log.md`):

```markdown
# RAID Log - {PROJECT_NAME}

Last Updated: {DATE}

## Risks

| ID | Description | Probability | Impact | Mitigation | Owner | Status |
|----|-------------|-------------|--------|------------|-------|--------|
| R1 | {RISK_1_DESCRIPTION} | {PROBABILITY} | {IMPACT} | {MITIGATION} | {OWNER} | Open |

## Assumptions

| ID | Description | Validation Date | Status |
|----|-------------|-----------------|--------|
| A1 | {ASSUMPTION_1} | {VALIDATION_DATE} | Valid |

## Issues

| ID | Description | Severity | Resolution | Owner | Status |
|----|-------------|----------|------------|-------|--------|
| I1 | {ISSUE_1} | {SEVERITY} | {RESOLUTION} | {OWNER} | Open |

## Dependencies

| ID | Description | Dependency On | Status |
|----|-------------|---------------|--------|
| D1 | {DEPENDENCY_1} | {EXTERNAL_TEAM} | Pending |

---

*Generated by VPMA on {DATE}*
```

**Template Filling Process** (in Project Initiation tab):

```python
def fill_template(template_path, user_description, project_type):
    # 1. Load template
    with open(template_path, 'r') as f:
        template_content = f.read()
    metadata = load_template_metadata(template_path)

    # 2. Extract placeholders
    placeholders = metadata['placeholders']

    # 3. LLM call to extract values from user description
    system_prompt = f"""
    You are a template filling assistant.
    Given a project description, extract values for these placeholders: {placeholders.keys()}

    Return JSON with placeholder values.
    """
    user_prompt = f"Project Description: {user_description}"

    filled_values = llm_client.call_structured(system_prompt, user_prompt, output_schema=placeholders)

    # 4. Replace placeholders in template
    filled_content = template_content
    for placeholder, value in filled_values.items():
        if isinstance(value, list):
            # Convert list to markdown bullets
            value_str = "\n".join([f"- {item}" for item in value])
        else:
            value_str = str(value)

        filled_content = filled_content.replace(f"{{{placeholder}}}", value_str)

    # 5. Replace date
    from datetime import datetime
    filled_content = filled_content.replace("{DATE}", datetime.now().strftime("%B %d, %Y"))

    return filled_content
```

---

### 6.4 Fixed Landscape Configuration

**Purpose**: Define user's standard meeting/artifact rhythm for personalized intelligence in Daily Planner and Artifact Sync.

**Schema** (stored in `projects.landscape_config` JSON field):

```json
{
  "artifacts": [
    {
      "artifact_type": "Status Report",
      "associated_meeting": "Weekly Steering Committee",
      "timing": "Every Monday 9:00 AM",
      "update_frequency": "Weekly",
      "active": true
    },
    {
      "artifact_type": "RAID Log",
      "associated_meeting": "Daily Standup",
      "timing": "Daily 9:30 AM",
      "update_frequency": "After every meeting",
      "active": true
    },
    {
      "artifact_type": "Meeting Agenda",
      "associated_meeting": "Weekly Steering Committee",
      "timing": "Every Monday 9:00 AM",
      "update_frequency": "Before every meeting (Sunday evening)",
      "active": true,
      "special_note": "Auto-updated by Daily Planner based on current RAID Log and Status Report"
    },
    {
      "artifact_type": "PRD",
      "associated_meeting": "Product Planning",
      "timing": "Bi-weekly Thursdays 2:00 PM",
      "update_frequency": "Bi-weekly",
      "active": true
    },
    {
      "artifact_type": "Action Item Log",
      "associated_meeting": "All Meetings",
      "timing": "N/A",
      "update_frequency": "After every meeting",
      "active": true
    }
  ],
  "custom_sensitive_terms": [
    "Project Falcon",
    "ACME Corp",
    "ClientCo",
    "Q4 Roadmap",
    "Partnership with VendorX"
  ],
  "default_personas_enabled": ["PM", "PO", "BA", "Product Manager", "Program Manager"]
}
```

**Pre-Populated Defaults** (for new projects):

When user creates a new project, Fixed Landscape is initialized with 8-10 smart defaults:

```python
DEFAULT_LANDSCAPE = {
    "artifacts": [
        # Core PM rhythms
        {"artifact_type": "Status Report", "associated_meeting": "Weekly Steering Committee", "timing": "Every Monday 9am", "update_frequency": "Weekly"},
        {"artifact_type": "RAID Log", "associated_meeting": "Weekly Steering Committee", "timing": "Every Monday 9am", "update_frequency": "Weekly"},
        {"artifact_type": "Meeting Agenda", "associated_meeting": "Weekly Steering Committee", "timing": "Every Monday 9am", "update_frequency": "Before every meeting"},

        # Agile/Product rhythms (if project_type == "software")
        {"artifact_type": "User Stories", "associated_meeting": "Sprint Planning", "timing": "Bi-weekly Mondays 10am", "update_frequency": "Bi-weekly"},
        {"artifact_type": "PRD", "associated_meeting": "Product Review", "timing": "Monthly last Friday 2pm", "update_frequency": "Monthly"},

        # Universal
        {"artifact_type": "Action Item Log", "associated_meeting": "All Meetings", "timing": "N/A", "update_frequency": "After every meeting"},
        {"artifact_type": "Decision Log", "associated_meeting": "All Meetings", "timing": "N/A", "update_frequency": "After key decisions"},
        {"artifact_type": "Meeting Notes", "associated_meeting": "All Meetings", "timing": "N/A", "update_frequency": "After every meeting"}
    ],
    "custom_sensitive_terms": [],
    "default_personas_enabled": ["PM", "PO", "BA", "Product Manager", "Program Manager"]
}
```

User can edit this in **Settings & Landscape** tab (inline table editing or natural language configurator).

**Usage in Daily Planner**:

```python
def generate_daily_script(calendar_text, landscape_config):
    # 1. Parse calendar
    meetings = parse_calendar(calendar_text)

    # 2. Match meetings to landscape
    for meeting in meetings:
        # Fuzzy match meeting title to landscape entries
        landscape_entry = find_best_match(meeting['title'], landscape_config['artifacts'])

        if landscape_entry:
            # 3. Get associated artifacts
            associated_artifacts = [landscape_entry['artifact_type']]

            # 4. Check artifact freshness
            for artifact_type in associated_artifacts:
                last_updated = get_artifact_last_updated(artifact_type)
                days_stale = (datetime.now() - last_updated).days

                if days_stale > 3:  # Example threshold
                    meeting['prep_notes'].append(
                        f"⚠️ {artifact_type} last updated {days_stale} days ago - consider updating before meeting"
                    )

            # 5. Generate agenda, talking points, etc.
            meeting['suggested_agenda'] = generate_agenda(meeting, landscape_entry, current_artifact_state)
            meeting['talking_points'] = generate_talking_points(meeting, current_artifact_state)

    return daily_script
```

**Landscape Editing via Natural Language**:

User types: "Add a new artifact: Technical Design Doc, updated monthly, presented at Architecture Review every last Friday"

LLM parses:
```json
{
  "artifact_type": "Technical Design Doc",
  "associated_meeting": "Architecture Review",
  "timing": "Every last Friday of the month",
  "update_frequency": "Monthly",
  "active": true
}
```

Inserted into landscape_config → User sees new row in Settings table.

---

### 6.5 Artifact Lifecycle Management

**Creation** (Project Initiation tab):
- User describes project → LLM generates baseline artifacts from templates
- Artifacts saved as markdown files in `~/VPMA/artifacts/{project_name}/`
- Metadata inserted into `artifacts` table

**Updates** (Artifact Sync tab):
- User provides input (transcript, notes) → LLM identifies deltas
- User reviews and applies bubbles → Markdown files updated
- `last_updated` timestamp incremented, `version_number` incremented

**Consistency Checks** (Deep Strategy tab):
- User uploads artifacts → LLM builds dependency graph
- Multi-pass reasoning detects inconsistencies → Generates proposed updates
- User reviews diffs and applies → All artifacts updated atomically

**Export**:
- Per-artifact export: [Export to DOCX/PDF/Markdown] buttons
- Bulk export: [Export All Artifacts] in Settings → Generates ZIP file

**Version Control** (MVP: Simple Undo):
- Before each update, save current version to session state
- [Undo] button restores previous version (one-level rollback only)
- **Phase 2**: Full version history in `artifact_versions` table (view all past versions, restore any)

**Deletion**:
- User can delete artifact via Settings → Artifacts table
- Soft delete: `UPDATE artifacts SET active = FALSE WHERE artifact_id = ?`
- File remains on disk but hidden from UI (can be manually recovered if needed)

---

## 7. Roadmap & Phasing

### Overview: 5-Phase Rollout Strategy

VPMA will be delivered in 5 phases, with each phase building on the previous foundation. The phasing strategy prioritizes:

0. **Foundation MVP** (Phase 0: Lean validation in ~4 weeks with simplified stack)
1. **Core Experience** (Phase 1: Full Artifact Sync + Settings + Cross-Tab features)
2. **Intelligence + Multi-Project** (Phase 2: Deep Strategy + Local LLM + Multi-Project)
3. **Proactive Workflows** (Phase 3: Daily Planner + Project Initiation + History)
4. **Commercial Readiness** (Phase 4: Security, Auth, Integrations, HR Planning)

**Total Development Time**: ~52-68 weeks (~12-16 months total)
**Phase 0 (Foundation MVP)**: 4 weeks — validates core hypothesis with minimal scope
**Full Feature Set**: Months 12-16 (Phase 4 complete)

**Development Methodology**: AI-assisted development using Claude Code + RALPH loop technique (see Section 10.6). Developer is a novice programmer directing AI agents; time estimates reflect this workflow.

**Note on MVP Strategy**: Rather than building the full React/TypeScript/Redux/Electron/Material-UI stack in one large Phase 1 (16-24 weeks), Phase 0 uses a **simplified tech stack** (JavaScript React, Tailwind CSS, no Redux, no Electron) to validate the core value proposition in 4 weeks. Complexity is added progressively in later phases, preventing premature over-engineering while maintaining architectural foundations that avoid technical debt.

**Technical Debt Prevention**: Phase 0 includes 5 specific architectural foundations (abstract LLM interface, project-scoped data, modular Privacy Proxy, environment-based config, input type detection) that cost ~8-12 hours extra but prevent weeks of refactoring when adding future features (local LLM, multi-project, web deployment, integrations, image support). See Section 10.6 for details.

---

### Phase 0: Foundation MVP (Lean Validation)

**Timeline**: 4 weeks (~1 month)

**Goal**: Validate core hypothesis — does pasting meeting notes and getting artifact suggestions with copy-to-clipboard actually save a PM meaningful time? Minimal scope, maximum learning.

**Development Approach**: AI-assisted via Claude Code + RALPH loop technique. ~20 discrete tasks, human-in-the-loop mode. Estimated 50-70 keyboard hours over 4 weeks. See Section 10.6 for detailed breakdown.

**Simplified Tech Stack** (debt-preventing foundations included, complexity deferred):

| Component | Phase 0 Choice | Why (vs. full stack) | Cost to Add Later |
|-----------|---------------|---------------------|-------------------|
| **Frontend Language** | JavaScript React | Removes TypeScript compilation errors, faster iteration for novice | 1-2 days to add types |
| **State Management** | React useState + useContext | Eliminates Redux boilerplate for 5-7 component app | 1-2 days when state grows |
| **Desktop Wrapper** | None (browser tab at localhost:3000) | Eliminates Electron native build complexity | 2-3 days to wrap |
| **UI Framework** | Tailwind CSS | Simpler than Material-UI, AI generates it fluently, less config | 2-3 days to swap |
| **Backend** | Python FastAPI (unchanged) | Already simple, async-capable, right choice | N/A |
| **Database** | SQLite (unchanged) | Already lightweight and appropriate | N/A |
| **NER Model** | spaCy en_core_web_sm | Lightweight (~15MB), sufficient for MVP | Upgrade model in-place |

**Features Delivered**:

1. **Artifact Sync** (Single-page core flow)
   - Text input area (paste meeting notes, transcripts, or free-form updates)
   - Submit button → backend processes → returns artifact suggestions
   - Suggestion cards displayed (artifact name, change type, proposed text)
   - **Copy-to-clipboard** button per suggestion (primary action — user pastes into real artifacts)
   - **Apply** button per suggestion (stores update in VPMA's local database)
   - Basic loading state and error handling
   - Session logging (write-only — records what was synced, no History UI yet)

2. **Privacy Proxy** (Core anonymization)
   - Regex patterns for PII detection (emails, phone numbers, URLs)
   - spaCy NER for names, organizations, locations (en_core_web_sm)
   - Token vault (SQLite table, global scope with `project_id` ready)
   - Re-identification on LLM response
   - Preview mode when confidence < 70%
   - Audit log (`~/VPMA/privacy/audit_log.jsonl`)

3. **Basic Settings Panel**
   - API key configuration (Claude + Gemini keys)
   - LLM provider toggle (Claude ⟷ Gemini)
   - Custom sensitive terms list (user-defined PII additions)

4. **Core Infrastructure** (with 5 debt-preventing foundations)
   - **Frontend**: JavaScript React 18+ with Tailwind CSS (localhost:3000)
   - **Backend**: Python FastAPI (localhost:8000), REST API, CORS middleware
   - **Database**: SQLite with full schema (projects, artifacts, sessions, pii_vault) — includes `project_id` on all tables even though MVP is single-project
   - **Storage**: Markdown artifact files (`~/VPMA/artifacts/{project_name}/*.md`)
   - **LLM Client**: Abstract interface with `call()` and `stream()` methods + Claude adapter + Gemini adapter (ready for Ollama adapter in Phase 2)
   - **Privacy Proxy**: Standalone module with clean interface (`anonymize()` → `reidentify()`) — internals swappable without touching other code
   - **Config**: All URLs, API keys, paths from `.env` (no hardcoded localhost in business logic)
   - **Input Pipeline**: Backend classifies input type (text, transcript) — extensible for images later
   - **Error Handling**: Retry with exponential backoff, dual-brain fallback offer

**NOT in Phase 0** (deferred to later phases):
- No TypeScript, Redux, Electron, or Material-UI
- No onboarding wizard
- No Communications Assistant or Feedback Box
- No export engine (Markdown/DOCX/PDF)
- No landscape configuration UI
- No iterative refinement (conversational feedback on suggestions)
- No meeting transcript special processing (Meeting Notes, GitHub tasks, Tech Fluency)
- No History UI, Daily Planner, Deep Strategy, or Project Initiation tabs
- 3 artifact types only: RAID Log, Status Report, Meeting Notes

**Deliverables**:
- Working React app + FastAPI backend with core Artifact Sync flow
- Privacy Proxy with basic regex + NER (tested on 100-sample labeled dataset)
- 3 artifact types with templates
- Basic Settings panel for API keys and LLM toggle
- All 5 architectural foundations in place (abstract LLM client, project-scoped data, modular privacy, env config, input type detection)

**Success Criteria**:

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Core Flow Works** | End-to-end: paste text → get suggestions → copy to clipboard | Manual testing |
| **Artifact Sync Speed** | < 30 seconds (median) | Time from paste to suggestions displayed |
| **PII Detection** | 95%+ on 100-sample test set | Manual audit |
| **Personal Validation** | "This saves me time vs. doing it manually" | Self-assessment after 1 week of daily use |

**Technical Milestones** (RALPH tasks — ~20 tasks total):
- **Week 1**: Project scaffolding (React + FastAPI), SQLite schema, folder structure, Privacy Proxy regex patterns
- **Week 2**: spaCy NER integration, vault storage, LLM client interface + Claude/Gemini adapters, Artifact Sync backend logic + system prompts
- **Week 3**: FastAPI endpoints, React app shell, text input component, suggestion cards with copy-to-clipboard, basic settings panel
- **Week 4**: End-to-end integration testing, prompt quality tuning (test with real meeting notes), basic styling + error handling, polish

**Go/No-Go Criteria** (end of Week 4):
- ✅ Core flow works end-to-end without errors
- ✅ Privacy Proxy: No PII leaks in 100-sample audit
- ✅ Artifact suggestions are relevant and useful (personal assessment)
- ✅ Copy-to-clipboard works reliably
- ❌ If core flow feels clunky or slow → Polish before adding features
- ❌ If suggestions are consistently poor → Focus on prompt engineering before Phase 1

---

### Phase 1: Core Experience (Full Artifact Sync + Settings + Cross-Tab)

**Timeline**: 6-8 weeks (Months 2-3)

**Goal**: Build out the complete Artifact Sync experience with all planned features, full Settings tab, and cross-tab capabilities. Transition from personal validation to beta user testing.

**Tech Stack Additions**: Add TypeScript (migrate existing JS), consider Material-UI or keep Tailwind

**Features Delivered**:

1. **Artifact Sync Enhancements**
   - Meeting transcript detection + special processing (Meeting Notes, GitHub task suggestions, Tech Fluency Translation)
   - Iterative refinement (conversational feedback: "make the status report more executive-focused")
   - Bubble confidence scoring (show "⚠ Low Confidence" when < 70%)
   - Discrepancy warnings when LLM deviates from user request
   - Color-coded suggestions by urgency (Red/Yellow/Green)
   - Hover-to-expand previews

2. **Full Settings & Landscape Tab**
   - Fixed Landscape table (editable: artifact type, meeting, timing, frequency)
   - Natural language landscape configurator
   - Role toggles (PM, PO, BA, Product Manager, Program Manager)
   - Privacy settings (preview toggle, audit log viewer)
   - Technical Fluency Translation global toggle
   - Data retention settings
   - Manual project backup (ZIP export)
   - Analytics toggle
   - Landscape import/export (JSON)

3. **Cross-Tab Features**
   - Communications Assistant (Slack/email drafting with automatic project context)
   - Persistent Feedback Box (bug/feature/UX feedback → `~/VPMA/feedback/feedback_log.md`)

4. **Export Engine**
   - Markdown, DOCX, PDF, Plain Text export per artifact
   - python-docx for DOCX, reportlab for PDF

5. **Onboarding Wizard**
   - API keys → test connection → first project → configure landscape → sample sync

6. **Artifact Expansion**
   - Expand from 3 to 8 artifact types (+Project Charter, Project Schedule, PRD, User Stories, Communications Plan)
   - 10 artifact templates across 3 project types

**Deliverables**:
- Full Artifact Sync with transcript processing, iterative refinement, confidence scoring
- Complete Settings & Landscape tab
- Communications Assistant + Feedback Box
- Export engine (4 formats)
- Onboarding wizard
- 8 artifact types with templates

**Success Criteria**:

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Beta Users** | 5 users (friendly alpha testers) | Recruitment from PM networks |
| **Artifact Sync Speed** | < 30 seconds (median) | Time from paste to suggestions displayed |
| **PII Detection Accuracy** | 98%+ true positive rate | Audit test with 1000 labeled samples |
| **Update Relevance** | 85%+ user approval rate | User rates each suggestion: "Relevant" vs. "Not Relevant" |
| **User Retention** | 80% return after 1 week | Track: Did user complete 2+ sessions in first week? |
| **Privacy Confidence** | 9+/10 average rating | Survey |

**Technical Milestones**:
- **Weeks 1-2**: TypeScript migration, transcript detection logic, iterative refinement backend
- **Weeks 3-4**: Settings & Landscape tab UI, landscape configuration, NL configurator
- **Weeks 5-6**: Cross-tab features (Communications Assistant, Feedback Box), export engine
- **Weeks 7-8**: Onboarding wizard, artifact expansion (5 new types + templates), beta testing + polish

**Go/No-Go Criteria**:
- ✅ 4+ beta users actively using (2+ sessions/week)
- ✅ Privacy Proxy: 0 PII leaks detected in 1000-sample audit
- ✅ Artifact Sync: < 30s median speed
- ✅ No critical bugs (app crashes, data loss)
- ❌ If < 3 active users → Reassess product-market fit before Phase 2
- ❌ If PII leaks detected → Fix Privacy Proxy before proceeding

---

### Phase 2: Intelligence + Multi-Project + Local LLM

**Timeline**: 8-10 weeks (Months 4-6)

**Goal**: Expand beyond reactive artifact sync to proactive intelligence, multi-artifact consistency, multi-project support, and local LLM for zero-cost/zero-privacy-risk operations.

**Features Delivered**:

1. **Tab 3: Deep Strategy** (Change Integration Management)
   - Artifact upload (DOCX, PDF, markdown, Excel/CSV)
   - Priority sequencing (drag-and-drop to define source-of-truth order)
   - Multi-pass reasoning (4 passes: dependency graph → inconsistency detection → proposed updates → cross-validation)
   - Integration report (tabbed view per artifact with diffs, consistency checks)
   - Accept/reject controls per update
   - Export integration report (PDF summary for stakeholders)
   - Progress bar UI ("Pass 1/4... Pass 2/4...")
   - Target: 100% consistency after updates, 90%+ accuracy

2. **Local LLM via Ollama** (Zero-Cost, Zero-Privacy-Risk Option)
   - **Architecture**: OllamaClient adapter added to existing LLM client interface (same `call()`/`stream()` methods as Claude/Gemini adapters)
   - **Integration**: Ollama REST API at localhost:11434 (OpenAI-compatible format)
   - **Recommended Model**: Llama 3.1 8B (best quality/speed balance for M4 24GB hardware)
   - **Supported Models**: Any Ollama-compatible model (Llama 3.1 8B, Mistral 7B, Mistral Nemo 12B, Phi-3 Mini, Gemma 2 9B)
   - **Settings UI**: Three-way LLM toggle: [Claude Pro] [Gemini] [Local (Ollama)]
   - **Model Selection**: Dropdown to choose installed Ollama model (auto-detect via `ollama list` API)
   - **Use Case Guidance**: "Use Local for routine artifact sync (good quality, free). Use Claude/Gemini for Deep Strategy and complex reasoning (higher quality)."
   - **Performance on M4 24GB**: ~40-60 tokens/sec for 8B models (usable for daily workflows)
   - **Privacy Benefit**: When using local LLM, Privacy Proxy anonymization is optional (data never leaves machine)
   - **Cost Benefit**: $0/month for all local operations (vs. ~$3-15/month API costs for typical usage)

3. **Multi-Project Support**
   - Dropdown in app header for quick project switching
   - Each project has isolated artifacts, landscape config, session history
   - Global PII vault (shared across projects for consistent token mappings)
   - **[Create New Project]** button → Redirects to Project Initiation tab (Phase 3) or quick-start wizard

4. **AI-Powered Risk Prediction** (**TOP PRIORITY**)
   - Analyze current project health (artifact freshness, pending action items, schedule delays)
   - Proactively suggest RAID log risks BEFORE they're mentioned in meetings
   - Example: "Schedule shows Phase 2 milestone slipping by 1 week, but RAID log has no timeline risk. Suggest adding: R_NEW_1: Phase 2 delay risk."
   - LLM reasoning: Compare current state across artifacts → Identify gaps → Suggest risks/issues
   - User can approve/reject suggestions (learn from feedback to improve accuracy)

5. **Full Version History**
   - Move beyond 1-level Undo to full version history
   - `artifact_versions` table stores all past versions
   - UI: [View Version History] per artifact → Timeline view → Restore any version
   - Diff view: Compare any two versions side-by-side

6. **GitHub API Integration**
   - Direct GitHub issue creation from meeting transcript task suggestions (PyGithub)
   - User approves task → VPMA creates GitHub issue with title, description, labels, assignee
   - Search existing issues by title/keywords to suggest updates vs. new tasks

**Deliverables**:
- Deep Strategy tab fully functional
- Local LLM via Ollama (three-way toggle in Settings)
- Multi-project dropdown in header
- AI Risk Prediction integrated into Artifact Sync
- Full version history with rollback
- GitHub API integration (optional, de-scope if timeline slips)

**Success Criteria**:

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Active Users** | 15 users (from 5 in Phase 1) | 3x growth via referrals, PM communities |
| **Deep Strategy Adoption** | 50% of users run Deep Strategy at least once | Track usage in analytics |
| **Local LLM Adoption** | 30% of users try local LLM at least once | Track LLM provider switching |
| **Consistency Accuracy** | 95%+ error-free integrations | Audit: no inconsistencies found after Deep Strategy |
| **AI Risk Prediction Accuracy** | 70%+ approval rate on suggested risks | User approves vs. rejects AI-suggested risks |
| **Multi-Project Usage** | 30% of users manage 2+ projects | Track project count per user |

**Technical Milestones**:
- **Weeks 1-2**: Deep Strategy UI (upload, priority sequencing, diff view)
- **Weeks 3-4**: Multi-pass LLM reasoning (dependency graph, inconsistency detection, update generation, cross-validation)
- **Weeks 5-6**: Local LLM integration (OllamaClient adapter, Settings UI three-way toggle, model selection dropdown)
- **Week 7**: Multi-project support (dropdown, project switching, isolation)
- **Week 8**: AI Risk Prediction (project health analysis, proactive suggestions)
- **Weeks 9-10**: Full version history, GitHub API integration, testing + polish

**Go/No-Go Criteria**:
- ✅ 12+ active users (80% retention from Phase 1)
- ✅ Deep Strategy: 95%+ consistency accuracy in test scenarios
- ✅ Local LLM: Working end-to-end with Llama 3.1 8B via Ollama
- ❌ If Deep Strategy accuracy < 90% → Fix multi-pass logic before Phase 3
- ❌ If user growth stagnates (< 10 users) → Marketing/outreach push before Phase 3

---

### Phase 3: Proactive Features (Daily Planner + Project Initiation + History)

**Timeline**: 8-10 weeks (Months 7-9)

**Goal**: Transform VPMA from reactive tool to proactive daily partner + enable greenfield project kickoff + add session history management.

**Features Delivered**:

1. **Tab 1: Daily Planner** (The Proactive Preparation Engine)
   - Calendar input (paste text, image upload with OCR via pytesseract)
   - Timeframe selection (Today / This Week / Custom Range)
   - Multi-meeting orchestration (prep package for each meeting)
   - Per-meeting outputs:
     - Suggested agenda (pre-populated from recurring meeting agenda artifact)
     - Talking points (context-aware based on current project state)
     - Personal context notes (follow-ups from previous meetings)
     - Artifacts to bring (icons with quick preview modal)
   - Recommended work blocks (proactive artifact maintenance suggestions)
   - Iterative refinement ("add more technical detail to Architecture Review prep")
   - Export options (Copy Full Script, Export to PDF, Export to Markdown)
   - Target: < 60 seconds to generate full daily script

2. **Tab 4: Project Initiation** (The Greenfield Engine)
   - Project description input (text area, supports markdown, optional file upload)
   - Intelligent analysis (project type classification, artifact recommendations)
   - Artifact selection (checklist, all recommended checked by default)
   - Baseline generation (~5 minutes for 6 artifacts with progress indicator)
   - Accordion UI (expandable sections per artifact with inline editing)
   - Iterative refinement (per-artifact or global feedback)
   - Save baseline (creates new project, saves markdown files, initializes landscape)
   - Redirect to Artifact Sync after save (start daily workflow)

3. **Tab 5: History & Context** (The Memory Engine)
   - Context depth slider (0-50 sessions, controls LLM memory)
   - Session log (reverse-chronological, 20 per page)
   - Expanded session view (input, pulse output, persona used, include-in-context override)
   - Search & filter (date range, artifact type, persona used, full-text search)
   - Context preview panel (shows which sessions currently in LLM context, token count, cost estimate)
   - Session export (per-session markdown, bulk export to ZIP)
   - [Clear All Context] emergency reset

4. **Enhanced Image Reading**
   - OCR via pytesseract for screenshots in Artifact Sync (Slack threads, email screenshots)
   - Calendar screenshot upload in Daily Planner
   - Multimodal LLM support where available (Claude/Gemini vision APIs for richer image understanding)

5. **Artifact Expansion + Custom Templates**
   - Add remaining artifact types: Action Item Log, Decision Log, Feature Specifications, Project Dashboard, Meeting Agenda
   - Total: 13+ artifact types (full catalog complete)
   - Custom artifact templates (users define new artifact types with custom structure)
   - Google Calendar API integration (OAuth 2.0, replace manual paste in Daily Planner)

**Deliverables**:
- Daily Planner, Project Initiation, History tabs fully functional
- 13+ artifact types supported (complete catalog + custom)
- Enhanced image reading (OCR + multimodal LLM)
- Google Calendar integration

**Success Criteria**:

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Active Users** | 30 users (from 15 in Phase 2) | 2x growth, broader PM community outreach |
| **Daily Planner Adoption** | 70% of users generate daily script at least once/week | Track usage frequency |
| **Project Initiation Adoption** | 50% of users create at least 1 baseline via Project Initiation | Track new projects created via this tab |
| **Baseline Usefulness** | 80%+ users rate generated baselines as "useful" or "very useful" | Survey |
| **Context Control Usage** | 60% of users adjust context slider from default | Track slider changes in analytics |

**Technical Milestones**:
- **Weeks 1-3**: Daily Planner UI + LLM orchestration (calendar parsing, meeting prep generation)
- **Weeks 4-5**: Project Initiation UI + baseline generation (template filling, artifact creation)
- **Weeks 6-7**: History tab (session log, context slider, search/filter)
- **Week 8**: Artifact expansion (remaining types, custom templates), image reading (OCR + multimodal)
- **Weeks 9-10**: Google Calendar integration, testing + polish

**Go/No-Go Criteria**:
- ✅ 25+ active users (83% retention from Phase 2)
- ✅ Daily Planner: < 60s generation time achieved
- ✅ Project Initiation: 70%+ baseline usefulness rating
- ❌ If user growth stalls (< 20 users) → Reassess marketing, feature priorities
- ❌ If Daily Planner quality poor (< 60% usefulness) → Improve LLM prompts before Phase 4

---

### Phase 4: Commercial Readiness (Security, Auth, Integrations, HR Planning)

**Timeline**: 8-12 weeks (Months 10-13)

**Goal**: Elevate VPMA from personal tool to commercially viable product. Improved security, web deployment with authentication, third-party integrations, and HR capacity planning module.

**Features Delivered**:

1. **Improved Data Security**
   - **Keychain API key storage**: Migrate from `.env` to Python `keyring` library (macOS Keychain, Windows Credential Manager)
   - **Commercial-grade anonymization**: Upgrade from basic spaCy NER to Microsoft Presidio (enterprise PII detection with support for custom recognizers, multiple languages)
   - **Encrypted local database**: SQLite encryption via sqlcipher or similar
   - **Secure session management**: JWT-based sessions for web deployment

2. **Web App with Authentication**
   - **Deployment**: FastAPI backend deployed to cloud (Railway, Render, or AWS), React frontend as static build (Vercel, Netlify, or S3)
   - **Authentication**: Google OAuth via Firebase Auth (free tier, ~50 lines of integration code)
     - Users log in with existing Google account (zero friction)
     - Firebase handles token management, session refresh, account recovery
     - Alternative: Auth0 if multi-provider auth needed (Google, GitHub, email/password)
   - **Data isolation**: Per-user data partitioning (user_id on all tables, API middleware enforces access)
   - **Architecture advantage**: React + FastAPI separation already enables this — no frontend rewrite needed
   - **Environment config**: All settings from environment variables (already in place from Phase 0 foundation)

3. **Third-Party Integrations**
   - **Slack API**: Post status updates and RAID log alerts to Slack channels (OAuth 2.0, bot token)
   - **Gmail API**: Send status reports, meeting notes as formatted emails (Google OAuth, already available from auth)
   - **Google Calendar API**: Auto-import calendar events (already implemented in Phase 3, extend for web users)
   - **Jira API**: Bidirectional sync — VPMA artifacts ↔ Jira issues (read tasks, create/update issues)
   - **GitHub API**: Already implemented in Phase 2, extend with webhook support for real-time updates
   - **Integration architecture**: Each integration is a separate FastAPI router module (clean separation, independently testable)

4. **HR Capacity Planning Module** (New Tab or Section within Project Initiation)
   - **Resource Entry**: Add team members to project (name, role, FTE %, skills, availability dates)
   - **Intelligent Allocation**: LLM analyzes project scope (from Charter, Schedule, PRD) + resource pool → recommends allocation
   - **Bottleneck Detection**: Identify over-allocated resources, skill gaps, timeline conflicts
   - **What-If Scenarios**: "What if we lose 1 developer?" or "What happens if project B starts 2 weeks early?"
   - **Visual Output**: Resource allocation timeline, utilization heat map (text-based or data export for visualization tools)
   - **Integration**: Works with Project Plan artifact (Phase 2), informs RAID Log (capacity risks)

5. **UX Polish + Performance**
   - Dark mode toggle
   - Keyboard shortcuts (customizable in Settings)
   - Performance optimization (30s → 20s median Artifact Sync, caching, prompt optimization)
   - Accessibility audit (WCAG 2.1 AA)
   - Electron wrapper with system tray, native OS notifications, auto-updater

6. **Advanced Analytics Dashboard**
   - Usage trends visualization, most-used tabs, artifact update frequency
   - Export to CSV for external analysis
   - LLM-powered insights

7. **Comprehensive Documentation**
   - In-app help, video tutorials, written guides, FAQ

**Deliverables**:
- Keychain storage + Presidio anonymization + encrypted DB
- Web deployment with Google OAuth login
- Slack, Gmail, Jira integrations (GitHub enhanced)
- HR capacity planning module
- Electron desktop app with system tray + notifications
- Dark mode, keyboard shortcuts, performance improvements
- Full documentation

**Success Criteria**:

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Active Users** | 50 users | Growth via web access + integrations lowering friction |
| **Web App Adoption** | 30% of users switch to or add web access | Track auth method |
| **Integration Usage** | 40% of users connect at least 1 integration | Track OAuth connections |
| **HR Planning Usage** | 20% of users try capacity planning | Track feature usage |
| **Security Audit** | Pass external security review | Third-party audit |
| **UX Rating** | 4.5+/5 CSAT | Survey |
| **Performance** | 20s median Artifact Sync | Measure across user base |

**Technical Milestones**:
- **Weeks 1-2**: Security upgrades (keyring, Presidio, encrypted DB)
- **Weeks 3-4**: Web deployment + Google OAuth (Firebase Auth integration, cloud deployment)
- **Weeks 5-6**: Slack API + Gmail API integrations
- **Weeks 7-8**: Jira API integration + HR capacity planning module
- **Weeks 9-10**: Electron desktop enhancements, UX polish (dark mode, shortcuts, accessibility)
- **Weeks 11-12**: Analytics dashboard, documentation, final testing + launch prep

**Launch Readiness Criteria**:
- ✅ 50+ active users with 90%+ retention
- ✅ All critical bugs resolved
- ✅ Security audit passed (no PII leaks, encrypted storage, secure auth)
- ✅ Performance targets met (20s Artifact Sync)
- ✅ Documentation complete
- ✅ NPS 50+, CSAT 4.5+/5

---

### Future Phases (Post-Launch Enhancements)

**Phase 5: Enterprise Features** (if demand exists)
- **Multi-User Collaboration** (team mode):
  - Shared project state (via cloud sync or git-based collaboration)
  - Role-based permissions (viewer, editor, admin)
  - Real-time updates (when teammate updates artifact)
- **Additional Integrations**:
  - Confluence API (publish artifacts directly to Confluence pages)
  - Microsoft Teams, Monday.com, Asana (integrations as demanded by users)
  - Bidirectional Jira sync (extend Phase 4 integration)

**Phase 6: AI Intelligence Upgrades**
- **Proactive Artifact Maintenance**:
  - "Your Status Report is stale (last updated 10 days ago). Would you like me to generate an update based on recent sessions?"
  - Auto-draft updates without user input, present for review
- **Predictive Timeline Risk**:
  - Analyze schedule velocity → Predict future delays before they happen
  - "Based on current progress, Phase 3 milestone will likely slip by 1 week. Add timeline risk?"
- **Stakeholder Communication Templates**:
  - "You have a 1:1 with VP Product tomorrow. Here's a suggested update based on recent project activity."
  - Context-aware email/Slack drafts tailored to specific stakeholders
- **Meeting Outcome Prediction**:
  - Analyze agenda + current project state → Predict likely meeting outcomes
  - "Steering Committee tomorrow: expect budget approval discussion, prepare cost breakdown"

**Phase 7: Mobile + Advanced UI**
- **Mobile Companion App** (Exploratory, not committed):
  - Read-only mobile interface (view artifacts, session history)
  - Push notifications for critical updates
  - NOT planned for near-term (desktop/web-first strategy)

---

### Roadmap Summary

| Phase | Timeline | Key Features | Success Metric |
|-------|----------|--------------|----------------|
| **Phase 0: Foundation MVP** | Month 1 (4 weeks) | Simplified React/FastAPI, core Artifact Sync, Privacy Proxy, basic Settings, 3 artifact types | Core flow works, < 30s sync, 95% PII accuracy, "saves me time" validated |
| **Phase 1: Core Experience** | Months 2-3 (6-8 weeks) | Full Artifact Sync (transcripts, refinement, confidence), Settings & Landscape, Cross-Tab features, Export, Onboarding, 8 artifacts | 5 beta users, < 30s sync, 98% PII accuracy, 85% relevance |
| **Phase 2: Intelligence** | Months 4-6 (8-10 weeks) | Deep Strategy, Local LLM (Ollama), Multi-Project, AI Risk Prediction, Version History, GitHub API | 15 users, 95% consistency, 30% local LLM adoption |
| **Phase 3: Proactive** | Months 7-9 (8-10 weeks) | Daily Planner, Project Initiation, History & Context, Image Reading, Custom Templates, 13+ artifacts | 30 users, 70% Daily Planner adoption, 80% baseline usefulness |
| **Phase 4: Commercial** | Months 10-13 (8-12 weeks) | Security (keychain, Presidio), Web App + Auth, Slack/Gmail/Jira integrations, HR Capacity Planning, Electron desktop, Dark Mode | 50 users, 4.5+/5 CSAT, security audit passed |
| **Future** | Post-Month 13 | Enterprise collaboration, AI intelligence upgrades, Mobile | Market-driven priorities |

**Total Foundation MVP to Full Launch**: ~52-68 weeks (~12-16 months)
**Foundation MVP**: Month 1 (personal validation)
**Beta Launch**: Month 3 (Phase 1 complete, first external users)
**Feature-Complete Launch**: Month 13+ (Phase 4 complete)

**Development Methodology**: AI-assisted (Claude Code + RALPH). See Section 10.6 for detailed keyboard time, token estimates, and RALPH task decomposition per phase.

---

## 8. Success Criteria & Measurement

This section defines how we'll measure VPMA's success across product development phases and long-term adoption. Metrics are organized into three categories: **Phase-Specific Goals** (tied to development milestones), **Long-Term Success Indicators** (12-month vision), and **Measurement Methods** (how we'll track progress).

---

### 8.1 Phase-Specific Success Metrics

Each development phase has distinct success criteria that must be met before advancing to the next phase.

#### Phase 0: Foundation MVP (Month 1)

**Primary Goal**: Personal validation — does the core text-in → suggestions → copy-to-clipboard flow actually save time?

**Validation Metrics**:
- **Core Flow**: End-to-end paste → suggestions → copy works without errors
- **Speed**: < 30 seconds from paste to suggestions displayed
- **PII Detection**: 95%+ accuracy on 100-sample test set
- **Personal ROI**: Self-assessment: "This saves me meaningful time vs. doing it manually"

**Note**: Phase 0 has no external users. This is personal validation before investing in the full experience.

---

#### Phase 1: Core Experience (Months 2-3)

**Primary Goal**: Validate core value proposition with beta users — can VPMA save PMs meaningful time on artifact maintenance?

**Adoption Metrics**:
- **Target**: 5 beta users actively using VPMA
- **Measurement**: At least 5 sessions per user per week for 2 consecutive weeks
- **Success Threshold**: 4 out of 5 beta users complete 2-week trial (80% retention)

**Performance Benchmarks**:
- **Artifact Sync Speed**: < 30 seconds from paste to bubble display
  - Measurement: Log timestamp deltas (input received → bubbles rendered)
  - Success: 95% of syncs complete in < 30 seconds (p95 latency)
- **Privacy Proxy Accuracy**: 98% PII detection rate
  - Measurement: Manual audit of 100 anonymized payloads (sample diverse input types: transcripts, notes, emails)
  - Success: ≤2 PII leaks per 100 payloads (names, emails, orgs, proprietary terms)
  - Method: Two-person review (creator + independent reviewer) with ground truth labeling

**Quality Metrics**:
- **Update Relevance**: 85% of suggested artifact updates rated "Relevant" or "Highly Relevant" by users
  - Measurement: After each session, user rates each bubble: Highly Relevant / Relevant / Somewhat Relevant / Not Relevant
  - Success: (Highly Relevant + Relevant) / Total ≥ 85%
- **False Positives**: < 15% of bubbles rated "Not Relevant"
  - Indicates LLM correctly identifies which artifacts need updates

**User Satisfaction**:
- **CSAT (Customer Satisfaction)**: 4.0/5.0 average rating
  - Measurement: Weekly survey "How satisfied are you with VPMA this week?" (1-5 scale)
  - Success: 4-week average ≥ 4.0
- **Qualitative Feedback**: Collect detailed feedback via Persistent Feedback Box
  - Target: 3+ feature requests or UX suggestions per user (indicates engagement)

**Technical Stability**:
- **Uptime**: No critical crashes preventing session completion
  - Measurement: Error logs, user bug reports
  - Success: Zero critical bugs blocking MVP workflows
- **LLM API Reliability**: < 5% failed API calls
  - Measurement: Log API call success/failure with retry logic
  - Success: 95% success rate (including retries)

---

#### Phase 2: Intelligence + Multi-Project + Local LLM (Months 4-6)

**Primary Goal**: Expand intelligence with Deep Strategy, add local LLM via Ollama for zero-cost/zero-privacy-risk operations, enable multi-project support

**Adoption Metrics**:
- **Target**: 15 active users (3x Phase 1)
- **Feature Engagement**:
  - **Deep Strategy Adoption**: 20% of users run Deep Strategy at least once
    - Measurement: Session log analysis (tab_used = "Deep Strategy")
    - Indicates users trust VPMA for high-stakes artifact integration
  - **Local LLM Adoption**: 30% of users try Ollama local LLM at least once
    - Measurement: LLM provider switching events in settings logs
    - Validates triple-brain value proposition (Claude + Gemini + Local)

**Performance Benchmarks**:
- **Deep Strategy Multi-Pass**: Progress bar implementation (no strict time target)
  - Measurement: User feedback on progress transparency
  - Success: 80% of users rate progress visibility as "Clear" or "Very Clear"
- **Export Functionality**: 90% of users export artifacts in at least one format (Markdown, DOCX, PDF, Plain Text)
  - Measurement: Export button click events
  - Validates workflow integration (users incorporate VPMA outputs into real artifacts)

**Quality Metrics**:
- **Change Integration Accuracy**: 95% consistency across artifacts after Deep Strategy
  - Measurement: Manual review of 10 Deep Strategy sessions - check for cross-artifact consistency (e.g., Charter scope matches Schedule phases)
  - Success: ≤1 inconsistency per 20 artifact updates
- **Gemini Parity**: Gemini output quality within 10% of Claude on user ratings
  - Measurement: A/B test - same input to both LLMs, blind user rating
  - Success: Gemini CSAT ≥ 90% of Claude CSAT (validates dual-brain strategy)

**User Satisfaction**:
- **NPS (Net Promoter Score)**: 30+ (more promoters than detractors)
  - Measurement: Monthly survey "How likely are you to recommend VPMA?" (0-10 scale)
  - Calculation: % Promoters (9-10) - % Detractors (0-6)
  - Success: Positive NPS indicates product-market fit trajectory

---

#### Phase 3: Proactive Features (Months 7-9)

**Primary Goal**: Complete core workflow coverage (Artifact Sync + Deep Strategy + Daily Planner + Project Initiation + History)

**Adoption Metrics**:
- **Target**: 30 active users (2x Phase 2)
- **Feature Engagement**:
  - **Project Initiation Adoption**: 70% of users create at least one project baseline
    - Measurement: Project Initiation tab sessions
    - Indicates VPMA useful beyond maintenance (also for greenfield projects)
  - **History Slider Usage**: 60% of users adjust context depth slider
    - Measurement: Settings change events (context slider moved from default)
    - Validates user desire for control over LLM memory

**Quality Metrics**:
- **Baseline Usefulness**: 80% of generated baselines rated "Useful" or "Very Useful"
  - Measurement: Post-initiation survey "How useful was the generated baseline?" (1-5 scale)
  - Success: (4+5) / Total ≥ 80%
- **Template Coverage**: 90% of projects match a template type
  - Measurement: Project type classification success rate
  - Indicates template library comprehensiveness

**User Satisfaction**:
- **Session Completion Rate**: 90% of sessions end with "Log" button click
  - Measurement: Sessions started vs. sessions committed
  - Success: ≥90% completion (indicates users find value and complete workflows)

---

#### Phase 4: Commercial Readiness (Months 10-13)

**Primary Goal**: Security hardening, web deployment with auth, third-party integrations, HR capacity planning, UX polish

**Adoption Metrics**:
- **Target**: 50 active users
- **Feature Completeness**: All 6 tabs + 2 cross-tab features fully functional
  - Measurement: Feature usage across all tabs (at least 10% of users use each tab)
  - Success: No "ghost features" (every tab used by ≥10% of users)

**Quality Metrics**:
- **Landscape Customization**: 60% of users customize Fixed Landscape
  - Measurement: Landscape table edits or natural language configurator usage
  - Indicates users personalize VPMA to their workflows
- **Privacy Audit Pass Rate**: 99.5% PII anonymization accuracy
  - Measurement: Audit 200 payloads (broader input diversity than Phase 1)
  - Success: ≤1 PII leak per 200 payloads

**User Satisfaction**:
- **UX Rating**: 4.5/5.0 average on "ease of use"
  - Measurement: Post-session survey "How easy was it to complete your task today?" (1-5 scale)
  - Success: 4-week average ≥ 4.5 (validates UX polish)
- **Feature Utilization**: 50% of users use at least 4 out of 6 tabs
  - Measurement: Session logs (unique tabs per user)
  - Indicates broad workflow coverage (not just one-trick pony)

---

### 8.2 Long-Term Success Indicators (12-Month Vision)

These metrics define what sustained success looks like 12 months after MVP launch.

#### Adoption & Retention

**Active User Base**:
- **Target**: 50+ active users (PMs, POs, BAs, Product Managers)
- **Definition**: Active = 5+ sessions per week for 4 consecutive weeks
- **Measurement**: User activity logs, cohort analysis
- **Why it matters**: Validates product-market fit beyond early adopters

**Daily Active Use**:
- **Target**: 80% of users engage with VPMA at least 5 days per week
- **Measurement**: Session frequency distribution
- **Why it matters**: Indicates VPMA is integral to daily workflows, not occasional tool

**Retention**:
- **Target**: 90% retention after 3 months
- **Definition**: Users who complete 3-month mark are still active (5+ sessions/week) in month 4
- **Measurement**: Cohort retention analysis
- **Why it matters**: High retention proves long-term value, not novelty

---

#### Productivity Impact

**Artifact Maintenance Time Reduction**:
- **Target**: 70% reduction in time spent on artifact maintenance
- **Baseline**: Typical PM spends ~20 hours/week on artifact updates (status reports, RAID logs, meeting notes, planning docs)
- **Target State**: Reduce to ~6 hours/week with VPMA
- **Measurement**:
  - **Before/After Study**: Track 10 users for 1 month - measure artifact maintenance time before VPMA (self-reported + time tracking)
  - **After VPMA**: Measure for 1 month post-adoption
  - **Calculation**: (Time Before - Time After) / Time Before
- **Why it matters**: Core value proposition - free up PM time for strategic work

**Specific Workflow Improvements**:
- **Status Report Generation**: 90% faster (2 hours → 10 minutes)
  - Measurement: Time from "start report" to "report finalized" (before vs. after VPMA)
  - Success: Median time reduction ≥90%
- **Deep Strategy Integration**: 80% faster (4 hours → 45 minutes)
  - Measurement: Time to propagate major change across 5+ artifacts (manual vs. VPMA Deep Strategy)
  - Success: Median time reduction ≥80%
- **Project Initiation Baseline**: 95% faster (8 hours → 20 minutes)
  - Measurement: Time to create Charter, Schedule, RAID Log, PRD from scratch (manual vs. VPMA Project Initiation)
  - Success: Median time reduction ≥95%

---

#### Quality & Accuracy

**Artifact Completeness**:
- **Target**: 95%+ completeness score on generated artifacts
- **Definition**: Completeness = % of required sections present and substantively filled
  - Example: Charter must have Objective, Scope, Deliverables, Success Criteria, Stakeholders, Constraints
  - Score = (Sections Present & Complete) / Total Required Sections
- **Measurement**: Manual audit of 50 artifacts (10 per type: Charter, RAID, Status, PRD, Meeting Notes)
- **Why it matters**: Ensures VPMA outputs are production-ready, not just drafts

**Change Integration Accuracy**:
- **Target**: 90%+ accuracy in Deep Strategy cross-artifact consistency
- **Definition**: After Deep Strategy session, no inconsistencies found across updated artifacts
  - Example: If Charter adds new deliverable, Schedule must reflect new phase, RAID must include new risks
- **Measurement**: Expert review of 20 Deep Strategy outputs - count inconsistencies
  - Success: ≤2 inconsistencies per 20 artifact updates (90% accuracy)
- **Why it matters**: Validates Deep Strategy multi-pass reasoning quality

**PII Anonymization Accuracy**:
- **Target**: 98%+ detection rate with ≤2% false positives
- **Measurement**:
  - **Detection Rate**: Manual audit of 500 diverse inputs (transcripts, notes, emails, Slack threads)
    - Ground truth: Human labelers identify all PII
    - Compare: Privacy Proxy detected PII vs. ground truth
    - Success: Recall ≥98% (miss ≤2% of actual PII)
  - **False Positives**: Precision ≥98% (≤2% of anonymized tokens were not actually PII)
- **Why it matters**: Privacy is core differentiator - must be bulletproof

---

#### User Satisfaction

**Net Promoter Score (NPS)**:
- **Target**: 50+ (strong promoter base)
- **Calculation**: % Promoters (9-10 rating) - % Detractors (0-6 rating) on "How likely are you to recommend VPMA?"
- **Measurement**: Monthly survey to all active users
- **Benchmark**: SaaS industry average NPS is ~30-40, top products >50
- **Why it matters**: Predicts organic growth through word-of-mouth

**Customer Satisfaction (CSAT)**:
- **Target**: 4.5/5.0 average rating
- **Question**: "How satisfied are you with VPMA this week?" (1-5 scale)
- **Measurement**: Weekly micro-survey (1 question, <10 seconds to complete)
- **Tracking**: 12-week rolling average
- **Why it matters**: Weekly pulse on user happiness, early warning for issues

**Feature Request Rate**:
- **Target**: 2+ suggestions per user per month
- **Measurement**: Persistent Feedback Box submissions (category = "Feature Request")
- **Why it matters**: High engagement indicator - users invested enough to suggest improvements

---

### 8.3 Measurement Methods

This subsection details **how** we'll collect, analyze, and act on success metrics.

#### Instrumentation (Built into VPMA)

**Session Logging**:
- **What**: Every VPMA session logged to SQLite database (`sessions` table)
- **Captured Data**:
  - `session_id` (UUID)
  - `timestamp` (start time)
  - `tab_used` (Daily Planner / Artifact Sync / Deep Strategy / Project Initiation / History / Settings)
  - `artifacts_touched` (list of artifact types updated)
  - `tokens_used` (LLM API token count)
  - `llm_model` (claude-3-5-sonnet / gemini-1.5-pro)
  - `duration_seconds` (time from session start to "Log" button)
  - `user_rating` (optional post-session satisfaction rating)
- **Privacy**: No session content logged (only metadata) - respects user privacy
- **Storage**: `~/VPMA/analytics/sessions.db`

**Performance Metrics**:
- **What**: Timestamp critical workflow steps
- **Artifact Sync Timing**:
  - `input_received_at` (user pastes/uploads input)
  - `anonymization_complete_at` (Privacy Proxy finishes)
  - `llm_call_sent_at` (API request sent)
  - `llm_response_received_at` (API response received)
  - `bubbles_rendered_at` (UI displays output)
  - **Calculation**: `bubbles_rendered_at - input_received_at` = total sync time
- **Deep Strategy Timing**:
  - Log each multi-pass step with timestamps
  - Track: artifact parsing → dependency graph → inconsistency detection → update generation → validation
- **Storage**: `~/VPMA/analytics/performance_log.jsonl` (JSON Lines format for easy analysis)

**Error Logging**:
- **What**: Track API failures, privacy detection errors, user corrections
- **Captured Events**:
  - LLM API failures (with error code, retry attempts)
  - Privacy Proxy low-confidence detections (PII flagged for user review)
  - User corrections (when user edits LLM output before committing)
- **Analysis**: Identify failure patterns, prioritize bug fixes
- **Storage**: `~/VPMA/analytics/error_log.jsonl`

**Learning Ledger**:
- **What**: Which personas/skills used per task (transparency + improvement data)
- **Captured Data**:
  - `session_id`
  - `task_type` (risk identification, PRD generation, status report, etc.)
  - `personas_used` (comma-separated: "PM,BA" or "PO,Product Manager")
  - `confidence` (LLM's self-assessed confidence in persona selection)
- **Purpose**: Understand which professional skills are most valuable, inform future persona tuning
- **Storage**: `~/VPMA/analytics/learning_ledger.jsonl`

---

#### User Surveys

**Weekly Pulse Survey** (5-10 seconds to complete):
- **Trigger**: Every Friday after session, pop-up modal (dismissible)
- **Question 1**: "How satisfied are you with VPMA this week?" (1-5 scale)
- **Question 2** (optional): "What's one thing we could improve?"
- **Response Rate Target**: 70% (high completion due to brevity)
- **Analysis**: Track CSAT trends, identify emerging issues from qualitative feedback

**Monthly Deep-Dive Survey** (3-5 minutes):
- **Trigger**: First session of each month, email reminder
- **Questions** (10 total):
  1. **NPS**: "How likely are you to recommend VPMA to a colleague?" (0-10 scale)
  2. **Time Savings**: "Approximately how much time does VPMA save you per week?" (0, 1-2, 3-5, 6-10, 10+ hours)
  3. **Feature Usage**: "Which tabs do you use regularly?" (checkboxes: Daily Planner, Artifact Sync, etc.)
  4. **Artifact Quality**: "How would you rate the quality of VPMA's artifact updates?" (1-5 scale)
  5. **Privacy Confidence**: "How confident are you in VPMA's privacy protections?" (1-5 scale)
  6. **LLM Preference**: "Which LLM do you prefer?" (Claude Pro / Gemini / No Preference / Haven't tried both)
  7. **Top Value**: "What's the most valuable feature for you?" (open text)
  8. **Top Pain Point**: "What's your biggest frustration with VPMA?" (open text)
  9. **Feature Requests**: "What feature would you most like to see added?" (open text)
  10. **Overall Experience**: "How would you rate your overall VPMA experience?" (1-5 scale)
- **Response Rate Target**: 50%
- **Analysis**: Quantitative trend tracking + thematic analysis of open-text responses

---

#### Before/After Time-Tracking Study

**Purpose**: Rigorously measure productivity impact with controlled study

**Study Design**:
- **Participants**: 10 active users (representative mix of PM/PO/BA roles)
- **Duration**: 8 weeks total (4 weeks before VPMA, 4 weeks with VPMA)
- **Measurement Method**: Time tracking + weekly diary

**Phase 1: Baseline (4 weeks without VPMA)**:
- Participants track time spent on artifact-related tasks daily:
  - Status report creation/updates
  - RAID log maintenance
  - Meeting notes writing
  - PRD drafting/updating
  - Project planning
  - Action item tracking
- **Tool**: Toggl or Harvest time tracker with predefined categories
- **Diary**: Weekly reflection - "What took the longest this week? Where did you get stuck?"

**Phase 2: VPMA Adoption (4 weeks with VPMA)**:
- Participants use VPMA for artifact maintenance
- Continue time tracking (same categories)
- Additional tracking:
  - VPMA session duration (how long in tool)
  - Manual editing time (after VPMA generates output)
  - Total time = VPMA session + manual editing
- **Diary**: "Where did VPMA save you time? Where did you still need manual work?"

**Analysis**:
- **Per-User Comparison**: Time Before vs. Time After for each task category
- **Aggregate Reduction**: Average % time savings across 10 participants
- **Qualitative Insights**: Diary analysis - which workflows improved most, remaining pain points

**Success Criteria**: 70% average time reduction with ≥8 out of 10 participants reporting positive ROI

---

#### Privacy Audits

**Purpose**: Ensure PII anonymization accuracy through rigorous testing

**Monthly Manual Review**:
- **Sample Size**: 100 random anonymized payloads (sent to LLM APIs)
- **Sampling Method**: Stratified random sampling across input types:
  - 40 meeting transcripts
  - 30 meeting notes (manual summaries)
  - 20 Slack thread screenshots (OCR output)
  - 10 email updates
- **Review Process**:
  1. **Two-Person Review**: Creator + independent reviewer
  2. **Ground Truth Labeling**: Reviewers identify all PII in original input (before anonymization)
  3. **Comparison**: Check if Privacy Proxy detected all ground truth PII
  4. **Classification**:
     - **True Positive**: PII correctly detected and anonymized
     - **False Negative**: PII missed (PRIVACY BREACH - critical)
     - **False Positive**: Non-PII incorrectly anonymized (acceptable, conservative approach)
     - **True Negative**: Non-PII correctly ignored
  5. **Metrics Calculation**:
     - **Recall** (Detection Rate) = TP / (TP + FN) - Target: ≥98%
     - **Precision** = TP / (TP + FP) - Target: ≥98%
- **Remediation**: Any false negative triggers immediate review of detection patterns, regex/NER model tuning

**Quarterly Comprehensive Audit**:
- **Sample Size**: 500 payloads (5x monthly audit)
- **Broader Diversity**: Include edge cases, international names, rare organizations, technical jargon
- **External Review**: Consider 3rd-party security audit for validation

---

#### Usage Analytics (Local Logging)

**Anonymous Local Analytics** (no external sending):
- **Location**: `~/VPMA/analytics/` (local filesystem, never uploaded)
- **Tracked Metrics**:
  - **Feature Usage Counts**: How often each tab, button, feature is used
  - **Session Durations**: Time spent per tab
  - **Error Rates**: API failures, UI errors, crashes
  - **LLM Call Metadata**: Model used, token counts, response times (no content)
- **Format**: JSON files per month: `usage_2026_02.json`
- **User Control**: Settings toggle to enable/disable analytics (opt-in during onboarding)
- **Privacy**: Zero PII, zero session content - only usage patterns

**Analysis**:
- Aggregate across all users (on developer's machine only, users control their own data)
- Identify:
  - Most/least used features (inform prioritization)
  - Common error patterns (guide bug fixes)
  - Performance bottlenecks (optimize slow workflows)

---

### 8.4 Key Performance Indicators (KPIs) Dashboard

**Purpose**: Single-page view of VPMA health across all metrics

**Dashboard Structure**:

```
┌─────────────────────────────────────────────────────────┐
│  VPMA KPI Dashboard - [Current Month]                  │
├─────────────────────────────────────────────────────────┤
│  ADOPTION                                               │
│  • Active Users: 47 / 50 target  [████████░░] 94%     │
│  • DAU: 38 users (5+ sessions/week)  [████████░░] 81% │
│  • 3-Month Retention: 43/48  [█████████░] 90%         │
├─────────────────────────────────────────────────────────┤
│  PRODUCTIVITY                                           │
│  • Time Savings: 68% avg reduction  [Target: 70%]     │
│    - Status Reports: 2.1h → 12m  (90% faster) ✓       │
│    - Deep Strategy: 3.8h → 48m  (79% faster) ⚠        │
│    - Initiation: 7.5h → 18m  (96% faster) ✓           │
├─────────────────────────────────────────────────────────┤
│  QUALITY                                                │
│  • Artifact Completeness: 96%  [Target: 95%] ✓        │
│  • Change Integration Accuracy: 92%  [Target: 90%] ✓  │
│  • PII Detection: 98.2% recall  [Target: 98%] ✓       │
├─────────────────────────────────────────────────────────┤
│  SATISFACTION                                           │
│  • NPS: +52  [Target: 50+] ✓                          │
│  • CSAT: 4.6/5.0  [Target: 4.5] ✓                     │
│  • Feature Requests: 2.3/user/month  [Target: 2+] ✓   │
├─────────────────────────────────────────────────────────┤
│  TECHNICAL                                              │
│  • Artifact Sync p95 Latency: 28s  [Target: <30s] ✓   │
│  • LLM API Success: 96%  [Target: 95%] ✓              │
│  • Crash Rate: 0.2%  [Target: <1%] ✓                  │
└─────────────────────────────────────────────────────────┘
```

**Update Frequency**: Weekly refresh from analytics logs and survey data

**Alerts**:
- **Red Flag**: Any metric 10%+ below target for 2 consecutive weeks → immediate investigation
- **Yellow Warning**: Metric 5-10% below target → monitor closely

---

### 8.5 Success Criteria Summary

**Foundation MVP (Phase 0)** is successful if:
- ✅ Core flow works end-to-end (paste → suggestions → copy)
- ✅ Artifact Sync < 30s
- ✅ 95% PII detection on 100-sample test
- ✅ Personal validation: "This saves me meaningful time"

**Beta Launch (Phase 1)** is successful if:
- ✅ 5 beta users complete 2-week trial (80% retention)
- ✅ 98% PII detection accuracy (1000-sample audit)
- ✅ 85% update relevance rating
- ✅ 4.0/5.0 CSAT

**Commercial Launch (Phase 4)** is successful if:
- ✅ 50 active users (local + web)
- ✅ Security audit passed
- ✅ All 6 tabs used by ≥10% of users
- ✅ 4.5/5.0 UX rating
- ✅ At least 1 integration connected by 40% of users

**12-Month Vision** is achieved if:
- ✅ 90% retention after 3 months
- ✅ 70% artifact maintenance time reduction
- ✅ 95% artifact completeness
- ✅ NPS 50+
- ✅ CSAT 4.5/5.0

**Bottom Line**: If users save 10+ hours per week, trust VPMA with sensitive data (high privacy confidence), and actively recommend it to colleagues (NPS 50+), we've built a product that fundamentally changes how PMs work.

---

## 9. Risks & Mitigation

This section identifies potential risks across technical, product, operational, and business dimensions, along with concrete mitigation strategies for each.

---

### 9.1 Technical Risks

#### Risk 1: Privacy Proxy False Negatives ⚠️ **CRITICAL**

**Description**: PII detection misses sensitive information, causing leaks to external LLM APIs

**Impact**:
- **Severity**: CRITICAL (privacy breach, loss of user trust)
- **Scope**: Potential compliance violation (GDPR, CCPA), reputational damage
- **User Impact**: Users lose confidence in privacy guarantees, abandon product

**Likelihood**: MEDIUM
- spaCy NER has known limitations (rare names, non-Western names, new organizations may be missed)
- Regex patterns can't catch every edge case (misspelled emails, creative PII obfuscation)
- Complex technical jargon may contain proprietary project codenames that slip through

**Mitigation Strategies**:

1. **Conservative Anonymization Approach**:
   - **Principle**: "When in doubt, anonymize" - favor false positives (over-anonymization) over false negatives (missed PII)
   - **Implementation**: Lower confidence threshold for spaCy NER (≥60% confidence triggers anonymization, not ≥80%)
   - **Trade-off**: Some non-PII may be tokenized, but privacy is protected

2. **User Preview Mode**:
   - **Setting**: "Show anonymization preview when confidence is uncertain" (enabled by default in MVP)
   - **UX**: Before sending to LLM, show user side-by-side comparison:
     - **Left Panel**: Original input with PII highlighted in yellow
     - **Right Panel**: Anonymized version with tokens
   - **User Action**: "Looks good" (proceed) OR "Add to vault" (flag missed PII manually)
   - **Impact**: Users catch false negatives before they reach LLM

3. **Custom Sensitive Terms Dictionary**:
   - **Location**: Settings tab → Privacy Settings → "Add Custom Sensitive Terms"
   - **User Input**: List of project-specific terms (codenames, proprietary acronyms, client names)
   - **Example**: User adds "Project Falcon", "ACME Corp", "ClientCo" → all instances auto-anonymized
   - **Storage**: Stored in anonymization vault, applied globally across all sessions

4. **Monthly Privacy Audits**:
   - **Process**: Manual review of 100 random anonymized payloads
   - **Two-Person Review**: Creator + independent reviewer with PII detection expertise
   - **Action on Failure**: Any false negative triggers:
     - Immediate regex pattern update OR NER model retraining
     - User notification (if their data was affected)
     - Post-mortem to prevent recurrence

5. **Future Enhancement - Local LLM Option**:
   - **Phase 3+ Roadmap**: Add support for local LLMs (Llama, Mistral running via Ollama)
   - **Benefit**: Zero external API calls = zero PII leakage risk
   - **Trade-off**: Lower quality outputs, but 100% privacy for ultra-sensitive projects
   - **User Control**: Toggle "Local-Only Mode" in Settings for highest-sensitivity sessions

**Risk Reduction Timeline**:
- **MVP (Phase 1)**: User preview mode + custom dictionary + 98% detection target
- **Phase 2**: Monthly audits establish baseline, refine patterns based on findings
- **Phase 3**: Local LLM option for zero-risk alternative

---

#### Risk 2: LLM API Reliability

**Description**: Claude/Gemini APIs experience downtime, rate limits, or latency spikes

**Impact**:
- **Severity**: HIGH (blocks core functionality)
- **User Impact**: Cannot sync artifacts, frustration, lost productivity
- **Financial**: Delays in critical PM workflows (e.g., status report due in 1 hour, API down)

**Likelihood**: LOW-MEDIUM
- **Historical Data**: Claude/Gemini have 99%+ uptime, but outages do occur (2-3 incidents/year industry average)
- **Rate Limits**: High-volume users could hit limits (Claude Pro: 5 requests/minute default)

**Mitigation Strategies**:

1. **Retry Logic with Exponential Backoff**:
   - **Implementation**: 3 retry attempts with delays: 1s → 2s → 4s
   - **HTTP Error Codes**:
     - 429 (Rate Limit): Backoff and retry
     - 500/502/503 (Server Error): Retry
     - 401 (Auth Error): Do NOT retry, show user "Check API key" message
   - **User Feedback**: Progress indicator shows "Retrying... (Attempt 2/3)"

2. **Dual-Brain Fallback**:
   - **Automatic Switching**: If Claude fails after 3 retries, offer Gemini:
     - Modal: "Claude API is currently unavailable. Try Gemini instead?"
     - [Use Gemini] [Cancel] buttons
   - **Vice Versa**: If Gemini fails, offer Claude
   - **Impact**: Increases resilience - unlikely both APIs down simultaneously

3. **Offline Mode (Future Enhancement)**:
   - **Phase 2+**: Allow manual artifact updates when API unavailable
   - **UX**: "API unavailable. You can still manually edit artifacts or try again later."
   - **Storage**: Queued updates saved locally, auto-sync when API recovers

4. **API Status Monitoring**:
   - **Health Check**: Before expensive operations (Deep Strategy), ping API with lightweight request
   - **Status Page Integration**: Check status.anthropic.com / status.gemini.google.com via API
   - **User Notification**: "Claude API reporting degraded performance. Proceed or try later?"

5. **Token Quotas & Alerts**:
   - **User Settings**: "Max tokens per session" or "Max cost per day" (e.g., $5/day limit)
   - **Real-time Tracking**: Show running token count in header: "1,245 tokens used this session (~$0.02)"
   - **Alert at Threshold**: "Approaching daily limit ($4.50/$5.00). Continue?"

**Risk Reduction**:
- **MVP**: Retry logic + dual-brain fallback = 99.9% effective uptime (both APIs down <0.1% of time)
- **Phase 2**: Offline mode, status monitoring

---

#### Risk 3: Document Parsing Failures

**Description**: Complex DOCX/PDF formatting breaks parser, garbled text extracted

**Impact**:
- **Severity**: MEDIUM (Deep Strategy produces nonsense)
- **User Impact**: User wastes time on unusable Deep Strategy outputs, must redo manually
- **Frequency**: Likely to occur with enterprise documents (complex tables, embedded images, custom fonts)

**Likelihood**: MEDIUM
- **python-docx** and **PyPDF2** handle standard formats well, but struggle with:
  - Scanned PDFs (no text layer)
  - Complex nested tables
  - Embedded objects (charts, images with text)
  - Password-protected files

**Mitigation Strategies**:

1. **Plain Text Fallback**:
   - **Error Handling**: If parsing fails, display clear message:
     - "Unable to parse [filename.docx]. This file may have complex formatting."
     - "Please try: (1) Copy/paste plain text, OR (2) Export as simpler format (Markdown, plain PDF)"
   - **User Action**: Copy content manually, paste into text area → bypasses parsing

2. **Format Pre-Check**:
   - **Before Upload**: Detect problematic elements:
     - Check if PDF is scanned (no text layer) → Warn: "This appears to be a scanned PDF. Extract text first or use OCR."
     - Check for password protection → Error: "File is password-protected. Decrypt first."
   - **Supported Formats**: Clearly list in UI:
     - ✅ DOCX (Word), PDF (text-based), Markdown, Plain Text
     - ⚠️ Complex tables may not parse perfectly
     - ❌ Scanned PDFs, password-protected files, Excel with macros

3. **OCR for Scanned PDFs** (Phase 2+):
   - **Tool**: pytesseract (local OCR, privacy-preserving)
   - **Auto-Detect**: Check if PDF has text layer → if not, run OCR automatically
   - **User Control**: Settings toggle "Auto-OCR scanned documents" (off by default due to slower performance)

4. **Testing Suite**:
   - **Build Test Library**: 50+ diverse document types
     - Simple DOCX (plain text)
     - Complex DOCX (nested tables, embedded images)
     - PDFs (text-based, scanned, mixed)
     - Edge cases: international characters, right-to-left text, math notation
   - **CI/CD Integration**: Run parsing tests on every code change → catch regressions

5. **Graceful Degradation**:
   - **Partial Parsing**: Extract what's parsable, flag unparseable sections
   - **Example Output**: "Successfully parsed 80% of document. Sections with complex formatting skipped: [Page 5 Table], [Page 12 Chart]"
   - **User Review**: User manually adds skipped content or accepts partial parse

**Risk Reduction**:
- **MVP**: Plain text fallback, format pre-check, clear error messages
- **Phase 2**: OCR support, comprehensive testing suite
- **Target**: 90% successful parsing of real-world PM documents

---

#### Risk 4: LLM Hallucinations / Inaccurate Updates

**Description**: LLM generates artifact updates that misinterpret user input or add fictional details

**Impact**:
- **Severity**: HIGH (user commits bad data to artifacts)
- **Downstream Impact**: Wrong decisions made based on hallucinated info (e.g., fake risk added to RAID log)
- **User Trust**: Erodes confidence in AI-generated outputs

**Likelihood**: MEDIUM
- Inherent to LLMs, especially with:
  - Ambiguous inputs (vague meeting notes)
  - Complex multi-step reasoning (Deep Strategy)
  - Low-context scenarios (no history loaded)

**Mitigation Strategies**:

1. **Confidence Scoring on Every Bubble**:
   - **Display**: Only show confidence when LOW (<70%)
     - Example: "⚠ Low Confidence - Please review carefully"
   - **High Confidence**: No indicator (reduces UI clutter when LLM is confident)
   - **User Behavior**: Low confidence triggers heightened scrutiny

2. **User Review Before Commit** (NEVER auto-save):
   - **Workflow**: Bubble click → Preview modal → User reviews → [Confirm] OR [Edit] OR [Reject]
   - **No Auto-Commit**: User must explicitly confirm every update
   - **Edit Option**: User can modify text inline before committing
   - **Reject**: Discards bubble, excludes from session log

3. **Discrepancy Disclaimer**:
   - **Detection**: Compare LLM output keywords to user input keywords
     - If overlap <50%, flag as potential deviation
   - **Warning Footer**: "⚠ Note: This update may deviate from your original request. Review carefully."
   - **Example**: User says "update risk timeline", LLM adds new risk instead of updating existing → discrepancy detected

4. **Iterative Refinement**:
   - **User Feedback Loop**: "Make the status report more executive-focused" → LLM regenerates
   - **Multiple Iterations**: User can refine until output matches intent
   - **Conversational Correction**: "This isn't quite right - I meant..." → LLM adjusts

5. **Version History (Phase 2+)**:
   - **Rollback Capability**: Every artifact update creates new version
   - **UI**: "Undo" button per artifact → revert to previous version (one-level rollback in MVP, full history in Phase 2)
   - **Safety Net**: User can always recover from hallucinated commit

6. **Grounding in Artifact State**:
   - **Context Loading**: Always load current artifact state before generating updates
   - **Diff-Based Prompts**: "Here's the current RAID Log. Based on this input, what should change?"
   - **Reduces Hallucination**: LLM modifies existing content rather than generating from scratch

**Risk Reduction**:
- **MVP**: Confidence scoring, mandatory user review, discrepancy warnings, iterative refinement
- **Phase 2**: Full version history for easy rollback
- **Philosophy**: "Trust but verify" - AI suggests, human decides

---

#### Risk 5: Cost Escalation

**Description**: Heavy users rack up high LLM API costs, especially with Deep Strategy multi-pass

**Impact**:
- **Severity**: MEDIUM (unexpected expenses)
- **User Impact**: May need to implement usage limits or pricing (free tool → paid)
- **Example**: Power user runs 20 Deep Strategy sessions/day @ $0.35 each = $7/day = $210/month

**Likelihood**: MEDIUM
- Free tier limits easily exceeded by active PM (Claude Pro: ~$20/month API costs for heavy user)
- Deep Strategy is expensive (4-pass reasoning, large context windows)

**Mitigation Strategies**:

1. **Cost Preview Before Expensive Operations**:
   - **Deep Strategy**: Before starting, show estimate:
     - "Estimated cost: $0.35 (based on 5 artifacts, 4 multi-pass steps)"
     - [Proceed] [Cancel] buttons
   - **Calculation**: Token count estimate × API pricing (Claude: $3/$15 per 1M tokens input/output)

2. **User-Configurable Spending Limits**:
   - **Settings**: "Max daily spending: $5" (warning only, not hard cap)
   - **Alert at 80%**: "You've used $4.00 of your $5.00 daily limit. Continue?"
   - **No Hard Cap**: User can override (trust user to manage own costs)

3. **Token Optimization**:
   - **Cache System Prompts**: Reuse static prompts across sessions (Claude supports prompt caching)
   - **Minimize Redundant Context**: Only load relevant history (not full 50 sessions if unnecessary)
   - **Efficient Prompts**: Shorter prompts where possible without sacrificing quality

4. **Gemini as Low-Cost Alternative**:
   - **Pricing**: Gemini generally cheaper than Claude (~50% lower per token in some tiers)
   - **User Guidance**: "For budget-conscious workflows, try Gemini (similar quality, lower cost)"
   - **Dual-Brain Value**: Users can choose Claude for critical work, Gemini for routine syncs

5. **Batching & Efficiency**:
   - **Artifact Sync**: Single LLM call generates all bubbles (not one call per artifact)
   - **Daily Planner**: Batch all meetings in one prompt (not per-meeting calls)
   - **Impact**: 5x fewer API calls for multi-artifact workflows

**Risk Reduction**:
- **MVP**: Cost preview, user warnings, Gemini option
- **Phase 2**: Prompt caching, usage analytics to identify optimization opportunities
- **Pricing Model** (Future): If costs become prohibitive, consider:
  - Freemium (limited sessions/month) + paid tier
  - Bring-your-own-API-key model (user pays OpenAI/Anthropic directly)

---

### 9.2 Product Risks

#### Risk 6: User Adoption Failure

**Description**: PMs don't trust AI-generated artifact updates, prefer manual control

**Impact**:
- **Severity**: CRITICAL (product-market fit failure)
- **User Behavior**: Low engagement, high churn, negative reviews
- **Root Cause**: AI skepticism, fear of errors, perceived loss of control

**Likelihood**: MEDIUM
- **Industry Context**: Many professionals skeptical of AI for critical work
- **PM Role**: High stakes (bad status report → stakeholder trust loss)

**Mitigation Strategies**:

1. **Transparency in All Outputs**:
   - **Show Confidence Scores**: Users know when to double-check (low confidence = higher scrutiny)
   - **Learning Ledger**: Users see which personas/skills were used (builds trust through transparency)
   - **Privacy Audit Log**: Users can review all anonymized payloads (verify privacy guarantees)

2. **Gradual Trust-Building**:
   - **Onboarding Journey**: Start with low-stakes tasks
     - Week 1: Artifact Sync for meeting notes (low risk)
     - Week 2: Status report updates (medium risk)
     - Week 3: Deep Strategy for Charter changes (high risk)
   - **Success Reinforcement**: Celebrate wins "You saved 2 hours this week with VPMA!"

3. **Manual Override Always Available**:
   - **User Control**: Every output is editable, rejectable
   - **Hybrid Workflow**: User can use VPMA for draft, refine manually
   - **No Black Box**: Clear what VPMA did vs. what user changed

4. **Early Adopter Testimonials**:
   - **Social Proof**: Video testimonials from beta users
     - "VPMA saved me 10 hours last week. I was skeptical at first, but now I can't imagine going back."
   - **Case Studies**: Detailed before/after stories
   - **Peer Credibility**: Other PMs vouching for quality

5. **Privacy Guarantees Front & Center**:
   - **Landing Page**: "100% Local Processing. Your data never leaves your laptop (except anonymized API calls)"
   - **Visible Anonymization**: User sees tokenization in action (builds confidence)
   - **Compliance**: Future GDPR/SOC2 compliance for enterprise adoption

**Risk Reduction**:
- **MVP**: Transparency, user control, privacy emphasis
- **Growth Phase**: Testimonials, case studies, word-of-mouth
- **Target**: 90% trial → active user conversion

---

#### Risk 7: Complexity Overwhelms Users

**Description**: Six tabs, dozens of settings, too many features → users confused

**Impact**:
- **Severity**: MEDIUM (usability barrier)
- **User Behavior**: Churn due to perceived difficulty, low feature utilization
- **Feedback**: "Too complicated, I just want to update my RAID log"

**Likelihood**: MEDIUM
- **Common Pattern**: Feature creep leads to bloated UX
- **Target Users**: PMs are busy, want tools that "just work"

**Mitigation Strategies**:

1. **Progressive Disclosure**:
   - **Onboarding Wizard**: Only show Tab 2 (Artifact Sync) initially
   - **Unlock Triggers**: After 5 successful syncs, show "Unlock Deep Strategy" tooltip
   - **Phased Rollout**: Week 1 = Tab 2 only, Week 2 = Tabs 1-2, Week 3 = Full access
   - **User Control**: "Show all features now" button for power users

2. **Smart Defaults Work Out-of-Box**:
   - **Zero Config Required**: Pre-populated Landscape, all personas enabled, Claude Pro selected
   - **First Session**: User can paste transcript immediately, no setup needed
   - **API Keys**: Only required config (unavoidable)

3. **Google-Minimalist Philosophy**:
   - **Hide Advanced Features**: Collapse settings by default
   - **Tab 2 (Artifact Sync) as Default Landing**: Most common use case front & center
   - **Contextual Help**: Tooltips, inline hints ("Paste your meeting transcript here")

4. **Onboarding Video Tutorials**:
   - **3-Minute Walkthrough**: "Your first VPMA session in 3 minutes"
   - **Per-Tab Guides**: Dedicated videos for Deep Strategy, Project Initiation (for advanced users)
   - **Accessibility**: Embedded in app (? icon in header)

5. **User Testing with Non-Technical PMs**:
   - **Usability Testing**: Observe 5 new users completing first session
   - **Friction Points**: Where do they get stuck? What's confusing?
   - **Iterate**: Simplify based on feedback

**Risk Reduction**:
- **MVP**: Smart defaults, contextual help, default landing on Tab 2
- **Phase 2**: Progressive disclosure, video tutorials
- **Target**: 90% task completion rate on first session

---

#### Risk 8: Artifact Quality Varies by Type

**Description**: Some artifacts (Charter, PRD) generate beautifully, others (RAID Log, Tasks) are mediocre

**Impact**:
- **Severity**: MEDIUM (uneven user experience)
- **User Behavior**: Use VPMA only for subset of artifacts, not full workflow
- **Example**: "VPMA writes great status reports, but RAID logs need heavy manual editing"

**Likelihood**: HIGH
- **LLM Strengths**: Prose, summaries, explanations (Charter, PRD, Meeting Notes)
- **LLM Weaknesses**: Structured data (RAID tables, task lists with precise fields)

**Mitigation Strategies**:

1. **Per-Artifact Prompt Tuning**:
   - **Dedicated Prompts**: Optimize each artifact type separately
   - **Few-Shot Examples**: Include 2-3 exemplar outputs in system prompt
     - RAID Log: "Here's an excellent RAID Log structure: [example]. Match this format."
   - **Iteration**: Refine prompts based on user feedback ("RAID logs are too verbose" → tune for conciseness)

2. **Template Refinement**:
   - **User Feedback Loop**: Rate each artifact update (Highly Relevant / Relevant / Needs Work / Poor)
   - **Analytics**: Identify low-rated artifact types (e.g., Tasks consistently rated "Needs Work")
   - **Improvement Cycle**: Update templates, retrain prompts, A/B test

3. **Structured Output Modes**:
   - **JSON Schema**: For tabular artifacts (RAID, Tasks), use LLM JSON mode
     - Prompt: "Return RAID log as JSON: {risks: [{id, description, probability, impact, mitigation}]}"
     - Post-Process: Convert JSON → Markdown table (guaranteed structure)
   - **Validation**: Check required fields present before displaying to user

4. **Manual Edit Encouraged**:
   - **UX Messaging**: "VPMA provides a draft. Review and refine to fit your style."
   - **Not Positioning**: VPMA as "perfect output generator"
   - **Realistic Expectation**: 80% done, user polishes remaining 20%

5. **Artifact-Specific User Guides**:
   - **Help Documentation**: "Tips for great RAID Logs with VPMA"
     - "Provide specific context: 'Vendor X may delay delivery' vs. 'Potential delay'"
     - "VPMA works best with clear, detailed input"

**Risk Reduction**:
- **MVP**: Per-artifact prompt tuning, user feedback ratings
- **Phase 2**: JSON structured output, template refinement based on data
- **Target**: 85%+ relevance rating across ALL artifact types (not just top performers)

---

### 9.3 Operational Risks

#### Risk 9: Support Burden

**Description**: Users need help with setup, troubleshooting, configuration

**Impact**:
- **Severity**: MEDIUM (time sink for developers)
- **Opportunity Cost**: Time spent on support ≠ time building new features
- **Common Issues**: API key setup, Privacy Proxy config, landscape customization

**Likelihood**: HIGH
- Local setup always has friction (environment variables, credentials, dependencies)
- Non-technical PMs may struggle with `.env` files, API key creation

**Mitigation Strategies**:

1. **Comprehensive Setup Documentation**:
   - **Step-by-Step Guide**: "VPMA Setup in 10 Minutes"
     - Screenshots for every step (Google Cloud Console, Anthropic API dashboard)
     - Copy-paste commands for terminal operations
     - Troubleshooting section: "API key not working? Check these 3 things..."
   - **Video Walkthrough**: Screenshare of full setup process

2. **Self-Serve Diagnostics**:
   - **Settings Tab - System Health**:
     - ✅ Claude API: Connected (last tested: 2 min ago)
     - ❌ Gemini API: Not configured ([Setup Guide])
     - ✅ Privacy Proxy: Enabled, 245 terms in vault
     - ✅ Database: Healthy (3 projects, 47 sessions)
   - **"Test Connection" Buttons**: User clicks → VPMA pings API → shows success/error

3. **Automated Setup Wizard** (Phase 2+):
   - **Onboarding Flow**:
     - Step 1: "Let's set up your Claude API key"
       - Link to Anthropic dashboard
       - Paste field for API key
       - "Test Connection" button → immediate feedback
     - Step 2: "Configure your first project"
       - Project name, select artifact types
     - Step 3: "Sample Artifact Sync"
       - Pre-filled example input → user sees VPMA in action
   - **Reduces Setup Friction**: Guided, validated, instant feedback

4. **Community Forum / Discord**:
   - **Peer Support**: Users help each other
   - **FAQs**: Common issues documented by community
   - **Developer Engagement**: Monitor forum, answer tough questions
   - **Reduces 1:1 Support**: Most questions answered by peers

5. **Error Messages with Actionable Guidance**:
   - **Bad Error**: "API call failed"
   - **Good Error**: "Claude API call failed (401 Unauthorized). Your API key may be invalid or expired. [Check API Key Settings] [View Setup Guide]"
   - **Links to Solutions**: Every error has next-step action

**Risk Reduction**:
- **MVP**: Comprehensive docs, self-serve diagnostics, clear error messages
- **Phase 2**: Automated setup wizard, community forum
- **Target**: <1 hour developer time per week on support (vs. 5-10 hours without mitigation)

---

#### Risk 10: Data Loss / Corruption

**Description**: SQLite database corruption, user loses artifact history

**Impact**:
- **Severity**: CRITICAL (catastrophic for user)
- **User Impact**: Loss of work, broken trust, potential project setbacks
- **Likelihood**: LOW (SQLite is robust), but impact is severe

**Likelihood**: LOW
- SQLite is production-grade, used in billions of devices
- Corruption rare, usually from:
  - Hard crash during write operation
  - Disk failure
  - File system issues

**Mitigation Strategies**:

1. **SQLite Write-Ahead Logging (WAL) Mode**:
   - **Crash Resilience**: WAL mode ensures atomicity - writes either fully complete or fully rolled back
   - **Implementation**: `PRAGMA journal_mode=WAL;` on database open
   - **Benefit**: Reduces corruption risk from crashes

2. **Manual Backup Functionality**:
   - **Settings Tab**: [Export Full Project] button
   - **Output**: Timestamped ZIP file: `~/VPMA/backups/project_name_2026-02-12.zip`
   - **Contents**: SQLite DB + Markdown artifacts + Settings JSON
   - **User Responsibility**: User initiates backups (no automatic daily backups in MVP)
   - **Guidance**: Onboarding message "Tip: Export your project weekly to avoid data loss"

3. **Artifact Version Control**:
   - **Every Update Creates New Version**: Never overwrite (artifact_versions table)
   - **Rollback**: User can always revert to previous version (one-level undo in MVP, full history in Phase 2)
   - **Safety Net**: Even if DB corrupted, Markdown files in `~/VPMA/artifacts/*.md` survive

4. **Dual Storage Model**:
   - **SQLite**: Metadata only (timestamps, references)
   - **Markdown Files**: Artifact content lives in human-readable files
   - **Resilience**: If DB corrupted, Markdown files intact → user can recover most data

5. **Database Integrity Checks**:
   - **On Startup**: `PRAGMA integrity_check;` → detect corruption early
   - **Error Handling**: If corruption detected:
     - Alert user: "Database corruption detected. Attempting recovery..."
     - Run SQLite recovery tools (`sqlite3 .recover`)
     - Restore from latest backup (if available)

6. **Recovery Tool (Phase 2+)**:
   - **CLI Utility**: `vpma-recover` command
   - **Functionality**: Rebuild database from Markdown artifacts + analytics logs
   - **Use Case**: Worst-case recovery when DB completely lost

**Risk Reduction**:
- **MVP**: WAL mode, manual export, version control, dual storage (SQLite + Markdown)
- **Phase 2**: Automated integrity checks, recovery tool
- **Target**: Zero data loss incidents (<0.1% user impact if corruption occurs)

---

### 9.4 Business Risks

#### Risk 11: Competitive Response

**Description**: Jira, Asana, or AI leaders (OpenAI, Google) build similar PM assistant features

**Impact**:
- **Severity**: HIGH (market competition intensifies)
- **Threat Scenarios**:
  - Jira adds "AI Project Assistant" powered by Gemini
  - Microsoft Copilot expands to PM workflows
  - New startup with better UX/features
- **User Impact**: Users may switch to competitor if features are comparable and integrated into existing tools

**Likelihood**: HIGH
- AI + PM tools is an obvious product opportunity
- Large players have resources to move quickly

**Mitigation Strategies**:

1. **Differentiate on Privacy (Unique Moat)**:
   - **VPMA's Edge**: 100% local-first, PII anonymization
   - **Competitors**: Cloud-dependent (Jira Cloud, Microsoft 365 require uploading sensitive data)
   - **Target Persona**: Privacy-conscious PMs, regulated industries (finance, healthcare, government)
   - **Messaging**: "VPMA: The only PM assistant that keeps your data on YOUR laptop"

2. **Speed to Market (First-Mover Advantage)**:
   - **MVP in 2 Months**: Launch before big players notice opportunity
   - **Iterate Quickly**: Monthly feature releases based on user feedback
   - **Community Building**: Loyal early adopters become evangelists

3. **Niche Focus (Solo PMs, Not Enterprises)**:
   - **Different Target**: VPMA serves solo PMs, small teams (1-5 PMs)
   - **Jira/Asana Focus**: Enterprise teams, complex org structures
   - **VPMA Advantage**: Simple, personal, frictionless (vs. enterprise bloat)
   - **Market Size**: Millions of solo PMs underserved by enterprise tools

4. **Open Source Potential (Future)**:
   - **Phase 3+**: Consider open-sourcing VPMA
   - **Benefit**: Community contributions, rapid innovation, trust through transparency
   - **Monetization**: Hosted version, premium features, support contracts

5. **Integration as Defense**:
   - **Phase 2+**: Integrate with tools competitors can't (GitHub, Google Workspace, Jira API)
   - **Ecosystem Play**: VPMA becomes hub connecting fragmented PM tool stack
   - **Switching Cost**: User invested in VPMA workflows, integrations → harder to leave

**Risk Reduction**:
- **MVP**: Privacy differentiation, speed to market
- **Growth**: Niche focus, community building
- **Long-term**: Open source consideration, deep integrations
- **Philosophy**: Can't out-resource big players, but can out-focus and out-iterate them

---

#### Risk 12: LLM Dependency

**Description**: Claude/Gemini API pricing changes, access restricted, or quality degrades

**Impact**:
- **Severity**: HIGH (economics or quality compromised)
- **Scenarios**:
  - API price doubles → VPMA cost unsustainable
  - API access restricted (geo-blocking, enterprise-only)
  - Model quality degrades (new version performs worse)

**Likelihood**: LOW-MEDIUM
- **Pricing Stability**: APIs generally stable, but future uncertain (competitive pressure, cost changes)
- **Access Risk**: Low for major APIs (high availability priority), but policy changes possible

**Mitigation Strategies**:

1. **Dual-Brain Architecture (Already Built-In)**:
   - **Not Locked to One Provider**: Toggle between Claude, Gemini
   - **Pricing Leverage**: If Claude raises prices, switch users to Gemini
   - **Quality Hedge**: If one model degrades, fallback to other

2. **LLM-Agnostic Prompt Design**:
   - **Portable Prompts**: Design prompts to work across multiple LLMs (Claude, Gemini, GPT-4, Llama)
   - **Minimal Provider-Specific Features**: Avoid Claude-only or Gemini-only API features
   - **Easy Migration**: Adding new LLM = change API client, prompts remain same

3. **Local LLM Support (Phase 3+)**:
   - **Complete Independence**: Add Llama 3, Mistral via Ollama (runs locally)
   - **Trade-off**: Lower quality, but zero cost, 100% local
   - **User Choice**: "Use Claude (best quality), Gemini (balanced), or Local (free, private)"

4. **Monitor API Pricing Trends**:
   - **Quarterly Review**: Track Claude, Gemini, GPT-4 pricing
   - **Alerts**: If pricing changes >20%, evaluate alternatives
   - **User Communication**: Transparent about costs, pricing strategy

5. **Fallback to Simpler Workflows**:
   - **Graceful Degradation**: If LLM access lost, VPMA still useful for:
     - Artifact export (Markdown → DOCX)
     - Privacy Proxy (anonymization without LLM)
     - Manual artifact editing
   - **Not Dead in Water**: Core value (artifact management) doesn't disappear

**Risk Reduction**:
- **MVP**: Dual-brain (2 providers), LLM-agnostic design
- **Phase 3**: Local LLM option (complete independence)
- **Philosophy**: Reduce vendor lock-in at every opportunity

---

### 9.5 Risk Prioritization Matrix

| Risk | Severity | Likelihood | Priority | Mitigation Status (MVP) |
|------|----------|------------|----------|------------------------|
| **Privacy Proxy False Negatives** | CRITICAL | Medium | 🔴 P0 | User preview, conservative anonymization, custom dictionary |
| **LLM API Reliability** | High | Low-Med | 🟡 P1 | Retry logic, dual-brain fallback |
| **User Adoption Failure** | CRITICAL | Medium | 🔴 P0 | Transparency, user control, gradual trust-building |
| **Data Loss / Corruption** | CRITICAL | Low | 🟡 P1 | WAL mode, manual backup, version control, dual storage |
| **Competitive Response** | High | High | 🟡 P1 | Privacy differentiation, speed to market, niche focus |
| **LLM Dependency** | High | Low-Med | 🟡 P1 | Dual-brain, LLM-agnostic prompts |
| **Document Parsing Failures** | Medium | Medium | 🟢 P2 | Plain text fallback, format pre-check |
| **LLM Hallucinations** | High | Medium | 🟡 P1 | Confidence scores, user review, discrepancy warnings |
| **Cost Escalation** | Medium | Medium | 🟢 P2 | Cost preview, user limits, Gemini option |
| **Complexity Overwhelms Users** | Medium | Medium | 🟢 P2 | Smart defaults, contextual help, default landing Tab 2 |
| **Artifact Quality Variance** | Medium | High | 🟢 P2 | Per-artifact prompt tuning, user feedback loop |
| **Support Burden** | Medium | High | 🟢 P2 | Comprehensive docs, self-serve diagnostics |

**Priority Definitions**:
- **🔴 P0**: Must address before MVP launch (blocking risks)
- **🟡 P1**: Address in MVP, critical for production readiness
- **🟢 P2**: Monitor, mitigate in Phase 2+ based on data

---

### 9.6 Risk Review Cadence

**Weekly Risk Review** (during active development):
- Review P0 risks: Any new incidents? Mitigation effectiveness?
- Update risk likelihood based on beta user feedback

**Monthly Risk Assessment** (post-launch):
- Privacy audit results → adjust Privacy Proxy patterns if needed
- User adoption metrics → if declining, investigate (Risk 6)
- Competitive landscape scan → new threats emerged?

**Quarterly Strategic Review**:
- Re-prioritize risks based on 3-month data
- Identify new risks (e.g., new competitor, API policy change)
- Update mitigation strategies based on lessons learned

---

## 10. Appendices

This section provides supporting reference materials: glossary of key terms, sample artifact templates, architecture diagram concepts, and detailed user journey walkthroughs.

---

### 10.1 Glossary

**VPMA (Virtual Project Management Assistant)**
- **Definition**: Local, privacy-centric React/Electron application with FastAPI backend serving as an elite-level cross-functional partner for PMs, POs, BAs, and Product Managers
- **Core Function**: Artifact management, intelligent orchestration, professional persona switching
- **Architecture**: Local-first with Privacy Proxy, dual-brain LLM toggle (Claude/Gemini), REST API communication

**Privacy Proxy**
- **Definition**: Local anonymization layer using regex + spaCy NER to tokenize PII before external LLM API calls
- **Purpose**: Ensure sensitive data (names, emails, orgs, proprietary terms) never reaches cloud services
- **Implementation**: Outbound anonymization (`John Smith` → `<PERSON_1>`), inbound re-identification (`<PERSON_1>` → `John Smith`)
- **Storage**: Local vault (SQLite table or Python dict) mapping tokens to original values

**Artifact Sync**
- **Definition**: Tab 2 workflow for daily artifact maintenance from raw inputs (transcripts, notes, screenshots, emails)
- **Primary Use Case**: Reactive update engine - paste meeting transcript → get suggested updates for RAID Log, Status Report, Meeting Notes, etc.
- **Output**: Interactive bubbles with copy-to-clipboard and apply-to-database options

**Deep Strategy**
- **Definition**: Tab 3 workflow for high-rigor change propagation across interconnected artifacts
- **Primary Use Case**: When major change (e.g., Charter scope expansion) needs to ripple through Schedule, RAID Log, Status Report, PRD
- **Implementation**: Multi-pass reasoning (4 LLM calls) to build dependency graph, identify inconsistencies, generate updates, validate consistency

**Daily Planner**
- **Definition**: Tab 1 workflow for proactive daily/multi-day planning
- **Primary Use Case**: Paste calendar → get personalized daily script with meeting prep, talking points, project health suggestions
- **Outputs**: Per-meeting agendas, talking points, artifacts to bring, recommended work blocks

**Project Initiation**
- **Definition**: Tab 4 workflow for greenfield project baseline generation
- **Primary Use Case**: Describe new project → get Charter, Schedule, RAID Log, PRD, Communications Plan drafts
- **Intelligence**: LLM classifies project type, selects appropriate templates, fills with project-specific content

**Fixed Landscape**
- **Definition**: User-configured mapping of artifacts, meetings, and timing for personalized intelligence
- **Example**: "Status Report" artifact associated with "Weekly Steering Committee" meeting, updated "Every Monday 9am"
- **Purpose**: VPMA knows user's standard rhythm, prioritizes updates based on timing
- **Configuration**: Settings tab → editable table + natural language configurator

**Multi-Pass Reasoning**
- **Definition**: Sequential LLM calls to handle complex tasks requiring multiple steps
- **Example**: Deep Strategy uses 4 passes:
  1. Build dependency graph from artifacts
  2. Identify inconsistencies based on priority order
  3. Generate proposed updates for each artifact
  4. Cross-validate for consistency
- **Purpose**: Break down complex reasoning into manageable steps, improve accuracy

**Learning Ledger**
- **Definition**: Hidden log tracking which professional skills/personas used per task
- **Captured Data**: Session ID, task type (risk identification, PRD generation), personas used (PM, BA, PO, Product Manager)
- **Purpose**: Transparency into agent decision-making, continuous improvement data
- **Access**: Settings tab → expandable section (collapsed by default)

**PII (Personally Identifiable Information)**
- **Definition**: Data that identifies individuals or organizations (names, emails, phone numbers, company names, proprietary project terms)
- **VPMA Context**: Detected and anonymized by Privacy Proxy before LLM API calls
- **Detection Methods**: Regex patterns (emails, phones, URLs) + spaCy NER (PERSON, ORG, GPE, PRODUCT)

**NER (Named Entity Recognition)**
- **Definition**: ML technique to identify and classify entities in text (person names, organizations, locations, products)
- **VPMA Implementation**: spaCy library with `en_core_web_sm` model
- **Entity Types**: PERSON (John Smith), ORG (ACME Corp), GPE (San Francisco), PRODUCT (iPhone)

**RAID Log**
- **Definition**: Project management artifact tracking Risks, Assumptions, Issues, Dependencies
- **Format**: Markdown table or JSON with fields: ID, Type, Description, Owner, Status, Mitigation, Probability, Impact
- **VPMA Usage**: One of most frequently updated artifacts (after every meeting, weekly reviews)

**PRD (Product Requirements Document)**
- **Definition**: Product management artifact defining problem statement, user personas, features, acceptance criteria
- **Format**: Markdown or DOCX (typically 5-20 pages)
- **VPMA Usage**: Generated in Project Initiation, updated in Artifact Sync when feature discussions occur

**Charter (Project Charter)**
- **Definition**: Foundational PM artifact defining project objectives, scope, deliverables, success criteria, stakeholders, constraints
- **Format**: Markdown or DOCX (typically 2-5 pages)
- **VPMA Usage**: Source of truth for project definition, influences all downstream artifacts (Schedule, RAID, Communications Plan)

**WBS (Work Breakdown Structure)**
- **Definition**: Hierarchical decomposition of project deliverables into tasks
- **VPMA Context**: Captured in Tasks artifact (#15), not standalone WBS document
- **Format**: Markdown outline or JSON hierarchy

**Triple-Brain / Multi-Provider**
- **Definition**: VPMA's architecture supporting toggle between Claude Pro, Gemini, and local LLM (Ollama) APIs
- **Purpose**: User choice (quality vs. cost vs. speed vs. privacy), resilience (if one API down, switch to another), zero-cost option via local models
- **Implementation**: Unified LLM client abstraction with provider adapters (Claude, Gemini, Ollama) — same interface, different backends
- **Phase Availability**: Claude + Gemini in Phase 0, Ollama added in Phase 2

**Bubble**
- **Definition**: UI element in Artifact Sync (Tab 2) representing a suggested artifact update
- **Structure**: `[Artifact Name] • [Change Type] • [Confidence Score]`
- **Interactions**: Hover to expand preview, click to copy or apply to database
- **Visual Hierarchy**: Color-coded by urgency (Red=Critical, Yellow=Important, Green=FYI)

**Technical Fluency Translation**
- **Definition**: Feature to translate technical discussions into PM-friendly language
- **Toggle**: Session-level switch in app header + default setting in Settings tab
- **Output**: "🎓 Technical Translation" section explaining technical concepts, architecture decisions, jargon
- **Purpose**: Help PMs build technical vocabulary, understand engineering discussions

**Communications Assistant**
- **Definition**: Cross-tab feature (💬 Compose) for on-demand Slack/email drafting
- **Access**: Floating action button in header (always visible)
- **Context-Aware**: Automatically reads current project/session context to provide relevant drafts
- **Output**: Copy-to-clipboard only (VPMA never sends messages directly)

**Persistent Feedback Box**
- **Definition**: Cross-tab feature (📝 Feedback) for capturing bugs, feature requests, UX improvements
- **Access**: Small floating button in bottom-right corner (always visible)
- **Storage**: `~/VPMA/feedback/feedback_log.md` with intelligent categorization
- **Independence**: App-level feedback (not tied to specific project/session)

**NPS (Net Promoter Score)**
- **Definition**: User satisfaction metric based on "How likely are you to recommend VPMA?" (0-10 scale)
- **Calculation**: % Promoters (9-10) - % Detractors (0-6)
- **Benchmark**: SaaS average ~30-40, top products >50
- **VPMA Target**: 50+ (12-month vision)

**CSAT (Customer Satisfaction Score)**
- **Definition**: Simple satisfaction rating "How satisfied are you with VPMA this week?" (1-5 scale)
- **Frequency**: Weekly pulse survey
- **VPMA Target**: 4.5/5.0 (12-month vision)

**RALPH (Ralph Wiggum Loop)**
- **Definition**: Iterative AI development methodology where a loop repeatedly feeds a prompt to Claude Code until a task is complete
- **Core Pattern**: `while :; do cat PROMPT.md | claude ; done` — Claude writes code, runs tests, fixes errors, commits
- **Usage in VPMA**: Each development phase is decomposed into 15-25 RALPH tasks; human-in-the-loop mode for Phase 0-1
- **Reference**: See Section 10.6 for full RALPH workflow and task decomposition

**Ollama**
- **Definition**: Local LLM runtime that provides a REST API (localhost:11434) for running open-source models on personal hardware
- **VPMA Usage**: Third LLM provider option (Phase 2+) enabling zero-cost, zero-data-egress operations
- **Recommended Model**: Llama 3.1 8B on M4 MacBook Air with 24GB RAM (~40-60 tokens/sec)
- **Install**: `brew install ollama && ollama pull llama3.1:8b`

**Firebase Auth**
- **Definition**: Google's authentication-as-a-service platform for adding login to web/mobile apps
- **VPMA Usage**: Phase 4 web deployment — Google OAuth sign-in with ~50 lines of integration code (free tier)

**Presidio**
- **Definition**: Microsoft's open-source PII detection and anonymization framework (enterprise-grade alternative to basic spaCy NER)
- **VPMA Usage**: Phase 4 security upgrade — replaces basic regex+NER with commercial-grade anonymization supporting custom recognizers and multiple languages

---

### 10.2 Sample Artifact Templates

This subsection provides concrete examples of artifact structure and content for reference during development and user onboarding.

---

#### Template 1: Project Charter (Software Development Project)

```markdown
# {PROJECT_NAME} - Project Charter

**Document Owner**: {PM_NAME}
**Last Updated**: {DATE}
**Status**: Draft | Approved | Active

---

## 1. Project Objective

{Clear 1-2 sentence statement of what this project will accomplish and why it matters}

**Example**:
Migrate our monolithic e-commerce platform to a microservices architecture to improve scalability, reduce deployment complexity, and enable faster feature delivery. This migration will support our goal of doubling transaction volume by Q4 2026 without infrastructure collapse.

---

## 2. Scope

### In Scope
- {DELIVERABLE_1}: {Brief description}
- {DELIVERABLE_2}: {Brief description}
- {DELIVERABLE_3}: {Brief description}

**Example**:
- **User Service Migration**: Extract user authentication, profile management into standalone service
- **Product Catalog Service**: Separate product data, inventory management from monolith
- **API Gateway**: Implement Kong or AWS API Gateway for request routing
- **CI/CD Pipeline Update**: Adapt deployment pipeline for multi-service architecture

### Out of Scope
- {EXCLUDED_ITEM_1}: {Why excluded - future phase, different team, etc.}
- {EXCLUDED_ITEM_2}: {Why excluded}

**Example**:
- **Payment Service Migration**: Handled in separate Phase 2 project (Q3 2026) due to PCI compliance complexity
- **Frontend Rewrite**: Current React app will remain, only backend services migrate
- **Database Sharding**: Deferred to 2027 pending data growth analysis

---

## 3. Deliverables

| Deliverable | Description | Owner | Target Completion |
|-------------|-------------|-------|-------------------|
| {DELIVERABLE_NAME_1} | {Description} | {OWNER} | {DATE} |
| {DELIVERABLE_NAME_2} | {Description} | {OWNER} | {DATE} |

**Example**:
| Deliverable | Description | Owner | Target Completion |
|-------------|-------------|-------|-------------------|
| User Service | Standalone auth/profile microservice with REST API | Backend Team | 2026-04-30 |
| Product Catalog Service | Product data service with GraphQL interface | Backend Team | 2026-05-31 |
| API Gateway | Kong gateway configured with routing, rate limiting | DevOps | 2026-04-15 |
| Migration Runbook | Step-by-step migration procedure with rollback plan | PM + Tech Lead | 2026-06-15 |

---

## 4. Success Criteria

**How we'll know this project succeeded:**

- **Criterion 1**: {Measurable outcome}
- **Criterion 2**: {Measurable outcome}
- **Criterion 3**: {Measurable outcome}

**Example**:
- **Performance**: API response time p95 improves from 450ms to <200ms
- **Scalability**: System handles 10,000 concurrent users (vs. current 3,000 limit) without degradation
- **Deployment Velocity**: Time to deploy new feature reduces from 2 weeks to 2 days
- **Reliability**: 99.9% uptime maintained throughout migration (no downtime >5 minutes)

---

## 5. Stakeholders

| Role | Name | Responsibilities | Involvement Level |
|------|------|------------------|-------------------|
| **Executive Sponsor** | {NAME} | Budget approval, strategic alignment | Monthly updates |
| **Project Manager** | {NAME} | Day-to-day coordination, risk management | Daily |
| **Tech Lead** | {NAME} | Architecture decisions, technical oversight | Daily |
| **Backend Team** | {NAMES} | Service development, testing | Daily |
| **DevOps** | {NAME} | Infrastructure, CI/CD, deployment | Weekly + on-demand |
| **QA Lead** | {NAME} | Test strategy, regression testing | Weekly |
| **Product Owner** | {NAME} | Requirements clarification, UAT | Bi-weekly |

---

## 6. Constraints

**Timeline**: {TARGET_DATE} (hard deadline due to {REASON})
**Budget**: {BUDGET_AMOUNT} (allocated from {BUDGET_SOURCE})
**Resources**: {TEAM_SIZE} engineers available ({FTE_TOTAL} FTE total)
**Dependencies**: {EXTERNAL_DEPENDENCY} must complete by {DATE} for us to proceed

**Example**:
- **Timeline**: June 30, 2026 (hard deadline - Q3 marketing campaign depends on improved scalability)
- **Budget**: $250,000 (allocated from 2026 infrastructure modernization fund)
- **Resources**: 4 backend engineers, 1 DevOps engineer, 1 QA engineer (6 FTE total)
- **Dependencies**: Cloud infrastructure upgrade (led by Platform team) must complete by April 1 for microservices to deploy

---

## 7. Assumptions

- {ASSUMPTION_1}: {What we're assuming to be true}
- {ASSUMPTION_2}: {What we're assuming to be true}

**Example**:
- **Cloud Capacity**: AWS will approve our increased EC2 quota request (submitted Feb 1)
- **Team Availability**: No major team turnover or extended PTO during Q2 2026
- **Vendor Support**: Kong Enterprise support contract renewal approved by finance
- **Data Migration**: Existing database schema supports clean service separation (no major refactoring needed)

---

## 8. High-Level Risks

*(Full RAID Log maintained separately - these are top 3 risks at project initiation)*

| Risk | Impact | Mitigation |
|------|--------|------------|
| {RISK_1} | {IMPACT} | {MITIGATION_STRATEGY} |
| {RISK_2} | {IMPACT} | {MITIGATION_STRATEGY} |

**Example**:
| Risk | Impact | Mitigation |
|------|--------|------------|
| **Data consistency issues** during migration | Production outage, revenue loss | Comprehensive integration testing, phased rollout with feature flags, instant rollback capability |
| **AWS quota increase delayed** | Timeline slip 2-4 weeks | Submit request early (Feb 1), escalate via AWS TAM, backup plan with current quota limits |
| **Backend engineer attrition** | Velocity reduction 25-40% | Cross-training on services, comprehensive documentation, retain knowledge before departures |

---

## 9. Communication Plan

**Status Reports**: {FREQUENCY} to {AUDIENCE} via {METHOD}
**Steering Committee**: {FREQUENCY} with {ATTENDEES}
**Daily Standups**: {TIME} with {TEAM}

**Example**:
- **Status Reports**: Weekly email to Executive Sponsor, Product Owner, Engineering Director (every Monday 9am)
- **Steering Committee**: Bi-weekly meeting with Sponsor, PM, Tech Lead, Product Owner (Wednesdays 2pm)
- **Daily Standups**: 9:30am with Backend Team, DevOps, QA Lead (15 minutes)
- **Demo Sessions**: End of each sprint (bi-weekly) with broader stakeholder group

---

## Approval

**Prepared By**: {PM_NAME}, Project Manager
**Reviewed By**: {TECH_LEAD_NAME}, Technical Lead
**Approved By**: {SPONSOR_NAME}, Executive Sponsor

**Approval Date**: {DATE}
**Signature**: ___________________________

---

*This Charter is a living document and may be updated as project scope, stakeholders, or constraints evolve. Major changes require Executive Sponsor approval.*
```

---

#### Template 2: RAID Log (with Multiple Format Options)

**Option A: Markdown Table Format**

```markdown
# {PROJECT_NAME} - RAID Log

**Last Updated**: {DATE}
**Owner**: {PM_NAME}

---

## Risks

| ID | Description | Probability | Impact | Mitigation | Owner | Status | Date Raised |
|----|-------------|-------------|--------|------------|-------|--------|-------------|
| R1 | AWS quota increase delayed beyond April 1 | Medium | High | Early submission (Feb 1), AWS TAM escalation, backup plan with current limits | DevOps Lead | Open | 2026-02-10 |
| R2 | Data migration causes inconsistencies between services | Low | Critical | Comprehensive integration tests, phased rollout, instant rollback | Backend Lead | Open | 2026-02-12 |
| R3 | Backend engineer attrition mid-project | Medium | High | Cross-training, documentation, knowledge transfer sessions | PM | Open | 2026-02-08 |

---

## Assumptions

| ID | Description | Validation Date | Status | Owner | Notes |
|----|-------------|-----------------|--------|-------|-------|
| A1 | AWS will approve EC2 quota increase | 2026-03-01 | Pending | DevOps Lead | Request submitted Feb 1 |
| A2 | No major team turnover Q2 2026 | Ongoing | Valid | PM | Monitor monthly 1:1s |
| A3 | Kong Enterprise license renewal approved | 2026-02-20 | Valid | PM | Finance approved Feb 5 |
| A4 | Database schema supports service separation | 2026-02-28 | Pending Validation | Tech Lead | Schema analysis in progress |

---

## Issues

| ID | Description | Severity | Resolution Plan | Owner | Status | Date Raised | Target Resolution |
|----|-------------|----------|-----------------|-------|--------|-------------|-------------------|
| I1 | CI/CD pipeline failing on multi-service builds | High | Investigate Jenkins configuration, consult DevOps | Backend Engineer 1 | In Progress | 2026-02-13 | 2026-02-15 |
| I2 | Product Catalog API spec conflict with frontend expectations | Medium | Schedule alignment meeting with Frontend Lead | Backend Engineer 2 | Open | 2026-02-14 | 2026-02-17 |

---

## Dependencies

| ID | Description | Dependency On | Required By | Status | Owner | Notes |
|----|-------------|---------------|-------------|--------|-------|-------|
| D1 | Cloud infrastructure upgrade | Platform Team | 2026-04-01 | On Track | Platform PM | Weekly sync calls |
| D2 | API gateway hardware provisioning | IT Procurement | 2026-03-15 | Blocked | DevOps Lead | PO submitted, awaiting approval |
| D3 | Security audit approval for new architecture | InfoSec Team | 2026-03-31 | Not Started | PM | Kickoff meeting scheduled Feb 20 |

---

**Legend**:
- **Probability**: Low | Medium | High
- **Impact**: Low | Medium | High | Critical
- **Severity**: Low | Medium | High | Critical
- **Status**: Open | In Progress | Resolved | Closed | Deferred
```

---

**Option B: JSON Schema** (for programmatic access, import/export)

```json
{
  "project_name": "{PROJECT_NAME}",
  "last_updated": "2026-02-14T10:30:00Z",
  "owner": "{PM_NAME}",

  "risks": [
    {
      "id": "R1",
      "description": "AWS quota increase delayed beyond April 1",
      "probability": "Medium",
      "impact": "High",
      "mitigation": "Early submission (Feb 1), AWS TAM escalation, backup plan with current limits",
      "owner": "DevOps Lead",
      "status": "Open",
      "date_raised": "2026-02-10"
    },
    {
      "id": "R2",
      "description": "Data migration causes inconsistencies between services",
      "probability": "Low",
      "impact": "Critical",
      "mitigation": "Comprehensive integration tests, phased rollout, instant rollback",
      "owner": "Backend Lead",
      "status": "Open",
      "date_raised": "2026-02-12"
    }
  ],

  "assumptions": [
    {
      "id": "A1",
      "description": "AWS will approve EC2 quota increase",
      "validation_date": "2026-03-01",
      "status": "Pending",
      "owner": "DevOps Lead",
      "notes": "Request submitted Feb 1"
    }
  ],

  "issues": [
    {
      "id": "I1",
      "description": "CI/CD pipeline failing on multi-service builds",
      "severity": "High",
      "resolution_plan": "Investigate Jenkins configuration, consult DevOps",
      "owner": "Backend Engineer 1",
      "status": "In Progress",
      "date_raised": "2026-02-13",
      "target_resolution": "2026-02-15"
    }
  ],

  "dependencies": [
    {
      "id": "D1",
      "description": "Cloud infrastructure upgrade",
      "dependency_on": "Platform Team",
      "required_by": "2026-04-01",
      "status": "On Track",
      "owner": "Platform PM",
      "notes": "Weekly sync calls"
    }
  ]
}
```

---

#### Template 3: Status Report

```markdown
# {PROJECT_NAME} - Status Report

**Reporting Period**: {START_DATE} - {END_DATE}
**Prepared By**: {PM_NAME}
**Report Date**: {DATE}
**Overall Status**: 🟢 On Track | 🟡 At Risk | 🔴 Off Track

---

## Executive Summary

{1-2 paragraph summary of project health, major accomplishments, top concerns}

**Example**:
The microservices migration project remains **🟢 On Track** for June 30 delivery. This week we completed User Service development (Milestone 1) and began integration testing. API Gateway configuration is 80% complete. One concern: CI/CD pipeline issues discovered (Issue #I1) may delay deployment readiness by 3-5 days if not resolved by Friday - DevOps team actively troubleshooting.

**Key Metrics**:
- **Schedule**: 35% complete (on track)
- **Budget**: $87,000 spent of $250,000 (35% - aligned with schedule)
- **Quality**: 12 user stories delivered, 0 critical bugs
- **Team Velocity**: 23 story points this sprint (target: 20-25)

---

## Progress Since Last Report

### Completed This Week
- ✅ **User Service Development**: REST API endpoints implemented, unit tests at 95% coverage
- ✅ **API Gateway**: Kong configured with routing rules for User Service
- ✅ **Documentation**: API specification published to internal docs site

### In Progress
- 🔄 **Product Catalog Service**: Database schema finalized, service skeleton created (60% complete)
- 🔄 **Integration Testing**: User Service + API Gateway end-to-end tests (3 of 8 test scenarios passing)
- 🔄 **CI/CD Pipeline**: Jenkins multi-service build configuration (blocked by Issue #I1)

### Blocked / At Risk
- 🔴 **Issue #I1**: CI/CD pipeline failing on multi-service builds - DevOps investigating, target fix by Feb 15
- 🟡 **Risk #R2**: Data migration complexity higher than estimated - may need additional sprint for testing

---

## Upcoming Work (Next 2 Weeks)

**This Week** (Feb 14-18):
- Complete Product Catalog Service development
- Resolve CI/CD pipeline issue (Issue #I1)
- Finalize User Service integration tests

**Next Week** (Feb 21-25):
- Begin Product Catalog Service integration testing
- Security audit kickoff meeting with InfoSec (Dependency #D3)
- Sprint planning for Phase 2 (User Service deployment to staging)

---

## Key Metrics Dashboard

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **Schedule Progress** | 35% by Feb 14 | 35% | 🟢 On Track |
| **Budget Spend** | <40% by Feb 14 | 35% | 🟢 Under Budget |
| **Story Points Delivered** | 20-25 per sprint | 23 | 🟢 On Track |
| **Code Coverage** | >90% | 95% | 🟢 Exceeds Target |
| **Open Critical Bugs** | 0 | 0 | 🟢 On Track |
| **API Response Time (p95)** | <200ms | 180ms | 🟢 Exceeds Target |

---

## Top Risks & Issues

### Critical Items Needing Attention

**🔴 Issue #I1: CI/CD Pipeline Failures**
- **Impact**: Blocks deployment automation, could delay Phase 2 by 1 week if not resolved
- **Status**: DevOps team troubleshooting, investigating Jenkins plugin conflicts
- **Next Steps**: Decision point Friday - escalate to vendor support if not resolved internally
- **Owner**: DevOps Lead

**🟡 Risk #R2: Data Migration Complexity**
- **Update**: Schema analysis revealed 3 additional data relationships requiring careful migration
- **Mitigation**: Adding 2-day buffer to integration testing sprint, Backend Lead reviewing migration scripts
- **Impact**: Low (buffer absorbs complexity), monitoring closely

### Recently Resolved
- ✅ **Risk #R3 (Backend Attrition)**: Engineer who gave notice last week completed knowledge transfer, documentation updated
- ✅ **Issue #I2 (API Spec Conflict)**: Resolved via alignment meeting with Frontend Lead, spec updated

---

## Stakeholder Actions Needed

**Action Required**:
1. **Executive Sponsor**: Approve $15K additional budget for Kong Enterprise support (needed for Issue #I1 escalation if internal troubleshooting fails) - **Decision needed by Feb 15**
2. **Product Owner**: Review and approve updated API specifications for Product Catalog Service - **Review by Feb 16**

**FYI / No Action**:
- InfoSec security audit kickoff scheduled Feb 20 (Dependency #D3 on track)
- AWS quota increase request submitted Feb 1, awaiting response (Assumption #A1)

---

## Budget Status

| Category | Allocated | Spent | Remaining | % Spent |
|----------|-----------|-------|-----------|---------|
| **Engineering Labor** | $180,000 | $65,000 | $115,000 | 36% |
| **Infrastructure (AWS)** | $40,000 | $12,000 | $28,000 | 30% |
| **Tools & Licenses** | $30,000 | $10,000 | $20,000 | 33% |
| **Total** | $250,000 | $87,000 | $163,000 | 35% |

**Variance**: On track - 35% spent aligns with 35% schedule completion

---

## Team Health

**Morale**: 🟢 High - team energized by User Service completion milestone
**Capacity**: 🟢 Full team available next 2 weeks
**Concerns**: 🟡 DevOps engineer working extra hours on CI/CD issue - monitoring for burnout

**Staffing Changes**:
- Backend Engineer 3 departed Feb 12 (planned resignation, knowledge transfer complete)
- Backfill interview process started, target offer by Feb 28

---

## Appendix: Detailed Metrics

*(Attach: Burndown chart, velocity trend, test coverage report, API performance graphs)*

---

**Next Report**: Feb 21, 2026
**Questions?** Contact {PM_NAME} at {EMAIL}
```

---

### 10.3 Architecture Diagram Concepts

This subsection describes key architecture diagrams to be created during implementation. These diagrams will visualize VPMA's technical design for developers and stakeholders.

---

#### Diagram 1: System Architecture Overview

**Purpose**: High-level view of VPMA components and data flow

**Components to Visualize**:

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│                  (React Frontend + Electron)                    │
│                                                                 │
│  [Daily Planner] [Artifact Sync] [Deep Strategy] [Initiation]  │
│  [History] [Settings] [💬 Compose] [📝 Feedback]               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Artifact    │  │  Deep        │  │  Project     │         │
│  │  Sync        │  │  Strategy    │  │  Initiation  │         │
│  │  Engine      │  │  Engine      │  │  Engine      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐          │
│  │         PRIVACY PROXY (Anonymization)            │          │
│  │  • Regex PII Detection                           │          │
│  │  • spaCy NER (PERSON, ORG, GPE, PRODUCT)        │          │
│  │  • Token Vault (SQLite)                          │          │
│  └──────────────────────────────────────────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LLM INTEGRATION LAYER                        │
│                                                                 │
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │   Claude API     │              │   Gemini API     │        │
│  │  (Anthropic)     │ ◄────────►   │   (Google)       │        │
│  │                  │   Toggle     │                  │        │
│  └──────────────────┘              └──────────────────┘        │
│                                                                 │
│         [HTTPS Requests to External APIs]                       │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
         [Anonymized Request] → LLM processes → [Anonymized Response]
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  PRIVACY PROXY (Re-identification)                              │
│  <PERSON_1> → John Smith                                        │
│  <ORG_2> → ACME Corp                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│                                                                 │
│  ┌────────────────────┐        ┌────────────────────┐          │
│  │  SQLite Database   │        │  Markdown Files    │          │
│  │  (Metadata)        │        │  (Artifact Content)│          │
│  │                    │        │                    │          │
│  │ • sessions         │        │ ~/VPMA/artifacts/  │          │
│  │ • artifacts        │        │  - charter.md      │          │
│  │ • pii_vault        │        │  - raid_log.md     │          │
│  │ • projects         │        │  - status.md       │          │
│  └────────────────────┘        └────────────────────┘          │
│                                                                 │
│  Storage: ~/VPMA/vpma.db + ~/VPMA/artifacts/*.md               │
└─────────────────────────────────────────────────────────────────┘
```

**Key Flows**:
1. **User Input** → Privacy Proxy (anonymize) → LLM API → Privacy Proxy (re-identify) → UI Output
2. **Artifact Update** → Business Logic validates → SQLite metadata updated → Markdown file written
3. **Session Log** → SQLite sessions table → History tab query → Display

---

#### Diagram 2: Privacy Proxy Data Flow

**Purpose**: Detailed view of PII anonymization and re-identification process

```
USER INPUT: "John Smith from ACME Corp emailed john@acme.com about Project Falcon budget increase"

         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: PII DETECTION                                      │
│                                                             │
│  Regex Patterns:                                            │
│  • Email: john@acme.com ✓                                  │
│  • URL: (none)                                             │
│  • Phone: (none)                                           │
│                                                             │
│  spaCy NER:                                                 │
│  • PERSON: "John Smith" (confidence: 0.95) ✓               │
│  • ORG: "ACME Corp" (confidence: 0.92) ✓                   │
│  • PRODUCT: "Project Falcon" (confidence: 0.78) ✓          │
│                                                             │
│  Custom Dictionary:                                         │
│  • "Project Falcon" → User-defined sensitive term ✓        │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: TOKENIZATION                                       │
│                                                             │
│  Create tokens and store in vault:                          │
│  • John Smith → <PERSON_1>                                 │
│  • ACME Corp → <ORG_1>                                      │
│  • john@acme.com → <EMAIL_1>                               │
│  • Project Falcon → <PRODUCT_1>                            │
│                                                             │
│  Vault Entry (SQLite pii_vault table):                      │
│  | token      | original       | entity_type | first_seen |│
│  |------------|----------------|-------------|------------|│
│  | <PERSON_1> | John Smith     | PERSON      | 2026-02-14 |│
│  | <ORG_1>    | ACME Corp      | ORG         | 2026-02-14 |│
│  | <EMAIL_1>  | john@acme.com  | EMAIL       | 2026-02-14 |│
│  | <PRODUCT_1>| Project Falcon | PRODUCT     | 2026-02-14 |│
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: ANONYMIZED OUTPUT (sent to LLM)                    │
│                                                             │
│  "<PERSON_1> from <ORG_1> emailed <EMAIL_1> about          │
│   <PRODUCT_1> budget increase"                              │
└─────────────────────────────────────────────────────────────┘
         │
         ▼  [HTTPS to Claude/Gemini API]
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: LLM RESPONSE (with tokens)                         │
│                                                             │
│  "Updated RAID Log: Added risk R4 - <PRODUCT_1> budget      │
│   increase pending <ORG_1> approval. Owner: <PERSON_1>.     │
│   Mitigation: Escalate to CFO if not approved by Feb 20."   │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: RE-IDENTIFICATION (lookup vault)                   │
│                                                             │
│  <PERSON_1> → John Smith                                   │
│  <ORG_1> → ACME Corp                                        │
│  <PRODUCT_1> → Project Falcon                              │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: FINAL OUTPUT (shown to user)                       │
│                                                             │
│  "Updated RAID Log: Added risk R4 - Project Falcon budget   │
│   increase pending ACME Corp approval. Owner: John Smith.   │
│   Mitigation: Escalate to CFO if not approved by Feb 20."   │
└─────────────────────────────────────────────────────────────┘
```

**Security Properties**:
- ✅ PII never sent to external APIs (only tokens)
- ✅ Vault stored locally (SQLite file on user's laptop)
- ✅ User can review anonymized payloads (Privacy Audit Log)
- ✅ Global vault ensures consistent token mappings across sessions

---

#### Diagram 3: Data Storage Model

**Purpose**: Database schema and file system organization

**SQLite Schema** (`~/VPMA/vpma.db`):

```sql
-- Projects table
CREATE TABLE projects (
  project_id TEXT PRIMARY KEY,
  project_name TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  landscape_config JSON  -- Fixed Landscape configuration
);

-- Artifacts table (metadata only, content in Markdown files)
CREATE TABLE artifacts (
  artifact_id TEXT PRIMARY KEY,
  project_id TEXT REFERENCES projects(project_id),
  artifact_type TEXT NOT NULL,  -- 'Charter', 'RAID Log', 'PRD', etc.
  file_path TEXT NOT NULL,       -- Path to .md file
  last_updated TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table (history)
CREATE TABLE sessions (
  session_id TEXT PRIMARY KEY,
  project_id TEXT REFERENCES projects(project_id),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  tab_used TEXT,  -- 'Daily Planner', 'Artifact Sync', etc.
  user_input TEXT,
  agent_output JSON,  -- List of artifact updates/bubbles
  persona_used TEXT,  -- 'PM,BA' or 'PO,Product Manager'
  tokens_used INTEGER,
  llm_model TEXT,  -- 'claude-3-5-sonnet' or 'gemini-1.5-pro'
  duration_seconds INTEGER
);

-- PII Vault table
CREATE TABLE pii_vault (
  token TEXT PRIMARY KEY,  -- '<PERSON_1>', '<ORG_2>', etc.
  original_value TEXT NOT NULL,
  entity_type TEXT,  -- 'PERSON', 'ORG', 'EMAIL', 'PRODUCT'
  first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_sessions_project ON sessions(project_id);
CREATE INDEX idx_sessions_timestamp ON sessions(timestamp DESC);
CREATE INDEX idx_artifacts_project ON artifacts(project_id);
```

**File System Structure**:

```
~/VPMA/
├── vpma.db                          # SQLite database (metadata)
├── artifacts/
│   ├── project_falcon_charter.md
│   ├── project_falcon_raid_log.md
│   ├── project_falcon_status.md
│   ├── project_falcon_prd.md
│   └── ... (all artifact content as Markdown)
├── exports/                         # User-initiated exports
│   ├── project_falcon/
│   │   ├── charter_2026-02-14.docx
│   │   ├── raid_log_2026-02-14.pdf
│   │   └── status_2026-02-14.md
├── backups/                         # Manual project exports
│   ├── project_falcon_2026-02-14.zip
│   └── project_falcon_2026-02-01.zip
├── feedback/
│   └── feedback_log.md              # Persistent Feedback Box log
├── analytics/                       # Anonymous usage logs
│   ├── sessions.db                  # Session-level analytics
│   ├── performance_log.jsonl
│   ├── error_log.jsonl
│   └── learning_ledger.jsonl
└── privacy/
    └── audit_log.jsonl              # All anonymized payloads sent to LLM
```

---

### 10.4 Sample User Journeys

This subsection provides step-by-step walkthroughs of common VPMA workflows.

---

#### Journey 1: Daily Artifact Sync (Most Common Workflow)

**User**: Senior PM managing software development project
**Context**: Just finished weekly steering committee meeting, has transcript from Zoom
**Goal**: Update RAID Log, Status Report, Meeting Notes, and Action Items based on meeting discussion
**Time Estimate**: 2 minutes (vs. 30 minutes manual)

**Step-by-Step Flow**:

**1. Launch VPMA** (8:00 AM)
- User opens terminal: `npm start` (starts React frontend on port 3000 + FastAPI backend on port 8000)
- Browser opens to `localhost:3000`
- **Default Landing**: Tab 2 (Artifact Sync) - clean search bar

**2. Input Meeting Transcript** (8:01 AM)
- User copies transcript from Zoom chat (3,500 words, 25 minutes of discussion)
- Pastes into VPMA input area (large text box with hint: "Paste meeting transcript, notes, or describe updates...")
- Clicks [Sync] button (or Enter)

**3. Privacy Proxy Anonymization** (8:01:05 AM, 5 seconds)
- **Detection**: Privacy Proxy identifies:
  - 5 person names (John Smith, Sarah Chen, Mike Rodriguez, Emily Davis, Tom Wilson)
  - 2 organizations (ACME Corp, VendorCo)
  - 3 emails
  - 1 proprietary term ("Project Falcon")
- **Confidence**: All >90% confidence except "Project Falcon" (78% - in custom dictionary, flagged as sensitive)
- **User Preview** (optional, if enabled in Settings):
  - Side-by-side view shows original vs. anonymized
  - User clicks [Looks Good] (proceeds) - preview disabled by default in this session
- **Tokenization**: 11 PII instances → 11 tokens (`<PERSON_1>` through `<PERSON_5>`, `<ORG_1>`, `<ORG_2>`, `<EMAIL_1>` through `<EMAIL_3>`, `<PRODUCT_1>`)

**4. LLM Processing** (8:01:10 AM, 5 seconds)
- **Claude API Call**: Anonymized transcript sent
- **Prompt**: "Analyze this meeting transcript. Identify which PM artifacts need updates and extract deltas. Return structured JSON with artifact types, change descriptions, proposed text, confidence scores."
- **LLM Response** (3 seconds):
  ```json
  [
    {
      "artifact_type": "RAID Log",
      "change_type": "3 New Risks",
      "proposed_text": "R12: VendorCo delivery delay may push Phase 2 timeline by 2 weeks...",
      "confidence": 0.92
    },
    {
      "artifact_type": "Status Report",
      "change_type": "Progress Update",
      "proposed_text": "Milestone 3 completed ahead of schedule...",
      "confidence": 0.88
    },
    {
      "artifact_type": "Meeting Notes",
      "change_type": "Complete Summary",
      "proposed_text": "# Weekly Steering Committee - Feb 14, 2026\n\nAttendees: <PERSON_1>, <PERSON_2>, <PERSON_3>...",
      "confidence": 0.95
    },
    {
      "artifact_type": "Action Items",
      "change_type": "5 New Items",
      "proposed_text": "1. <PERSON_2> to follow up with VendorCo by Feb 17...",
      "confidence": 0.90
    },
    {
      "artifact_type": "Decision Log",
      "change_type": "1 Decision Recorded",
      "proposed_text": "Decision D15: Approved additional $25K budget for Q2 contingency...",
      "confidence": 0.85
    }
  ]
  ```

**5. Re-identification & Bubble Display** (8:01:15 AM, 5 seconds)
- Privacy Proxy replaces tokens with original values
- **UI Renders 5 Bubbles** (vertical list, color-coded):
  ```
  🔴 RAID Log • 3 New Risks • High Confidence
  🟡 Status Report • Progress Update • High Confidence
  🟢 Meeting Notes • Complete Summary • High Confidence
  🟡 Action Items • 5 New Items • High Confidence
  🟢 Decision Log • 1 Decision Recorded • High Confidence
  ```

**6. User Reviews Bubbles** (8:01:30 AM, 15 seconds per bubble = 75 seconds total)
- **Hover over RAID Log bubble**:
  - Bubble expands to show preview:
    ```
    R12: VendorCo delivery delay may push Phase 2 timeline by 2 weeks (Probability: High, Impact: High)
    Mitigation: Schedule alignment meeting, explore backup vendor options
    Owner: Sarah Chen

    R13: Budget overage risk if contingency not approved ($25K requested)
    Mitigation: Executive sponsor approved additional budget in today's meeting
    Owner: Tom Wilson

    R14: Backend engineer departure (Emily Davis leaving end of March)
    Mitigation: Knowledge transfer sessions scheduled, begin backfill recruitment
    Owner: PM (me)
    ```
  - User thinks: "Looks good, captures all key risks"
  - Clicks [Apply] button → Preview modal shows full text → [Confirm] → Updates VPMA SQLite database

- **Hover over Status Report bubble**:
  - Expands to show:
    ```
    **Progress This Week:**
    - Milestone 3 (API Integration) completed Feb 13 (3 days ahead of schedule)
    - User authentication service deployed to staging environment
    - Integration testing in progress (5 of 8 test scenarios passing)

    **Key Metrics:**
    - Schedule: 58% complete (vs. 55% target - ahead of schedule)
    - Budget: $142K spent of $250K (57% - on track)
    - Velocity: 28 story points this sprint (exceeds 20-25 target)
    ```
  - User: "Perfect summary"
  - Clicks [Copy] button → Text copied to clipboard → Will paste into weekly status email later

- **Meeting Notes, Action Items, Decision Log**: Similar review process
  - All bubbles look accurate
  - User applies Meeting Notes and Decision Log to database
  - Copies Action Items to send in follow-up email

**7. Commit Session** (8:02:45 AM, 5 seconds)
- User clicks [Log] button at bottom
- **Session Saved**:
  - `sessions` table: session_id, timestamp, tab_used="Artifact Sync", artifacts_touched=["RAID Log", "Status Report", "Meeting Notes", "Action Items", "Decision Log"], tokens_used=3542, llm_model="claude-3-5-sonnet", duration_seconds=165
  - `artifacts` table: last_updated timestamps refreshed for RAID Log, Meeting Notes, Decision Log
  - Markdown files updated: `~/VPMA/artifacts/project_falcon_raid_log.md` (new risks appended), `project_falcon_meeting_notes.md` (new entry), `project_falcon_decision_log.md` (new decision)
- **UI**: Toast message "Session logged! 5 artifacts updated." + Input area clears

**Total Time**: 2 minutes 45 seconds (vs. 30-45 minutes manually writing meeting notes, updating RAID log, status report)

**User Outcome**:
- ✅ RAID Log updated with 3 new risks (before they're forgotten)
- ✅ Status Report draft ready (copy/paste into email)
- ✅ Meeting notes captured (searchable in History tab later)
- ✅ Action items extracted (ready to send follow-up)
- ✅ Decision formally logged (governance compliance)
- 💰 **27+ minutes saved** (can now focus on strategy instead of admin work)

---

#### Journey 2: Deep Strategy - Charter Scope Change Propagation

**User**: Senior PM on infrastructure migration project
**Context**: Executive sponsor just approved major scope expansion (adding 2 new services to migration)
**Goal**: Update Charter, then propagate changes to Schedule, RAID Log, PRD, Status Report to ensure consistency
**Time Estimate**: 45 minutes (vs. 4 hours manual)

**Step-by-Step Flow**:

**1. Navigate to Deep Strategy Tab** (10:00 AM)
- User clicks Tab 3 (Deep Strategy) in navigation
- **UI Shift**: High-contrast dark mode (signals "Deep Thinking" mode)
- Prompt: "Upload the latest versions of all relevant artifacts"

**2. Artifact Upload** (10:02 AM, 2 minutes)
- User drags/drops 5 files:
  - `project_charter_v2.docx` (current version with scope expansion notes)
  - `project_schedule.xlsx` (timeline before scope expansion)
  - `raid_log.csv` (current risks)
  - `prd.md` (product requirements)
  - `status_report_Feb10.docx` (last week's status)
- **Parsing**: VPMA extracts text from DOCX, Excel, CSV, Markdown (10 seconds)
- **User Confirmation**: "5 artifacts uploaded successfully"

**3. Priority Sequencing** (10:04 AM, 2 minutes)
- **UI**: Drag-and-drop list for ordering
- User defines hierarchy (changes flow downward):
  1. **Charter** (source of truth for scope)
  2. **Schedule** (timeline must reflect Charter deliverables)
  3. **RAID Log** (new risks from scope expansion)
  4. **PRD** (product features aligned with Charter)
  5. **Status Report** (reflects updated scope, timeline, risks)
- User clicks [Analyze] button

**4. Multi-Pass Reasoning** (10:06 AM, 8 minutes total)

**Pass 1: Dependency Graph** (2 minutes)
- **LLM Call 1**: "Analyze these 5 artifacts. Build a dependency graph showing how they influence each other. Identify which sections of each artifact reference other artifacts."
- **Privacy Proxy**: Anonymizes all 5 artifacts (4,200 words total → 4,500 tokens with anonymization)
- **LLM Response**:
  ```
  Dependency Graph:
  Charter (Scope: 4 services) →
    - Schedule (4 service migration phases)
    - RAID Log (risks for 4 services)
    - PRD (features for 4 services)

  Schedule (4 phases, June 30 completion) →
    - Status Report (timeline section)
    - RAID Log (date-based risks)

  RAID Log (12 risks) →
    - Status Report (top risks section)
  ```
- **UI**: Progress bar "Pass 1/4: Building dependency graph... ████░░░░ 25%"

**Pass 2: Inconsistency Detection** (2 minutes)
- **LLM Call 2**: "Based on the priority order (Charter > Schedule > RAID > PRD > Status), identify inconsistencies. Charter now has 6 services (expanded from 4). What needs to change in downstream artifacts?"
- **LLM Response**:
  ```
  Inconsistencies Detected:

  Charter Scope Expansion:
  - OLD: 4 services (User, Product Catalog, Order Management, Notification)
  - NEW: 6 services (added Payment Service, Analytics Service)

  Downstream Impacts:

  Schedule:
  - INCONSISTENT: Only shows 4 service migration phases
  - NEEDS: Add Phase 5 (Payment Service migration), Phase 6 (Analytics Service migration)
  - TIMELINE: Current completion June 30 → estimate August 15 (6-week extension)

  RAID Log:
  - INCONSISTENT: Risks only cover 4 services
  - NEEDS: Add risks for Payment Service (PCI compliance, vendor integration) and Analytics Service (data pipeline complexity, BI tool integration)
  - ESTIMATE: 4-6 new risks

  PRD:
  - INCONSISTENT: Feature list only includes 4 services
  - NEEDS: Add Payment Service features (multi-gateway support, fraud detection) and Analytics Service features (real-time dashboards, custom reports)

  Status Report:
  - INCONSISTENT: References June 30 completion, 4-service scope
  - NEEDS: Update timeline (August 15), scope (6 services), budget implications ($50K additional estimated)
  ```
- **UI**: Progress bar "Pass 2/4: Identifying inconsistencies... ████████░░ 50%"

**Pass 3: Update Generation** (3 minutes)
- **LLM Call 3**: "Generate proposed updates for each artifact to achieve consistency. Provide specific text changes (diff-style)."
- **LLM Response**: (Generates updated sections for all 5 artifacts)
  - **Charter**: Updated scope section (adds 2 services)
  - **Schedule**: New Phase 5 and Phase 6 rows, updated completion date
  - **RAID Log**: 5 new risks (R13-R17) for Payment and Analytics services
  - **PRD**: New feature sections for Payment and Analytics
  - **Status Report**: Updated timeline, scope, budget sections
- **Re-identification**: Privacy Proxy replaces tokens
- **UI**: Progress bar "Pass 3/4: Generating updates... ████████████░░ 75%"

**Pass 4: Cross-Validation** (1 minute)
- **LLM Call 4**: "Review all proposed updates. Check for consistency across artifacts. Ensure no conflicts."
- **LLM Response**:
  ```
  Cross-Validation Results:

  ✅ Charter scope (6 services) matches Schedule phases (6 phases)
  ✅ Schedule completion (Aug 15) matches Status Report timeline
  ✅ RAID Log risks cover all 6 services
  ✅ PRD features align with Charter deliverables
  ✅ Status Report budget ($50K increase) reflects scope expansion

  No inconsistencies detected. All artifacts aligned.
  ```
- **UI**: Progress bar "Pass 4/4: Validating consistency... ████████████████ 100%"

**5. Integration Report Display** (10:14 AM)
- **UI**: Tabbed view with 5 tabs (one per artifact)
- **Tab 1 (Charter)**:
  - **Detected Changes**: "Scope expanded from 4 to 6 services"
  - **Proposed Updates**:
    ```diff
    ### Deliverables

    - User Service
    - Product Catalog Service
    - Order Management Service
    - Notification Service
    + Payment Service
    + Analytics Service
    ```
  - **Consistency Check**: "✓ Aligned with Schedule (6 phases)"
  - [Accept] [Reject] buttons

- **Tab 2 (Schedule)**:
  - **Detected Changes**: "Charter added 2 services → need 2 new phases + timeline extension"
  - **Proposed Updates**:
    ```diff
    | Phase | Deliverable | Target Completion |
    |-------|-------------|-------------------|
    | 4     | Notification Service | 2026-06-15 |
    + | 5     | Payment Service | 2026-07-15 |
    + | 6     | Analytics Service | 2026-08-15 |

    - **Project Completion**: June 30, 2026
    + **Project Completion**: August 15, 2026
    ```
  - **Consistency Check**: "✓ 6 phases match Charter scope"
  - [Accept] [Reject] buttons

- *(Similar for RAID Log, PRD, Status Report tabs)*

**6. User Review & Accept** (10:20 AM, 6 minutes)
- User clicks through each tab
- Reviews proposed changes (all look accurate)
- Clicks [Accept] on all 5 tabs
- Clicks [Integrate Changes] button

**7. Commit & Export** (10:26 AM, 4 minutes)
- **Update Project State**:
  - `artifacts` table: last_updated timestamps refreshed for all 5 artifacts
  - Markdown files updated (Charter, RAID Log, PRD)
  - DOCX/Excel exports generated for Schedule and Status Report
- **Export Files**:
  - `~/VPMA/exports/project_falcon/charter_2026-02-14.docx` (updated)
  - `~/VPMA/exports/project_falcon/schedule_2026-02-14.xlsx` (with Phases 5-6)
  - `~/VPMA/exports/project_falcon/raid_log_2026-02-14.pdf` (with new risks)
  - User downloads these, uploads to SharePoint for stakeholder review
- **Session Logged**: Deep Strategy session recorded in History tab

**Total Time**: 26 minutes (vs. 4+ hours manual - reviewing 5 artifacts, finding all references, updating consistently)

**User Outcome**:
- ✅ All artifacts updated in perfect consistency
- ✅ No missed ripple effects (Charter change propagated everywhere)
- ✅ Ready for stakeholder review (executive sponsor sees complete picture)
- 💰 **3+ hours saved** + higher confidence in data accuracy

---

### 10.5 Implementation Decisions from User Interview

This subsection documents **37 critical implementation decisions** made during a comprehensive user interview conducted on February 13, 2026. These decisions clarify ambiguous requirements, resolve technical tradeoffs, and guide the development team through key architectural and UX choices.

---

#### **Architecture & Data Storage**

**1. Default Landing Tab** ✅
- **Decision**: Artifact Sync (Tab 2)
- **Rationale**: Positions VPMA as daily artifact maintenance tool (reactive use case is primary workflow)
- **Impact**: Users expect to paste meeting notes/transcripts immediately upon opening app

**2. Artifact Storage Model** ✅
- **Decision**: Markdown files only in `~/VPMA/artifacts/*.md` - SQLite stores metadata only (timestamps, references)
- **Rationale**: Human-readable, version control friendly, portable, no lock-in
- **Technical**: Content lives in markdown files, database tracks `last_updated`, `project_id`, `artifact_type`

**3. Anonymization Vault Scope** ✅
- **Decision**: Global vault across all projects
- **Rationale**: Consistent token mappings (same person → same token in all projects, simplifies management)
- **Storage**: Single SQLite table `pii_vault` shared across all projects

**4. Backup Strategy** ✅
- **Decision**: Manual export only (user-initiated from Settings tab)
- **Rationale**: User control, no automated background processes, explicit action
- **Implementation**: [Export Project] button → creates timestamped ZIP file: `~/VPMA/backups/project_name_2026-02-12.zip`

**5. Data Retention** ✅
- **Decision**: Configurable in Settings (e.g., "Keep last 90 days") - auto-delete older sessions
- **Rationale**: User control over data footprint and performance (large session history slows context loading)
- **Technical**: Background task checks session timestamps daily, deletes sessions older than threshold

**6. API Key Storage** ✅
- **Decision**: .env file in project root (plain text)
- **Rationale**: Simple, standard approach for local development tools
- **Security Note**: Future enhancement could use keytar for encrypted storage

---

#### **Privacy & Security**

**7. PII Uncertainty Handling** ✅
- **Decision**: Ask user to review when NER confidence is uncertain
- **Rationale**: Err on side of caution - false positives acceptable, false negatives catastrophic
- **Implementation**: Show preview modal when confidence < 70%, user confirms before sending

**8. Privacy Audit Trail** ✅
- **Decision**: Review log of all anonymized payloads sent to LLM (available in Settings for post-hoc verification)
- **Rationale**: Transparency, user can verify no PII leaked
- **Storage**: Append to `~/VPMA/privacy/audit_log.jsonl` with timestamp

**9. OCR Method** ✅
- **Decision**: Local pytesseract (privacy-preserving, no cloud upload)
- **Rationale**: Maintain privacy guarantee (no image data leaves laptop)
- **Use Cases**: Calendar screenshots in Daily Planner, Slack thread screenshots in Artifact Sync

---

#### **UX & Interaction Design**

**10. Bubble Click Behavior** ✅
- **Decision**: Show preview modal, then update database on user confirmation (hybrid approach)
- **Rationale**: User reviews change → confirms → commits to VPMA SQLite (balance between speed and control)
- **Flow**: Click bubble → Preview modal opens → [Apply] button → Update artifact markdown + SQLite metadata → Success toast

**11. Multi-Project UI** ✅
- **Decision**: Single project MVP, Phase 2 adds dropdown in header for quick switching
- **Rationale**: Simplifies Phase 1 development, most PMs start with 1 project, easy to add later
- **Future**: Dropdown selector in app header: "Current Project: [Alpha ▼]"

**12. Persona Selection** ✅
- **Decision**: Fully automatic - agent selects from personas enabled in Settings (all enabled by default)
- **Rationale**: Reduces cognitive load, LLM determines required role based on task type
- **User Control**: Settings tab allows disabling specific personas (e.g., turn off BA if not relevant)

**13. Onboarding** ✅
- **Decision**: Guided wizard (API keys → test connection → first project → configure landscape → sample artifact sync)
- **Rationale**: Reduces setup friction, validates configuration before user starts
- **Steps**: Welcome → Enter API keys → Test connectivity → Create project → Pre-populate landscape → Walk through first sync

**14. Confidence Score Display** ✅
- **Decision**: Only show when low (<70%) - don't clutter UI when LLM is confident
- **Rationale**: Reduces UI noise, highlights risky updates only
- **Visual**: "⚠ Low Confidence" badge on bubble when score < 70%

**15. Discrepancy Warnings** ✅
- **Decision**: Show subtle footer when LLM deviates from user request
- **Rationale**: Transparency, catches hallucinations or misinterpretations
- **Display**: "⚠ Note: This update may deviate from your original request. Review carefully."

**16. Landscape Retroactive Changes** ✅
- **Decision**: No - changes apply going forward only, past sessions preserved as-is
- **Rationale**: Historical integrity (don't rewrite history), simpler implementation
- **User Communication**: Show notice: "Landscape changes apply to future sessions only"

**17. Keyboard Shortcuts** ✅
- **Decision**: Not in MVP, add based on user feedback in later phases
- **Rationale**: Reduces scope, most users comfortable with mouse/click in early adoption
- **Future**: Common shortcuts (Cmd+Enter to sync, Cmd+K for communications assistant)

**18. Dark Mode** ✅
- **Decision**: Light mode only for MVP, defer dark mode to later phases
- **Rationale**: Reduces design/development scope, light mode sufficient for tech-savvy early adopters
- **Future**: Add dark mode toggle in Phase 3 based on user requests

**19. Demo Mode** ✅
- **Decision**: No demo mode, use guided wizard on real project (learn by doing)
- **Rationale**: Real data immediately useful, avoids confusion between demo and real projects
- **Alternative**: Guided wizard provides safe, step-by-step introduction

---

#### **Features & Capabilities**

**20. Versioning** ✅
- **Decision**: Simple "Undo" button per artifact (one-level rollback only, covers 90% of needs)
- **Rationale**: Full version history adds complexity, most users only need immediate undo
- **Future**: Phase 2 adds full version history UI (view/restore all past versions)

**21. Context Window Control** ✅
- **Decision**: User controls via History slider (0-50 sessions) - maximum flexibility per session
- **Rationale**: User decides context vs. cost tradeoff (more context = higher token count = higher cost)
- **Display**: "Context Depth: 10 sessions • ~8,500 tokens loaded"

**22. Export Formats** ✅
- **Decision**: All 4 for MVP (Markdown, DOCX, PDF, Plain Text) - complete flexibility
- **Rationale**: Users have varying artifact destinations (Google Docs, Confluence, email, Jira)
- **Implementation**: python-docx (DOCX), reportlab (PDF), native (MD/TXT)

**23. Daily Planner Image Support** ✅
- **Decision**: Yes, with OCR via pytesseract (calendar screenshot upload)
- **Rationale**: Many users screenshot calendar instead of copy/paste text
- **Flow**: Upload image → pytesseract OCR → text extracted → processed like text calendar input

**24. Landscape Initialization** ✅
- **Decision**: Pre-populated with 8-10 smart defaults (common artifacts + typical meetings)
- **Rationale**: Reduces setup time, user edits as needed rather than building from scratch
- **Defaults**: RAID Log, Status Report, Meeting Notes, Charter, Schedule, PRD, Action Items, Decision Log

**25. Artifact Import** ✅
- **Decision**: Manual paste only for MVP (user copies text from Google Docs/Confluence, pastes into VPMA)
- **Rationale**: Simplifies Phase 1, avoids Google Docs API / Confluence API integration complexity
- **Future**: Phase 2+ adds URL import, Google Docs integration

**26. GitHub Integration (MVP)** ✅
- **Decision**: Markdown-formatted task list (copy-to-clipboard, manual issue creation)
- **Rationale**: Avoids GitHub API complexity in Phase 1, still provides value (structured task suggestions)
- **Output Format**:
  ```markdown
  ## New GitHub Tasks Suggested:
  **Task 1: Implement user authentication refactor**
  - Description: [detailed description]
  - Labels: enhancement, backend
  - Assignee: @john
  ```
- **Future**: Phase 2+ adds GitHub API for direct issue creation/updates

**27. Meeting Transcript Processing** ✅
- **Decision**: Generate ALL 4 outputs when transcript detected:
  1. Meeting Notes artifact (structured with attendees, decisions, action items)
  2. Artifact update suggestions (RAID, Status, Decision Log, Action Items)
  3. GitHub task suggestions (new + existing task notes)
  4. Technical Fluency Translation (if toggle enabled)
- **Rationale**: Transcripts are rich data source, maximize value extraction
- **Detection**: LLM identifies via speaker labels, timestamps, conversational format

**28. Technical Fluency Translation** ✅
- **Decision**: Session-level toggle in app header (quick-access switch visible on all tabs) + default setting in Settings tab
- **Rationale**: Some sessions benefit (technical architecture review), others don't (status update meeting)
- **Output**: Collapsible "🎓 Technical Translation" section with 3-5 bullet points explaining technical concepts in PM-friendly language
- **Use Case**: "Refactor monolith to microservices" → "Break single app into smaller, independent services for faster future changes"

**29. Communications Assistant Context** ✅
- **Decision**: AUTOMATIC CONTEXT SHARING - reads current project/session context (knows what user is working on)
- **Rationale**: Provides relevant communication drafts without user manually copying context
- **Context**: Current project name, active artifacts, recent session summary
- **Privacy**: Anonymize context + user input → LLM → Re-identify output

**30. Persistent Feedback Box** ✅
- **Decision**: Ever-present feedback collection with intelligent categorization, logged to `~/VPMA/feedback/feedback_log.md`
- **Rationale**: Capture feedback as it occurs, independent of project/session (app-level improvement)
- **UI**: Small button fixed to bottom-right, modal with type selection (Bug/Feature/UX/General)

**31. Extensibility** ✅
- **Decision**: Phase 3+: Custom artifact templates (users define new artifact types with custom structure)
- **Rationale**: Covers 80% of needs with 15 built-in artifact types, custom templates for edge cases
- **Future**: No full plugin API in roadmap (adds architectural complexity)

---

#### **Technical Implementation**

**32. UI Framework** ✅ **[CRITICAL DECISION]**
- **Decision**: React + Electron from start (NOT Streamlit)
- **Rationale**: Production-grade UX, component ecosystem, desktop integration, maintainable codebase for long-term evolution
- **Impact**: MVP timeline increases from 2 months (Streamlit) to 4-6 months (React/FastAPI), but provides better foundation
- **Tech Stack**:
  - **Frontend**: React 18+, TypeScript, Material-UI (or Tailwind CSS), Redux for state management
  - **Backend**: Python FastAPI (localhost:8000), REST API, async LLM processing, CORS middleware
  - **Desktop**: Electron wrapper for native features (file system, system tray, notifications)

**33. Backend Architecture** ✅
- **Decision**: Python FastAPI - REST API for LLM integration, Privacy Proxy, document parsing
- **Rationale**: Keeps Python ecosystem (spaCy, python-docx, LLM SDKs), modern async framework, fast
- **API Communication**: Axios (React) ↔ FastAPI (JSON REST endpoints)

**34. Analytics** ✅
- **Decision**: Anonymous local logs (no external sending) - track usage, errors in `~/VPMA/analytics/`
- **Rationale**: Improve product based on usage patterns, maintain privacy (data never leaves laptop)
- **Logged**: Feature usage counts, session durations, error rates, LLM call metadata (all anonymous, no PII)

**35. Collaboration** ✅
- **Decision**: Single-user tool only (never multi-user, no real-time collaboration planned)
- **Rationale**: Simplifies architecture (no auth, permissions, sync conflicts), serves solo PM use case
- **Export**: User can export artifacts to share via email/Slack, not in-app collaboration

---

#### **Error Handling & Performance**

**36. LLM API Failures** ✅
- **Decision**: Offer to switch LLM (Claude ↔ Gemini) when API calls fail repeatedly
- **Rationale**: Smart fallback, leverages dual-brain architecture, provides resilience
- **Flow**: Attempt 1 fails → Retry (exponential backoff) → Attempt 2 fails → Prompt: "Claude API unavailable. Switch to Gemini?"

**37. Deep Strategy Performance** ✅
- **Decision**: No strict target, show progress bar ("Pass 1/4...", could take 2-10 minutes)
- **Rationale**: Multi-pass reasoning is intentionally thorough, user expectations matter more than speed
- **Display**: "Deep Strategy in progress... Pass 2 of 4: Identifying inconsistencies..."

---

#### **MVP Scope & Development Methodology** (v1.2 Decisions)

**38. Phase 0 Foundation MVP Scope** ✅ **[CRITICAL DECISION]**
- **Decision**: Strip MVP to minimum viable flow: text input → artifact suggestions → copy-to-clipboard. No screenshots, no wizard, no suggested artifacts, no deep planning, no daily planning.
- **Rationale**: Validates core value proposition in 4 weeks instead of 4-6 months. Faster learning, lower risk.
- **Impact**: Proves "does this save me time?" before investing in full feature set

**39. Simplified Tech Stack for MVP** ✅ **[CRITICAL DECISION]**
- **Decision**: JavaScript React (not TypeScript), Tailwind CSS (not Material-UI), useState/useContext (not Redux), browser tab (not Electron)
- **Rationale**: Novice developer using AI-assisted coding — simpler stack = faster iteration, fewer confusing errors. Each technology layer added only when complexity justifies it.
- **Cost to Upgrade Later**: TypeScript (1-2 days), Redux (1-2 days), Electron (2-3 days), MUI (2-3 days) — total ~8-10 days when needed
- **Impact**: Reduces Phase 0 from 16-24 weeks to 4 weeks

**40. Development Methodology: RALPH + Claude Code** ✅
- **Decision**: AI-assisted development using Claude Code CLI + RALPH loop technique (iterative task completion)
- **Rationale**: Developer is novice programmer — RALPH automates code generation while human guides, reviews, and tests
- **Workflow**: ~20 discrete tasks per phase, human-in-the-loop, commit after each task
- **Impact**: Enables novice to build production-quality application; estimated 50-70 keyboard hours for Phase 0

**41. Local LLM via Ollama (Phase 2)** ✅
- **Decision**: Add Ollama as third LLM provider (alongside Claude and Gemini) in Phase 2, using existing abstract LLM client interface
- **Rationale**: Zero cost ($0/month), zero privacy risk (no data leaves machine), good enough quality for routine artifact sync on M4 24GB hardware
- **Recommended Model**: Llama 3.1 8B (~40-60 tok/s on M4, ~5GB RAM)
- **Architecture**: OllamaClient adapter implementing same `call()`/`stream()` interface — trivial to add thanks to Phase 0 foundation #1

**42. Commercial Readiness Phase (Phase 4)** ✅
- **Decision**: Consolidate security, web deployment, auth, integrations, and HR capacity planning into a dedicated "Commercial Readiness" phase
- **Rationale**: Keeps personal-use features (Phases 0-3) separate from commercial features (Phase 4). Can stop after Phase 3 with a fully functional personal tool.
- **Key Components**: Keychain storage, Presidio anonymization, Google OAuth (Firebase Auth), Slack/Gmail/Jira APIs, HR capacity planning module

**43. Web App Authentication Method** ✅
- **Decision**: Google OAuth via Firebase Auth (free tier)
- **Rationale**: Zero-friction login (users already have Google accounts), Firebase handles token management/session refresh/account recovery, free for individual use
- **Alternative**: Auth0 if multi-provider auth needed later (Google + GitHub + email/password)
- **Architecture Enabler**: React + FastAPI separation already supports this — deploy FastAPI to cloud, React as static build

**44. HR Capacity Planning Module** ✅
- **Decision**: Add as new feature in Phase 4 — resource entry, intelligent allocation recommendations, bottleneck detection
- **Rationale**: Natural extension of PM assistant capabilities; leverages existing project data (Charter, Schedule, PRD) for intelligent analysis
- **LLM Usage**: LLM analyzes project scope + resource pool → recommends allocation, identifies over-allocation, suggests what-if scenarios

**45. Technical Debt Prevention Architecture** ✅
- **Decision**: Invest ~8-12 extra hours in Phase 0 for 5 specific architectural foundations (abstract LLM client, project-scoped data, modular privacy proxy, environment config, input type detection)
- **Rationale**: Prevents ~4-6 weeks of future refactoring when adding local LLM, multi-project, web deployment, integrations, and image support
- **ROI**: ~4 hours invested now saves ~160+ hours of refactoring later

---

#### **Summary: Impact on PRD**

These 45 decisions fundamentally shape VPMA's implementation:

**Highest Impact (v1.2)**:
- **#38 (Phase 0 MVP scope)**: Validates core hypothesis in 4 weeks instead of 4-6 months
- **#39 (Simplified tech stack)**: Enables novice developer to build and ship quickly
- **#41 (Local LLM)**: Zero-cost, zero-privacy-risk option for routine operations
- **#45 (Debt prevention)**: 8-12 hours investment prevents 4-6 weeks of future refactoring

**Highest Impact (v1.1)**:
- **#32 (React/FastAPI)**: Production-grade architecture from start, enables all future features
- **#2 (Markdown storage)**: Simplifies artifact handling, enables version control
- **#10 (Bubble behavior)**: Defines core interaction pattern for Artifact Sync
- **#27 (Transcript processing)**: Maximizes value from most common input type

**User Experience**:
- Decisions #10-19 define entire UX philosophy (automatic personas, minimal UI clutter, confidence scores, onboarding wizard)

**Privacy**:
- Decisions #3, #7-9, #41 ensure bulletproof privacy guarantee (global vault, OCR local, audit trail, local LLM option)

**Development Strategy**:
- Decisions #38-40, #45 define how VPMA gets built: lean MVP, simplified stack, AI-assisted development, debt-preventing foundations

**Scope Management**:
- Decisions #20, #25, #26, #31, #42 organize features into clear phases (personal tool Phases 0-3, commercial Phase 4)

---

### 10.6 Development Methodology & Implementation Estimates

This section documents the planned development approach, estimated effort, and cost projections for building VPMA. These estimates reflect a **novice programmer** working primarily through **AI-assisted development** (Claude Code + RALPH loop technique).

---

#### Development Approach: Claude Code + RALPH

**RALPH** (Ralph Wiggum loop) is an iterative AI development methodology where a simple loop repeatedly feeds a prompt to an AI coding agent (Claude Code) until a task is complete. Instead of spending time crafting perfect prompts, the technique leans into rapid iteration — Claude writes code, runs tests, fixes errors, and commits, all in a loop.

**Core Pattern**:
```bash
#!/bin/bash
# ralph-vpma.sh — Run one RALPH task
claude --permission-mode acceptEdits \
  "@PRD.md @progress.txt \
  Read the PRD and progress file. \
  Find the next incomplete task and implement it. \
  Write tests for what you build. \
  Commit your changes with a descriptive message. \
  Update progress.txt with what you completed. \
  ONLY DO ONE TASK AT A TIME."
```

**Workflow**:
1. Break each phase into ~15-25 discrete RALPH tasks (specific, testable, independent)
2. Run RALPH per-task (not per-phase — too broad for reliable loops)
3. **Human-in-the-loop mode** for Phase 0-1 (watch output, provide feedback, learn codebase)
4. Graduate to supervised autonomous mode in later phases (run 2-3 tasks unattended)
5. Commit after each successful task — git is the safety net
6. Manual integration testing between related tasks

**Where RALPH excels** (automate these):
- React component creation (spec → component)
- FastAPI endpoint implementation (schema → endpoint)
- Database CRUD operations
- Unit tests for individual modules
- CSS/Tailwind styling
- Error handling patterns
- Documentation generation

**Where RALPH struggles** (requires human guidance):
- Complex multi-file integration (needs human oversight)
- Prompt engineering for VPMA's artifact detection quality (iterative, subjective)
- Environment/API key configuration (first-time setup)
- Debugging CORS issues between React and FastAPI (common, confusing for novice)
- Security hardening and privacy testing with real data
- Git workflow management (branching, merge conflicts)

---

#### Phase 0 RALPH Task Decomposition (~20 tasks)

```markdown
## Phase 0: Foundation MVP — RALPH Tasks

### Infrastructure (Tasks 1-4)
- [ ] Project scaffolding (React app via create-react-app, FastAPI skeleton, folder structure, .env template)
- [ ] SQLite database setup (schema with all 6 tables including project_id on everything, connection module, basic queries)
- [ ] Privacy Proxy module — regex PII detection patterns (email, phone, URL, custom terms)
- [ ] Privacy Proxy module — spaCy NER integration (en_core_web_sm, PERSON/ORG/GPE detection)

### Privacy & LLM (Tasks 5-8)
- [ ] Privacy Proxy module — vault (store/retrieve token mappings in SQLite, anonymize/reidentify functions)
- [ ] LLM Client — base abstract interface (call, call_structured, count_tokens methods)
- [ ] LLM Client — Claude API adapter (Anthropic SDK)
- [ ] LLM Client — Gemini API adapter (Google AI SDK)

### Backend Logic (Tasks 9-12)
- [ ] Artifact Manager — artifact type definitions + 3 templates (RAID Log, Status Report, Meeting Notes)
- [ ] Artifact Sync — backend logic (input → Privacy Proxy → LLM → parse response → suggestions)
- [ ] Artifact Sync — system prompts for artifact detection and delta extraction
- [ ] FastAPI endpoints (POST /api/artifact-sync, GET /api/settings, POST /api/settings, GET /api/health)

### Frontend (Tasks 13-17)
- [ ] React — App shell with two-tab nav (Artifact Sync + Settings)
- [ ] React — Text input component with submit button and loading state
- [ ] React — Suggestion cards component with expandable preview and copy-to-clipboard
- [ ] React — Basic Settings page (API key inputs, LLM provider toggle, custom sensitive terms)
- [ ] React — Error handling (API failure messages, empty states, loading spinners)

### Integration & Polish (Tasks 18-20)
- [ ] End-to-end integration test (paste text → anonymize → LLM → reidentify → display suggestions → copy)
- [ ] Prompt quality tuning (test with 5+ real meeting notes samples, refine system prompts)
- [ ] Basic styling with Tailwind + error handling polish
```

---

#### Keyboard Time Estimates

"Keyboard time" for a novice using Claude Code + RALPH: writing prompts, reviewing AI output, testing, providing feedback, debugging. **You will not write much code yourself** — Claude Code writes it, you guide and verify.

| Phase | Calendar Time | Keyboard Hours | Activity Breakdown |
|-------|--------------|----------------|-------------------|
| **Phase 0** (Foundation MVP) | 4 weeks | 50-70 hrs | 40% reviewing code, 25% testing, 20% writing prompts, 15% debugging |
| **Phase 1** (Core Experience) | 6-8 weeks | 80-120 hrs | Similar split, more prompt engineering for artifact quality |
| **Phase 2** (Intelligence + Local LLM) | 8-10 weeks | 100-140 hrs | More complex features, more debugging/integration testing |
| **Phase 3** (Proactive Features) | 8-10 weeks | 100-140 hrs | More UI work, API integrations (Calendar, OCR) |
| **Phase 4** (Commercial Readiness) | 8-12 weeks | 120-180 hrs | Security/auth/infra — most complex, needs careful testing |
| **Total** | **~12-16 months** | **~450-650 hrs** | Spread across active development periods |

**Where you'll need the most human guidance** (not RALPH-automatable):
1. **Environment setup** (day 1) — installing Python, Node.js, dependencies, API keys
2. **CORS debugging** — React → FastAPI cross-origin issues (universal first-time pain point)
3. **Prompt engineering** — tuning VPMA's system prompts for artifact detection quality
4. **Privacy Proxy testing** — validating PII detection with real meeting data
5. **Git workflow** — managing commits, branches, recovering from mistakes
6. **API authentication** (Phase 4) — OAuth flows for Slack, Gmail, Jira
7. **Cloud deployment** (Phase 4) — server configuration, environment variables, DNS

---

#### Token Estimates (Claude Code Usage for Building VPMA)

These estimate **tokens consumed by Claude Code while building VPMA** (not tokens consumed by VPMA when running for users):

| Phase | Estimated Token Usage | Claude Max $100/mo | Claude Max $200/mo |
|-------|----------------------|--------------------|--------------------|
| **Phase 0** (Foundation MVP) | 3-6M tokens | ~3-4 weeks of plan | ~2-3 weeks of plan |
| **Phase 1** (Core Experience) | 6-10M tokens | ~6-8 weeks | ~4-5 weeks |
| **Phase 2** (Intelligence) | 5-10M tokens | ~5-8 weeks | ~3-5 weeks |
| **Phase 3** (Proactive) | 6-12M tokens | ~6-10 weeks | ~4-6 weeks |
| **Phase 4** (Commercial) | 8-15M tokens | ~8-12 weeks | ~5-8 weeks |
| **Total** | **~28-53M tokens** | **~7-10 months** | **~4-6 months** |

**Key factors affecting token usage**:
- **RALPH loops burn tokens fast**: Each iteration is ~30-100K tokens (prompt + context + response)
- **Novice developer = more iterations**: Better prompts come with experience, reducing waste over time
- **Phase 0 is most token-efficient**: Simpler tasks, shorter context
- **Phase 4 is least token-efficient**: Security/auth/deployment involve complex debugging
- **Recommendation**: Claude Max $200/month plan for comfortable RALPH loops without hitting limits

**Token usage for running VPMA** (after it's built — user-facing costs):

| Operation | Tokens Per Use | Cost (Claude API) | Local LLM Cost |
|-----------|---------------|-------------------|----------------|
| Artifact Sync (one paste) | ~2K-5K tokens | ~$0.01-0.05 | Free |
| Deep Strategy (multi-pass) | ~15K-40K tokens | ~$0.10-0.50 | Free (slower) |
| Daily Planner | ~5K-10K tokens | ~$0.03-0.10 | Free |
| Communications Assistant | ~500-1K tokens | ~$0.005 | Free |
| **Daily usage (heavy PM)** | ~20K-60K/day | ~$0.15-0.75/day | Free |
| **Monthly usage** | ~500K-1.5M/month | ~$3-15/month | Free |

With local LLM (Phase 2+): **$0/month** for routine operations, API only for complex tasks.

---

#### Technical Debt Prevention: 5 Architectural Foundations

These are built into Phase 0 at ~8-12 hours of extra effort, preventing weeks of refactoring later:

| Foundation | What It Is | Extra Cost Now | Future Feature It Enables | Refactoring Cost if Skipped |
|-----------|-----------|---------------|--------------------------|---------------------------|
| **1. Abstract LLM Client** | Base class with `call()`/`stream()` + provider adapters | ~1 hour | Local LLM (Ollama), any future provider | 3-5 days |
| **2. Project-Scoped Data** | `project_id` on all DB tables + file paths, even with 1 project | ~30 min | Multi-project support | 1-2 weeks (data migration) |
| **3. Modular Privacy Proxy** | Clean interface: `anonymize(text)` → `reidentify(text, vault)` | ~30 min | Commercial-grade Presidio, encrypted vault | 2-3 days |
| **4. Environment Config** | All URLs, keys, paths from `.env` (no hardcoded localhost) | ~30 min | Web deployment, cloud hosting | 1-2 weeks (find/replace everywhere) |
| **5. Input Type Detection** | Backend classifies input (text, transcript, future: image) | ~1 hour | OCR, multimodal LLM, image parsing | 2-3 days |

**Total prevention cost**: ~4 hours of intentional architecture
**Total debt prevented**: ~4-6 weeks of future refactoring

---

#### Commercialization Considerations (Low-Effort, High-Optionality)

These decisions are already built into the architecture or require minimal extra effort, keeping the door open for future commercialization without investment now:

1. **React + FastAPI separation** (already done): Backend can be deployed to cloud, frontend as static build — no rewrite needed for web app
2. **Environment-based config** (Phase 0 foundation): Switch from localhost to production URLs by changing `.env` only
3. **Google OAuth** (Phase 4): Firebase Auth free tier gives Google sign-in with ~50 lines of code
4. **Per-user data isolation** (Phase 4): Add `user_id` column to existing `project_id`-scoped tables — straightforward migration
5. **Anonymous local analytics** (already in PRD): Usage data for product decisions when evaluating market fit
6. **Configurable data directory** (Phase 0): Don't hardcode `~/VPMA/` — use config variable so multi-user deployment can set per-user paths

---

## Document Status

**Current Version**: v1.2 - Phase 0 MVP + Implementation Estimates + Local LLM + Commercial Readiness

**Revision History**:
| Version | Date | Changes |
|---------|------|---------|
| v1.0 | February 14, 2026 | Initial PRD - All 10 sections finalized |
| v1.1 | February 14, 2026 | Architecture update (Streamlit → React/FastAPI), 37 implementation decisions from user interview added (Section 10.5), roadmap timeline updated (4-6 month MVP) |
| v1.2 | February 14, 2026 | Phase 0 Foundation MVP (4-week lean validation), simplified tech stack for MVP (JS React, Tailwind, no TS/Redux/Electron/MUI), Local LLM via Ollama (Phase 2), RALPH development methodology + implementation estimates (Section 10.6), 5-phase rollout replacing 4-phase, Phase 4 becomes Commercial Readiness (security, web auth, integrations, HR planning), 8 new implementation decisions (#38-45), technical debt prevention architecture, commercialization considerations |

**Completion Status**:
- ✅ **Section 1**: Executive Summary (updated v1.2 - development approach overview, triple-brain toggle)
- ✅ **Section 2**: Problem Statement & Market Context (complete)
- ✅ **Section 3**: Goals & Success Metrics (complete)
- ✅ **Section 4**: User Experience Design - The Six-Tab System (complete - 6 tabs + 2 cross-tab features)
- ✅ **Section 5**: Technical Architecture (updated v1.2 - progressive tech stack, Ollama client, local LLM quality/speed tables)
- ✅ **Section 6**: Artifact Landscape & Content Model (complete - 15 artifact types, templates, interdependencies)
- ✅ **Section 7**: Roadmap & Phasing (updated v1.2 - 5-phase rollout with Phase 0 Foundation MVP, Phase 4 Commercial Readiness)
- ✅ **Section 8**: Success Criteria & Measurement (updated v1.2 - Phase 0 validation metrics, phase numbering aligned)
- ✅ **Section 9**: Risks & Mitigation (complete - 12 risks across technical/product/operational/business dimensions)
- ✅ **Section 10**: Appendices (updated v1.2 - Section 10.5: 45 implementation decisions, Section 10.6: development methodology + estimates)

**v1.2 Key Changes**:
- **Phase 0 Foundation MVP**: New 4-week lean validation phase (text → suggestions → copy) with simplified tech stack
- **Simplified Tech Stack**: JS React + Tailwind CSS + useState (no TypeScript, Redux, Electron, Material-UI in MVP)
- **Local LLM**: Ollama integration (Phase 2) with Llama 3.1 8B recommended for M4 24GB hardware
- **5-Phase Rollout**: Phase 0 (Foundation) → Phase 1 (Core) → Phase 2 (Intelligence + Local LLM) → Phase 3 (Proactive) → Phase 4 (Commercial)
- **Phase 4 Commercial Readiness**: Keychain storage, Presidio, Google OAuth, Slack/Gmail/Jira integrations, HR capacity planning
- **Section 10.6**: New appendix with RALPH methodology, 20-task Phase 0 decomposition, keyboard time estimates, token cost projections, debt prevention architecture, commercialization considerations
- **Section 10.5**: 8 new implementation decisions (#38-45) covering MVP scope, simplified stack, RALPH, local LLM, commercial phase, auth, HR, debt prevention
- **Technical Debt Prevention**: 5 architectural foundations (abstract LLM client, project-scoped data, modular privacy, env config, input type detection) — ~8-12 hours extra in Phase 0, prevents ~4-6 weeks future refactoring

---

*End of VPMA Vision Product Requirements Document*

---

**Document Prepared By**: VPMA Product Team
**Version**: 1.2 (Phase 0 MVP + Implementation Strategy)
**Date**: February 14, 2026
**Status**: Ready for Phase 0 Development

**Next Steps**:
1. **Set up development environment**: Install Node.js, Python 3.10+, create-react-app, FastAPI, SQLite, Ollama (for future testing)
2. **Configure Claude Code + RALPH**: Set up RALPH loop script with Phase 0 task decomposition (Section 10.6)
3. **Phase 0 Kickoff**: Begin Foundation MVP development (~20 RALPH tasks, 4-week target)
4. **Personal validation**: Use Phase 0 MVP daily for 1 week to validate "does this save me time?"
5. **Phase 1 planning**: Based on Phase 0 learnings, refine Phase 1 scope and recruit 5 beta testers
