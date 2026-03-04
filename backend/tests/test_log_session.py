"""Tests for VPMA Log Session Bridge (Task 27).

Tests that:
1. log_session mode parses LLM response into summary + LPD updates + artifact suggestions
2. LPD updates are applied directly when LPD exists
3. Artifact suggestions are returned for review
4. Privacy proxy is applied
5. Backward compatibility: existing modes are unaffected
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.models.schemas import LPD_SECTION_NAMES
from app.services.artifact_sync import _parse_log_session, run_artifact_sync
from app.services.crud import get_session_summary_count
from app.services.lpd_manager import get_full_lpd, initialize_lpd

PROJECT_ID = "default"


# ============================================================
# HELPERS
# ============================================================


def _log_session_response(
    summary="Discussed Phase 2 planning.",
    lpd_updates=None,
    artifact_suggestions=None,
) -> str:
    if lpd_updates is None:
        lpd_updates = [
            {"section": "Decisions", "content": "- Decided to use PostgreSQL for production."},
        ]
    if artifact_suggestions is None:
        artifact_suggestions = [
            {
                "artifact_type": "RAID Log",
                "change_type": "add",
                "section": "Decisions",
                "proposed_text": "- Chose PostgreSQL for production database",
                "confidence": 0.95,
                "reasoning": "Architecture decision with long-term impact.",
            }
        ]
    return json.dumps(
        {
            "session_summary": summary,
            "lpd_updates": lpd_updates,
            "artifact_suggestions": artifact_suggestions,
        }
    )


def _patch_llm(monkeypatch, responses: list[str]):
    """Patch the LLM client. Responses are returned in order (first for classify, second for main)."""
    call_count = [0]

    async def mock_call(system_prompt, user_prompt, max_tokens=4096):
        idx = call_count[0]
        call_count[0] += 1
        if idx < len(responses):
            return responses[idx]
        return "general_text"

    client = MagicMock()
    client.call = mock_call
    client.estimate_tokens = MagicMock(return_value=50)
    client.model = "mock"
    monkeypatch.setattr(
        "app.services.artifact_sync.get_llm_client",
        AsyncMock(return_value=client),
    )
    return client


# ============================================================
# _parse_log_session
# ============================================================


class TestParseLogSession:
    def test_valid_json(self):
        response = _log_session_response()
        summary, lpd_updates, suggestions = _parse_log_session(response)
        assert summary == "Discussed Phase 2 planning."
        assert len(lpd_updates) == 1
        assert lpd_updates[0].section == "Decisions"
        assert "PostgreSQL" in lpd_updates[0].content
        assert len(suggestions) == 1

    def test_with_code_fences(self):
        response = "```json\n" + _log_session_response() + "\n```"
        summary, lpd_updates, suggestions = _parse_log_session(response)
        assert summary is not None
        assert len(lpd_updates) == 1

    def test_malformed_json(self):
        summary, lpd_updates, suggestions = _parse_log_session("not json")
        assert summary is None
        assert lpd_updates == []
        assert suggestions == []

    def test_empty_updates(self):
        response = _log_session_response(lpd_updates=[], artifact_suggestions=[])
        summary, lpd_updates, suggestions = _parse_log_session(response)
        assert summary == "Discussed Phase 2 planning."
        assert lpd_updates == []
        assert suggestions == []

    def test_multiple_lpd_updates(self):
        response = _log_session_response(
            lpd_updates=[
                {"section": "Risks", "content": "- New timeline risk."},
                {"section": "Decisions", "content": "- Chose React."},
                {"section": "Stakeholders", "content": "- Alice — PM"},
            ]
        )
        _, lpd_updates, _ = _parse_log_session(response)
        assert len(lpd_updates) == 3
        sections = [u.section for u in lpd_updates]
        assert "Risks" in sections
        assert "Decisions" in sections
        assert "Stakeholders" in sections

    def test_skips_malformed_items(self):
        response = json.dumps(
            {
                "session_summary": "Test.",
                "lpd_updates": [
                    {"section": "Risks", "content": "- Valid."},
                    {"bad_key": "missing section"},
                ],
                "artifact_suggestions": [
                    {"bad": "missing fields"},
                ],
            }
        )
        summary, lpd_updates, suggestions = _parse_log_session(response)
        assert summary == "Test."
        assert len(lpd_updates) == 1
        assert len(suggestions) == 0


# ============================================================
# LOG SESSION IN PIPELINE
# ============================================================


class TestLogSessionPipeline:
    @pytest.mark.asyncio
    async def test_log_session_mode_returns_lpd_updates(self, monkeypatch):
        """log_session mode returns LPD updates and artifact suggestions."""
        await initialize_lpd(PROJECT_ID)

        responses = [
            "general_text",
            _log_session_response(),
            json.dumps([{"index": 0, "classification": "new", "reason": "New info"}]),
        ]
        _patch_llm(monkeypatch, responses)

        result = await run_artifact_sync(
            "We decided to use PostgreSQL.",
            project_id=PROJECT_ID,
            mode="log_session",
        )

        assert result.mode == "log_session"
        assert len(result.lpd_updates) == 1
        assert result.lpd_updates[0].section == "Decisions"
        assert len(result.suggestions) == 1
        assert result.session_summary is not None

    @pytest.mark.asyncio
    async def test_lpd_updates_applied_directly(self, monkeypatch):
        """LPD updates are applied directly to the LPD sections."""
        await initialize_lpd(PROJECT_ID)

        responses = [
            "general_text",
            _log_session_response(
                lpd_updates=[
                    {"section": "Risks", "content": "- Vendor delay risk."},
                    {"section": "Decisions", "content": "- Chose PostgreSQL."},
                ]
            ),
            json.dumps(
                [
                    {"index": 0, "classification": "new", "reason": "New risk"},
                    {"index": 1, "classification": "new", "reason": "New decision"},
                ]
            ),
        ]
        _patch_llm(monkeypatch, responses)

        await run_artifact_sync(
            "Session conclusions.",
            project_id=PROJECT_ID,
            mode="log_session",
        )

        lpd = await get_full_lpd(PROJECT_ID)
        assert "Vendor delay risk" in lpd["Risks"]
        assert "Chose PostgreSQL" in lpd["Decisions"]

    @pytest.mark.asyncio
    async def test_lpd_updates_skipped_when_no_lpd(self, monkeypatch):
        """LPD updates are returned but not applied when no LPD exists."""
        responses = [
            "general_text",
            _log_session_response(),
        ]
        _patch_llm(monkeypatch, responses)

        result = await run_artifact_sync(
            "Some conclusions.",
            project_id=PROJECT_ID,
            mode="log_session",
        )

        # Updates returned in response (for display)
        assert len(result.lpd_updates) == 1
        # But LPD doesn't exist, so nothing was applied
        lpd = await get_full_lpd(PROJECT_ID)
        assert lpd == {}

    @pytest.mark.asyncio
    async def test_session_summary_uses_llm_generated(self, monkeypatch):
        """log_session mode uses the LLM-generated summary for Recent Context."""
        await initialize_lpd(PROJECT_ID)

        responses = [
            "general_text",
            _log_session_response(summary="Major architecture decision: PostgreSQL."),
            json.dumps([{"index": 0, "classification": "new", "reason": "New info"}]),
        ]
        _patch_llm(monkeypatch, responses)

        await run_artifact_sync(
            "We decided on PostgreSQL.",
            project_id=PROJECT_ID,
            mode="log_session",
        )

        lpd = await get_full_lpd(PROJECT_ID)
        assert "Major architecture decision: PostgreSQL" in lpd["Recent Context"]

    @pytest.mark.asyncio
    async def test_session_summary_logged(self, monkeypatch):
        """log_session mode logs a session summary."""
        responses = [
            "general_text",
            _log_session_response(),
        ]
        _patch_llm(monkeypatch, responses)

        await run_artifact_sync(
            "Session input.",
            project_id=PROJECT_ID,
            mode="log_session",
        )

        count = await get_session_summary_count(PROJECT_ID)
        assert count == 1


# ============================================================
# PRIVACY PROXY
# ============================================================


class TestLogSessionPrivacy:
    @pytest.mark.asyncio
    async def test_pii_in_input_anonymized(self, monkeypatch):
        """PII in input is anonymized before sending to LLM in log_session mode."""
        call_args = []

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_args.append(user_prompt)
            if len(call_args) == 1:
                return "general_text"
            return _log_session_response()

        client = MagicMock()
        client.call = mock_call
        client.estimate_tokens = MagicMock(return_value=50)
        client.model = "mock"
        monkeypatch.setattr(
            "app.services.artifact_sync.get_llm_client",
            AsyncMock(return_value=client),
        )

        result = await run_artifact_sync(
            "Alice (alice@example.com) decided to use PostgreSQL.",
            project_id=PROJECT_ID,
            mode="log_session",
        )

        # Email should be anonymized in the LLM call
        llm_prompt = call_args[1]
        assert "alice@example.com" not in llm_prompt
        assert result.pii_detected >= 1


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================


class TestLogSessionBackwardCompatibility:
    @pytest.mark.asyncio
    async def test_extract_mode_unchanged(self, monkeypatch):
        """Extract mode still works with the new log_session additions."""
        responses = [
            "meeting_notes",
            json.dumps(
                [
                    {
                        "artifact_type": "Status Report",
                        "change_type": "add",
                        "section": "Accomplishments",
                        "proposed_text": "- Completed migration.",
                        "confidence": 0.9,
                        "reasoning": "Stated.",
                    }
                ]
            ),
        ]
        _patch_llm(monkeypatch, responses)

        result = await run_artifact_sync(
            "Completed the migration.",
            project_id=PROJECT_ID,
            mode="extract",
        )

        assert result.mode == "extract"
        assert len(result.suggestions) == 1
        assert result.lpd_updates == []
        assert result.session_summary is None

    @pytest.mark.asyncio
    async def test_analyze_mode_unchanged(self, monkeypatch):
        """Analyze mode still works with the new log_session additions."""
        responses = [
            "general_text",
            json.dumps(
                {
                    "summary": "Document reviewed.",
                    "items": [
                        {
                            "category": "strength",
                            "title": "Clear",
                            "detail": "Good structure.",
                            "priority": "low",
                        }
                    ],
                }
            ),
        ]
        _patch_llm(monkeypatch, responses)

        result = await run_artifact_sync(
            "Review this.",
            project_id=PROJECT_ID,
            mode="analyze",
        )

        assert result.mode == "analyze"
        assert len(result.analysis) == 1
        assert result.lpd_updates == []
        assert result.session_summary is None


# ============================================================
# PROMPT VERIFICATION
# ============================================================


class TestLogSessionPrompt:
    def test_prompt_has_required_structure(self):
        from app.prompts.lpd_prompts import LOG_SESSION_SYSTEM_PROMPT

        assert "session_summary" in LOG_SESSION_SYSTEM_PROMPT
        assert "lpd_updates" in LOG_SESSION_SYSTEM_PROMPT
        assert "artifact_suggestions" in LOG_SESSION_SYSTEM_PROMPT
        assert "JSON" in LOG_SESSION_SYSTEM_PROMPT

    def test_prompt_lists_valid_lpd_sections(self):
        from app.prompts.lpd_prompts import LOG_SESSION_SYSTEM_PROMPT

        for name in LPD_SECTION_NAMES:
            if name == "Recent Context":
                assert "Do NOT use" in LOG_SESSION_SYSTEM_PROMPT
            else:
                assert name in LOG_SESSION_SYSTEM_PROMPT
