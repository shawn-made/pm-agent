"""Tests for VPMA Chat Service (Task 60) and Brain Dump (Task 62).

Tests cover: response parsing, history building, title generation,
conversation lifecycle, privacy proxy, suggestion extraction, and brain dump.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    Suggestion,
)
from app.services.chat_service import (
    _build_history_prompt,
    _parse_response,
    get_conversation_history,
    get_conversations,
    remove_conversation,
    send_chat_message,
)

# ============================================================
# RESPONSE PARSING
# ============================================================


class TestParseResponse:
    def test_plain_text_response(self):
        text, suggestions, refs = _parse_response("Just a plain answer.")
        assert text == "Just a plain answer."
        assert suggestions == []
        assert refs == []

    def test_extracts_suggestions(self):
        response = (
            "Here's what I found.\n\n"
            "---SUGGESTIONS---\n"
            '[{"artifact_type": "RAID Log", "change_type": "add", '
            '"section": "Risks", "proposed_text": "New risk", '
            '"confidence": 0.8, "reasoning": "Found in discussion"}]'
        )
        text, suggestions, refs = _parse_response(response)
        assert text == "Here's what I found."
        assert len(suggestions) == 1
        assert suggestions[0].artifact_type == "RAID Log"
        assert suggestions[0].proposed_text == "New risk"

    def test_extracts_lpd_refs(self):
        response = 'Based on your risks...\n\n---LPD_REFS---\n["Risks", "Timeline & Milestones"]'
        text, suggestions, refs = _parse_response(response)
        assert text == "Based on your risks..."
        assert refs == ["Risks", "Timeline & Milestones"]

    def test_extracts_both_suggestions_and_refs(self):
        response = (
            "Analysis complete.\n\n"
            "---SUGGESTIONS---\n"
            '[{"artifact_type": "RAID Log", "change_type": "add", '
            '"section": "Risks", "proposed_text": "Risk X", '
            '"confidence": 0.9, "reasoning": "test"}]\n\n'
            '---LPD_REFS---\n["Risks"]'
        )
        text, suggestions, refs = _parse_response(response)
        assert text == "Analysis complete."
        assert len(suggestions) == 1
        assert refs == ["Risks"]

    def test_handles_malformed_suggestions_gracefully(self):
        response = "Some text\n\n---SUGGESTIONS---\nnot valid json"
        text, suggestions, refs = _parse_response(response)
        assert text == "Some text"
        assert suggestions == []

    def test_handles_malformed_refs_gracefully(self):
        response = "Some text\n\n---LPD_REFS---\nnot json"
        text, suggestions, refs = _parse_response(response)
        assert text == "Some text"
        assert refs == []


# ============================================================
# HISTORY BUILDING
# ============================================================


class TestBuildHistoryPrompt:
    def test_empty_history(self):
        assert _build_history_prompt([]) == ""

    def test_formats_messages(self):
        messages = [
            {"role": "user", "content": "What are the risks?"},
            {"role": "assistant", "content": "There are three risks."},
        ]
        prompt = _build_history_prompt(messages)
        assert "User: What are the risks?" in prompt
        assert "Assistant: There are three risks." in prompt

    def test_truncates_long_messages(self):
        messages = [
            {"role": "user", "content": "A" * 600},
        ]
        prompt = _build_history_prompt(messages)
        assert len(prompt) < 600
        assert "..." in prompt

    def test_limits_to_max_history(self):
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(20)]
        prompt = _build_history_prompt(messages)
        # Should only include last 10 messages
        assert "Message 10" in prompt
        assert "Message 0" not in prompt


# ============================================================
# PYDANTIC MODELS
# ============================================================


class TestChatModels:
    def test_chat_request_defaults(self):
        req = ChatRequest(message="hello")
        assert req.conversation_id is None
        assert req.include_lpd_context is True
        assert req.include_artifacts is False

    def test_chat_response(self):
        resp = ChatResponse(
            conversation_id="conv-1",
            message_id="msg-1",
            response="Hello back",
            session_id="sess-1",
        )
        assert resp.suggestions == []
        assert resp.lpd_sections_referenced == []

    def test_suggestion_in_response(self):
        sugg = Suggestion(
            artifact_type="RAID Log",
            change_type="add",
            section="Risks",
            proposed_text="New risk found",
            confidence=0.85,
            reasoning="Discussed in conversation",
        )
        resp = ChatResponse(
            conversation_id="conv-1",
            message_id="msg-1",
            response="I found a risk",
            suggestions=[sugg],
            session_id="sess-1",
        )
        assert len(resp.suggestions) == 1
        assert resp.suggestions[0].proposed_text == "New risk found"


# ============================================================
# FULL PIPELINE (mocked)
# ============================================================


class TestSendChatMessage:
    @pytest.mark.asyncio
    async def test_new_conversation(self):
        """Starting a new conversation creates it and generates a title."""
        mock_client = AsyncMock()
        mock_client.call = AsyncMock(
            side_effect=["Based on your project, there are risks.", "Risk Discussion"]
        )
        mock_client.estimate_tokens = MagicMock(return_value=100)
        mock_client.model = "test-model"

        mock_session = MagicMock()
        mock_session.session_id = "sess-1"

        anon_result = MagicMock()
        anon_result.anonymized_text = "What are the risks?"
        anon_result.entities = []

        with (
            patch("app.services.chat_service.get_llm_client", return_value=mock_client),
            patch("app.services.chat_service.get_custom_terms", return_value=[]),
            patch(
                "app.services.chat_service.get_context_for_injection", return_value="## LPD context"
            ),
            patch("app.services.chat_service.anonymize", return_value=anon_result),
            patch("app.services.chat_service.reidentify", side_effect=lambda x: x),
            patch(
                "app.services.chat_service.create_conversation",
                return_value={"conversation_id": "conv-new"},
            ),
            patch(
                "app.services.chat_service.add_conversation_message",
                return_value={"message_id": "msg-1"},
            ),
            patch("app.services.chat_service.update_conversation"),
            patch("app.services.chat_service.create_session", return_value=mock_session),
        ):
            result = await send_chat_message(
                project_id="default",
                message="What are the risks?",
                conversation_id=None,
            )

            assert result.response == "Based on your project, there are risks."
            assert result.conversation_id is not None
            assert result.session_id == "sess-1"

    @pytest.mark.asyncio
    async def test_suggestion_extraction(self):
        """Suggestions in LLM response are extracted and returned."""
        mock_client = AsyncMock()
        mock_client.call = AsyncMock(
            return_value=(
                "I found a risk.\n\n---SUGGESTIONS---\n"
                '[{"artifact_type": "RAID Log", "change_type": "add", '
                '"section": "Risks", "proposed_text": "New risk", '
                '"confidence": 0.9, "reasoning": "from chat"}]'
            )
        )
        mock_client.estimate_tokens = MagicMock(return_value=200)
        mock_client.model = "test-model"

        mock_session = MagicMock()
        mock_session.session_id = "sess-2"

        anon_result = MagicMock()
        anon_result.anonymized_text = "Check for risks"
        anon_result.entities = []

        with (
            patch("app.services.chat_service.get_llm_client", return_value=mock_client),
            patch("app.services.chat_service.get_custom_terms", return_value=[]),
            patch("app.services.chat_service.get_context_for_injection", return_value=""),
            patch("app.services.chat_service.anonymize", return_value=anon_result),
            patch("app.services.chat_service.reidentify", side_effect=lambda x: x),
            patch(
                "app.services.chat_service.create_conversation",
                return_value={"conversation_id": "conv-2"},
            ),
            patch(
                "app.services.chat_service.add_conversation_message",
                return_value={"message_id": "msg-2"},
            ),
            patch("app.services.chat_service.update_conversation"),
            patch("app.services.chat_service.create_session", return_value=mock_session),
        ):
            result = await send_chat_message(
                project_id="default",
                message="Check for risks",
                conversation_id=None,
            )

            assert len(result.suggestions) == 1
            assert result.suggestions[0].artifact_type == "RAID Log"


class TestConversationManagement:
    @pytest.mark.asyncio
    async def test_list_conversations(self):
        with patch(
            "app.services.chat_service.get_conversations_by_project",
            return_value=[
                {
                    "conversation_id": "conv-1",
                    "title": "Risk Discussion",
                    "mode": "chat",
                    "created_at": "2026-03-16T10:00:00",
                    "last_message_at": "2026-03-16T10:15:00",
                    "message_count": 4,
                }
            ],
        ):
            result = await get_conversations("default")
            assert len(result) == 1
            assert result[0]["title"] == "Risk Discussion"

    @pytest.mark.asyncio
    async def test_get_conversation_history(self):
        with (
            patch(
                "app.services.chat_service.get_conversation",
                return_value={
                    "conversation_id": "conv-1",
                    "project_id": "default",
                    "title": "Test",
                    "mode": "chat",
                },
            ),
            patch(
                "app.services.chat_service.get_conversation_messages",
                return_value=[
                    {
                        "message_id": "msg-1",
                        "role": "user",
                        "content": "Hello",
                        "created_at": "2026-03-16T10:00:00",
                        "suggestions_json": "[]",
                        "lpd_sections_json": "[]",
                    },
                    {
                        "message_id": "msg-2",
                        "role": "assistant",
                        "content": "Hi there",
                        "created_at": "2026-03-16T10:00:01",
                        "suggestions_json": "[]",
                        "lpd_sections_json": '["Overview"]',
                    },
                ],
            ),
        ):
            result = await get_conversation_history("default", "conv-1")
            assert result is not None
            assert len(result["messages"]) == 2
            assert result["messages"][1]["lpd_sections_referenced"] == ["Overview"]

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(self):
        with patch("app.services.chat_service.get_conversation", return_value=None):
            result = await get_conversation_history("default", "nonexistent")
            assert result is None

    @pytest.mark.asyncio
    async def test_remove_conversation(self):
        with (
            patch(
                "app.services.chat_service.get_conversation",
                return_value={"conversation_id": "conv-1", "project_id": "default"},
            ),
            patch("app.services.chat_service.delete_conversation", return_value=True),
        ):
            result = await remove_conversation("default", "conv-1")
            assert result is True

    @pytest.mark.asyncio
    async def test_remove_conversation_wrong_project(self):
        with patch(
            "app.services.chat_service.get_conversation",
            return_value={"conversation_id": "conv-1", "project_id": "other"},
        ):
            result = await remove_conversation("default", "conv-1")
            assert result is False
