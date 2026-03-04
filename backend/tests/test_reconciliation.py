"""Tests for VPMA Cross-Section LPD Reconciliation Engine.

Tests cover: impact parsing, pipeline orchestration, privacy proxy,
session logging, and edge cases.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.reconciliation import (
    _build_section_block,
    _parse_impacts,
    reconcile_lpd_sections,
)

# ============================================================
# SECTION BLOCK BUILDER
# ============================================================


class TestBuildSectionBlock:
    def test_formats_sections(self):
        sections = {"Overview": "Project overview", "Risks": "Risk list"}
        block = _build_section_block(sections)
        assert "Section: Overview" in block
        assert "Project overview" in block
        assert "End: Overview" in block

    def test_marks_empty_sections(self):
        sections = {"Overview": "", "Risks": None}
        block = _build_section_block(sections)
        assert "(empty)" in block


# ============================================================
# IMPACT PARSING
# ============================================================


class TestParseImpacts:
    def test_parses_valid_impacts(self):
        response = json.dumps(
            [
                {
                    "source_section": "Decisions",
                    "target_section": "Open Questions",
                    "impact_type": "resolves",
                    "description": "Decision D5 resolves Q3",
                    "source_excerpt": "Decided to use PostgreSQL",
                    "target_excerpt": "Which database should we use?",
                    "suggested_action": "Remove Q3 from Open Questions or mark as resolved",
                }
            ]
        )
        result = _parse_impacts(response)
        assert len(result) == 1
        assert result[0].impact_type == "resolves"
        assert result[0].source_section == "Decisions"

    def test_returns_empty_on_invalid_json(self):
        assert _parse_impacts("Not JSON at all") == []

    def test_parses_empty_array(self):
        assert _parse_impacts("[]") == []

    def test_strips_code_fences(self):
        response = '```json\n[{"source_section": "A", "target_section": "B", "impact_type": "contradicts", "description": "d", "excerpts": {}, "suggested_action": "a"}]\n```'
        result = _parse_impacts(response)
        assert len(result) == 1

    def test_skips_malformed_items(self):
        response = json.dumps(
            [
                {
                    "source_section": "Decisions",
                    "target_section": "Risks",
                    "impact_type": "requires_update",
                    "description": "Valid impact",
                    "excerpts": {},
                    "suggested_action": "Update risk entry",
                },
                {"bad": "item"},
            ]
        )
        result = _parse_impacts(response)
        assert len(result) == 1


# ============================================================
# FULL PIPELINE (Mocked LLM)
# ============================================================


class TestReconcileLPDSections:
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
                    "source_section": "Decisions",
                    "target_section": "Open Questions",
                    "impact_type": "resolves",
                    "description": "Decision resolves question",
                    "excerpts": {"source": "We decided X", "target": "Should we do X?"},
                    "suggested_action": "Mark question as resolved",
                }
            ]
        )

    @pytest.mark.asyncio
    async def test_full_pipeline(self, mock_llm_client, llm_response):
        mock_llm_client.call = AsyncMock(return_value=llm_response)

        mock_session = MagicMock()
        mock_session.session_id = "recon-session-1"

        with (
            patch("app.services.reconciliation.get_llm_client", return_value=mock_llm_client),
            patch("app.services.reconciliation.get_custom_terms", return_value=[]),
            patch(
                "app.services.reconciliation.get_full_lpd",
                return_value={
                    "Overview": "Project overview",
                    "Decisions": "We decided X",
                    "Open Questions": "Should we do X?",
                },
            ),
            patch("app.services.reconciliation.anonymize") as mock_anon,
            patch("app.services.reconciliation.reidentify", side_effect=lambda x: x),
            patch("app.services.reconciliation.create_session", return_value=mock_session),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon text", entities=[])

            result = await reconcile_lpd_sections(project_id="test-proj")

        assert result.session_id == "recon-session-1"
        assert len(result.impacts) == 1
        assert result.impacts[0].impact_type == "resolves"
        assert result.sections_analyzed == 3

    @pytest.mark.asyncio
    async def test_empty_lpd_returns_early(self, mock_llm_client):
        with (
            patch("app.services.reconciliation.get_llm_client", return_value=mock_llm_client),
            patch("app.services.reconciliation.get_custom_terms", return_value=[]),
            patch("app.services.reconciliation.get_full_lpd", return_value={}),
        ):
            result = await reconcile_lpd_sections(project_id="empty-proj")

        assert result.impacts == []
        assert result.sections_analyzed == 0
        assert result.session_id == ""
        mock_llm_client.call.assert_not_called()

    @pytest.mark.asyncio
    async def test_anonymizes_all_content(self, mock_llm_client, llm_response):
        mock_llm_client.call = AsyncMock(return_value=llm_response)

        mock_session = MagicMock()
        mock_session.session_id = "s1"

        with (
            patch("app.services.reconciliation.get_llm_client", return_value=mock_llm_client),
            patch("app.services.reconciliation.get_custom_terms", return_value=[]),
            patch(
                "app.services.reconciliation.get_full_lpd",
                return_value={"A": "content A", "B": "content B"},
            ),
            patch("app.services.reconciliation.anonymize") as mock_anon,
            patch("app.services.reconciliation.reidentify", side_effect=lambda x: x),
            patch("app.services.reconciliation.create_session", return_value=mock_session),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="redacted", entities=[MagicMock()])

            result = await reconcile_lpd_sections()

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
            patch("app.services.reconciliation.get_llm_client", return_value=mock_llm_client),
            patch("app.services.reconciliation.get_custom_terms", return_value=[]),
            patch(
                "app.services.reconciliation.get_full_lpd",
                return_value={"Overview": "content"},
            ),
            patch("app.services.reconciliation.anonymize") as mock_anon,
            patch("app.services.reconciliation.reidentify", side_effect=tracking_reidentify),
            patch("app.services.reconciliation.create_session", return_value=mock_session),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon", entities=[])

            result = await reconcile_lpd_sections()

        assert result.impacts[0].description.startswith("REID:")
        assert result.impacts[0].suggested_action.startswith("REID:")

    @pytest.mark.asyncio
    async def test_logs_session(self, mock_llm_client, llm_response):
        mock_llm_client.call = AsyncMock(return_value=llm_response)

        mock_session = MagicMock()
        mock_session.session_id = "logged"

        with (
            patch("app.services.reconciliation.get_llm_client", return_value=mock_llm_client),
            patch("app.services.reconciliation.get_custom_terms", return_value=[]),
            patch(
                "app.services.reconciliation.get_full_lpd",
                return_value={"Overview": "content"},
            ),
            patch("app.services.reconciliation.anonymize") as mock_anon,
            patch("app.services.reconciliation.reidentify", side_effect=lambda x: x),
            patch("app.services.reconciliation.create_session") as mock_create,
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon", entities=[])
            mock_create.return_value = mock_session

            await reconcile_lpd_sections(project_id="proj-123")

        mock_create.assert_called_once()
        session_arg = mock_create.call_args[0][0]
        assert session_arg.project_id == "proj-123"
        assert session_arg.tab_used == "reconciliation"

    @pytest.mark.asyncio
    async def test_handles_empty_impacts(self, mock_llm_client):
        mock_llm_client.call = AsyncMock(return_value="[]")
        mock_llm_client.estimate_tokens = MagicMock(return_value=50)
        mock_llm_client.model = "test"

        mock_session = MagicMock()
        mock_session.session_id = "empty"

        with (
            patch("app.services.reconciliation.get_llm_client", return_value=mock_llm_client),
            patch("app.services.reconciliation.get_custom_terms", return_value=[]),
            patch(
                "app.services.reconciliation.get_full_lpd",
                return_value={"Overview": "content"},
            ),
            patch("app.services.reconciliation.anonymize") as mock_anon,
            patch("app.services.reconciliation.reidentify", side_effect=lambda x: x),
            patch("app.services.reconciliation.create_session", return_value=mock_session),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon", entities=[])

            result = await reconcile_lpd_sections()

        assert result.impacts == []
        assert result.sections_analyzed == 1

    @pytest.mark.asyncio
    async def test_skips_empty_sections_in_anonymization(self, mock_llm_client, llm_response):
        mock_llm_client.call = AsyncMock(return_value=llm_response)

        mock_session = MagicMock()
        mock_session.session_id = "s1"

        with (
            patch("app.services.reconciliation.get_llm_client", return_value=mock_llm_client),
            patch("app.services.reconciliation.get_custom_terms", return_value=[]),
            patch(
                "app.services.reconciliation.get_full_lpd",
                return_value={"Overview": "content", "Risks": ""},
            ),
            patch("app.services.reconciliation.anonymize") as mock_anon,
            patch("app.services.reconciliation.reidentify", side_effect=lambda x: x),
            patch("app.services.reconciliation.create_session", return_value=mock_session),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon", entities=[])

            result = await reconcile_lpd_sections()

        # Only non-empty sections get anonymized
        assert mock_anon.call_count == 1
        # Only non-empty sections count as analyzed
        assert result.sections_analyzed == 1
