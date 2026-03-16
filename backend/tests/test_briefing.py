"""Tests for VPMA Morning Briefing Service (Task 59).

Tests cover: prompt building, response parsing, cache logic, privacy proxy,
empty project handling, and the full pipeline with mocked LLM.
"""

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.models.schemas import (
    BriefingAttentionItem,
    BriefingContradiction,
    BriefingResponse,
    BriefingUpcomingDate,
)
from app.services.briefing_service import (
    _build_activity_block,
    _build_cached_results_block,
    _build_lpd_block,
    _build_staleness_block,
    _parse_briefing,
    _strip_code_fences,
    generate_briefing,
)

# ============================================================
# HELPER BUILDERS
# ============================================================


class TestBuildLPDBlock:
    def test_formats_sections(self):
        sections = {"Overview": "Project overview", "Risks": "Some risks"}
        block = _build_lpd_block(sections)
        assert "Section: Overview" in block
        assert "Project overview" in block
        assert "End: Overview" in block

    def test_marks_empty_sections(self):
        sections = {"Overview": "", "Risks": None}
        block = _build_lpd_block(sections)
        assert "(empty)" in block


class TestBuildStalenessBlock:
    def test_formats_table(self):
        staleness = [
            {"section_name": "Overview", "days_since_update": 3, "has_content": True},
            {"section_name": "Risks", "days_since_update": 15, "has_content": False},
        ]
        block = _build_staleness_block(staleness)
        assert "Overview | 3 | Yes" in block
        assert "Risks | 15 | No" in block


class TestBuildActivityBlock:
    def test_formats_sessions(self):
        sessions = [
            MagicMock(
                tab_used="process",
                timestamp=datetime(2026, 3, 14, tzinfo=timezone.utc),
                user_input="Processed meeting notes",
            )
        ]
        block = _build_activity_block(sessions)
        assert "2026-03-14" in block
        assert "process" in block
        assert "meeting notes" in block

    def test_empty_sessions(self):
        block = _build_activity_block([])
        assert "No recent activity" in block


class TestBuildCachedResultsBlock:
    def test_extracts_risk_prediction(self):
        sessions = [
            MagicMock(
                tab_used="risk_prediction",
                agent_output='{"predictions": []}',
                timestamp="2026-03-14T10:00:00",
            )
        ]
        block = _build_cached_results_block(sessions)
        assert "Risk Prediction" in block

    def test_no_cached_results(self):
        sessions = [
            MagicMock(tab_used="process", agent_output='{"suggestions": []}'),
        ]
        block = _build_cached_results_block(sessions)
        assert "No cached analysis results" in block


# ============================================================
# RESPONSE PARSING
# ============================================================


class TestStripCodeFences:
    def test_strips_json_fences(self):
        text = '```json\n{"key": "value"}\n```'
        assert _strip_code_fences(text) == '{"key": "value"}'

    def test_no_fences(self):
        text = '{"key": "value"}'
        assert _strip_code_fences(text) == '{"key": "value"}'


class TestParseBriefing:
    def test_parses_valid_briefing(self):
        response = json.dumps(
            {
                "attention_items": [
                    {
                        "title": "Stale Timeline",
                        "detail": "Timeline section is 12 days old",
                        "source_section": "Timeline & Milestones",
                        "severity": "high",
                        "category": "staleness",
                    }
                ],
                "upcoming_dates": [
                    {
                        "description": "API milestone",
                        "date_text": "March 20",
                        "source_section": "Timeline & Milestones",
                        "urgency": "imminent",
                    }
                ],
                "contradictions": [],
                "suggested_next_action": "Update Timeline section first.",
            }
        )
        result = _parse_briefing(response)
        assert len(result["attention_items"]) == 1
        assert result["attention_items"][0]["severity"] == "high"
        assert len(result["upcoming_dates"]) == 1
        assert result["suggested_next_action"] == "Update Timeline section first."

    def test_returns_empty_on_invalid_json(self):
        assert _parse_briefing("Not JSON at all") == {}

    def test_returns_empty_on_no_object(self):
        assert _parse_briefing("[1, 2, 3]") == {}

    def test_handles_code_fenced_response(self):
        response = '```json\n{"attention_items": [], "suggested_next_action": "All good"}\n```'
        result = _parse_briefing(response)
        assert result["suggested_next_action"] == "All good"

    def test_handles_malformed_items(self):
        response = json.dumps(
            {
                "attention_items": [
                    {
                        "title": "Good item",
                        "detail": "OK",
                        "source_section": "Risks",
                        "severity": "low",
                        "category": "risk",
                    },
                    {"bad": "missing required fields"},
                ],
                "suggested_next_action": "Do stuff",
            }
        )
        result = _parse_briefing(response)
        assert "attention_items" in result
        # The raw dict is returned — validation happens in generate_briefing
        assert len(result["attention_items"]) == 2


# ============================================================
# PYDANTIC MODELS
# ============================================================


class TestBriefingModels:
    def test_attention_item_creation(self):
        item = BriefingAttentionItem(
            title="Stale data",
            detail="Overview is 14 days old",
            source_section="Overview",
            severity="high",
            category="staleness",
        )
        assert item.severity == "high"

    def test_upcoming_date_creation(self):
        item = BriefingUpcomingDate(
            description="Release date",
            date_text="April 1",
            source_section="Timeline & Milestones",
            urgency="upcoming",
        )
        assert item.urgency == "upcoming"

    def test_contradiction_creation(self):
        item = BriefingContradiction(
            description="Phase 2 date mismatch",
            section_a="Timeline & Milestones",
            section_b="Decisions",
            suggested_resolution="Align dates",
        )
        assert item.section_a == "Timeline & Milestones"

    def test_briefing_response_defaults(self):
        resp = BriefingResponse()
        assert resp.attention_items == []
        assert resp.upcoming_dates == []
        assert resp.contradictions == []
        assert resp.from_cache is False


# ============================================================
# FULL PIPELINE (mocked LLM)
# ============================================================


class TestGenerateBriefing:
    @pytest.mark.asyncio
    async def test_empty_project_returns_guidance(self):
        """Projects with no LPD return helpful empty state."""
        with (
            patch("app.services.briefing_service.get_llm_client"),
            patch("app.services.briefing_service.get_custom_terms", return_value=[]),
            patch("app.services.briefing_service.get_full_lpd", return_value={}),
            patch("app.services.briefing_service.get_section_staleness", return_value=[]),
            patch("app.services.briefing_service.get_sessions_by_project", return_value=[]),
            patch("app.services.briefing_service._get_cached_briefing", return_value=None),
        ):
            result = await generate_briefing("default", force_refresh=True)
            assert "No project data" in result.suggested_next_action
            assert result.attention_items == []

    @pytest.mark.asyncio
    async def test_cached_briefing_returned(self):
        """Cached briefing is returned when fresh."""
        cached = BriefingResponse(
            attention_items=[],
            upcoming_dates=[],
            contradictions=[],
            suggested_next_action="Cached action",
            generated_at="2026-03-16T10:00:00",
            session_id="cached-session",
            from_cache=True,
        )
        with patch("app.services.briefing_service._get_cached_briefing", return_value=cached):
            # Note: from_cache field is set on the cached response
            result = await generate_briefing("default", force_refresh=False)
            assert result.suggested_next_action == "Cached action"

    @pytest.mark.asyncio
    async def test_full_pipeline_with_llm(self):
        """Full pipeline: LPD → anonymize → LLM → parse → reidentify → session."""
        mock_client = AsyncMock()
        mock_client.call = AsyncMock(
            return_value=json.dumps(
                {
                    "attention_items": [
                        {
                            "title": "Stale risks",
                            "detail": "Risks section is 10 days old",
                            "source_section": "Risks",
                            "severity": "medium",
                            "category": "staleness",
                        }
                    ],
                    "upcoming_dates": [],
                    "contradictions": [],
                    "suggested_next_action": "Update Risks section.",
                }
            )
        )
        mock_client.estimate_tokens = MagicMock(return_value=500)
        mock_client.model = "test-model"

        mock_session = MagicMock()
        mock_session.session_id = "test-session-id"

        anon_result = MagicMock()
        anon_result.anonymized_text = "anonymized content"
        anon_result.entities = []

        with (
            patch("app.services.briefing_service.get_llm_client", return_value=mock_client),
            patch("app.services.briefing_service.get_custom_terms", return_value=[]),
            patch(
                "app.services.briefing_service.get_full_lpd",
                return_value={"Overview": "Test project", "Risks": "Some risks"},
            ),
            patch(
                "app.services.briefing_service.get_section_staleness",
                return_value=[
                    {"section_name": "Overview", "days_since_update": 1, "has_content": True},
                    {"section_name": "Risks", "days_since_update": 10, "has_content": True},
                ],
            ),
            patch("app.services.briefing_service.get_sessions_by_project", return_value=[]),
            patch("app.services.briefing_service._get_cached_briefing", return_value=None),
            patch("app.services.briefing_service.anonymize", return_value=anon_result),
            patch("app.services.briefing_service.reidentify", side_effect=lambda x: x),
            patch("app.services.briefing_service.create_session", return_value=mock_session),
        ):
            result = await generate_briefing("default", force_refresh=True)

            assert len(result.attention_items) == 1
            assert result.attention_items[0].title == "Stale risks"
            assert result.suggested_next_action == "Update Risks section."
            assert result.session_id == "test-session-id"
            assert result.from_cache is False
            mock_client.call.assert_called_once()
