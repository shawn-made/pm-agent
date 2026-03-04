"""Regression tests for Phase 2B prompts — Deep Strategy, Risk Prediction, Reconciliation.

Tests verify prompt structure, required output format, and absence of forbidden patterns.
Follows the same pattern as existing prompt tests in test_prompts.py.
"""

import pytest
from app.prompts.deep_strategy_prompts import (
    PASS1_DEPENDENCY_GRAPH,
    PASS2_INCONSISTENCY_DETECTION,
    PASS3_PROPOSED_UPDATES,
    PASS4_CROSS_VALIDATION,
)
from app.prompts.lpd_prompts import CROSS_SECTION_RECONCILIATION_PROMPT
from app.prompts.risk_prediction_prompts import RISK_PREDICTION_PROMPT

ALL_PROMPTS = [
    ("PASS1_DEPENDENCY_GRAPH", PASS1_DEPENDENCY_GRAPH),
    ("PASS2_INCONSISTENCY_DETECTION", PASS2_INCONSISTENCY_DETECTION),
    ("PASS3_PROPOSED_UPDATES", PASS3_PROPOSED_UPDATES),
    ("PASS4_CROSS_VALIDATION", PASS4_CROSS_VALIDATION),
    ("RISK_PREDICTION_PROMPT", RISK_PREDICTION_PROMPT),
    ("CROSS_SECTION_RECONCILIATION_PROMPT", CROSS_SECTION_RECONCILIATION_PROMPT),
]


class TestPromptStructure:
    """All prompts must specify JSON output format and be non-empty."""

    @pytest.mark.parametrize("name,prompt", ALL_PROMPTS)
    def test_prompt_is_non_empty(self, name, prompt):
        assert len(prompt.strip()) > 100, f"{name} prompt is too short"

    @pytest.mark.parametrize("name,prompt", ALL_PROMPTS)
    def test_prompt_specifies_json_output(self, name, prompt):
        assert "JSON" in prompt or "json" in prompt, f"{name} does not mention JSON output format"

    @pytest.mark.parametrize("name,prompt", ALL_PROMPTS)
    def test_prompt_has_no_placeholder_anti_pattern(self, name, prompt):
        # Prompts should instruct NOT to use placeholders, not contain them as output
        assert "[TBD]" not in prompt or "Never use" in prompt or "Do not" in prompt


class TestDeepStrategyPrompts:
    """Deep Strategy prompts must reference expected output fields."""

    def test_pass1_references_dependency_fields(self):
        assert "artifacts" in PASS1_DEPENDENCY_GRAPH
        assert "edges" in PASS1_DEPENDENCY_GRAPH
        assert "summary" in PASS1_DEPENDENCY_GRAPH
        assert "relationship" in PASS1_DEPENDENCY_GRAPH

    def test_pass2_references_inconsistency_fields(self):
        assert "source_artifact" in PASS2_INCONSISTENCY_DETECTION
        assert "target_artifact" in PASS2_INCONSISTENCY_DETECTION
        assert "severity" in PASS2_INCONSISTENCY_DETECTION
        assert "source_excerpt" in PASS2_INCONSISTENCY_DETECTION

    def test_pass3_references_update_fields(self):
        assert "inconsistency_id" in PASS3_PROPOSED_UPDATES
        assert "artifact_name" in PASS3_PROPOSED_UPDATES
        assert "current_text" in PASS3_PROPOSED_UPDATES
        assert "proposed_text" in PASS3_PROPOSED_UPDATES
        assert "change_type" in PASS3_PROPOSED_UPDATES

    def test_pass4_references_validation_fields(self):
        assert "artifact_name" in PASS4_CROSS_VALIDATION
        assert "check_description" in PASS4_CROSS_VALIDATION
        assert "passed" in PASS4_CROSS_VALIDATION


class TestRiskPredictionPrompt:
    """Risk prediction prompt must reference expected output fields and categories."""

    def test_references_output_fields(self):
        assert "description" in RISK_PREDICTION_PROMPT
        assert "severity" in RISK_PREDICTION_PROMPT
        assert "evidence" in RISK_PREDICTION_PROMPT
        assert "confidence" in RISK_PREDICTION_PROMPT
        assert "suggested_raid_entry" in RISK_PREDICTION_PROMPT
        assert "category" in RISK_PREDICTION_PROMPT

    def test_references_risk_categories(self):
        for cat in ["timeline", "resource", "scope", "stakeholder", "quality"]:
            assert cat in RISK_PREDICTION_PROMPT, f"Missing category: {cat}"

    def test_references_staleness(self):
        assert (
            "stale" in RISK_PREDICTION_PROMPT.lower()
            or "staleness" in RISK_PREDICTION_PROMPT.lower()
        )


class TestReconciliationPrompt:
    """Cross-section reconciliation prompt must reference impact types and LPD sections."""

    def test_references_impact_types(self):
        for impact_type in ["resolves", "contradicts", "supersedes", "requires_update"]:
            assert impact_type in CROSS_SECTION_RECONCILIATION_PROMPT, (
                f"Missing impact type: {impact_type}"
            )

    def test_references_output_fields(self):
        assert "source_section" in CROSS_SECTION_RECONCILIATION_PROMPT
        assert "target_section" in CROSS_SECTION_RECONCILIATION_PROMPT
        assert "impact_type" in CROSS_SECTION_RECONCILIATION_PROMPT
        assert "suggested_action" in CROSS_SECTION_RECONCILIATION_PROMPT

    def test_references_lpd_sections(self):
        for section in ["Overview", "Stakeholders", "Risks", "Decisions", "Open Questions"]:
            assert section in CROSS_SECTION_RECONCILIATION_PROMPT, f"Missing LPD section: {section}"
