"""Tests for VPMA AI Risk Prediction Engine.

Tests cover: prediction parsing, pipeline orchestration, privacy proxy,
session logging, health assessment, and edge cases.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.risk_prediction import (
    _assess_project_health,
    _build_lpd_block,
    _build_staleness_block,
    _parse_predictions,
    predict_risks,
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
            {"section_name": "Overview", "days_since_update": 3},
            {"section_name": "Risks", "days_since_update": 15},
        ]
        block = _build_staleness_block(staleness)
        assert "Overview | 3" in block
        assert "Risks | 15" in block


# ============================================================
# PREDICTION PARSING
# ============================================================


class TestParsePredictions:
    def test_parses_valid_predictions(self):
        response = json.dumps(
            [
                {
                    "description": "Timeline risk due to dependency chain",
                    "severity": "high",
                    "evidence": "Milestones section shows 3 sequential dependencies",
                    "confidence": 0.85,
                    "suggested_raid_entry": "R-NEW | Timeline risk | High",
                    "category": "timeline",
                }
            ]
        )
        result = _parse_predictions(response)
        assert len(result) == 1
        assert result[0].severity == "high"
        assert result[0].category == "timeline"

    def test_returns_empty_on_invalid_json(self):
        assert _parse_predictions("Not JSON at all") == []

    def test_returns_empty_on_no_array(self):
        assert _parse_predictions('{"key": "value"}') == []

    def test_parses_empty_array(self):
        assert _parse_predictions("[]") == []

    def test_strips_code_fences(self):
        response = '```json\n[{"description": "Risk", "severity": "low", "evidence": "e", "confidence": 0.5, "suggested_raid_entry": "entry", "category": "scope"}]\n```'
        result = _parse_predictions(response)
        assert len(result) == 1

    def test_skips_malformed_items(self):
        response = json.dumps(
            [
                {
                    "description": "Valid risk",
                    "severity": "medium",
                    "evidence": "evidence",
                    "confidence": 0.7,
                    "suggested_raid_entry": "entry",
                    "category": "resource",
                },
                {"bad": "item"},
            ]
        )
        result = _parse_predictions(response)
        assert len(result) == 1


# ============================================================
# PROJECT HEALTH ASSESSMENT
# ============================================================


class TestProjectHealth:
    def test_healthy_project(self):
        sections = {"Overview": "content", "Risks": "content"}
        staleness = [{"days_since_update": 2}, {"days_since_update": 5}]
        health = _assess_project_health(sections, staleness, [])
        assert health == "healthy"

    def test_needs_attention_with_high_risk(self):
        pred = MagicMock(severity="high")
        health = _assess_project_health({}, [{"days_since_update": 1}], [pred])
        assert health == "needs_attention"

    def test_needs_attention_with_stale_sections(self):
        staleness = [
            {"days_since_update": 14},
            {"days_since_update": 16},
        ]
        health = _assess_project_health({"A": "x"}, staleness, [])
        assert health == "needs_attention"

    def test_at_risk_with_many_high_risks(self):
        preds = [MagicMock(severity="high")] * 3
        health = _assess_project_health({}, [{"days_since_update": 1}], preds)
        assert health == "at_risk"

    def test_at_risk_with_many_stale_sections(self):
        staleness = [{"days_since_update": 20}] * 4
        health = _assess_project_health({"A": "x"}, staleness, [])
        assert health == "at_risk"

    def test_needs_attention_with_empty_sections(self):
        sections = {"A": "", "B": "", "C": ""}
        health = _assess_project_health(sections, [{"days_since_update": 1}], [])
        assert health == "needs_attention"


# ============================================================
# FULL PIPELINE (Mocked LLM)
# ============================================================


class TestPredictRisks:
    @pytest.fixture
    def mock_llm_client(self):
        client = AsyncMock()
        client.estimate_tokens = MagicMock(return_value=100)
        client.model = "test-model"
        return client

    @pytest.fixture
    def llm_response(self):
        return json.dumps(
            [
                {
                    "description": "Timeline risk: Phase 2 milestone has no buffer",
                    "severity": "high",
                    "evidence": "Timeline & Milestones section",
                    "confidence": 0.85,
                    "suggested_raid_entry": "R-NEW | Timeline risk | High | Add buffer",
                    "category": "timeline",
                }
            ]
        )

    @pytest.mark.asyncio
    async def test_full_pipeline(self, mock_llm_client, llm_response):
        mock_llm_client.call = AsyncMock(return_value=llm_response)

        mock_session = MagicMock()
        mock_session.session_id = "risk-session-1"

        with (
            patch("app.services.risk_prediction.get_llm_client", return_value=mock_llm_client),
            patch("app.services.risk_prediction.get_custom_terms", return_value=[]),
            patch(
                "app.services.risk_prediction.get_full_lpd",
                return_value={"Overview": "Project overview", "Risks": "No risks yet"},
            ),
            patch(
                "app.services.risk_prediction.get_section_staleness",
                return_value=[
                    {"section_name": "Overview", "days_since_update": 3},
                    {"section_name": "Risks", "days_since_update": 7},
                ],
            ),
            patch("app.services.risk_prediction.anonymize") as mock_anon,
            patch("app.services.risk_prediction.reidentify", side_effect=lambda x: x),
            patch("app.services.risk_prediction.create_session", return_value=mock_session),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon text", entities=[])

            result = await predict_risks(project_id="test-proj")

        assert result.session_id == "risk-session-1"
        assert len(result.predictions) == 1
        assert result.predictions[0].category == "timeline"
        assert result.project_health in ("healthy", "needs_attention", "at_risk")

    @pytest.mark.asyncio
    async def test_empty_lpd_returns_early(self, mock_llm_client):
        with (
            patch("app.services.risk_prediction.get_llm_client", return_value=mock_llm_client),
            patch("app.services.risk_prediction.get_custom_terms", return_value=[]),
            patch("app.services.risk_prediction.get_full_lpd", return_value={}),
            patch("app.services.risk_prediction.get_section_staleness", return_value=[]),
        ):
            result = await predict_risks(project_id="empty-proj")

        assert result.predictions == []
        assert result.project_health == "unknown"
        assert result.session_id == ""
        # LLM should not be called for empty LPD
        mock_llm_client.call.assert_not_called()

    @pytest.mark.asyncio
    async def test_anonymizes_all_content(self, mock_llm_client, llm_response):
        mock_llm_client.call = AsyncMock(return_value=llm_response)

        mock_session = MagicMock()
        mock_session.session_id = "s1"

        with (
            patch("app.services.risk_prediction.get_llm_client", return_value=mock_llm_client),
            patch("app.services.risk_prediction.get_custom_terms", return_value=["secret"]),
            patch(
                "app.services.risk_prediction.get_full_lpd",
                return_value={"Overview": "content A", "Risks": "content B"},
            ),
            patch(
                "app.services.risk_prediction.get_section_staleness",
                return_value=[],
            ),
            patch("app.services.risk_prediction.anonymize") as mock_anon,
            patch("app.services.risk_prediction.reidentify", side_effect=lambda x: x),
            patch("app.services.risk_prediction.create_session", return_value=mock_session),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="redacted", entities=[MagicMock()])

            result = await predict_risks()

        # anonymize called once per non-empty section
        assert mock_anon.call_count == 2
        assert result.pii_detected == 2

    @pytest.mark.asyncio
    async def test_reidentifies_outputs(self, mock_llm_client, llm_response):
        mock_llm_client.call = AsyncMock(return_value=llm_response)

        mock_session = MagicMock()
        mock_session.session_id = "s1"

        async def tracking_reidentify(text):
            return f"REID:{text}"

        with (
            patch("app.services.risk_prediction.get_llm_client", return_value=mock_llm_client),
            patch("app.services.risk_prediction.get_custom_terms", return_value=[]),
            patch(
                "app.services.risk_prediction.get_full_lpd",
                return_value={"Overview": "content"},
            ),
            patch("app.services.risk_prediction.get_section_staleness", return_value=[]),
            patch("app.services.risk_prediction.anonymize") as mock_anon,
            patch("app.services.risk_prediction.reidentify", side_effect=tracking_reidentify),
            patch("app.services.risk_prediction.create_session", return_value=mock_session),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon", entities=[])

            result = await predict_risks()

        assert result.predictions[0].description.startswith("REID:")
        assert result.predictions[0].evidence.startswith("REID:")

    @pytest.mark.asyncio
    async def test_logs_session(self, mock_llm_client, llm_response):
        mock_llm_client.call = AsyncMock(return_value=llm_response)

        mock_session = MagicMock()
        mock_session.session_id = "logged-session"

        with (
            patch("app.services.risk_prediction.get_llm_client", return_value=mock_llm_client),
            patch("app.services.risk_prediction.get_custom_terms", return_value=[]),
            patch(
                "app.services.risk_prediction.get_full_lpd",
                return_value={"Overview": "content"},
            ),
            patch("app.services.risk_prediction.get_section_staleness", return_value=[]),
            patch("app.services.risk_prediction.anonymize") as mock_anon,
            patch("app.services.risk_prediction.reidentify", side_effect=lambda x: x),
            patch("app.services.risk_prediction.create_session") as mock_create,
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon", entities=[])
            mock_create.return_value = mock_session

            await predict_risks(project_id="proj-123")

        mock_create.assert_called_once()
        session_arg = mock_create.call_args[0][0]
        assert session_arg.project_id == "proj-123"
        assert session_arg.tab_used == "risk_prediction"

    @pytest.mark.asyncio
    async def test_handles_empty_predictions(self, mock_llm_client):
        mock_llm_client.call = AsyncMock(return_value="[]")
        mock_llm_client.estimate_tokens = MagicMock(return_value=50)
        mock_llm_client.model = "test"

        mock_session = MagicMock()
        mock_session.session_id = "empty-preds"

        with (
            patch("app.services.risk_prediction.get_llm_client", return_value=mock_llm_client),
            patch("app.services.risk_prediction.get_custom_terms", return_value=[]),
            patch(
                "app.services.risk_prediction.get_full_lpd",
                return_value={"Overview": "healthy project"},
            ),
            patch("app.services.risk_prediction.get_section_staleness", return_value=[]),
            patch("app.services.risk_prediction.anonymize") as mock_anon,
            patch("app.services.risk_prediction.reidentify", side_effect=lambda x: x),
            patch("app.services.risk_prediction.create_session", return_value=mock_session),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon", entities=[])

            result = await predict_risks()

        assert result.predictions == []
        assert result.project_health == "healthy"
