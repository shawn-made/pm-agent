# Data Lakehouse Project — Project Plan

**Version**: 1.0 (Draft)
**Date**: February 17, 2026
**Author**: Company_480_B (Project Manager)
**Charter Reference**: [PROJECT_CHARTER.md](PROJECT_CHARTER.md)
**Status**: Draft — In Review (sent to Architect + Reporting Mgr 2/18)
**Current As Of**: 2026-02-25 (added baseline resource allocation reference)

---

## 1. Overview

This project plan details the approach, timeline, and execution strategy for the Data Lakehouse Project. It builds on the Project Charter (which defines scope, objectives, and governance) and provides the operational roadmap for the project team.

The Data Lakehouse Project is part of a broader technology program that also includes Salesforce/CRM work. Both projects share program leadership and executive sponsorship but currently operate with limited hard dependencies. This plan covers the Data Lakehouse Project only.

**How this plan relates to other project artifacts:**

| Artifact | Purpose | Maintained By |
|----------|---------|---------------|
| **Project Charter** | Scope, objectives, milestones, governance. Static — changes via change request. | PM |
| **This Project Plan** | Approach, workstream detail, methodology, timeline. Updated periodically at phase boundaries. | PM |
| **GitHub Projects Board** | Day-to-day work tracking, sprint backlogs, individual tickets | PM + Team |
| **Risk Register** | Active risks, severity, mitigation plans | PM |
| **ERA Backlog** | Prioritized report backlog with status and dependencies | PM + ERA Lead |

This plan is a **guiding document** — it shows the team's approach and grounds execution. It is not a substitute for the day-to-day work tracked in GitHub or the active risk management in the Risk Register.

---

## 2. Program Context

### Where We've Been

The Data Lakehouse project has been running since early 2024. Key context for understanding the current plan:

- **Pre-Phase 1 (Early–Mid 2024)**: Grant secured, consulting firm engaged, discovery and architecture planning
- **Phase 1 Start (Oct 2024)**: Development begins on Snowflake data lakehouse; scope narrowed to Colleague, PowerCampus, Salesforce EDA, and TargetX
- **Phase 1 Challenges (2025)**: Colleague data complexity, Dynamic Tables crisis, consulting transitions, RIF impact, production deployment backed out
- **Phase 1 Reset (Nov 2025–Present)**: Team stabilized around current Lead Architect (independent consultant), re-engagement focused on completing the SIS data model and delivering ERA reports
- **Phase 2 Start (Jan 2026)**: New BA + Developer onboarded for StarRez and PowerFAIDS ingestion, running in parallel with Phase 1 completion

### Where We're Going

The program has three horizons:

1. **Near-term (Now – Jun 2026)**: Complete the current-state data platform — deliver the ERA report backlog against Colleague/PowerCampus/StarRez/PowerFAIDS data, freeze current-state reports
2. **Medium-term (2026 – 2027)**: Integrate Workday Student data into the platform — discover, ingest, model, and rebuild reports against the new SIS
3. **Long-term (2027+)**: Operate a production data platform on Workday Student; retire Colleague/PowerCampus data models; expand to deferred scope items

---

## 3. Workstreams

The program is organized into five concurrent workstreams. Each workstream has a distinct scope but shares resources and dependencies with the others.

### 3.1 Phase 1 Completion: SIS Data Model & Core Reports

**Objective**: Complete and validate the Colleague/PowerCampus data model; deliver the core ERA report backlog.

**This is the current critical path.** All downstream ERA reports are gated by the All Active Report validation, which establishes the foundation data model that other reports build on.

#### Scope
- College All Active Report (Colleague)
- Conservatory All Active Report (PowerCampus)
- Registration/Enrollment w/ Demographics (College & Conservatory)
- Net Tuition Revenue / NTR (College & Conservatory)
- Restrictions Report (College)
- Graduation Report (College)

#### Approach
Each report follows a standard delivery lifecycle:

```
Discovery → Data Ingestion → Development/Modeling → Validation → UAT → Delivery
```

- **Discovery**: Confirm data sources, business rules, field mappings, and acceptance criteria with ERA and SMEs
- **Data Ingestion**: Ensure required source data flows through the pipeline (Raw → Cleansed → Modelled → Datamart)
- **Development/Modeling**: Build or extend the Gold layer data model and Datamart views
- **Validation**: Compare Snowflake outputs against Informer baselines; resolve discrepancies
- **UAT**: ERA team confirms the report meets their needs
- **Delivery**: Tableau dashboard published and accessible

**Validation philosophy**: Discrepancies between Snowflake and Informer are expected and often reflect the Snowflake platform being *more correct* (e.g., better deduplication, consistent logic). Each discrepancy is investigated, categorized (pipeline issue vs. source data issue), and documented. The 95% accuracy threshold (excluding some key critical fields, reviewed on a case by case basis, which may require higher accuracy) is the current pragmatic target for All Active.

**Example — Deduplication (confirmed 2/21)**: When a student exists in both Colleague and PowerCampus, Snowflake deduplicates and uses the most-recently-enrolled system's demographics (~8-10 fields affected). Informer, built only on PowerCampus data, shows different values for these students. This is a positive architectural outcome — the platform prioritizes current student data (e.g., preferred names) — and is being presented to ERA as a trust-building story.

#### Key Dependencies
- Colleague SME**: Required for Informer report creation and Colleague business rules. Single point of dependency.
- **Lead Architect**: Primary validator for data model correctness.
- **Colleague Dev Team**: Required for NTR — charge/financial fields must be made available before NTR work can proceed.
- **ERA Team**: Defines requirements, accepts deliverables.

#### Target Timeline

| Activity | Target Period | Notes |
|----------|--------------|-------|
| College All Active validation | Jan – Mar 2026 | Critical path. In progress. 95% accuracy target. |
| Conservatory All Active validation | Mar 2026 | Dev resource assigned to work in parallel with College |
| College Registration/Enrollment w/ Demographics | Mar – Apr 2026 | Ready for validation; pending team capacity |
| Conservatory Registration/Enrollment w/ Demographics | Apr 2026 | Follows College version |
| NTR Data Ingestion | Mar – Apr 2026 | Blocked on Colleague Dev team for charge/financial fields |
| College NTR Report | Apr – May 2026 | Requires NTR data ingestion complete |
| Conservatory NTR Report | May 2026 | Follows College version |
| Discovery: Restrictions & Graduation | Apr – May 2026 | Discovery to determine scope and complexity |
| Restrictions Report | May – Jun 2026 | |
| Graduation Report | Jun 2026 | |
| **Current-State Scope Freeze (M6)** | **Jun 2026** | All current-state ERA reports delivered; platform stabilized |

---

### 3.2 Phase 2: New Source Ingestion (StarRez & PowerFAIDS)

**Objective**: Ingest StarRez (housing) and PowerFAIDS (financial aid) data into the Snowflake platform at the Bronze layer; validate and prepare for ERA reporting.

**This workstream is intentionally decoupled from the Phase 1 critical path.** The new BA + Developer team (onboarded Jan 2026) leads this work independently, with architectural oversight from the Lead Architect.

#### Scope
- StarRez: Housing registration data (room assignments, housing status, occupancy)
- PowerFAIDS: Financial aid data (FAFSA filing, student attributes, award amounts, package dates)

#### Approach
Each source follows the same lifecycle:

```
Discovery → Access/Ingestion Approach → Bronze Layer Ingestion → Validation → Gold Layer Modeling (future)
```

- **Discovery**: Understand source system schema, key tables, business rules, data volumes
- **Access/Ingestion Approach**: Establish secure connections, define SnapLogic pipeline design, address security requirements (PII masking, RBAC)
- **Bronze Layer Ingestion**: Land data in Snowflake Raw layer via SnapLogic → S3 → Snowpipe
- **Validation**: Confirm data completeness and accuracy at Bronze layer

Gold layer modeling and ERA reporting (e.g., fall room allocation report, affordability analysis) will follow in a subsequent cycle once Bronze data is validated.

#### Key Dependencies
- **PowerFAIDS secure connection**: External dependency — SQL Server access/credentialing has been slow due to PII masking and RBAC configuration requirements. The primary technical contact is not a dedicated project resource.
- **PowerFAIDS server load risk**: A server load incident occurred on the PowerFAIDS server (week of 2/10/2026). If the institution determines that data replication to a separate server is needed, this could introduce additional schedule risk.
- **Lead Architect**: Provides architectural guidance and oversight for ingestion design.

#### Target Timeline

| Activity | Target Period | Notes |
|----------|--------------|-------|
| StarRez Discovery | Feb 2026 | **Near-complete** — 14 tables loaded in dev, fall sheet reviewed, preliminary validation starting |
| PowerFAIDS Discovery | Feb 2026 | In progress — some access granted, blocked on open questions with Colleague SME |
| StarRez Ingestion | Mar 2026 | Bronze layer pipeline build |
| PowerFAIDS Ingestion | Mar 2026 | Bronze layer pipeline build; dependent on secure access |
| StarRez Validation | Apr 2026 | Bronze layer data quality check |
| PowerFAIDS Validation | Apr 2026 | Bronze layer data quality check |

---

### 3.3 Salesforce/TargetX Validation

**Objective**: Validate existing Salesforce EDA and TargetX data in the platform; confirm data quality for admissions reporting.

**Status**: Approach TBD. This work was originally in-scope for Phase 1 but was deprioritized during the October 2025 pivot to focus on ERA needs. Some validation occurred in a prior phase but likely not all objects.

#### Scope
- Contact Object (core admissions data)
- Application Object (core admissions data)
- Audition & Interview Object (core admissions data)
- Cases, Contact Schedule Items, Organization Events, Sites & Venues (secondary)

#### Approach
- A representative from the Salesforce team regularly attends standup — this is the coordination channel
- Need to define the validation approach: who owns it, what "validated" means for each object, and how to handle objects with partial prior validation
- This workstream will be staffed and scheduled once the approach is defined

#### Key Dependencies
- Salesforce/CRM team availability for validation support
- Prioritization decision relative to other workstreams

#### Target Timeline
- **Approach definition**: TBD — flagged as open action item
- **Execution**: Timing will be determined after approach is defined and prioritization is confirmed

---

### 3.4 Platform Health & Observability

**Objective**: Establish production-grade infrastructure, monitoring, CI/CD, and data governance for the platform.

#### Scope
- Notification centralization (pipeline alerts and notifications)
- SnapLogic troubleshooting and pipeline reliability
- YAML standardization and production deployment process
- PII data tags and masking policies
- Informer record reconciliation process (ongoing validation tooling)
- Data dictionary creation
- Environment setup (test and production — currently dev only)

#### Approach
This work runs as a background stream alongside the primary report delivery workstreams. Items are tracked in GitHub and prioritized in sprint planning alongside feature work. There is no dedicated team for this — work is absorbed by the existing team as capacity allows.

**Key near-term priority**: Establishing test and production environments as Phase 1 nears completion. The team is currently operating in dev only (production was backed out in Fall 2025).

#### Target Timeline
- Ongoing throughout 2026. Individual items are tracked in GitHub and will be sequenced through sprint planning.
- **Environment setup**: Should be planned for as Phase 1 core reports approach delivery readiness (estimated Q2 2026).

---

### 3.5 Workday Student Integration

**Objective**: Discover, ingest, model, and eventually rebuild the data platform on Workday Student data sources, replacing Colleague/PowerCampus.

**This is the longest-horizon workstream.** It spans from current discovery work through the Workday Student go-live (Fall 2027) and beyond. The work is staged to align with the WDS implementation timeline.

#### Context
- Workday Student replaces both Colleague (College) and PowerCampus (Conservatory) as the institution's SIS
- **WDS code freeze**: ~June 2026 — after this, the WDS configuration is locked and the data lakehouse team can model against a stable schema
- **WDS go-live**: Target Fall 2027
- **Zero Copy Integration**: Confirmed unavailable for this environment (as of Feb 2026)
- **Primary integration path**: RaaS (Reporting as a Service) via SnapLogic → S3 → Snowflake (same pattern as current sources). WQL (Workday Query Language) also being explored as an alternative.
- **Risk**: Data points identified after WDS code freeze may not be available without WDS configuration changes

#### Staged Approach

**Stage 1: Discovery & Mapping (Now – Mar 10, 2026)** — *Charter M7*
- Map current data model entities to WDS equivalents
- Identify data points needed from WDS
- Determine technical integration approach (RaaS/SnapLogic vs. WQL)
- Define data mapping and technical approach
- **Key alignment (confirmed 2/21)**: Data model will NOT retrofit WDS data into Colleague-centric structures. Workday terminology will be adopted in the data lake. CRM/SF file layout being reviewed as cross-reference for field mapping.

**Stage 2: Proof of Concept (Mar – End of Apr 2026)** — *Charter M8*
- Build ingestion POC for WDS data
- Validate technical integration path end-to-end
- Confirm RaaS/SnapLogic or WQL approach works at scale

**Stage 3: Data Modeling & Approval (May – End of Jun 2026)** — *Charter M9*
- Build initial WDS data model
- Review and approve data model, aligned with WDS Scope Freeze (~Jun 2026)
- Begin WDS data pipeline through medallion layers

**Stage 4: Data Modeling, Report Rebuild & Testing (Jul 2026 – 2027)** — *Charter M10*
- Build out WDS data pipeline through medallion layers
- Rebuild ERA reports against WDS data model
- Testing cycles aligned with WDS implementation milestones

**Stage 5: Go-Live & Transition (2027)**
- Deploy rebuilt data platform
- Migrate users from Colleague/PowerCampus reports to WDS reports
- Retire legacy data models

#### Key Dependencies
- **WDS Implementation Team**: Cross-project coordination for data mapping, schema questions, and integration testing. WDS team availability will be limited during their own testing and go-live periods.
- **Lead Architect**: Primary resource for WDS data modeling decisions. Architect's allocation to WDS grows as Phase 1 wraps, but Phase 1 delays compress WDS time.
- **Person_7 (Colleague SME)**: Needed for current-state → future-state mapping (understanding what Colleague data means in business terms to ensure the WDS model captures the same concepts).

#### Target Timeline

| Activity | Target | Charter Milestone | Notes |
|----------|--------|-------------------|-------|
| WDS Discovery Complete — data mapping & technical approach | Mar 10, 2026 | M7 | Define what data is needed and how to get it |
| WDS Technical POC Complete | End of Apr 2026 | M8 | Prove the integration path works end-to-end |
| WDS Data Model Approved | End of Jun 2026 | M9 | Aligned with WDS Scope Freeze (~Jun 2026) |
| Data Modeling, Report Rebuild, Testing | Jul 2026 – 2027 | — | Ongoing through WDS go-live cycle |
| WDS Data Platform Operational | TBD 2027 | M10 | Dependent on WDS implementation schedule (Fall 2027 go-live) |

---

## 4. Integrated Timeline

This view shows all workstreams on a single timeline. Dates are targets as of February 2026.

### Q1 2026 (Jan – Mar)

| Period | Phase 1 (SIS Reports) | Phase 2 (StarRez/PowerFAIDS) | WDS Integration |
|--------|----------------------|------------------------------|-----------------|
| Jan 21 – Feb 4 | College All Active validation | Discovery | |
| Feb 4 – Feb 18 | College All Active validation | Discovery | |
| Feb 18 – Mar 4 | College All Active target completion | Discovery complete | |
| Mar 4 – Mar 18 | Conservatory All Active | Ingestion | **M7: WDS Discovery Complete (3/10)** |

### Q2 2026 (Apr – Jun)

| Period | Phase 1 (SIS Reports) | Phase 2 (StarRez/PowerFAIDS) | WDS Integration |
|--------|----------------------|------------------------------|-----------------|
| Mar 18 – Apr 1 | College Enrollment w/ Demo; NTR Data Ingestion | Ingestion | WDS POC development |
| Apr 1 – Apr 15 | College Enrollment w/ Demo | Validation | WDS POC development |
| Apr 15 – Apr 29 | Conservatory Enrollment w/ Demo; College NTR | | **M8: WDS Technical POC Complete** |
| Apr 29 – May 13 | College NTR; Discovery: Restrictions & Grad | | WDS data modeling |
| May 13 – May 27 | Conservatory NTR; Discovery: Restrictions & Grad | | WDS data modeling |
| May 27 – Jun 10 | Restrictions Report | | WDS data model review |
| Jun 10 – Jun 24 | Graduation Report | | WDS data model review |
| **Jun 24** | **M6: Current-State Scope Freeze** | | **M9: WDS Data Model Approved / WDS Scope Freeze** |

### H2 2026 – 2027

| Period | Activity |
|--------|----------|
| Jul – Dec 2026 | WDS data modeling, ERA report rebuild, testing cycles |
| 2027 | WDS integration testing, go-live preparation, legacy model retirement |
| Fall 2027 | WDS Go-Live (target) |

---

## 5. Methodology

### 5.1 Hybrid Approach

The team follows a **hybrid methodology** adapted to the institution's context. This is the first formal methodology implementation for this institution's data team — the process is still maturing and will evolve.

**Agile elements** (sprint cadence, iterative delivery):
- 2-week sprint cadence provides a clear, repeatable rhythm for the technical team
- Balance of clarity (what is my priority right now?) with agility (if priorities change, we pivot in the next sprint)
- Built-in process for estimating work size and tracking team velocity, providing insight into remaining work

**Waterfall elements** (milestone-driven planning, firm targets):
- Cross-project dependencies (WDS integration, Colleague Dev team) require firm milestone dates and coordination windows that don't shift sprint-to-sprint
- MVP and scope freeze targets (M6, M9) are managed as fixed planning gates — the work within sprints flexes, but the gates hold
- Phase-sequenced delivery (Phase 1 completion before Phase 2 reporting, current-state before future-state) follows a deliberate waterfall progression

**Sprint cadence**: 2-week iterations (Wednesday to Tuesday)

### 5.2 Ceremonies

The team holds a **daily 11am–12pm ET block**. The format varies by day:

| Day | Format | Purpose |
|-----|--------|---------|
| **Mon, Wed, Thu, Fri** | Standup + Working Time | Standup (~15 min), then parking lot items, blocker review, and working discussion as needed |
| **Tuesday (alternating)** | Sprint Planning + Retro | Define sprint goal, select backlog items, reflect on what's working / what to change |
| **Tuesday (alternating)** | Backlog Refinement + Retro | Review and refine upcoming work, estimate effort, surface questions, reflect on process |

**Retrospective is baked into the Tuesday sessions** — not a separate ceremony. This keeps the cadence simple and clean. We can iterate on the format as the team matures.

#### Standup (Mon / Wed / Thu / Fri)
Each team member answers:
1. What did I accomplish yesterday that contributed to the sprint goal?
2. What will I work on today?
3. Am I facing any impediments or blockers?

Remaining time is used for parking lot items, blocker follow-up, and working discussion. PM follows up on blockers outside the session as needed.

#### Sprint Planning (Alternating Tuesdays — Start of Sprint)
- Confirm team availability (PTO calendar)
- Review prioritized backlog
- Discuss proposed sprint goal
- Select items the team can realistically complete based on capacity and velocity
- Break down selected items into tasks
- Identify dependencies between tasks
- Commit to sprint goal and selected items
- **Retro check-in**: What went well last sprint? What should we change?

#### Backlog Refinement (Alternating Tuesdays — Mid-Sprint)
- Are current sprint goals and tickets still aligned and on track?
- Review and refine new backlog items, emphasizing anticipated items for next sprint
- Discuss and clarify requirements and acceptance criteria (what does "done" mean?)
- Break down larger items into manageable tasks
- Estimate effort (story points or time-based)
- Prioritize based on business value and dependencies
- Surface questions or concerns from the development team
- **Retro check-in**: Any process issues to address? Quick wins to implement?

### 5.3 Work Tracking

| Tool | What It Tracks |
|------|---------------|
| **GitHub Projects** | Sprint backlogs, individual tickets, day-to-day work, ticket status (To Triage → Refinement Needed → Backlog → Ready → In Progress → In Review → Done) |
| **ERA Backlog** (ERA_BACKLOG.md) | Prioritized report backlog — what the ERA team needs, in what order |
| **Risk Register** (RISKS.md) | Active risks with severity, mitigation, and ownership |
| **This Project Plan** | Strategic roadmap — workstreams, timeline, methodology. Updated periodically, not daily. |
| **Project Charter** | Scope, milestones, governance. Static — changes via change request. |

---

## 6. Communication Plan

### 6.1 Regular Meetings

| Meeting | Frequency | Attendees | Purpose |
|---------|-----------|-----------|---------|
| Daily Block (Standup + Working Time) | Mon/Wed/Thu/Fri, 11am–12pm ET | Core dev team + PM | Standup, parking lot, blocker review |
| Sprint Planning / Backlog Refinement | Alternating Tuesdays, 11am–12pm ET | Core team | Sprint and backlog management + retro |
| ERA Weekly Sync | Weekly, Thu 3:30pm | PM + ERA Team Lead | Report backlog review, validation status, priorities |
| ITS Leadership Weekly | Weekly, Thu 10am | PM + Director of ETS + Program Lead | Program oversight, cross-project coordination |
| Sponsor Check-in | Bi-weekly, Fri ~10am | PM + Program Sponsors | Executive visibility, strategic alignment |
| CRM/Data Lakehouse Technical Working Session | Bi-weekly | Data Lakehouse + CRM team members | Cross-project technical alignment |

### 6.2 Meeting Responsibilities

**Requestors/Organizers:**
- Create and distribute a clear agenda in advance
- Delineate required vs. optional attendees
- Define desired outcomes

**Facilitators:**
- Ensure meeting link is accessible
- Capture key decisions, action items, and notes
- Manage discussion focus; use "parking lot" for off-topic items
- Keep time

**Attendees:**
- Review agenda beforehand
- Prepare feedback and questions
- Respond to meeting invitations promptly (especially if required)

### 6.3 Escalation Path

| Level | Forum | When to Use |
|-------|-------|-------------|
| Team-level | Standup / Slack | Day-to-day blockers, technical questions |
| PM escalation | Direct to PM | Blocker not resolved within 24 hours; cross-team coordination needed |
| Leadership | ITS Leadership Weekly | Resource conflicts, priority disagreements, cross-project issues |
| Sponsor | Sponsor Check-in | Strategic decisions, scope changes, major risk escalation |

---

## 7. Dependencies & Integration Points

### 7.1 Internal Dependencies

| Dependency | Workstream(s) Affected | Risk Level | Notes |
|-----------|----------------------|-----------|-------|
| Person_7 (Colleague SME) availability | Phase 1, WDS | High | Single point of failure for Colleague institutional knowledge. Non-Colleague responsibilities already removed to maximize focus. |
| Lead Architect capacity | All | High | Spans all workstreams. Phase 1 delays compress WDS time. Mitigation: decentralize Phase 2 leadership to new BA/Dev. |
| Colleague Dev Team | Phase 1 (NTR) | Medium | Needed to make charge/financial fields available. Team lost a person in Oct 2025 RIF — likely spread thin. |
| Test/Production environments | Phase 1, Platform | Medium | Currently dev only. Environments needed before reports can go operational. |

### 7.2 External Dependencies

| Dependency | Workstream(s) Affected | Risk Level | Notes |
|-----------|----------------------|-----------|-------|
| WDS Implementation Team | WDS Integration | Medium-High | Cross-project coordination for data mapping. WDS team unavailable during their testing/go-live periods. |
| PowerFAIDS secure connection | Phase 2 | Medium | External tech lead not dedicated to this project. PII masking / RBAC configuration causing delays. |
| Salesforce/CRM Team | SF Validation | Low-Medium | Rep attends standup. Validation approach TBD. |

### 7.3 Cross-Project Integration

| Project | Integration Point | Coordination Mechanism |
|---------|------------------|----------------------|
| Workday Student Implementation | Data mapping, schema alignment, code freeze coordination | Bi-weekly tech working sessions; ITS Leadership weekly |
| Salesforce/CRM Project | Salesforce data validation, EDA scope decisions | CRM/Data Lakehouse bi-weekly session; SF rep at standup |

---

## 8. Quality & Validation Approach

### 8.1 Validation Methodology

The primary validation method compares Snowflake data platform outputs against Informer (legacy reporting tool) baselines:

1. **Run a known query** in Informer (e.g., all active students for a given term)
2. **Run the equivalent query** against Snowflake Gold layer / Datamart
3. **Compare** counts and spot-check records
4. **Investigate** discrepancies — categorize as pipeline issue vs. source data issue
5. **Document** every discrepancy and resolution

### 8.2 Accuracy Targets

| Report Type | Target | Notes |
|-------------|--------|-------|
| All Active Reports | 95% accuracy (excluding complex computed fields like GPA, credits) | Pragmatic threshold — GPA and credit fields may require additional development cycles |
| Other reports | TBD per report | Acceptance criteria defined during Discovery/Refinement |

### 8.3 Key Principle: "Unmasking" Legacy Data Issues

The Snowflake platform enforces rigorous, automated, auditable logic. This will surface data quality issues that were previously hidden by manual workarounds (fragmented flat reports, Google Sheets, Tableau fixes with manual "patches").

**The platform is not creating problems — it is making pre-existing problems visible.**

This is expected and healthy, but it increases validation effort and requires careful stakeholder communication. Every discrepancy is documented, and the team clearly distinguishes between "pipeline issue" (our problem to fix) and "source data issue" (pre-existing, needs awareness and potentially source-system remediation).

---

## 9. Risk Management

### 9.1 Approach

Risks are tracked in a dedicated Risk Register (RISKS.md), maintained by the PM, and reviewed regularly in the following forums:

| Forum | Risk Review Activity |
|-------|---------------------|
| Sprint Planning | Review risks affecting the upcoming sprint; ensure mitigations are reflected in sprint work |
| ITS Leadership Weekly | Escalate high/critical risks; review mitigation progress |
| Sponsor Check-in | Communicate program-level risks; request support for mitigation where needed |

### 9.2 Current Top Risks (Summary)

| Risk | Severity | Key Mitigation |
|------|----------|---------------|
| Colleague SME single point of failure | High | Removed non-Colleague responsibilities; aggressive documentation |
| Architect capacity across all workstreams | High | Decentralized Phase 2 leadership; capacity relief as Phase 1 wraps |
| All Active schedule delay (cascading) | High | 95% accuracy target; parallel Conservatory work; term-preview queries |
| Legacy technical debt increasing validation burden | High | Clear pipeline-vs-source categorization; stakeholder communication |
| WDS/Lakehouse schedule misalignment | High | Cross-project coordination; flexible scope freeze date |

See the Risk Register for the full list, detailed descriptions, and mitigation plans.

---

## 10. Tools & Infrastructure

| Tool | Purpose |
|------|---------|
| **Snowflake** | Data lakehouse platform (medallion architecture) |
| **SnapLogic** | ETL — moves data from source systems to S3/Snowflake |
| **AWS S3** | Staging area between source extracts and Snowflake |
| **Snowpipe** | Automated ingestion from S3 into Snowflake |
| **Tableau** | Reporting and dashboard visualization |
| **Informer** | Legacy reporting tool (Colleague-native) — validation baseline |
| **GitHub** | Source control |
| **GitHub Actions** | CI/CD pipeline |
| **GitHub Projects** | Work tracking, sprint management |
| **Terraform** | Infrastructure as code (LIMITED USE) |
| **SchemaChange** | Snowflake schema migration management |
| **Snowflake Horizon** (CONFIRM?) | Data governance, lineage, quality monitoring |

---

## 11. Resource Allocation

### Current Allocation by Workstream

| Resource | Phase 1 (SIS Reports) | Phase 2 (StarRez/PFAIDS) | WDS Integration | Platform/Observability |
|----------|----------------------|--------------------------|-----------------|----------------------|
| PM (Company_480_B) | Lead | Oversight | Coordination | Oversight |
| Director of ETS | Resource allocation, escalation | Resource allocation | Resource allocation | Technical oversight |
| Lead Architect | Primary (validation, modeling) | Oversight / guidance | Growing (discovery → modeling) | Guidance |
| Company_480_A (Tech Lead) | Development | — | TBD | Development |
| Person_7 (Colleague SME) | Critical (Informer, biz rules) | — | Mapping support | — |
| Company_480_BCompany_546 (Analyst) | Validation, Tableau | — | — | — |
| Person_39 (Tester) | QA, reconciliation | — | — | — |
| New BA | — | Lead (discovery, requirements) | — | — |
| New Dev | — | Lead (ingestion development) | — | — |
| Program Lead | Stakeholder coordination | — | Cross-project | — |

### Baseline Resource Allocation Plan

See [RESOURCE_PLAN_BASELINE.md](RESOURCE_PLAN_BASELINE.md) for the original Phase 2 staffing allocation by workstream and month (Nov '25 – Oct '26). Key takeaway: ERA resources were planned through March '26 only; Architect was planned at 75% WDS from January '26 onward. As of February '26, actual allocation diverges significantly from baseline — see the Planned vs. Actual comparison in that document.

### Core Tension

The Lead Architect and Person_7 (Colleague SME) are needed across multiple workstreams simultaneously. The primary capacity strategy is:

1. **Decentralize Phase 2**: New BA/Dev team operates independently with architectural guidance only
2. **Sequence Phase 1 reports**: Reports are delivered sequentially (not all at once) to manage validation throughput
3. **Architect allocation shifts**: As Phase 1 wraps, architect time pivots increasingly to WDS integration
4. **Protect Person_7**: Non-Colleague responsibilities already removed; team provides extra support for Workday-related tasks

---

## 12. Document Maintenance

This plan is a living document, updated at phase boundaries or when significant changes warrant it. It is **not** updated for every sprint or individual ticket change — that level of detail lives in GitHub Projects.

| Trigger | Action |
|---------|--------|
| Phase boundary (e.g., Phase 1 → Phase 2 completion) | Review and update workstream status, timeline, resource allocation |
| Major scope or timeline change | Update affected sections; note change in revision history |
| Quarterly review | Confirm plan still reflects reality; prune outdated content |
| New workstream or significant pivot | Add new workstream section |

### Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-17 | Company_480_B | Initial draft |
| 1.1 | 2026-02-22 | Company_480_B | Updated Phase 2 StarRez status (14 tables loaded, validation starting). Added WDS Stage 1 alignment notes (not retrofitting to Colleague model, WDS terminology adoption, CRM file layout reference). Added deduplication validation example to Section 3.1 validation philosophy. |
