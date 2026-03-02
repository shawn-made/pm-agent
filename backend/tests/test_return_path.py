"""Tests for VPMA Return Path (Task 25).

Tests that:
1. Applying suggestions updates the LPD via section mapping
2. Session summaries are generated and logged after artifact sync
3. Recent Context pruning works with accumulated summaries
4. No behavior change when LPD doesn't exist
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.models.schemas import Suggestion
from app.services.artifact_manager import ArtifactType, get_or_create_artifact
from app.services.artifact_sync import run_artifact_sync
from app.services.crud import get_session_summary_count
from app.services.lpd_manager import (
    ARTIFACT_SECTION_TO_LPD,
    generate_session_summary,
    get_full_lpd,
    initialize_lpd,
    update_lpd_from_suggestion,
)

PROJECT_ID = "default"


# ============================================================
# HELPERS
# ============================================================


def _make_suggestion(
    artifact_type="RAID Log",
    section="Risks",
    proposed_text="- New risk: vendor delay",
    confidence=0.9,
) -> Suggestion:
    return Suggestion(
        artifact_type=artifact_type,
        change_type="add",
        section=section,
        proposed_text=proposed_text,
        confidence=confidence,
        reasoning="Extracted from input.",
    )


def _mock_suggestions_json(count=2) -> str:
    items = []
    for i in range(count):
        items.append(
            {
                "artifact_type": "RAID Log",
                "change_type": "add",
                "section": "Risks",
                "proposed_text": f"- Risk item {i + 1}",
                "confidence": 0.9,
                "reasoning": "From input.",
            }
        )
    return json.dumps(items)


def _mock_analysis_json(count=3) -> str:
    return json.dumps(
        {
            "summary": "Document reviewed.",
            "items": [
                {
                    "category": "observation",
                    "title": f"Observation {i + 1}",
                    "detail": f"Detail for observation {i + 1}.",
                    "priority": "medium",
                }
                for i in range(count)
            ],
        }
    )


def _patch_llm(monkeypatch, mock_call_fn):
    client = MagicMock()
    client.call = mock_call_fn
    client.estimate_tokens = MagicMock(return_value=50)
    client.model = "mock"
    monkeypatch.setattr(
        "app.services.artifact_sync._get_llm_client",
        AsyncMock(return_value=client),
    )
    return client


# ============================================================
# update_lpd_from_suggestion — SECTION MAPPING
# ============================================================


class TestUpdateLPDFromSuggestion:
    @pytest.mark.asyncio
    async def test_risks_maps_to_lpd_risks(self):
        """Artifact 'Risks' section maps to LPD 'Risks'."""
        await initialize_lpd(PROJECT_ID)
        result = await update_lpd_from_suggestion(
            PROJECT_ID, "Risks", "- Vendor API may be delayed"
        )
        assert result is True
        lpd = await get_full_lpd(PROJECT_ID)
        assert "Vendor API may be delayed" in lpd["Risks"]

    @pytest.mark.asyncio
    async def test_decisions_maps_to_lpd_decisions(self):
        """Artifact 'Decisions' section maps to LPD 'Decisions'."""
        await initialize_lpd(PROJECT_ID)
        result = await update_lpd_from_suggestion(
            PROJECT_ID, "Decisions", "D5: Chose PostgreSQL for production"
        )
        assert result is True
        lpd = await get_full_lpd(PROJECT_ID)
        assert "Chose PostgreSQL for production" in lpd["Decisions"]

    @pytest.mark.asyncio
    async def test_action_items_maps_to_open_questions(self):
        """Artifact 'Action Items' section maps to LPD 'Open Questions'."""
        await initialize_lpd(PROJECT_ID)
        result = await update_lpd_from_suggestion(
            PROJECT_ID, "Action Items", "- Follow up on contract review"
        )
        assert result is True
        lpd = await get_full_lpd(PROJECT_ID)
        assert "Follow up on contract review" in lpd["Open Questions"]

    @pytest.mark.asyncio
    async def test_accomplishments_maps_to_overview(self):
        """Artifact 'Accomplishments' section maps to LPD 'Overview'."""
        await initialize_lpd(PROJECT_ID)
        result = await update_lpd_from_suggestion(
            PROJECT_ID, "Accomplishments", "- Completed database migration"
        )
        assert result is True
        lpd = await get_full_lpd(PROJECT_ID)
        assert "Completed database migration" in lpd["Overview"]

    @pytest.mark.asyncio
    async def test_blockers_maps_to_risks(self):
        """Artifact 'Blockers' section maps to LPD 'Risks'."""
        await initialize_lpd(PROJECT_ID)
        result = await update_lpd_from_suggestion(
            PROJECT_ID, "Blockers", "- Waiting on security review approval"
        )
        assert result is True
        lpd = await get_full_lpd(PROJECT_ID)
        assert "Waiting on security review approval" in lpd["Risks"]

    @pytest.mark.asyncio
    async def test_case_insensitive_mapping(self):
        """Section mapping is case-insensitive."""
        await initialize_lpd(PROJECT_ID)
        result = await update_lpd_from_suggestion(PROJECT_ID, "ACTION ITEMS", "- Review proposal")
        assert result is True
        lpd = await get_full_lpd(PROJECT_ID)
        assert "Review proposal" in lpd["Open Questions"]

    @pytest.mark.asyncio
    async def test_unmapped_section_returns_false(self):
        """Sections without an LPD mapping are silently skipped."""
        await initialize_lpd(PROJECT_ID)
        result = await update_lpd_from_suggestion(PROJECT_ID, "Attendees", "- Alice, Bob")
        assert result is False

    @pytest.mark.asyncio
    async def test_no_lpd_returns_false(self):
        """Does nothing when LPD is not initialized."""
        result = await update_lpd_from_suggestion(PROJECT_ID, "Risks", "- Some risk")
        assert result is False

    @pytest.mark.asyncio
    async def test_duplicate_text_not_appended(self):
        """Same text is not appended twice to the LPD section."""
        await initialize_lpd(PROJECT_ID)
        await update_lpd_from_suggestion(PROJECT_ID, "Risks", "- Budget risk")
        result = await update_lpd_from_suggestion(PROJECT_ID, "Risks", "- Budget risk")
        assert result is False
        lpd = await get_full_lpd(PROJECT_ID)
        assert lpd["Risks"].count("- Budget risk") == 1

    @pytest.mark.asyncio
    async def test_multiple_updates_accumulate(self):
        """Multiple different suggestions accumulate in the LPD."""
        await initialize_lpd(PROJECT_ID)
        await update_lpd_from_suggestion(PROJECT_ID, "Risks", "- Risk A")
        await update_lpd_from_suggestion(PROJECT_ID, "Risks", "- Risk B")
        lpd = await get_full_lpd(PROJECT_ID)
        assert "- Risk A" in lpd["Risks"]
        assert "- Risk B" in lpd["Risks"]


# ============================================================
# SECTION MAPPING CONSTANT
# ============================================================


class TestSectionMappingConstant:
    def test_all_expected_mappings_exist(self):
        """Verify all documented mappings are present."""
        assert ARTIFACT_SECTION_TO_LPD["risks"] == "Risks"
        assert ARTIFACT_SECTION_TO_LPD["decisions"] == "Decisions"
        assert ARTIFACT_SECTION_TO_LPD["action items"] == "Open Questions"
        assert ARTIFACT_SECTION_TO_LPD["accomplishments"] == "Overview"
        assert ARTIFACT_SECTION_TO_LPD["blockers"] == "Risks"


# ============================================================
# generate_session_summary
# ============================================================


class TestGenerateSessionSummary:
    def test_extract_mode_with_suggestions(self):
        suggestions = [
            _make_suggestion(artifact_type="RAID Log"),
            _make_suggestion(artifact_type="RAID Log"),
            _make_suggestion(artifact_type="Status Report", section="Accomplishments"),
        ]
        summary = generate_session_summary(suggestions, input_type="meeting_notes")
        assert "meeting notes" in summary
        assert "2 RAID Log" in summary
        assert "1 Status Report" in summary

    def test_extract_mode_no_suggestions(self):
        summary = generate_session_summary([], input_type="transcript")
        assert "transcript" in summary
        assert "no suggestions" in summary

    def test_analyze_mode(self):
        from app.models.schemas import AnalysisItem

        items = [
            AnalysisItem(
                category="observation",
                title="Test",
                detail="Detail",
                priority="medium",
            )
        ] * 4
        summary = generate_session_summary(
            [], analysis_items=items, input_type="status_update", mode="analyze"
        )
        assert "Analyzed" in summary
        assert "4 observation(s)" in summary
        assert "status update" in summary

    def test_analyze_mode_no_items(self):
        summary = generate_session_summary(
            [], analysis_items=[], input_type="general_text", mode="analyze"
        )
        assert "0 observation(s)" in summary


# ============================================================
# SESSION SUMMARY LOGGED DURING ARTIFACT SYNC
# ============================================================


class TestSessionSummaryInPipeline:
    @pytest.mark.asyncio
    async def test_extract_logs_session_summary(self, monkeypatch):
        """Extract mode generates and logs a session summary."""
        await initialize_lpd(PROJECT_ID)

        call_count = [0]

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_count[0] += 1
            if call_count[0] == 1:
                return "meeting_notes"
            return _mock_suggestions_json(2)

        _patch_llm(monkeypatch, mock_call)

        await run_artifact_sync("Sprint review notes.", project_id=PROJECT_ID)

        # Session summary should have been logged
        count = await get_session_summary_count(PROJECT_ID)
        assert count == 1

        # Recent Context should reflect the summary
        lpd = await get_full_lpd(PROJECT_ID)
        assert "RAID Log" in lpd["Recent Context"]

    @pytest.mark.asyncio
    async def test_analyze_logs_session_summary(self, monkeypatch):
        """Analyze mode generates and logs a session summary."""
        await initialize_lpd(PROJECT_ID)

        call_count = [0]

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_count[0] += 1
            if call_count[0] == 1:
                return "general_text"
            return _mock_analysis_json(3)

        _patch_llm(monkeypatch, mock_call)

        await run_artifact_sync("Review this draft.", project_id=PROJECT_ID, mode="analyze")

        count = await get_session_summary_count(PROJECT_ID)
        assert count == 1

        lpd = await get_full_lpd(PROJECT_ID)
        assert "Analyzed" in lpd["Recent Context"]

    @pytest.mark.asyncio
    async def test_summary_logged_even_without_lpd(self, monkeypatch):
        """Session summary is logged even when LPD doesn't exist (for future use)."""
        call_count = [0]

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_count[0] += 1
            if call_count[0] == 1:
                return "general_text"
            return "[]"

        _patch_llm(monkeypatch, mock_call)

        await run_artifact_sync("Some text.", project_id=PROJECT_ID)

        count = await get_session_summary_count(PROJECT_ID)
        assert count == 1

    @pytest.mark.asyncio
    async def test_multiple_syncs_accumulate_summaries(self, monkeypatch):
        """Multiple artifact sync calls accumulate session summaries."""
        await initialize_lpd(PROJECT_ID)

        call_count = [0]

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_count[0] += 1
            if call_count[0] % 2 == 1:
                return "meeting_notes"
            return _mock_suggestions_json(1)

        _patch_llm(monkeypatch, mock_call)

        await run_artifact_sync("First session.", project_id=PROJECT_ID)
        await run_artifact_sync("Second session.", project_id=PROJECT_ID)

        count = await get_session_summary_count(PROJECT_ID)
        assert count == 2


# ============================================================
# RETURN PATH VIA API ENDPOINT
# ============================================================


class TestReturnPathViaAPI:
    @pytest.mark.asyncio
    async def test_apply_by_type_updates_lpd(self):
        """apply_suggestion_by_type triggers LPD update for mapped sections."""
        from app.main import app
        from httpx import ASGITransport, AsyncClient

        await initialize_lpd(PROJECT_ID)

        # Create the RAID Log artifact first
        await get_or_create_artifact(PROJECT_ID, ArtifactType.RAID_LOG)

        suggestion = {
            "artifact_type": "RAID Log",
            "change_type": "add",
            "section": "Risks",
            "proposed_text": "- API vendor may delay Q3 milestone",
            "confidence": 0.9,
            "reasoning": "Mentioned in standup notes.",
        }

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/artifacts/apply",
                json=suggestion,
                params={"project_id": PROJECT_ID},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "applied"
        assert data["lpd_updated"] is True

        lpd = await get_full_lpd(PROJECT_ID)
        assert "API vendor may delay Q3 milestone" in lpd["Risks"]

    @pytest.mark.asyncio
    async def test_apply_by_type_no_lpd_no_error(self):
        """apply_suggestion_by_type works normally when LPD doesn't exist."""
        from app.main import app
        from httpx import ASGITransport, AsyncClient

        # No LPD initialized — should still apply to artifact without error
        await get_or_create_artifact(PROJECT_ID, ArtifactType.STATUS_REPORT)

        suggestion = {
            "artifact_type": "Status Report",
            "change_type": "add",
            "section": "Accomplishments",
            "proposed_text": "- Deployed v2.0 to staging",
            "confidence": 0.85,
            "reasoning": "Stated in update.",
        }

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/artifacts/apply",
                json=suggestion,
                params={"project_id": PROJECT_ID},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "applied"
        assert data["lpd_updated"] is False
