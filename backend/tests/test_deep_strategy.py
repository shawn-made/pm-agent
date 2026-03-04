"""Tests for VPMA Deep Strategy — 4-Pass Multi-Artifact Consistency Analysis Engine.

Tests cover: JSON parsers, pipeline orchestration, privacy proxy integration,
session logging, apply logic, and edge cases.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.models.schemas import (
    DeepStrategyApplyRequest,
    DeepStrategyArtifact,
    ProposedUpdate,
    ValidationCheck,
)
from app.services.deep_strategy import (
    _apply_updates_for_validation,
    _build_artifact_block,
    _compute_summary,
    _extract_json_array,
    _extract_json_object,
    _parse_dependency_graph,
    _parse_inconsistencies,
    _parse_proposed_updates,
    _parse_validation,
    _strip_code_fences,
    apply_deep_strategy_updates,
    run_deep_strategy,
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================


def _make_artifact(name: str, content: str, priority: int = 1) -> DeepStrategyArtifact:
    return DeepStrategyArtifact(name=name, content=content, priority=priority)


# ============================================================
# CODE FENCE STRIPPING
# ============================================================


class TestStripCodeFences:
    def test_strips_json_fence(self):
        text = '```json\n{"key": "value"}\n```'
        assert _strip_code_fences(text) == '{"key": "value"}'

    def test_strips_plain_fence(self):
        text = "```\n[1, 2, 3]\n```"
        assert _strip_code_fences(text) == "[1, 2, 3]"

    def test_no_fence_unchanged(self):
        text = '{"key": "value"}'
        assert _strip_code_fences(text) == '{"key": "value"}'

    def test_strips_whitespace(self):
        text = '  \n```json\n{"key": "value"}\n```  \n'
        assert _strip_code_fences(text) == '{"key": "value"}'


# ============================================================
# JSON EXTRACTION
# ============================================================


class TestExtractJsonObject:
    def test_extracts_plain_json(self):
        text = '{"artifacts": ["a", "b"], "summary": "test"}'
        result = _extract_json_object(text)
        assert result == {"artifacts": ["a", "b"], "summary": "test"}

    def test_extracts_from_surrounding_text(self):
        text = 'Here is the result:\n{"key": "value"}\nDone!'
        result = _extract_json_object(text)
        assert result == {"key": "value"}

    def test_extracts_from_code_fence(self):
        text = '```json\n{"key": "value"}\n```'
        result = _extract_json_object(text)
        assert result == {"key": "value"}

    def test_returns_none_for_no_json(self):
        assert _extract_json_object("No JSON here") is None

    def test_returns_none_for_invalid_json(self):
        assert _extract_json_object("{invalid json}") is None


class TestExtractJsonArray:
    def test_extracts_plain_array(self):
        text = '[{"a": 1}, {"b": 2}]'
        result = _extract_json_array(text)
        assert result == [{"a": 1}, {"b": 2}]

    def test_extracts_from_surrounding_text(self):
        text = 'Results:\n[{"item": "test"}]\nEnd.'
        result = _extract_json_array(text)
        assert result == [{"item": "test"}]

    def test_returns_none_for_no_array(self):
        assert _extract_json_array("No array here") is None

    def test_returns_empty_array(self):
        result = _extract_json_array("[]")
        assert result == []


# ============================================================
# PARSERS — Pass 1: Dependency Graph
# ============================================================


class TestParseDependencyGraph:
    def test_parses_valid_graph(self):
        response = json.dumps(
            {
                "artifacts": ["Charter", "Schedule"],
                "edges": [
                    {
                        "source": "Charter",
                        "target": "Schedule",
                        "relationship": "defines timeline for",
                    }
                ],
                "summary": "Charter drives Schedule",
            }
        )
        graph = _parse_dependency_graph(response)
        assert graph.artifacts == ["Charter", "Schedule"]
        assert len(graph.edges) == 1
        assert graph.edges[0].source == "Charter"
        assert graph.summary == "Charter drives Schedule"

    def test_returns_empty_graph_on_invalid_json(self):
        graph = _parse_dependency_graph("Not JSON at all")
        assert graph.artifacts == []
        assert graph.edges == []
        assert graph.summary == ""

    def test_skips_malformed_edges(self):
        response = json.dumps(
            {
                "artifacts": ["A"],
                "edges": [
                    {"source": "A", "target": "B", "relationship": "good"},
                    {"bad": "edge"},  # Missing required fields
                ],
                "summary": "test",
            }
        )
        graph = _parse_dependency_graph(response)
        assert len(graph.edges) == 1

    def test_handles_missing_fields(self):
        response = json.dumps({"artifacts": ["A"]})
        graph = _parse_dependency_graph(response)
        assert graph.artifacts == ["A"]
        assert graph.edges == []
        assert graph.summary == ""


# ============================================================
# PARSERS — Pass 2: Inconsistencies
# ============================================================


class TestParseInconsistencies:
    def test_parses_valid_inconsistencies(self):
        response = json.dumps(
            [
                {
                    "id": "INC-1",
                    "source_artifact": "Charter",
                    "target_artifact": "Schedule",
                    "description": "Timeline mismatch",
                    "severity": "high",
                    "source_excerpt": "Q3 delivery",
                    "target_excerpt": "Q4 start",
                }
            ]
        )
        result = _parse_inconsistencies(response)
        assert len(result) == 1
        assert result[0].id == "INC-1"
        assert result[0].severity == "high"

    def test_returns_empty_on_invalid(self):
        assert _parse_inconsistencies("Not JSON") == []

    def test_skips_malformed_items(self):
        response = json.dumps(
            [
                {
                    "id": "INC-1",
                    "source_artifact": "A",
                    "target_artifact": "B",
                    "description": "Valid",
                    "severity": "low",
                    "source_excerpt": "x",
                    "target_excerpt": "y",
                },
                {"bad": "item"},
            ]
        )
        result = _parse_inconsistencies(response)
        assert len(result) == 1


# ============================================================
# PARSERS — Pass 3: Proposed Updates
# ============================================================


class TestParseProposedUpdates:
    def test_parses_valid_updates(self):
        response = json.dumps(
            [
                {
                    "inconsistency_id": "INC-1",
                    "artifact_name": "Schedule",
                    "section": "Timeline",
                    "current_text": "Q4 start",
                    "proposed_text": "Q3 start",
                    "change_type": "modify",
                    "rationale": "Align with Charter",
                }
            ]
        )
        result = _parse_proposed_updates(response)
        assert len(result) == 1
        assert result[0].change_type == "modify"

    def test_returns_empty_on_invalid(self):
        assert _parse_proposed_updates("garbage") == []

    def test_skips_malformed_items(self):
        response = json.dumps(
            [
                {
                    "inconsistency_id": "INC-1",
                    "artifact_name": "A",
                    "section": "S",
                    "current_text": "old",
                    "proposed_text": "new",
                    "change_type": "modify",
                    "rationale": "reason",
                },
                {},
            ]
        )
        result = _parse_proposed_updates(response)
        assert len(result) == 1


# ============================================================
# PARSERS — Pass 4: Validation Checks
# ============================================================


class TestParseValidation:
    def test_parses_valid_checks(self):
        response = json.dumps(
            [
                {
                    "artifact_name": "Schedule",
                    "check_description": "Timeline alignment",
                    "passed": True,
                    "detail": "All dates consistent",
                }
            ]
        )
        result = _parse_validation(response)
        assert len(result) == 1
        assert result[0].passed is True

    def test_returns_empty_on_invalid(self):
        assert _parse_validation("not json") == []


# ============================================================
# ARTIFACT BLOCK BUILDER
# ============================================================


class TestBuildArtifactBlock:
    def test_builds_sorted_by_priority(self):
        artifacts = [
            _make_artifact("B", "Content B", priority=2),
            _make_artifact("A", "Content A", priority=1),
        ]
        block = _build_artifact_block(artifacts)
        assert block.index("A") < block.index("B")

    def test_includes_name_and_content(self):
        artifacts = [_make_artifact("Charter", "The project charter text")]
        block = _build_artifact_block(artifacts)
        assert "Artifact: Charter" in block
        assert "The project charter text" in block
        assert "End: Charter" in block


# ============================================================
# APPLY UPDATES FOR VALIDATION
# ============================================================


class TestApplyUpdatesForValidation:
    def test_apply_add_update(self):
        artifacts = [_make_artifact("Doc", "Original content")]
        updates = [
            ProposedUpdate(
                inconsistency_id="INC-1",
                artifact_name="Doc",
                section="Scope",
                current_text="",
                proposed_text="New scope item",
                change_type="add",
                rationale="r",
            )
        ]
        result = _apply_updates_for_validation(artifacts, updates)
        assert "[NEW in Scope]" in result
        assert "New scope item" in result

    def test_apply_modify_update(self):
        artifacts = [_make_artifact("Doc", "Old text here")]
        updates = [
            ProposedUpdate(
                inconsistency_id="INC-1",
                artifact_name="Doc",
                section="",
                current_text="Old text",
                proposed_text="New text",
                change_type="modify",
                rationale="r",
            )
        ]
        result = _apply_updates_for_validation(artifacts, updates)
        assert "[UPDATED] New text" in result
        assert "Old text" not in result

    def test_apply_remove_update(self):
        artifacts = [_make_artifact("Doc", "Keep this. Remove this part. Keep too.")]
        updates = [
            ProposedUpdate(
                inconsistency_id="INC-1",
                artifact_name="Doc",
                section="",
                current_text="Remove this part.",
                proposed_text="",
                change_type="remove",
                rationale="r",
            )
        ]
        result = _apply_updates_for_validation(artifacts, updates)
        assert "[REMOVED]" in result
        assert "Remove this part." not in result

    def test_ignores_unknown_artifact(self):
        artifacts = [_make_artifact("Doc", "Content")]
        updates = [
            ProposedUpdate(
                inconsistency_id="INC-1",
                artifact_name="Unknown",
                section="",
                current_text="",
                proposed_text="text",
                change_type="add",
                rationale="r",
            )
        ]
        result = _apply_updates_for_validation(artifacts, updates)
        assert "Content" in result
        assert "Unknown" not in result


# ============================================================
# SUMMARY COMPUTATION
# ============================================================


class TestComputeSummary:
    def test_all_passed(self):
        artifacts = [_make_artifact("A", "x"), _make_artifact("B", "y")]
        checks = [
            ValidationCheck(artifact_name="A", check_description="c1", passed=True, detail="ok"),
            ValidationCheck(artifact_name="B", check_description="c2", passed=True, detail="ok"),
        ]
        summary = _compute_summary(artifacts, [], [], checks)
        assert summary.artifacts_analyzed == 2
        assert summary.validation_passed is True
        assert summary.consistency_score == 1.0

    def test_partial_pass(self):
        checks = [
            ValidationCheck(artifact_name="A", check_description="c1", passed=True, detail="ok"),
            ValidationCheck(artifact_name="B", check_description="c2", passed=False, detail="fail"),
        ]
        summary = _compute_summary([], [MagicMock()], [MagicMock()], checks)
        assert summary.validation_passed is False
        assert summary.consistency_score == 0.5

    def test_no_checks_defaults_to_passed(self):
        summary = _compute_summary([], [], [], [])
        assert summary.validation_passed is True
        assert summary.consistency_score == 1.0

    def test_counts(self):
        arts = [_make_artifact("A", "x")]
        incs = [MagicMock(), MagicMock()]
        updates = [MagicMock()]
        summary = _compute_summary(arts, incs, updates, [])
        assert summary.artifacts_analyzed == 1
        assert summary.inconsistencies_found == 2
        assert summary.updates_proposed == 1


# ============================================================
# FULL PIPELINE (Mocked LLM)
# ============================================================


class TestRunDeepStrategy:
    """Full pipeline tests with mocked LLM client and privacy proxy."""

    @pytest.fixture
    def mock_llm_client(self):
        client = AsyncMock()
        client.estimate_tokens = MagicMock(return_value=100)
        client.model = "test-model"
        return client

    @pytest.fixture
    def pass1_response(self):
        return json.dumps(
            {
                "artifacts": ["Charter", "Schedule"],
                "edges": [{"source": "Charter", "target": "Schedule", "relationship": "drives"}],
                "summary": "Charter drives Schedule",
            }
        )

    @pytest.fixture
    def pass2_response(self):
        return json.dumps(
            [
                {
                    "id": "INC-1",
                    "source_artifact": "Charter",
                    "target_artifact": "Schedule",
                    "description": "Timeline mismatch",
                    "severity": "high",
                    "source_excerpt": "Q3",
                    "target_excerpt": "Q4",
                }
            ]
        )

    @pytest.fixture
    def pass3_response(self):
        return json.dumps(
            [
                {
                    "inconsistency_id": "INC-1",
                    "artifact_name": "Schedule",
                    "section": "Timeline",
                    "current_text": "Q4",
                    "proposed_text": "Q3",
                    "change_type": "modify",
                    "rationale": "Align with Charter",
                }
            ]
        )

    @pytest.fixture
    def pass4_response(self):
        return json.dumps(
            [
                {
                    "artifact_name": "Schedule",
                    "check_description": "Timeline alignment",
                    "passed": True,
                    "detail": "All dates consistent",
                }
            ]
        )

    @pytest.mark.asyncio
    async def test_full_pipeline(
        self, mock_llm_client, pass1_response, pass2_response, pass3_response, pass4_response
    ):
        mock_llm_client.call = AsyncMock(
            side_effect=[pass1_response, pass2_response, pass3_response, pass4_response]
        )

        mock_session = MagicMock()
        mock_session.session_id = "test-session-id"

        with (
            patch("app.services.deep_strategy.get_llm_client", return_value=mock_llm_client),
            patch("app.services.deep_strategy.get_custom_terms", return_value=[]),
            patch("app.services.deep_strategy.anonymize") as mock_anon,
            patch("app.services.deep_strategy.reidentify", side_effect=lambda x: x),
            patch("app.services.deep_strategy.create_session", return_value=mock_session),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon text", entities=[])

            artifacts = [
                _make_artifact("Charter", "Project charter content", priority=1),
                _make_artifact("Schedule", "Project schedule content", priority=2),
            ]
            result = await run_deep_strategy(artifacts, project_id="test-proj")

        assert result.session_id == "test-session-id"
        assert len(result.dependency_graph.edges) == 1
        assert len(result.inconsistencies) == 1
        assert len(result.proposed_updates) == 1
        assert len(result.validation_checks) == 1
        assert result.summary.artifacts_analyzed == 2
        assert result.summary.inconsistencies_found == 1
        assert result.summary.validation_passed is True

    @pytest.mark.asyncio
    async def test_pipeline_requires_min_2_artifacts(self):
        with pytest.raises(ValueError, match="at least 2 artifacts"):
            await run_deep_strategy([_make_artifact("A", "x")])

    @pytest.mark.asyncio
    async def test_pipeline_anonymizes_all_artifacts(
        self, mock_llm_client, pass1_response, pass2_response, pass3_response, pass4_response
    ):
        mock_llm_client.call = AsyncMock(
            side_effect=[pass1_response, pass2_response, pass3_response, pass4_response]
        )

        mock_session = MagicMock()
        mock_session.session_id = "s1"

        with (
            patch("app.services.deep_strategy.get_llm_client", return_value=mock_llm_client),
            patch("app.services.deep_strategy.get_custom_terms", return_value=["secret"]),
            patch("app.services.deep_strategy.anonymize") as mock_anon,
            patch("app.services.deep_strategy.reidentify", side_effect=lambda x: x),
            patch("app.services.deep_strategy.create_session", return_value=mock_session),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="redacted", entities=[MagicMock()])

            artifacts = [
                _make_artifact("A", "sensitive content A", priority=1),
                _make_artifact("B", "sensitive content B", priority=2),
            ]
            result = await run_deep_strategy(artifacts)

        # anonymize called once per artifact
        assert mock_anon.call_count == 2
        # PII detected count = 1 entity per artifact * 2 artifacts
        assert result.pii_detected == 2

    @pytest.mark.asyncio
    async def test_pipeline_reidentifies_outputs(
        self, mock_llm_client, pass1_response, pass2_response, pass3_response, pass4_response
    ):
        mock_llm_client.call = AsyncMock(
            side_effect=[pass1_response, pass2_response, pass3_response, pass4_response]
        )

        mock_session = MagicMock()
        mock_session.session_id = "s1"

        reidentify_calls = []

        async def tracking_reidentify(text):
            reidentify_calls.append(text)
            return f"REID:{text}"

        with (
            patch("app.services.deep_strategy.get_llm_client", return_value=mock_llm_client),
            patch("app.services.deep_strategy.get_custom_terms", return_value=[]),
            patch("app.services.deep_strategy.anonymize") as mock_anon,
            patch("app.services.deep_strategy.reidentify", side_effect=tracking_reidentify),
            patch("app.services.deep_strategy.create_session", return_value=mock_session),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon", entities=[])

            artifacts = [
                _make_artifact("A", "content A", priority=1),
                _make_artifact("B", "content B", priority=2),
            ]
            result = await run_deep_strategy(artifacts)

        # Reidentify is called for inconsistency fields, update fields, validation details,
        # graph summary, and edge relationships
        assert len(reidentify_calls) > 0
        # Check that reidentified values are in the output
        assert result.dependency_graph.summary.startswith("REID:")

    @pytest.mark.asyncio
    async def test_pipeline_logs_session(
        self, mock_llm_client, pass1_response, pass2_response, pass3_response, pass4_response
    ):
        mock_llm_client.call = AsyncMock(
            side_effect=[pass1_response, pass2_response, pass3_response, pass4_response]
        )

        mock_session = MagicMock()
        mock_session.session_id = "logged-session"

        with (
            patch("app.services.deep_strategy.get_llm_client", return_value=mock_llm_client),
            patch("app.services.deep_strategy.get_custom_terms", return_value=[]),
            patch("app.services.deep_strategy.anonymize") as mock_anon,
            patch("app.services.deep_strategy.reidentify", side_effect=lambda x: x),
            patch("app.services.deep_strategy.create_session") as mock_create,
        ):
            mock_anon.return_value = MagicMock(anonymized_text="anon", entities=[])
            mock_create.return_value = mock_session

            artifacts = [
                _make_artifact("A", "content", priority=1),
                _make_artifact("B", "content", priority=2),
            ]
            result = await run_deep_strategy(artifacts, project_id="proj-123")

        mock_create.assert_called_once()
        session_arg = mock_create.call_args[0][0]
        assert session_arg.project_id == "proj-123"
        assert session_arg.tab_used == "deep_strategy"
        assert "2 artifacts" in session_arg.user_input
        assert result.session_id == "logged-session"


# ============================================================
# APPLY UPDATES
# ============================================================


class TestApplyDeepStrategyUpdates:
    @pytest.mark.asyncio
    async def test_apply_managed_artifact_modify(self):
        """Managed artifacts (RAID Log, etc.) get direct file writes."""
        mock_artifact = MagicMock()
        mock_artifact.file_path = "/tmp/test_artifact.md"

        request = DeepStrategyApplyRequest(
            updates=[
                ProposedUpdate(
                    inconsistency_id="INC-1",
                    artifact_name="RAID Log",
                    section="Risks",
                    current_text="Old risk text",
                    proposed_text="Updated risk text",
                    change_type="modify",
                    rationale="Align with Charter",
                )
            ],
            project_id="test",
        )

        with (
            patch(
                "app.services.artifact_manager.get_or_create_artifact",
                return_value=mock_artifact,
            ),
            patch(
                "app.services.artifact_manager.read_artifact_content",
                return_value="## Risks\nOld risk text\n",
            ),
            patch("pathlib.Path.write_text") as mock_write,
        ):
            result = await apply_deep_strategy_updates(request)

        assert len(result.applied) == 1
        assert result.applied[0]["status"] == "applied"
        mock_write.assert_called_once()
        written_content = mock_write.call_args[0][0]
        assert "Updated risk text" in written_content

    @pytest.mark.asyncio
    async def test_apply_unmanaged_artifact_goes_to_clipboard(self):
        """Non-VPMA artifacts go to clipboard list."""
        request = DeepStrategyApplyRequest(
            updates=[
                ProposedUpdate(
                    inconsistency_id="INC-1",
                    artifact_name="External Charter",
                    section="Scope",
                    current_text="old",
                    proposed_text="new",
                    change_type="modify",
                    rationale="r",
                )
            ],
            project_id="test",
        )

        result = await apply_deep_strategy_updates(request)
        assert "External Charter" in result.copied_to_clipboard
        assert len(result.applied) == 0

    @pytest.mark.asyncio
    async def test_apply_add_to_managed_artifact(self):
        """Add change type appends content."""
        mock_artifact = MagicMock()
        mock_artifact.file_path = "/tmp/test.md"

        request = DeepStrategyApplyRequest(
            updates=[
                ProposedUpdate(
                    inconsistency_id="INC-1",
                    artifact_name="Status Report",
                    section="Accomplishments",
                    current_text="",
                    proposed_text="New accomplishment",
                    change_type="add",
                    rationale="r",
                )
            ],
            project_id="test",
        )

        with (
            patch(
                "app.services.artifact_manager.get_or_create_artifact",
                return_value=mock_artifact,
            ),
            patch(
                "app.services.artifact_manager.read_artifact_content",
                return_value="## Accomplishments\nExisting item\n\n## Next Steps\nTodo",
            ),
            patch("pathlib.Path.write_text") as mock_write,
        ):
            result = await apply_deep_strategy_updates(request)

        assert result.applied[0]["status"] == "applied"
        written = mock_write.call_args[0][0]
        assert "New accomplishment" in written

    @pytest.mark.asyncio
    async def test_apply_handles_error_gracefully(self):
        """Errors in apply are logged and returned, not raised."""
        request = DeepStrategyApplyRequest(
            updates=[
                ProposedUpdate(
                    inconsistency_id="INC-1",
                    artifact_name="Meeting Notes",
                    section="Actions",
                    current_text="",
                    proposed_text="Action item",
                    change_type="add",
                    rationale="r",
                )
            ],
            project_id="test",
        )

        with patch(
            "app.services.artifact_manager.get_or_create_artifact",
            side_effect=Exception("DB error"),
        ):
            result = await apply_deep_strategy_updates(request)

        assert len(result.applied) == 1
        assert "error" in result.applied[0]["status"]


# ============================================================
# EDGE CASES
# ============================================================


class TestEdgeCases:
    def test_parse_graph_with_code_fences(self):
        response = '```json\n{"artifacts": ["A"], "edges": [], "summary": "s"}\n```'
        graph = _parse_dependency_graph(response)
        assert graph.artifacts == ["A"]

    def test_parse_inconsistencies_empty_array(self):
        result = _parse_inconsistencies("[]")
        assert result == []

    def test_parse_updates_empty_array(self):
        result = _parse_proposed_updates("[]")
        assert result == []

    def test_parse_validation_empty_array(self):
        result = _parse_validation("[]")
        assert result == []

    @pytest.mark.asyncio
    async def test_pipeline_handles_empty_llm_responses(self):
        """Pipeline completes even when LLM returns no results."""
        mock_client = AsyncMock()
        mock_client.call = AsyncMock(
            side_effect=[
                '{"artifacts": [], "edges": [], "summary": ""}',  # Pass 1
                "[]",  # Pass 2
                "[]",  # Pass 3
                "[]",  # Pass 4
            ]
        )
        mock_client.estimate_tokens = MagicMock(return_value=50)
        mock_client.model = "test"

        mock_session = MagicMock()
        mock_session.session_id = "empty-session"

        with (
            patch("app.services.deep_strategy.get_llm_client", return_value=mock_client),
            patch("app.services.deep_strategy.get_custom_terms", return_value=[]),
            patch("app.services.deep_strategy.anonymize") as mock_anon,
            patch("app.services.deep_strategy.reidentify", side_effect=lambda x: x),
            patch("app.services.deep_strategy.create_session", return_value=mock_session),
        ):
            mock_anon.return_value = MagicMock(anonymized_text="text", entities=[])

            artifacts = [
                _make_artifact("A", "content", priority=1),
                _make_artifact("B", "content", priority=2),
            ]
            result = await run_deep_strategy(artifacts)

        assert result.summary.inconsistencies_found == 0
        assert result.summary.updates_proposed == 0
        assert result.summary.validation_passed is True
