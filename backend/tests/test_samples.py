"""Test samples for manual and automated prompt quality evaluation.

Each sample has:
- name: Descriptive label
- input_text: The text to paste into VPMA
- expected_type: What input classification should return
- expected_artifacts: Which artifact types should have suggestions
- expected_sections: Key sections that should be populated
- notes: What to look for when evaluating quality

Usage:
    Run the backend, then use the evaluation script:
        python -m backend.tests.test_samples

    Or paste individual samples into the UI manually.
"""

SAMPLES = [
    # ---------------------------------------------------------------
    # Sample 1: Formal meeting notes with structure
    # ---------------------------------------------------------------
    {
        "name": "Formal meeting notes — structured with attendees and agenda",
        "input_text": """Meeting: Weekly Project Sync
Date: February 10, 2026
Attendees: Jessica Chen, Mark Rivera, Priya Patel, David Kim

Agenda:
1. Sprint review
2. Upcoming milestones
3. Open issues

Discussion:
Jessica opened the meeting by reviewing last sprint's deliverables. The user authentication module is complete and passed QA. Mark noted the API response times are averaging 340ms, which exceeds our 200ms SLA target. Priya mentioned she's been working on the dashboard redesign and expects wireframes by Friday.

David raised a concern that the third-party payment gateway (Stripe) has announced a breaking API change effective April 1. We need to update our integration before then.

Decisions:
- We will prioritize the API performance optimization in the next sprint.
- David will lead the Stripe migration effort.
- The dashboard redesign will proceed with the current timeline.

Action Items:
- Mark to profile the API endpoints and propose optimization plan by Wednesday.
- David to review Stripe migration guide and estimate effort by next Monday.
- Priya to share wireframe drafts with Jessica by Friday.
- Jessica to schedule a stakeholder demo for February 21.""",
        "expected_type": "meeting_notes",
        "expected_artifacts": ["RAID Log", "Status Report", "Meeting Notes"],
        "expected_sections": [
            "Accomplishments",  # auth module complete
            "In Progress",  # dashboard redesign, API work
            "Upcoming",  # stakeholder demo, optimization sprint
            "Blockers / Risks",  # API SLA, Stripe breaking change
            "Risks",  # Stripe API change deadline
            "Dependencies",  # Stripe migration
            "Action Items",  # 4 explicit action items
            "Decisions",  # 3 explicit decisions
            "Discussion",  # key topics
        ],
        "notes": "Rich input — should produce 10+ suggestions. Stripe breaking change is both a Risk and Dependency. API SLA miss is an Issue.",
    },
    # ---------------------------------------------------------------
    # Sample 2: Raw transcript with speaker labels
    # ---------------------------------------------------------------
    {
        "name": "Raw transcript — casual team standup",
        "input_text": """Alex: Hey everyone. Quick standup. I'll go first — I finished the email notification system yesterday. Going to start on the PDF export feature today.

Sam: Nice. I'm still working on the search indexing. Hit a weird bug with Elasticsearch — documents aren't being indexed when they have special characters in the title. Been debugging for two days.

Jordan: I can help with that, I dealt with something similar last quarter. Let's pair after this call.

Alex: Cool. Oh, and heads up — the staging server SSL cert expires next Thursday. Someone should renew it before it breaks CI.

Sam: I'll add it to my list, I have the CloudFlare access.

Jordan: For my update — the mobile responsive refactor is about 70% done. Should be finished by end of week. One thing though, I'm assuming we're only supporting iOS 16+ and Android 13+. Is that right?

Alex: Yeah, that's what we agreed last month. Anything below that is less than 2% of our users.

Jordan: Perfect. That simplifies things a lot.""",
        "expected_type": "transcript",
        "expected_artifacts": ["RAID Log", "Status Report", "Meeting Notes"],
        "expected_sections": [
            "Accomplishments",  # email notification system
            "In Progress",  # search indexing, mobile refactor
            "Upcoming",  # PDF export
            "Blockers / Risks",  # Elasticsearch bug, SSL cert
            "Risks",  # SSL cert expiry
            "Issues",  # Elasticsearch special chars bug
            "Assumptions",  # iOS 16+, Android 13+
            "Action Items",  # Sam renew SSL, Jordan pair with Sam
        ],
        "notes": "Conversational tone — LLM must extract structured data from dialogue. SSL cert is time-sensitive. The mobile support assumption should be captured.",
    },
    # ---------------------------------------------------------------
    # Sample 3: Status update email style
    # ---------------------------------------------------------------
    {
        "name": "Status update — email format, brief",
        "input_text": """Hi team,

Quick update on Project Atlas:

What we shipped this week:
- Migrated all user data to the new schema (zero downtime!)
- Launched the beta invite system — 200 invites sent, 47 signups so far
- Fixed the memory leak in the background job processor

Currently working on:
- Performance testing under load (targeting 10K concurrent users)
- Onboarding flow redesign based on beta feedback

Blocked:
- Legal review of the updated Terms of Service — waiting on outside counsel. This is blocking our public launch.

Heads up:
- AWS costs jumped 40% this month due to the load testing environment. We'll tear it down after testing but wanted to flag it.
- The QA contractor's contract ends March 15. Need to decide whether to extend or hire permanent.

Best,
Rachel""",
        "expected_type": "status_update",
        "expected_artifacts": ["RAID Log", "Status Report"],
        "expected_sections": [
            "Accomplishments",  # 3 items shipped
            "In Progress",  # 2 items
            "Blockers / Risks",  # Legal review, AWS costs
            "Risks",  # AWS cost spike, QA contractor ending
            "Dependencies",  # Outside counsel for legal review
            "Issues",  # Legal review blocking launch
        ],
        "notes": "No meeting notes expected (this is an email, not a meeting). Should capture the AWS cost spike as a risk. QA contractor decision is a risk/upcoming item.",
    },
    # ---------------------------------------------------------------
    # Sample 4: Ad-hoc notes — messy, incomplete
    # ---------------------------------------------------------------
    {
        "name": "Ad-hoc notes — messy jottings, abbreviations",
        "input_text": """notes from call w/ client (Acme Corp):

- they want the dashboard by end of Q1, no later
- budget approved for phase 2!!! $150K
- concerned about data migration — their legacy DB is Oracle, ours is Postgres
- need to sign NDA before we can access their test env
- CEO specifically asked for executive summary view
- competitor (TechRival) apparently pitching them too, need to move fast
- follow up: send SOW draft by Weds (me), schedule data migration workshop (Tyler)
- they use Okta for SSO — we need to support that""",
        "expected_type": "general_text",
        "expected_artifacts": ["RAID Log", "Status Report", "Meeting Notes"],
        "expected_sections": [
            "Risks",  # Competitor threat, data migration complexity
            "Dependencies",  # NDA for test env, Okta SSO
            "Assumptions",  # Q1 deadline, $150K budget
            "Action Items",  # SOW draft, migration workshop
            "Upcoming",  # Phase 2, executive summary view
        ],
        "notes": "Messy input with abbreviations — tests how well the LLM handles informal text. Competitor mention is a risk. Budget approval is positive news. NDA is a dependency.",
    },
    # ---------------------------------------------------------------
    # Sample 5: Technical post-mortem
    # ---------------------------------------------------------------
    {
        "name": "Post-mortem — production incident",
        "input_text": """Incident Post-Mortem: Payment Processing Outage
Date: February 8, 2026
Duration: 2 hours 15 minutes (14:30 - 16:45 UTC)
Severity: P1

Summary: Payment processing was completely down for all users due to a database connection pool exhaustion.

Root Cause: A code deploy at 14:25 UTC introduced a query that didn't properly close database connections. Under load, connections accumulated until the pool was exhausted.

Timeline:
- 14:25 — Deploy v2.4.1 to production
- 14:30 — First alerts: payment timeouts
- 14:45 — Engineering team assembled, began investigation
- 15:10 — Root cause identified (connection leak in new query)
- 15:30 — Hotfix deployed (v2.4.2), connections slowly recovering
- 16:45 — Full recovery confirmed, all systems nominal

Impact: ~$45K in failed transactions, estimated 1,200 affected users. 3 enterprise clients escalated through support.

Action Items:
1. Add connection pool monitoring alerts (Maria, by Feb 12)
2. Implement mandatory connection leak tests in CI pipeline (Chen, by Feb 15)
3. Review and update rollback procedures (Ops team, by Feb 19)
4. Send incident report to affected enterprise clients (Sales, by Feb 10)
5. Add database connection pool size to grafana dashboard (Maria, by Feb 12)

Lessons Learned:
- Our pre-deploy staging tests don't simulate realistic connection pool behavior
- Need automated canary deploys that check connection metrics
- The 15-minute gap between first alert and team assembly is too long — need better on-call escalation""",
        "expected_type": "meeting_notes",
        "expected_artifacts": ["RAID Log", "Status Report", "Meeting Notes"],
        "expected_sections": [
            "Issues",  # Connection pool exhaustion, $45K impact
            "Risks",  # Staging doesn't simulate realistic conditions
            "Action Items",  # 5 explicit action items
            "Accomplishments",  # Incident resolved
            "Blockers / Risks",  # CI pipeline gap, on-call escalation gap
        ],
        "notes": "Post-mortem format — structured with clear action items. All 5 action items should be captured. Lessons learned should map to Risks or Issues. The $45K impact should be noted.",
    },
    # ---------------------------------------------------------------
    # Sample 6: Minimal input — tests edge case
    # ---------------------------------------------------------------
    {
        "name": "Minimal input — short sentence, little context",
        "input_text": """We decided to postpone the launch to April.""",
        "expected_type": "general_text",
        "expected_artifacts": ["Status Report", "Meeting Notes"],
        "expected_sections": [
            "Decisions",  # Postpone launch
            "Upcoming",  # Launch now in April
            "Risks",  # Possibly — launch delay risk
        ],
        "notes": "Minimal input — should still produce something useful. At minimum a Decision and Status Report update. Should not hallucinate details not in the input.",
    },
    # ---------------------------------------------------------------
    # Sample 7: Mixed content — combines different types
    # ---------------------------------------------------------------
    {
        "name": "Mixed content — project update with embedded decisions and risks",
        "input_text": """Project Phoenix — Monthly Review Notes

The frontend team has completed the new checkout flow, including A/B test integration. Early results show a 12% improvement in conversion rate compared to the old flow. We're going to keep the new flow as the default.

Backend migration to Kubernetes is 60% complete. The remaining services (billing, notifications, analytics) are scheduled for migration over the next 3 weeks. One concern: the analytics service has a hard dependency on a legacy Redis cluster that can't be easily containerized. We may need to run it in hybrid mode.

HR update: Two senior engineers (backend) put in their notice last week. We're starting the hiring process immediately but realistically won't have replacements onboarded for 8-10 weeks. This will slow down the K8s migration.

Budget: We're tracking 15% over budget for Q1 due to the additional cloud infrastructure costs. Finance has approved the overage but asked us to come in under budget for Q2.

Next steps:
- Frontend team starts on the recommendation engine (depends on ML team delivering the model by March 1)
- DevOps to create runbook for the hybrid Redis setup
- Hiring manager to post job listings by end of week""",
        "expected_type": "status_update",
        "expected_artifacts": ["RAID Log", "Status Report", "Meeting Notes"],
        "expected_sections": [
            "Accomplishments",  # Checkout flow, A/B results
            "In Progress",  # K8s migration
            "Upcoming",  # Recommendation engine, runbook, hiring
            "Blockers / Risks",  # Engineer attrition, budget, Redis dependency
            "Risks",  # Attrition, budget, legacy Redis
            "Dependencies",  # ML model by March 1, Redis cluster
            "Issues",  # 15% over budget, 2 engineers leaving
            "Decisions",  # Keep new checkout flow as default
            "Action Items",  # 3 next steps
        ],
        "notes": "Rich, multi-topic input that should produce many suggestions across all 3 artifact types. The engineer attrition is both a Risk and an Issue. Budget overage is an Issue. The 12% conversion improvement is a key accomplishment.",
    },
]


# ---------------------------------------------------------------
# Evaluation script — run against live backend
# ---------------------------------------------------------------

if __name__ == "__main__":
    import asyncio
    import sys

    async def evaluate():
        """Run all samples through the backend API and print results."""
        try:
            import httpx
        except ImportError:
            print("Install httpx to run evaluation: pip install httpx")
            sys.exit(1)

        base_url = "http://localhost:8000/api"

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Check health
            try:
                health = await client.get(f"{base_url}/health")
                health.raise_for_status()
            except Exception as e:
                print(f"Backend not reachable at {base_url}: {e}")
                print("Start the backend first: cd backend && uvicorn app.main:app --reload")
                sys.exit(1)

            print(f"Running {len(SAMPLES)} test samples against {base_url}\n")
            print("=" * 70)

            for i, sample in enumerate(SAMPLES, 1):
                print(f"\n{'=' * 70}")
                print(f"Sample {i}: {sample['name']}")
                print(f"Expected type: {sample['expected_type']}")
                print(f"Expected artifacts: {', '.join(sample['expected_artifacts'])}")
                print("-" * 70)

                try:
                    resp = await client.post(
                        f"{base_url}/artifact-sync",
                        json={"text": sample["input_text"]},
                    )
                    resp.raise_for_status()
                    result = resp.json()
                except Exception as e:
                    print(f"  ERROR: {e}")
                    continue

                # Evaluate input type
                actual_type = result.get("input_type", "unknown")
                type_match = actual_type == sample["expected_type"]
                expected = sample["expected_type"]
                type_status = "OK" if type_match else f"MISMATCH (expected {expected})"
                print(f"  Input type: {actual_type} {type_status}")
                print(f"  PII detected: {result.get('pii_detected', 0)}")
                print(f"  Suggestions: {len(result.get('suggestions', []))}")

                # Check which artifact types and sections appeared
                actual_artifacts = set()
                actual_sections = set()
                for s in result.get("suggestions", []):
                    actual_artifacts.add(s["artifact_type"])
                    actual_sections.add(s["section"])

                # Artifact type coverage
                expected_set = set(sample["expected_artifacts"])
                missing_artifacts = expected_set - actual_artifacts
                extra_artifacts = actual_artifacts - expected_set
                print(f"  Artifact types: {', '.join(sorted(actual_artifacts))}")
                if missing_artifacts:
                    print(f"    MISSING: {', '.join(missing_artifacts)}")
                if extra_artifacts:
                    print(f"    EXTRA: {', '.join(extra_artifacts)}")

                # Section coverage
                expected_sections = set(sample["expected_sections"])
                missing_sections = expected_sections - actual_sections
                found_sections = expected_sections & actual_sections
                print(f"  Sections found: {len(found_sections)}/{len(expected_sections)}")
                if missing_sections:
                    print(f"    MISSING sections: {', '.join(sorted(missing_sections))}")

                # Print each suggestion
                for j, s in enumerate(result.get("suggestions", []), 1):
                    conf = s.get("confidence", 0)
                    print(
                        f"  [{j}] {s['artifact_type']} > {s['section']} ({s['change_type']}, conf={conf:.2f})"
                    )
                    print(
                        f"      {s['proposed_text'][:100]}{'...' if len(s.get('proposed_text', '')) > 100 else ''}"
                    )

                print(f"\n  Evaluation notes: {sample['notes']}")

            print(f"\n{'=' * 70}")
            print("Evaluation complete.")

    asyncio.run(evaluate())
