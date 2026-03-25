"""Tests for the Skeptical Reviewer service (Phase 3C)."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.models.schemas import ReviewFinding, SkepticalReviewResponse
from app.services.skeptical_reviewer import (
    _build_lpd_block,
    _build_staleness_block,
    _filter_quality,
    _parse_findings,
    _strip_code_fences,
    skeptical_review,
)

# --- Helper / Parser Tests ---


class TestStripCodeFences:
    def test_strips_json_fences(self):
        text = '```json\n[{"a": 1}]\n```'
        assert _strip_code_fences(text) == '[{"a": 1}]'

    def test_no_fences(self):
        text = '[{"a": 1}]'
        assert _strip_code_fences(text) == '[{"a": 1}]'

    def test_plain_fences(self):
        text = "```\nhello\n```"
        assert _strip_code_fences(text) == "hello"


class TestBuildLPDBlock:
    def test_formats_sections(self):
        sections = {"Overview": "Project X", "Risks": "Risk A"}
        result = _build_lpd_block(sections)
        assert "--- Section: Overview ---" in result
        assert "Project X" in result
        assert "--- End: Risks ---" in result

    def test_empty_section_shows_placeholder(self):
        sections = {"Overview": ""}
        result = _build_lpd_block(sections)
        assert "(empty)" in result


class TestBuildStalenessBlock:
    def test_formats_staleness_table(self):
        staleness = [
            {"section_name": "Overview", "days_since_update": 5},
            {"section_name": "Risks", "days_since_update": 21},
        ]
        result = _build_staleness_block(staleness)
        assert "Overview | 5" in result
        assert "Risks | 21" in result
        assert "---|---" in result


class TestParseFindings:
    VALID_FINDING = {
        "category": "contradiction",
        "severity": "high",
        "title": "Timeline conflict between Overview and Milestones",
        "description": "The Overview states Phase 2 starts March 15 but Timeline section shows April 1.",
        "evidence": "Overview: 'Phase 2 begins March 15' vs Timeline: 'Phase 2 target: April 1'",
        "recommendation": "Align the dates — confirm with sponsor which is correct.",
    }

    def test_parses_valid_json_array(self):
        response = json.dumps([self.VALID_FINDING])
        findings = _parse_findings(response)
        assert len(findings) == 1
        assert findings[0].category == "contradiction"
        assert findings[0].severity == "high"

    def test_parses_with_code_fences(self):
        response = f"```json\n{json.dumps([self.VALID_FINDING])}\n```"
        findings = _parse_findings(response)
        assert len(findings) == 1

    def test_handles_invalid_json(self):
        findings = _parse_findings("not json at all")
        assert findings == []

    def test_skips_malformed_items(self):
        data = [self.VALID_FINDING, {"bad": "item"}]
        findings = _parse_findings(json.dumps(data))
        assert len(findings) == 1

    def test_handles_empty_array(self):
        findings = _parse_findings("[]")
        assert findings == []

    def test_extracts_from_surrounding_text(self):
        response = f"Here are findings:\n{json.dumps([self.VALID_FINDING])}\nDone."
        findings = _parse_findings(response)
        assert len(findings) == 1

    def test_multiple_findings(self):
        finding2 = {
            **self.VALID_FINDING,
            "category": "blind_spot",
            "title": "No data quality strategy",
        }
        response = json.dumps([self.VALID_FINDING, finding2])
        findings = _parse_findings(response)
        assert len(findings) == 2


class TestFilterQuality:
    def _make_finding(self, **overrides):
        base = {
            "category": "contradiction",
            "severity": "high",
            "title": "Test finding",
            "description": "A detailed description of the finding with enough context.",
            "evidence": "Overview: 'stated X' vs Risks: 'stated Y'",
            "recommendation": "Fix this.",
        }
        base.update(overrides)
        return ReviewFinding(**base)

    def test_keeps_quality_findings(self):
        findings = [self._make_finding()]
        result = _filter_quality(findings)
        assert len(result) == 1

    def test_removes_empty_evidence(self):
        findings = [self._make_finding(evidence="")]
        result = _filter_quality(findings)
        assert len(result) == 0

    def test_removes_short_evidence(self):
        findings = [self._make_finding(evidence="short")]
        result = _filter_quality(findings)
        assert len(result) == 0

    def test_removes_vague_description(self):
        findings = [self._make_finding(description="too short")]
        result = _filter_quality(findings)
        assert len(result) == 0

    def test_mixed_quality(self):
        good = self._make_finding()
        bad = self._make_finding(evidence="x")
        result = _filter_quality([good, bad])
        assert len(result) == 1


# --- Service Integration Tests ---


SAMPLE_LLM_RESPONSE = json.dumps(
    [
        {
            "category": "contradiction",
            "severity": "high",
            "title": "Phase 2 date conflict",
            "description": "Overview says Phase 2 starts March 15 but Timeline section says April 1. This 2-week gap could cascade to downstream milestones.",
            "evidence": "Overview: 'Phase 2 begins March 15' vs Timeline & Milestones: 'Phase 2 target: April 1'",
            "recommendation": "Confirm Phase 2 start date with sponsor and update both sections.",
        },
        {
            "category": "blind_spot",
            "severity": "medium",
            "title": "No data validation strategy",
            "description": "Project integrates 6 source systems but has no documented data quality validation approach.",
            "evidence": "Overview: '6 source system integrations' — Risks section has no mention of data quality risks",
            "recommendation": "Add data validation checkpoints to the Timeline for each source system integration.",
        },
    ]
)


class TestSkepticalReviewService:
    """Integration tests for the skeptical_review() function."""

    @pytest.fixture
    def mock_llm_client(self):
        client = AsyncMock()
        client.call = AsyncMock(return_value=SAMPLE_LLM_RESPONSE)
        client.estimate_tokens = MagicMock(return_value=500)
        client.model = "test-model"
        return client

    @pytest.fixture
    def mock_sections(self):
        return {
            "Overview": "Project integrates 6 source systems. Phase 2 begins March 15.",
            "Stakeholders": "PM: Jordan Rivera, Lead Dev: Alex Chen",
            "Timeline & Milestones": "Phase 1: Feb — Phase 2 target: April 1",
            "Risks": "R1: Vendor dependency on CloudPlatform",
            "Decisions": "D1: Use DataCloud for warehouse",
            "Open Questions": "Q1: Budget for Phase 3?",
            "Recent Context": "Sprint 4 completed. Phase 1 on track.",
        }

    @pytest.fixture
    def mock_staleness(self):
        return [
            {"section_name": "Overview", "days_since_update": 3},
            {"section_name": "Risks", "days_since_update": 18},
            {"section_name": "Open Questions", "days_since_update": 25},
        ]

    @pytest.mark.asyncio
    async def test_full_pipeline(self, tmp_database, mock_llm_client, mock_sections, mock_staleness):
        with (
            patch("app.services.skeptical_reviewer.get_llm_client", return_value=mock_llm_client),
            patch("app.services.skeptical_reviewer.get_custom_terms", return_value=[]),
            patch("app.services.skeptical_reviewer.get_full_lpd", return_value=mock_sections),
            patch("app.services.skeptical_reviewer.get_section_staleness", return_value=mock_staleness),
            patch("app.services.skeptical_reviewer.anonymize") as mock_anon,
            patch("app.services.skeptical_reviewer.reidentify", side_effect=lambda x: x),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon text", entities=[])
            result = await skeptical_review(project_id="default")

        assert isinstance(result, SkepticalReviewResponse)
        assert len(result.findings) == 2
        assert result.findings[0].category == "contradiction"
        assert result.findings[1].category == "blind_spot"
        assert result.sections_analyzed == 7
        assert result.session_id != ""

    @pytest.mark.asyncio
    async def test_empty_lpd_returns_empty(self, tmp_database, mock_llm_client):
        with (
            patch("app.services.skeptical_reviewer.get_llm_client", return_value=mock_llm_client),
            patch("app.services.skeptical_reviewer.get_custom_terms", return_value=[]),
            patch("app.services.skeptical_reviewer.get_full_lpd", return_value={}),
            patch("app.services.skeptical_reviewer.get_section_staleness", return_value=[]),
        ):
            result = await skeptical_review(project_id="default")

        assert result.findings == []
        assert result.sections_analyzed == 0
        assert result.session_id == ""

    @pytest.mark.asyncio
    async def test_privacy_proxy_applied(self, tmp_database, mock_llm_client, mock_sections, mock_staleness):
        with (
            patch("app.services.skeptical_reviewer.get_llm_client", return_value=mock_llm_client),
            patch("app.services.skeptical_reviewer.get_custom_terms", return_value=[]),
            patch("app.services.skeptical_reviewer.get_full_lpd", return_value=mock_sections),
            patch("app.services.skeptical_reviewer.get_section_staleness", return_value=mock_staleness),
            patch("app.services.skeptical_reviewer.anonymize") as mock_anon,
            patch("app.services.skeptical_reviewer.reidentify") as mock_reiden,
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon", entities=["PII1"])
            mock_reiden.side_effect = lambda x: x
            await skeptical_review(project_id="default")

        # Anonymize called for each non-empty LPD section
        assert mock_anon.call_count >= 7
        # Reidentify called for each field of each finding
        assert mock_reiden.call_count >= 4  # 4 fields * findings that pass filter

    @pytest.mark.asyncio
    async def test_pii_count(self, tmp_database, mock_llm_client, mock_sections, mock_staleness):
        with (
            patch("app.services.skeptical_reviewer.get_llm_client", return_value=mock_llm_client),
            patch("app.services.skeptical_reviewer.get_custom_terms", return_value=[]),
            patch("app.services.skeptical_reviewer.get_full_lpd", return_value=mock_sections),
            patch("app.services.skeptical_reviewer.get_section_staleness", return_value=mock_staleness),
            patch("app.services.skeptical_reviewer.anonymize") as mock_anon,
            patch("app.services.skeptical_reviewer.reidentify", side_effect=lambda x: x),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon", entities=["PII1", "PII2"])
            result = await skeptical_review(project_id="default")

        # 7 sections * 2 PII each = 14
        assert result.pii_detected == 14

    @pytest.mark.asyncio
    async def test_quality_filter_applied(self, tmp_database, mock_llm_client, mock_sections, mock_staleness):
        """Findings with insufficient evidence are filtered out."""
        weak_response = json.dumps(
            [
                {
                    "category": "blind_spot",
                    "severity": "low",
                    "title": "Vague finding",
                    "description": "Maybe some risk somewhere in the project.",
                    "evidence": "none",
                    "recommendation": "Check.",
                }
            ]
        )
        mock_llm_client.call = AsyncMock(return_value=weak_response)

        with (
            patch("app.services.skeptical_reviewer.get_llm_client", return_value=mock_llm_client),
            patch("app.services.skeptical_reviewer.get_custom_terms", return_value=[]),
            patch("app.services.skeptical_reviewer.get_full_lpd", return_value=mock_sections),
            patch("app.services.skeptical_reviewer.get_section_staleness", return_value=mock_staleness),
            patch("app.services.skeptical_reviewer.anonymize") as mock_anon,
            patch("app.services.skeptical_reviewer.reidentify", side_effect=lambda x: x),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon", entities=[])
            result = await skeptical_review(project_id="default")

        # The vague finding should be filtered out (evidence "none" is < 10 chars)
        assert len(result.findings) == 0


# --- Prompt Tests ---


class TestPromptStructure:
    def test_prompt_has_required_sections(self):
        from app.prompts.skeptical_reviewer_prompts import SKEPTICAL_REVIEW_PROMPT

        assert "contradiction" in SKEPTICAL_REVIEW_PROMPT
        assert "blind_spot" in SKEPTICAL_REVIEW_PROMPT
        assert "timeline_risk" in SKEPTICAL_REVIEW_PROMPT
        assert "underestimated_risk" in SKEPTICAL_REVIEW_PROMPT
        assert "Return ONLY valid JSON" in SKEPTICAL_REVIEW_PROMPT
        assert "evidence" in SKEPTICAL_REVIEW_PROMPT

    def test_prompt_has_quality_rules(self):
        from app.prompts.skeptical_reviewer_prompts import SKEPTICAL_REVIEW_PROMPT

        assert "MUST include specific evidence" in SKEPTICAL_REVIEW_PROMPT
        assert "USELESS" in SKEPTICAL_REVIEW_PROMPT or "useless" in SKEPTICAL_REVIEW_PROMPT.lower()


# --- Route / Smoke Tests ---


class TestReviewRoute:
    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_review_endpoint_exists(self, tmp_database):
        """Smoke test: the review endpoint is registered and callable."""
        from app.main import app
        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Mock the service to return a valid empty response
            mock_response = SkepticalReviewResponse(
                findings=[], sections_analyzed=0, artifacts_analyzed=0,
                pii_detected=0, session_id="test-session",
            )
            with patch(
                "app.services.skeptical_reviewer.skeptical_review",
                new_callable=AsyncMock,
                return_value=mock_response,
            ):
                response = await client.post("/api/review/default")
                assert response.status_code == 200
                data = response.json()
                assert data["findings"] == []
                assert data["session_id"] == "test-session"
