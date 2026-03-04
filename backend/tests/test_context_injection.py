"""Tests for VPMA Context Injection Engine (Task 24).

Tests that LPD project context is fetched, anonymized, and injected
into LLM prompts during the artifact sync pipeline.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.artifact_sync import run_artifact_sync
from app.services.lpd_manager import initialize_lpd, update_section

# All tests use project_id="default" — the conftest auto-creates this project via init_db().

PROJECT_ID = "default"


# ============================================================
# HELPERS
# ============================================================


def _empty_suggestions() -> str:
    return "[]"


def _one_suggestion() -> str:
    return json.dumps(
        [
            {
                "artifact_type": "Status Report",
                "change_type": "add",
                "section": "Accomplishments",
                "proposed_text": "- Completed database migration",
                "confidence": 0.95,
                "reasoning": "Explicitly stated",
            }
        ]
    )


def _one_analysis() -> str:
    return json.dumps(
        {
            "summary": "Overall looks good.",
            "items": [
                {
                    "category": "strength",
                    "title": "Clear structure",
                    "detail": "The document is well organized.",
                    "priority": "low",
                    "artifact_type": None,
                }
            ],
        }
    )


def _patch_llm(monkeypatch, mock_call_fn):
    """Patch the LLM client with a custom call function."""
    client = MagicMock()
    client.call = mock_call_fn
    client.estimate_tokens = MagicMock(return_value=50)
    client.model = "mock"
    monkeypatch.setattr(
        "app.services.artifact_sync.get_llm_client",
        AsyncMock(return_value=client),
    )
    return client


# ============================================================
# BACKWARD COMPATIBILITY (NO LPD)
# ============================================================


class TestNoLPDContext:
    """Pipeline should behave exactly as before when no LPD exists."""

    @pytest.mark.asyncio
    async def test_extract_without_lpd(self, monkeypatch):
        """Extract mode works normally when no LPD is initialized."""
        call_args = []

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_args.append(user_prompt)
            if len(call_args) == 1:
                return "general_text"
            return _one_suggestion()

        _patch_llm(monkeypatch, mock_call)

        result = await run_artifact_sync("Some update text.", project_id=PROJECT_ID)

        assert len(result.suggestions) == 1
        # No project context block in the prompt
        sync_prompt = call_args[1]
        assert "## Project Context" not in sync_prompt
        assert sync_prompt.startswith("[Input type:")

    @pytest.mark.asyncio
    async def test_analyze_without_lpd(self, monkeypatch):
        """Analyze mode works normally when no LPD is initialized."""
        call_args = []

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_args.append(user_prompt)
            if len(call_args) == 1:
                return "general_text"
            return _one_analysis()

        _patch_llm(monkeypatch, mock_call)

        result = await run_artifact_sync(
            "Review my status report.", project_id=PROJECT_ID, mode="analyze"
        )

        assert len(result.analysis) == 1
        sync_prompt = call_args[1]
        assert "## Project Context" not in sync_prompt

    @pytest.mark.asyncio
    async def test_empty_lpd_sections_no_context(self, monkeypatch):
        """LPD initialized but all sections empty — no context injected."""
        await initialize_lpd(PROJECT_ID)

        call_args = []

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_args.append(user_prompt)
            if len(call_args) == 1:
                return "general_text"
            return _empty_suggestions()

        _patch_llm(monkeypatch, mock_call)

        result = await run_artifact_sync("Test input.", project_id=PROJECT_ID)

        sync_prompt = call_args[1]
        assert "## Project Context" not in sync_prompt
        assert result.pii_detected == 0


# ============================================================
# CONTEXT INJECTION (WITH LPD)
# ============================================================


class TestWithLPDContext:
    """Pipeline should inject LPD context when it exists and has content."""

    @pytest.mark.asyncio
    async def test_context_injected_into_extract_prompt(self, monkeypatch):
        """LPD context appears in the user prompt sent to LLM in extract mode."""
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Overview", "Acme Corp web platform redesign.")

        call_args = []

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_args.append(user_prompt)
            if len(call_args) == 1:
                return "general_text"
            return _one_suggestion()

        _patch_llm(monkeypatch, mock_call)

        result = await run_artifact_sync("Sprint review went well.", project_id=PROJECT_ID)

        sync_prompt = call_args[1]
        assert "## Project Context" in sync_prompt
        assert "Acme Corp web platform redesign" in sync_prompt
        assert "[Input type:" in sync_prompt
        assert len(result.suggestions) == 1

    @pytest.mark.asyncio
    async def test_context_injected_into_analyze_prompt(self, monkeypatch):
        """LPD context appears in the user prompt for analyze mode."""
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Risks", "- Vendor API may delay past March.")

        call_args = []

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_args.append(user_prompt)
            if len(call_args) == 1:
                return "general_text"
            return _one_analysis()

        _patch_llm(monkeypatch, mock_call)

        await run_artifact_sync("Review this draft.", project_id=PROJECT_ID, mode="analyze")

        sync_prompt = call_args[1]
        assert "## Project Context" in sync_prompt
        assert "Vendor API may delay past March" in sync_prompt

    @pytest.mark.asyncio
    async def test_context_appears_before_input(self, monkeypatch):
        """LPD context block is prepended before the input type and user text."""
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Overview", "Project Falcon overview.")

        call_args = []

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_args.append(user_prompt)
            if len(call_args) == 1:
                return "general_text"
            return _empty_suggestions()

        _patch_llm(monkeypatch, mock_call)

        await run_artifact_sync("User text here.", project_id=PROJECT_ID)

        sync_prompt = call_args[1]
        context_pos = sync_prompt.index("## Project Context")
        input_type_pos = sync_prompt.index("[Input type:")
        assert context_pos < input_type_pos

    @pytest.mark.asyncio
    async def test_multiple_sections_included(self, monkeypatch):
        """Multiple non-empty LPD sections are included in context."""
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Overview", "Multi-section test project.")
        await update_section(PROJECT_ID, "Risks", "- Budget risk identified.")
        await update_section(PROJECT_ID, "Decisions", "- Chose React for frontend.")

        call_args = []

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_args.append(user_prompt)
            if len(call_args) == 1:
                return "general_text"
            return _empty_suggestions()

        _patch_llm(monkeypatch, mock_call)

        await run_artifact_sync("New update.", project_id=PROJECT_ID)

        sync_prompt = call_args[1]
        assert "Multi-section test project" in sync_prompt
        assert "Budget risk identified" in sync_prompt
        assert "Chose React for frontend" in sync_prompt


# ============================================================
# PRIVACY PROXY ON LPD CONTEXT
# ============================================================


class TestContextPrivacy:
    """LPD context must be anonymized before reaching the LLM."""

    @pytest.mark.asyncio
    async def test_pii_in_lpd_is_anonymized(self, monkeypatch):
        """PII in LPD content is anonymized before injection into the prompt."""
        await initialize_lpd(PROJECT_ID)
        await update_section(
            PROJECT_ID,
            "Stakeholders",
            "Lead: alice@example.com, Sponsor: Bob Johnson",
        )

        call_args = []

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_args.append(user_prompt)
            if len(call_args) == 1:
                return "general_text"
            return _empty_suggestions()

        _patch_llm(monkeypatch, mock_call)

        result = await run_artifact_sync("New update.", project_id=PROJECT_ID)

        sync_prompt = call_args[1]
        # Email should be anonymized
        assert "alice@example.com" not in sync_prompt
        assert "<EMAIL_" in sync_prompt
        # PII count should include entities from context
        assert result.pii_detected >= 1

    @pytest.mark.asyncio
    async def test_pii_counts_combine_input_and_context(self, monkeypatch):
        """PII detected count includes entities from both user input and LPD context."""
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Stakeholders", "Lead: charlie@test.com")

        call_args = []

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_args.append(user_prompt)
            if len(call_args) == 1:
                return "general_text"
            return _empty_suggestions()

        _patch_llm(monkeypatch, mock_call)

        # Input also contains PII
        result = await run_artifact_sync(
            "Contact dave@example.com for info.", project_id=PROJECT_ID
        )

        # Should have at least 2 PII entities: one from input, one from LPD
        assert result.pii_detected >= 2


# ============================================================
# TOKEN BUDGET
# ============================================================


class TestTokenBudget:
    """Context injection respects the token budget from get_context_for_injection."""

    @pytest.mark.asyncio
    async def test_large_context_is_truncated(self, monkeypatch):
        """When LPD sections exceed the token budget, context is truncated."""
        await initialize_lpd(PROJECT_ID)
        # Fill overview with a large amount of text (~5000 tokens worth)
        large_text = "This is a detailed project overview. " * 500
        await update_section(PROJECT_ID, "Overview", large_text)
        await update_section(PROJECT_ID, "Risks", "- A risk that might get cut.")

        call_args = []

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_args.append(user_prompt)
            if len(call_args) == 1:
                return "general_text"
            return _empty_suggestions()

        _patch_llm(monkeypatch, mock_call)

        await run_artifact_sync("Test.", project_id=PROJECT_ID)

        sync_prompt = call_args[1]
        # Context should be present but truncated (not the full ~18000 chars)
        assert "## Project Context" in sync_prompt
        assert "..." in sync_prompt  # Truncation marker

    @pytest.mark.asyncio
    async def test_context_injection_with_custom_budget(self):
        """get_context_for_injection respects a custom token budget."""
        from app.services.lpd_manager import get_context_for_injection

        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Overview", "Short overview.")
        await update_section(PROJECT_ID, "Risks", "- A risk.")

        # Very small budget — should still get at least the header
        context = await get_context_for_injection(PROJECT_ID, max_tokens=50)
        assert "## Project Context" in context


# ============================================================
# SYSTEM PROMPT VERIFICATION
# ============================================================


class TestSystemPrompts:
    """Verify system prompts include project context instructions."""

    def test_extract_prompt_has_context_section(self):
        from app.prompts.artifact_sync import ARTIFACT_SYNC_SYSTEM_PROMPT

        assert "## Project Context" in ARTIFACT_SYNC_SYSTEM_PROMPT
        assert "Avoid duplicates" in ARTIFACT_SYNC_SYSTEM_PROMPT
        assert "Flag contradictions" in ARTIFACT_SYNC_SYSTEM_PROMPT
        assert "Connect the dots" in ARTIFACT_SYNC_SYSTEM_PROMPT

    def test_analyze_prompt_has_context_section(self):
        from app.prompts.artifact_sync import ANALYZE_ADVISE_SYSTEM_PROMPT

        assert "## Project Context" in ANALYZE_ADVISE_SYSTEM_PROMPT
        assert "Flag gaps" in ANALYZE_ADVISE_SYSTEM_PROMPT
        assert "Identify contradictions" in ANALYZE_ADVISE_SYSTEM_PROMPT
        assert "Acknowledge alignment" in ANALYZE_ADVISE_SYSTEM_PROMPT
