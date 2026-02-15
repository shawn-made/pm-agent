"""Tests for VPMA Artifact Sync — Pipeline and prompt parsing (Tasks 10-11)."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.artifact_sync import _parse_suggestions, classify_input, run_artifact_sync


# ============================================================
# SUGGESTION PARSING
# ============================================================


class TestParseSuggestions:
    def test_parse_valid_json(self):
        response = json.dumps([
            {
                "artifact_type": "RAID Log",
                "change_type": "add",
                "section": "Risks",
                "proposed_text": "New risk identified",
                "confidence": 0.9,
                "reasoning": "Explicitly mentioned as a risk",
            }
        ])
        suggestions = _parse_suggestions(response)
        assert len(suggestions) == 1
        assert suggestions[0].artifact_type == "RAID Log"
        assert suggestions[0].confidence == 0.9

    def test_parse_multiple_suggestions(self):
        response = json.dumps([
            {
                "artifact_type": "RAID Log",
                "change_type": "add",
                "section": "Risks",
                "proposed_text": "Risk 1",
                "confidence": 0.9,
                "reasoning": "Reason 1",
            },
            {
                "artifact_type": "Status Report",
                "change_type": "add",
                "section": "Accomplishments",
                "proposed_text": "Completed task X",
                "confidence": 0.85,
                "reasoning": "Reason 2",
            },
        ])
        suggestions = _parse_suggestions(response)
        assert len(suggestions) == 2

    def test_parse_with_code_fences(self):
        response = '```json\n[{"artifact_type": "RAID Log", "change_type": "add", "section": "Risks", "proposed_text": "text", "confidence": 0.9, "reasoning": "reason"}]\n```'
        suggestions = _parse_suggestions(response)
        assert len(suggestions) == 1

    def test_parse_with_surrounding_text(self):
        response = 'Here are the suggestions:\n[{"artifact_type": "RAID Log", "change_type": "add", "section": "Risks", "proposed_text": "text", "confidence": 0.9, "reasoning": "reason"}]\nDone!'
        suggestions = _parse_suggestions(response)
        assert len(suggestions) == 1

    def test_parse_empty_array(self):
        suggestions = _parse_suggestions("[]")
        assert suggestions == []

    def test_parse_invalid_json(self):
        suggestions = _parse_suggestions("This is not JSON at all.")
        assert suggestions == []

    def test_parse_no_array(self):
        suggestions = _parse_suggestions('{"key": "value"}')
        assert suggestions == []

    def test_parse_skips_malformed_items(self):
        response = json.dumps([
            {
                "artifact_type": "RAID Log",
                "change_type": "add",
                "section": "Risks",
                "proposed_text": "Valid",
                "confidence": 0.9,
                "reasoning": "Valid reason",
            },
            {"bad": "data"},  # Missing required fields
        ])
        suggestions = _parse_suggestions(response)
        assert len(suggestions) == 1


# ============================================================
# INPUT CLASSIFICATION
# ============================================================


class TestClassifyInput:
    @pytest.mark.asyncio
    async def test_classify_meeting_notes(self):
        mock_client = MagicMock()
        mock_client.call = AsyncMock(return_value="meeting_notes")

        result = await classify_input("Attendees: Alice, Bob...", mock_client)
        assert result == "meeting_notes"

    @pytest.mark.asyncio
    async def test_classify_status_update(self):
        mock_client = MagicMock()
        mock_client.call = AsyncMock(return_value="status_update")

        result = await classify_input("Completed migration...", mock_client)
        assert result == "status_update"

    @pytest.mark.asyncio
    async def test_classify_falls_back_on_error(self):
        from app.services.llm_client import LLMError

        mock_client = MagicMock()
        mock_client.call = AsyncMock(side_effect=LLMError("fail"))

        result = await classify_input("Some text", mock_client)
        assert result == "general_text"

    @pytest.mark.asyncio
    async def test_classify_invalid_response_defaults(self):
        mock_client = MagicMock()
        mock_client.call = AsyncMock(return_value="banana")

        result = await classify_input("Some text", mock_client)
        assert result == "general_text"


# ============================================================
# FULL PIPELINE (MOCKED LLM)
# ============================================================


class TestRunArtifactSync:
    @pytest.mark.asyncio
    async def test_full_pipeline(self, monkeypatch):
        """End-to-end pipeline with mocked LLM."""
        llm_suggestions = json.dumps([
            {
                "artifact_type": "Status Report",
                "change_type": "add",
                "section": "Accomplishments",
                "proposed_text": "- Completed database migration",
                "confidence": 0.95,
                "reasoning": "Explicitly stated as completed",
            }
        ])

        mock_client = MagicMock()
        # First call: classification, Second call: artifact sync
        mock_client.call = AsyncMock(
            side_effect=["status_update", llm_suggestions]
        )
        mock_client.estimate_tokens = MagicMock(return_value=50)
        mock_client.model = "mock-model"

        monkeypatch.setattr(
            "app.services.artifact_sync._get_llm_client",
            AsyncMock(return_value=mock_client),
        )

        result = await run_artifact_sync("Completed the database migration.")

        assert result.input_type == "status_update"
        assert len(result.suggestions) == 1
        assert result.suggestions[0].artifact_type == "Status Report"
        assert result.session_id  # Should have a session ID

    @pytest.mark.asyncio
    async def test_pipeline_with_pii(self, monkeypatch):
        """Pipeline anonymizes PII before sending to LLM."""
        call_args = []

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_args.append(user_prompt)
            if len(call_args) == 1:
                return "general_text"
            return "[]"

        mock_client = MagicMock()
        mock_client.call = mock_call
        mock_client.estimate_tokens = MagicMock(return_value=10)
        mock_client.model = "mock"

        monkeypatch.setattr(
            "app.services.artifact_sync._get_llm_client",
            AsyncMock(return_value=mock_client),
        )

        await run_artifact_sync("Contact alice@example.com for details.")

        # The LLM should have received anonymized text (no email)
        sync_prompt = call_args[1]  # Second call is artifact sync
        assert "alice@example.com" not in sync_prompt
        assert "<EMAIL_1>" in sync_prompt

    @pytest.mark.asyncio
    async def test_pipeline_logs_session(self, monkeypatch):
        """Pipeline creates a session record."""
        mock_client = MagicMock()
        mock_client.call = AsyncMock(side_effect=["general_text", "[]"])
        mock_client.estimate_tokens = MagicMock(return_value=10)
        mock_client.model = "mock"

        monkeypatch.setattr(
            "app.services.artifact_sync._get_llm_client",
            AsyncMock(return_value=mock_client),
        )

        result = await run_artifact_sync("Test input.")

        from app.services.crud import get_session

        session = await get_session(result.session_id)
        assert session is not None
        assert session.tab_used == "artifact_sync"
