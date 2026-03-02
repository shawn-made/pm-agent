"""Tests for VPMA Content Quality Gate — dedup and contradiction detection.

Tests that:
1. _parse_classification_response handles valid, malformed, and edge-case LLM output
2. classify_lpd_updates correctly classifies updates against existing content
3. Content gate integrates with the log_session pipeline
4. Graceful degradation when LLM call fails
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.models.schemas import LPDUpdate
from app.services.artifact_sync import run_artifact_sync
from app.services.content_gate import (
    AUTO_APPLY_CLASSIFICATIONS,
    _parse_classification_response,
    classify_lpd_updates,
)
from app.services.llm_client import LLMError
from app.services.lpd_manager import (
    append_to_section,
    get_full_lpd,
    initialize_lpd,
)

PROJECT_ID = "default"


# ============================================================
# HELPERS
# ============================================================


def _gate_response(classifications: list[dict]) -> str:
    """Build a mock content gate LLM response."""
    return json.dumps(classifications)


def _log_session_response(
    summary="Session conclusions logged.",
    lpd_updates=None,
    artifact_suggestions=None,
) -> str:
    if lpd_updates is None:
        lpd_updates = [
            {"section": "Risks", "content": "- Vendor delay risk identified."},
        ]
    if artifact_suggestions is None:
        artifact_suggestions = []
    return json.dumps(
        {
            "session_summary": summary,
            "lpd_updates": lpd_updates,
            "artifact_suggestions": artifact_suggestions,
        }
    )


def _make_client(responses: list[str]):
    """Create a mock LLM client that returns responses in order."""
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
    return client


def _patch_llm(monkeypatch, responses: list[str]):
    """Patch the LLM client for full pipeline tests."""
    client = _make_client(responses)
    monkeypatch.setattr(
        "app.services.artifact_sync._get_llm_client",
        AsyncMock(return_value=client),
    )
    return client


# ============================================================
# _parse_classification_response
# ============================================================


class TestParseClassificationResponse:
    def test_valid_json(self):
        response = json.dumps(
            [
                {"index": 0, "classification": "new", "reason": "Not in existing"},
                {"index": 1, "classification": "duplicate", "reason": "Already exists"},
            ]
        )
        result = _parse_classification_response(response, 2)
        assert len(result) == 2
        assert result[0]["classification"] == "new"
        assert result[1]["classification"] == "duplicate"

    def test_with_code_fences(self):
        inner = json.dumps(
            [{"index": 0, "classification": "contradiction", "reason": "Date changed"}]
        )
        response = f"```json\n{inner}\n```"
        result = _parse_classification_response(response, 1)
        assert result[0]["classification"] == "contradiction"

    def test_malformed_json_falls_back(self):
        result = _parse_classification_response("not json at all", 3)
        assert len(result) == 3
        assert all(r["classification"] == "new" for r in result)

    def test_no_array_falls_back(self):
        result = _parse_classification_response('{"key": "value"}', 2)
        assert len(result) == 2
        assert all(r["classification"] == "new" for r in result)

    def test_missing_indices_filled(self):
        """Indices not returned by LLM are filled in as 'new'."""
        response = json.dumps(
            [
                {"index": 0, "classification": "duplicate", "reason": "Exists"},
                # index 1 is missing
            ]
        )
        result = _parse_classification_response(response, 2)
        assert len(result) == 2
        assert result[0]["classification"] == "duplicate"
        assert result[1]["classification"] == "new"
        assert "Not classified" in result[1]["reason"]

    def test_invalid_classification_normalized(self):
        response = json.dumps(
            [
                {"index": 0, "classification": "INVALID_VALUE", "reason": "Bad"},
            ]
        )
        result = _parse_classification_response(response, 1)
        assert result[0]["classification"] == "new"

    def test_empty_count(self):
        result = _parse_classification_response("[]", 0)
        assert result == []

    def test_all_four_classifications(self):
        response = json.dumps(
            [
                {"index": 0, "classification": "new", "reason": "a"},
                {"index": 1, "classification": "duplicate", "reason": "b"},
                {"index": 2, "classification": "update", "reason": "c"},
                {"index": 3, "classification": "contradiction", "reason": "d"},
            ]
        )
        result = _parse_classification_response(response, 4)
        assert [r["classification"] for r in result] == [
            "new",
            "duplicate",
            "update",
            "contradiction",
        ]


# ============================================================
# classify_lpd_updates
# ============================================================


class TestClassifyLPDUpdates:
    @pytest.mark.asyncio
    async def test_empty_updates_returns_empty(self):
        client = _make_client([])
        result, active = await classify_lpd_updates(PROJECT_ID, [], client)
        assert result == []
        assert active is True

    @pytest.mark.asyncio
    async def test_no_lpd_all_new(self):
        """When no LPD exists, all updates classified as 'new' without LLM call."""
        updates = [LPDUpdate(section="Risks", content="- New risk")]
        client = _make_client([])  # No responses needed — no LLM call
        result, active = await classify_lpd_updates(PROJECT_ID, updates, client)
        assert len(result) == 1
        assert result[0].classification.classification == "new"
        assert active is True

    @pytest.mark.asyncio
    async def test_duplicate_detected(self):
        """LLM classifies a semantically duplicate update."""
        await initialize_lpd(PROJECT_ID)
        await append_to_section(PROJECT_ID, "Risks", "- Vendor API may be delayed")

        updates = [LPDUpdate(section="Risks", content="- Vendor API might be late")]
        gate_response = _gate_response(
            [{"index": 0, "classification": "duplicate", "reason": "Same vendor delay risk"}]
        )
        client = _make_client([gate_response])

        result, active = await classify_lpd_updates(PROJECT_ID, updates, client)
        assert result[0].classification.classification == "duplicate"
        assert active is True

    @pytest.mark.asyncio
    async def test_contradiction_detected(self):
        """LLM detects a contradiction with existing content."""
        await initialize_lpd(PROJECT_ID)
        await append_to_section(PROJECT_ID, "Decisions", "- Chose React for frontend")

        updates = [LPDUpdate(section="Decisions", content="- Switched to Vue for frontend")]
        gate_response = _gate_response(
            [{"index": 0, "classification": "contradiction", "reason": "Reverses React decision"}]
        )
        client = _make_client([gate_response])

        result, active = await classify_lpd_updates(PROJECT_ID, updates, client)
        assert result[0].classification.classification == "contradiction"

    @pytest.mark.asyncio
    async def test_new_info_detected(self):
        """LLM classifies genuinely new information."""
        await initialize_lpd(PROJECT_ID)

        updates = [LPDUpdate(section="Risks", content="- Budget overrun risk")]
        gate_response = _gate_response(
            [{"index": 0, "classification": "new", "reason": "Not in existing content"}]
        )
        client = _make_client([gate_response])

        result, active = await classify_lpd_updates(PROJECT_ID, updates, client)
        assert result[0].classification.classification == "new"

    @pytest.mark.asyncio
    async def test_mixed_batch(self):
        """Multiple updates with different classifications."""
        await initialize_lpd(PROJECT_ID)
        await append_to_section(PROJECT_ID, "Risks", "- Vendor delay risk")

        updates = [
            LPDUpdate(section="Risks", content="- Vendor delay risk identified"),
            LPDUpdate(section="Decisions", content="- Chose PostgreSQL"),
            LPDUpdate(section="Risks", content="- Q2 deadline now at risk"),
        ]
        gate_response = _gate_response(
            [
                {"index": 0, "classification": "duplicate", "reason": "Already recorded"},
                {"index": 1, "classification": "new", "reason": "New decision"},
                {"index": 2, "classification": "new", "reason": "New risk"},
            ]
        )
        client = _make_client([gate_response])

        result, active = await classify_lpd_updates(PROJECT_ID, updates, client)
        assert result[0].classification.classification == "duplicate"
        assert result[1].classification.classification == "new"
        assert result[2].classification.classification == "new"

    @pytest.mark.asyncio
    async def test_llm_failure_graceful_degradation(self):
        """When LLM call fails, all updates classified as 'new' and gate_active=False."""
        await initialize_lpd(PROJECT_ID)

        updates = [LPDUpdate(section="Risks", content="- Some risk")]

        # Client that raises LLMError
        client = MagicMock()

        async def failing_call(*args, **kwargs):
            raise LLMError("API timeout")

        client.call = failing_call

        result, active = await classify_lpd_updates(PROJECT_ID, updates, client)
        assert len(result) == 1
        assert result[0].classification.classification == "new"
        assert result[0].classification.reason == "Content gate unavailable"
        assert active is False

    @pytest.mark.asyncio
    async def test_unexpected_error_graceful_degradation(self):
        """Unexpected exceptions also degrade gracefully."""
        await initialize_lpd(PROJECT_ID)

        updates = [LPDUpdate(section="Risks", content="- Some risk")]

        client = MagicMock()

        async def bad_call(*args, **kwargs):
            raise RuntimeError("unexpected")

        client.call = bad_call

        result, active = await classify_lpd_updates(PROJECT_ID, updates, client)
        assert result[0].classification.classification == "new"
        assert active is False


# ============================================================
# PIPELINE INTEGRATION
# ============================================================


class TestContentGateInPipeline:
    @pytest.mark.asyncio
    async def test_duplicates_not_applied_to_lpd(self, monkeypatch):
        """Duplicate updates are skipped — not written to LPD."""
        await initialize_lpd(PROJECT_ID)
        await append_to_section(PROJECT_ID, "Risks", "- Existing risk")

        gate_response = _gate_response(
            [{"index": 0, "classification": "duplicate", "reason": "Already exists"}]
        )
        responses = [
            "general_text",  # input classification
            _log_session_response(),  # log session LLM
            gate_response,  # content gate
        ]
        _patch_llm(monkeypatch, responses)

        result = await run_artifact_sync(
            "Session conclusions.",
            project_id=PROJECT_ID,
            mode="log_session",
        )

        # Update returned in response with classification
        assert len(result.lpd_updates) == 1
        assert result.lpd_updates[0].classification.classification == "duplicate"

        # But NOT written to LPD
        lpd = await get_full_lpd(PROJECT_ID)
        assert "Vendor delay" not in lpd.get("Risks", "")
        assert "Existing risk" in lpd["Risks"]

    @pytest.mark.asyncio
    async def test_contradictions_not_applied_to_lpd(self, monkeypatch):
        """Contradiction updates are flagged but not written to LPD."""
        await initialize_lpd(PROJECT_ID)
        await append_to_section(PROJECT_ID, "Risks", "- Original risk statement")

        gate_response = _gate_response(
            [{"index": 0, "classification": "contradiction", "reason": "Contradicts existing"}]
        )
        responses = ["general_text", _log_session_response(), gate_response]
        _patch_llm(monkeypatch, responses)

        result = await run_artifact_sync(
            "Session.",
            project_id=PROJECT_ID,
            mode="log_session",
        )

        assert result.lpd_updates[0].classification.classification == "contradiction"
        lpd = await get_full_lpd(PROJECT_ID)
        assert "Vendor delay" not in lpd.get("Risks", "")

    @pytest.mark.asyncio
    async def test_new_and_update_applied_to_lpd(self, monkeypatch):
        """New and update classifications are written to LPD."""
        await initialize_lpd(PROJECT_ID)

        log_resp = _log_session_response(
            lpd_updates=[
                {"section": "Risks", "content": "- New risk item"},
                {"section": "Decisions", "content": "- Updated decision details"},
            ]
        )
        gate_response = _gate_response(
            [
                {"index": 0, "classification": "new", "reason": "New info"},
                {"index": 1, "classification": "update", "reason": "Extends existing"},
            ]
        )
        responses = ["general_text", log_resp, gate_response]
        _patch_llm(monkeypatch, responses)

        await run_artifact_sync(
            "Session.",
            project_id=PROJECT_ID,
            mode="log_session",
        )

        lpd = await get_full_lpd(PROJECT_ID)
        assert "New risk item" in lpd["Risks"]
        assert "Updated decision details" in lpd["Decisions"]

    @pytest.mark.asyncio
    async def test_gate_failure_applies_all(self, monkeypatch):
        """When content gate fails, all updates are applied (graceful degradation)."""
        await initialize_lpd(PROJECT_ID)

        responses = [
            "general_text",
            _log_session_response(),
            # Third call will hit the default "general_text" fallback which is invalid JSON
            # But we need to simulate an LLM error — let's provide bad JSON
            "not valid json",
        ]
        _patch_llm(monkeypatch, responses)

        result = await run_artifact_sync(
            "Session.",
            project_id=PROJECT_ID,
            mode="log_session",
        )

        # Gate parse failure falls back to all-new, which are auto-applied
        assert len(result.lpd_updates) == 1
        lpd = await get_full_lpd(PROJECT_ID)
        assert "Vendor delay" in lpd.get("Risks", "")

    @pytest.mark.asyncio
    async def test_content_gate_active_in_response(self, monkeypatch):
        """API response includes content_gate_active flag."""
        await initialize_lpd(PROJECT_ID)

        gate_response = _gate_response([{"index": 0, "classification": "new", "reason": "New"}])
        responses = ["general_text", _log_session_response(), gate_response]
        _patch_llm(monkeypatch, responses)

        result = await run_artifact_sync(
            "Session.",
            project_id=PROJECT_ID,
            mode="log_session",
        )

        assert result.content_gate_active is True

    @pytest.mark.asyncio
    async def test_extract_mode_unaffected(self, monkeypatch):
        """Extract mode doesn't invoke the content gate."""
        await initialize_lpd(PROJECT_ID)

        extract_response = json.dumps(
            [
                {
                    "artifact_type": "RAID Log",
                    "change_type": "add",
                    "section": "Risks",
                    "proposed_text": "| R-NEW | Test risk | Low | Low | Monitor | PM | Open |",
                    "confidence": 0.9,
                    "reasoning": "Test",
                }
            ]
        )
        responses = ["general_text", extract_response]
        _patch_llm(monkeypatch, responses)

        result = await run_artifact_sync(
            "Some meeting notes.",
            project_id=PROJECT_ID,
            mode="extract",
        )

        assert result.mode == "extract"
        assert result.content_gate_active is True  # default, gate not involved

    @pytest.mark.asyncio
    async def test_no_lpd_skips_gate(self, monkeypatch):
        """When no LPD exists, updates are marked as 'new' without gate LLM call."""
        responses = [
            "general_text",
            _log_session_response(),
            # No third response needed — gate is skipped
        ]
        _patch_llm(monkeypatch, responses)

        result = await run_artifact_sync(
            "Session.",
            project_id=PROJECT_ID,
            mode="log_session",
        )

        assert len(result.lpd_updates) == 1
        assert result.lpd_updates[0].classification.classification == "new"
        assert "No existing project hub" in result.lpd_updates[0].classification.reason


# ============================================================
# AUTO_APPLY_CLASSIFICATIONS CONSTANT
# ============================================================


class TestAutoApplyClassifications:
    def test_new_is_auto_apply(self):
        assert "new" in AUTO_APPLY_CLASSIFICATIONS

    def test_update_is_auto_apply(self):
        assert "update" in AUTO_APPLY_CLASSIFICATIONS

    def test_duplicate_not_auto_apply(self):
        assert "duplicate" not in AUTO_APPLY_CLASSIFICATIONS

    def test_contradiction_not_auto_apply(self):
        assert "contradiction" not in AUTO_APPLY_CLASSIFICATIONS
