"""End-to-End Integration Tests for Phase 1A.

Simulates the full multi-session flow with a mocked LLM client but real
database, privacy proxy, LPD manager, and artifact sync pipeline.

Test flow:
1. Init LPD → artifact sync → verify session summary logged
2. Apply suggestion → verify return path updates LPD
3. Second sync → verify context injection includes LPD data
4. Log session → verify LPD updates applied
5. Third sync → verify accumulated context from all sessions
6. Intake flow → import files → verify LPD populated
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.artifact_sync import run_artifact_sync
from app.services.lpd_manager import (
    _lpd_file_path,
    get_full_lpd,
    initialize_lpd,
    update_section,
)

PROJECT_ID = "default"


# ============================================================
# MOCK LLM HELPERS
# ============================================================


def _make_extract_response(suggestions):
    """Build a JSON string the LLM would return for extract mode."""
    return json.dumps(suggestions)


def _make_log_session_response(summary, lpd_updates, artifact_suggestions=None):
    """Build a JSON string the LLM would return for log_session mode."""
    return json.dumps(
        {
            "session_summary": summary,
            "lpd_updates": lpd_updates,
            "artifact_suggestions": artifact_suggestions or [],
        }
    )


def _make_analyze_response(summary, items):
    """Build a JSON string the LLM would return for analyze mode."""
    return json.dumps(
        {
            "summary": summary,
            "items": items,
        }
    )


def _patch_llm(monkeypatch, responses):
    """Patch LLM client. responses is a list of return values for sequential calls.

    The first call is always input classification (returns a string).
    The second call is the main pipeline call (returns JSON).
    """
    call_count = 0
    call_args = []

    async def mock_call(system_prompt, user_prompt, max_tokens=4096):
        nonlocal call_count
        idx = call_count
        call_count += 1
        call_args.append({"system_prompt": system_prompt, "user_prompt": user_prompt})
        return responses[idx] if idx < len(responses) else "[]"

    client = MagicMock()
    client.call = mock_call
    client.estimate_tokens = MagicMock(return_value=50)
    client.model = "mock-model"
    monkeypatch.setattr(
        "app.services.artifact_sync.get_llm_client",
        AsyncMock(return_value=client),
    )
    return call_args


# ============================================================
# E2E FLOW: MULTI-SESSION CONTEXT ACCUMULATION
# ============================================================


class TestMultiSessionContextAccumulation:
    """Simulates: init LPD → 3+ sync sessions → verify context accumulates."""

    @pytest.mark.asyncio
    async def test_session1_extract_logs_summary(self, monkeypatch):
        """Session 1: Extract mode produces suggestions and logs a session summary."""
        await initialize_lpd(PROJECT_ID)
        # Use NER-safe terms (spaCy would anonymize org names like "Acme Corp")
        await update_section(
            PROJECT_ID, "Overview", "Portal redesign project targeting next quarter launch."
        )

        suggestions = [
            {
                "artifact_type": "RAID Log",
                "change_type": "add",
                "section": "Risks",
                "proposed_text": "| R-NEW | Vendor API delayed until March | Medium | High | Follow up with vendor | Mike | Open |",
                "confidence": 0.9,
                "reasoning": "Vendor delay threatens timeline",
            },
            {
                "artifact_type": "Status Report",
                "change_type": "add",
                "section": "Accomplishments",
                "proposed_text": "- Database migration completed successfully",
                "confidence": 0.95,
                "reasoning": "Major milestone unblocks dependent features",
            },
        ]

        call_args = _patch_llm(
            monkeypatch,
            [
                "meeting_notes",
                _make_extract_response(suggestions),
            ],
        )

        result = await run_artifact_sync(
            "Sprint review: DB migration done. Vendor API delayed until March.",
            project_id=PROJECT_ID,
        )

        # Verify suggestions returned
        assert len(result.suggestions) == 2
        assert result.mode == "extract"
        assert result.input_type == "meeting_notes"

        # Verify session summary was logged to Recent Context
        lpd = await get_full_lpd(PROJECT_ID)
        assert "meeting notes" in lpd["Recent Context"].lower()
        assert "1 RAID Log" in lpd["Recent Context"]

        # Verify context injection prompt included project context
        sync_prompt = call_args[1]["user_prompt"]
        assert "## Project Context" in sync_prompt
        assert "Portal redesign project" in sync_prompt

    @pytest.mark.asyncio
    async def test_session2_sees_accumulated_context(self, monkeypatch):
        """Session 2: Context from session 1 appears in the LLM prompt."""
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Overview", "Portal redesign for the web platform.")
        await update_section(PROJECT_ID, "Risks", "- Vendor delayed until next month")

        # Session 1: extract
        _patch_llm(
            monkeypatch,
            [
                "meeting_notes",
                _make_extract_response(
                    [
                        {
                            "artifact_type": "Meeting Notes",
                            "change_type": "add",
                            "section": "Decisions",
                            "proposed_text": "- Team agreed to use a component framework",
                            "confidence": 0.9,
                            "reasoning": "Framework decision made",
                        }
                    ]
                ),
            ],
        )
        await run_artifact_sync("Kickoff meeting: chose a framework.", project_id=PROJECT_ID)

        # Session 2: extract — should see context from session 1 summary
        call_args_s2 = _patch_llm(
            monkeypatch,
            [
                "status_update",
                _make_extract_response([]),
            ],
        )
        await run_artifact_sync("Progress update: API work started.", project_id=PROJECT_ID)

        sync_prompt = call_args_s2[1]["user_prompt"]
        assert "## Project Context" in sync_prompt
        # Overview should be present
        assert "Portal redesign" in sync_prompt
        # Risks should be present
        assert "Vendor delayed" in sync_prompt
        # Recent context from session 1 should be visible
        assert "Recent Context" in sync_prompt

    @pytest.mark.asyncio
    async def test_three_sessions_accumulate(self, monkeypatch):
        """Three sessions each add a session summary; all appear in Recent Context."""
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Overview", "Project Falcon.")

        for i, (input_type, text) in enumerate(
            [
                ("meeting_notes", "Sprint planning: assigned tasks."),
                ("status_update", "Completed auth module."),
                ("transcript", "Discussed API architecture."),
            ]
        ):
            _patch_llm(
                monkeypatch,
                [
                    input_type,
                    _make_extract_response(
                        [
                            {
                                "artifact_type": "Status Report",
                                "change_type": "add",
                                "section": "In Progress",
                                "proposed_text": f"- Session {i + 1} work item",
                                "confidence": 0.8,
                                "reasoning": "Active work",
                            }
                        ]
                    ),
                ],
            )
            await run_artifact_sync(text, project_id=PROJECT_ID)

        lpd = await get_full_lpd(PROJECT_ID)
        recent = lpd["Recent Context"]
        # All three sessions should have summaries in Recent Context
        assert recent.count("**") >= 3  # At least 3 date-bold entries


# ============================================================
# E2E FLOW: RETURN PATH (APPLY → LPD UPDATED)
# ============================================================


class TestReturnPathE2E:
    """Simulates: extract → apply suggestion → verify LPD updated → next sync sees it."""

    @pytest.mark.asyncio
    async def test_apply_updates_lpd_via_return_path(self, monkeypatch):
        """Applying a RAID Log risk suggestion also updates the LPD Risks section."""
        from app.services.lpd_manager import update_lpd_from_suggestion

        await initialize_lpd(PROJECT_ID)

        # Apply a risk suggestion
        lpd_updated = await update_lpd_from_suggestion(
            project_id=PROJECT_ID,
            artifact_section="Risks",
            proposed_text="| R-NEW | Budget overrun risk | High | High | Monthly reviews | CFO | Open |",
        )
        assert lpd_updated is True

        lpd = await get_full_lpd(PROJECT_ID)
        assert "Budget overrun risk" in lpd["Risks"]

    @pytest.mark.asyncio
    async def test_applied_content_visible_in_next_sync(self, monkeypatch):
        """Content applied via return path shows up in context for the next sync."""
        from app.services.lpd_manager import update_lpd_from_suggestion

        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Overview", "Project Falcon.")

        # Simulate applying a suggestion with return path (use NER-safe text)
        await update_lpd_from_suggestion(
            project_id=PROJECT_ID,
            artifact_section="Decisions",
            proposed_text="- Decided to use a relational database instead of a document store",
        )

        # Next sync should see the decision in context
        call_args = _patch_llm(
            monkeypatch,
            [
                "general_text",
                _make_extract_response([]),
            ],
        )
        await run_artifact_sync("Any update.", project_id=PROJECT_ID)

        sync_prompt = call_args[1]["user_prompt"]
        assert "relational database instead of a document store" in sync_prompt

    @pytest.mark.asyncio
    async def test_return_path_dedup(self, monkeypatch):
        """Return path dedup prevents the same text from being added twice."""
        from app.services.lpd_manager import update_lpd_from_suggestion

        await initialize_lpd(PROJECT_ID)

        text = "- Critical dependency on external vendor"

        first = await update_lpd_from_suggestion(PROJECT_ID, "Risks", text)
        second = await update_lpd_from_suggestion(PROJECT_ID, "Risks", text)

        assert first is True
        assert second is False  # Dedup caught it

        lpd = await get_full_lpd(PROJECT_ID)
        assert lpd["Risks"].count("Critical dependency") == 1


# ============================================================
# E2E FLOW: LOG SESSION BRIDGE
# ============================================================


class TestLogSessionBridgeE2E:
    """Simulates: log_session mode → LPD updates applied → context visible next sync."""

    @pytest.mark.asyncio
    async def test_log_session_updates_lpd_directly(self, monkeypatch):
        """Log session mode applies LPD updates directly without user approval."""
        await initialize_lpd(PROJECT_ID)

        _patch_llm(
            monkeypatch,
            [
                "general_text",
                _make_log_session_response(
                    summary="Decided to drop mobile from Phase 1 and reassigned API ownership.",
                    lpd_updates=[
                        {
                            "section": "Decisions",
                            "content": "- Dropped mobile app from Phase 1; web-only focus",
                        },
                        {
                            "section": "Risks",
                            "content": "- Q2 deadline at risk: vendor API spec not confirmed",
                        },
                    ],
                    artifact_suggestions=[
                        {
                            "artifact_type": "RAID Log",
                            "change_type": "add",
                            "section": "Risks",
                            "proposed_text": "| R-NEW | Q2 deadline at risk | Medium | High | Follow up | PM | Open |",
                            "confidence": 0.9,
                            "reasoning": "Vendor dependency",
                        }
                    ],
                ),
            ],
        )

        result = await run_artifact_sync(
            "Met with team. Dropped mobile from Phase 1. Vendor API spec still pending.",
            project_id=PROJECT_ID,
            mode="log_session",
        )

        # Verify response structure
        assert result.mode == "log_session"
        assert result.session_summary is not None
        assert (
            "mobile" in result.session_summary.lower()
            or "phase 1" in result.session_summary.lower()
        )
        assert len(result.lpd_updates) == 2
        assert len(result.suggestions) == 1

        # Verify LPD was updated directly
        lpd = await get_full_lpd(PROJECT_ID)
        assert "Dropped mobile app from Phase 1" in lpd["Decisions"]
        assert "vendor API spec not confirmed" in lpd["Risks"]

    @pytest.mark.asyncio
    async def test_log_session_context_visible_in_next_extract(self, monkeypatch):
        """Content from log_session mode appears in context for the next extract sync."""
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Overview", "Acme Corp portal.")

        # Log session: adds decision to LPD
        _patch_llm(
            monkeypatch,
            [
                "general_text",
                _make_log_session_response(
                    summary="Architecture decision: chose microservices.",
                    lpd_updates=[
                        {
                            "section": "Decisions",
                            "content": "- Architecture: microservices over monolith",
                        },
                    ],
                ),
            ],
        )
        await run_artifact_sync(
            "Decided on microservices.", project_id=PROJECT_ID, mode="log_session"
        )

        # Next extract sync should see the decision in context
        call_args = _patch_llm(
            monkeypatch,
            [
                "meeting_notes",
                _make_extract_response([]),
            ],
        )
        await run_artifact_sync("New sprint planning.", project_id=PROJECT_ID)

        sync_prompt = call_args[1]["user_prompt"]
        assert "microservices over monolith" in sync_prompt


# ============================================================
# E2E FLOW: FULL LIFECYCLE (INIT → SYNC → APPLY → LOG → VERIFY)
# ============================================================


class TestFullLifecycle:
    """End-to-end lifecycle: init → extract → apply → log → verify accumulation."""

    @pytest.mark.asyncio
    async def test_full_e2e_lifecycle(self, monkeypatch):
        """Full lifecycle: init LPD → extract sync → apply → log session → verify context."""
        from app.services.lpd_manager import update_lpd_from_suggestion

        # 1. Initialize LPD with project overview
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Overview", "Project Falcon: Q2 customer portal redesign.")
        await update_section(PROJECT_ID, "Stakeholders", "- Sarah (PM)\n- Mike (Tech Lead)")

        # 2. Session 1: Extract mode
        _patch_llm(
            monkeypatch,
            [
                "meeting_notes",
                _make_extract_response(
                    [
                        {
                            "artifact_type": "RAID Log",
                            "change_type": "add",
                            "section": "Risks",
                            "proposed_text": "| R-NEW | SSO blocked on identity provider docs | Medium | High | Escalate | Lisa | Open |",
                            "confidence": 0.9,
                            "reasoning": "Active blocker with hard deadline",
                        }
                    ]
                ),
            ],
        )
        result1 = await run_artifact_sync(
            "Sprint review: SSO feature blocked on identity provider docs.",
            project_id=PROJECT_ID,
        )
        assert len(result1.suggestions) == 1

        # 3. Apply the suggestion (return path updates LPD)
        lpd_updated = await update_lpd_from_suggestion(
            project_id=PROJECT_ID,
            artifact_section="Risks",
            proposed_text="| R-NEW | SSO blocked on identity provider docs | Medium | High | Escalate | Lisa | Open |",
        )
        assert lpd_updated is True

        # 4. Session 2: Log session mode — adds decisions
        _patch_llm(
            monkeypatch,
            [
                "general_text",
                _make_log_session_response(
                    summary="Decided to prioritize web-only for Phase 1.",
                    lpd_updates=[
                        {
                            "section": "Decisions",
                            "content": "- Phase 1 scoped to web-only; mobile deferred to Phase 2",
                        },
                    ],
                ),
            ],
        )
        result2 = await run_artifact_sync(
            "We decided: web-only for Phase 1, mobile comes later.",
            project_id=PROJECT_ID,
            mode="log_session",
        )
        assert result2.mode == "log_session"

        # 5. Session 3: Extract mode — should see ALL accumulated context
        call_args = _patch_llm(
            monkeypatch,
            [
                "status_update",
                _make_extract_response([]),
            ],
        )
        await run_artifact_sync(
            "Weekly status: auth module progressing well.",
            project_id=PROJECT_ID,
        )

        # Verify accumulated context in the LLM prompt
        sync_prompt = call_args[1]["user_prompt"]
        assert "## Project Context" in sync_prompt
        assert "Project Falcon" in sync_prompt
        assert "SSO blocked" in sync_prompt  # From return path
        assert "web-only" in sync_prompt  # From log session

        # 6. Verify the LPD state
        lpd = await get_full_lpd(PROJECT_ID)
        assert "Project Falcon" in lpd["Overview"]
        assert "SSO blocked" in lpd["Risks"]
        assert "web-only" in lpd["Decisions"]
        assert lpd["Recent Context"]  # Should have session summaries

        # 7. Verify markdown file is in sync
        file_path = _lpd_file_path(PROJECT_ID)
        md_content = file_path.read_text()
        assert "SSO blocked" in md_content
        assert "web-only" in md_content


# ============================================================
# E2E FLOW: INTAKE
# ============================================================


class TestIntakeE2E:
    """Simulates: intake preview → apply → verify LPD populated."""

    @pytest.mark.asyncio
    async def test_intake_populates_lpd(self, monkeypatch):
        """Intake extracts entities from files and populates the LPD."""
        from app.services.intake import apply_intake_draft, generate_intake_draft

        # Mock LLM for intake (different module)
        client = MagicMock()

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            return json.dumps(
                {
                    "overview": "Project Falcon — customer portal redesign targeting Q2.",
                    "stakeholders": "- Sarah — PM\n- Mike — Tech Lead",
                    "timeline": "- Feb 15 — Alpha\n- March 1 — Beta",
                    "risks": "- API performance under load",
                    "decisions": "- Use React for frontend",
                    "open_questions": "- Need to confirm vendor API timeline",
                }
            )

        client.call = mock_call
        client.estimate_tokens = MagicMock(return_value=50)
        client.model = "mock"
        monkeypatch.setattr(
            "app.services.intake._get_llm_client",
            AsyncMock(return_value=client),
        )

        from app.models.schemas import IntakeFile

        files = [
            IntakeFile(
                filename="kickoff_notes.md", content="Project Falcon kickoff meeting notes..."
            ),
        ]

        draft = await generate_intake_draft(files, PROJECT_ID)
        assert len(draft.proposed_sections) > 0
        assert "Overview" in draft.proposed_sections

        # Apply all proposed sections
        updated, skipped = await apply_intake_draft(
            project_id=PROJECT_ID,
            proposed_sections=draft.proposed_sections,
            approved_sections=list(draft.proposed_sections.keys()),
        )
        assert len(updated) > 0

        # Verify LPD is populated
        lpd = await get_full_lpd(PROJECT_ID)
        assert "Project Falcon" in lpd["Overview"]
        assert "Sarah" in lpd["Stakeholders"]
        assert "Alpha" in lpd["Timeline & Milestones"]

    @pytest.mark.asyncio
    async def test_intake_then_sync_sees_context(self, monkeypatch):
        """After intake, the next sync should see the imported context."""
        from app.models.schemas import IntakeFile
        from app.services.intake import apply_intake_draft, generate_intake_draft

        # Intake step
        client = MagicMock()

        async def mock_intake_call(system_prompt, user_prompt, max_tokens=4096):
            return json.dumps(
                {
                    "overview": "Acme Corp ERP migration to cloud.",
                    "stakeholders": "- Jordan — Project Sponsor",
                    "timeline": "",
                    "risks": "- Data loss during migration",
                    "decisions": "",
                    "open_questions": "",
                }
            )

        client.call = mock_intake_call
        client.estimate_tokens = MagicMock(return_value=50)
        client.model = "mock"
        monkeypatch.setattr(
            "app.services.intake._get_llm_client",
            AsyncMock(return_value=client),
        )

        draft = await generate_intake_draft(
            [IntakeFile(filename="project_plan.md", content="ERP migration plan...")],
            PROJECT_ID,
        )
        await apply_intake_draft(
            PROJECT_ID,
            draft.proposed_sections,
            list(draft.proposed_sections.keys()),
        )

        # Sync step — should see intake content in context
        call_args = _patch_llm(
            monkeypatch,
            [
                "general_text",
                _make_extract_response([]),
            ],
        )
        await run_artifact_sync("Status update on migration.", project_id=PROJECT_ID)

        sync_prompt = call_args[1]["user_prompt"]
        assert "## Project Context" in sync_prompt
        assert "ERP migration" in sync_prompt
        assert "Data loss during migration" in sync_prompt


# ============================================================
# EDGE CASES
# ============================================================


class TestEdgeCases:
    """Edge cases for the E2E flow."""

    @pytest.mark.asyncio
    async def test_extract_without_lpd_still_works(self, monkeypatch):
        """Full extract pipeline works when no LPD is initialized (backward compat)."""
        _patch_llm(
            monkeypatch,
            [
                "general_text",
                _make_extract_response(
                    [
                        {
                            "artifact_type": "Status Report",
                            "change_type": "add",
                            "section": "Accomplishments",
                            "proposed_text": "- Finished code review",
                            "confidence": 0.9,
                            "reasoning": "Stated accomplishment",
                        }
                    ]
                ),
            ],
        )

        result = await run_artifact_sync(
            "Code review completed today.",
            project_id=PROJECT_ID,
        )
        assert len(result.suggestions) == 1
        assert result.mode == "extract"

    @pytest.mark.asyncio
    async def test_log_session_without_lpd_returns_updates(self, monkeypatch):
        """Log session without LPD returns updates but doesn't apply them."""
        _patch_llm(
            monkeypatch,
            [
                "general_text",
                _make_log_session_response(
                    summary="Discussed architecture.",
                    lpd_updates=[
                        {"section": "Decisions", "content": "- Chose microservices"},
                    ],
                ),
            ],
        )

        result = await run_artifact_sync(
            "Architecture discussion.",
            project_id=PROJECT_ID,
            mode="log_session",
        )

        # Updates returned but not applied (no LPD)
        assert len(result.lpd_updates) == 1
        # No LPD to check — the updates just live in the response

    @pytest.mark.asyncio
    async def test_empty_llm_response_handled_gracefully(self, monkeypatch):
        """Pipeline handles empty or malformed LLM responses without crashing."""
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Overview", "Test project.")

        _patch_llm(
            monkeypatch,
            [
                "general_text",
                "[]",  # Empty suggestions
            ],
        )

        result = await run_artifact_sync("Some text.", project_id=PROJECT_ID)
        assert result.suggestions == []
        assert result.mode == "extract"

    @pytest.mark.asyncio
    async def test_all_three_modes_in_sequence(self, monkeypatch):
        """All three modes work in sequence on the same project."""
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Overview", "Multi-mode test project.")

        # Extract mode
        _patch_llm(
            monkeypatch,
            [
                "meeting_notes",
                _make_extract_response(
                    [
                        {
                            "artifact_type": "Meeting Notes",
                            "change_type": "add",
                            "section": "Action Items",
                            "proposed_text": "| Review PRD | Jordan | Friday | Open |",
                            "confidence": 0.85,
                            "reasoning": "Action item from meeting",
                        }
                    ]
                ),
            ],
        )
        r1 = await run_artifact_sync(
            "Meeting: Jordan to review PRD by Friday.", project_id=PROJECT_ID
        )
        assert r1.mode == "extract"
        assert len(r1.suggestions) == 1

        # Analyze mode
        _patch_llm(
            monkeypatch,
            [
                "general_text",
                _make_analyze_response(
                    "Document is well-structured but missing risk mitigation.",
                    [
                        {
                            "category": "gap",
                            "title": "Missing mitigations",
                            "detail": "Risks listed without mitigation strategies.",
                            "priority": "high",
                            "artifact_type": "RAID Log",
                        }
                    ],
                ),
            ],
        )
        r2 = await run_artifact_sync(
            "Review this RAID log draft.", project_id=PROJECT_ID, mode="analyze"
        )
        assert r2.mode == "analyze"
        assert len(r2.analysis) == 1

        # Log session mode
        _patch_llm(
            monkeypatch,
            [
                "general_text",
                _make_log_session_response(
                    "Sprint retro: agreed to add code review step.",
                    [
                        {
                            "section": "Decisions",
                            "content": "- Added mandatory code review to workflow",
                        }
                    ],
                ),
            ],
        )
        r3 = await run_artifact_sync(
            "Retro: adding code review.", project_id=PROJECT_ID, mode="log_session"
        )
        assert r3.mode == "log_session"
        assert len(r3.lpd_updates) == 1

        # Verify accumulated state
        lpd = await get_full_lpd(PROJECT_ID)
        assert "mandatory code review" in lpd["Decisions"]
        recent = lpd["Recent Context"]
        # Should have summaries from all 3 sessions
        assert recent.count("**") >= 3
