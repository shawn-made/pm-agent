"""Tests for VPMA Prompt Refinement (Task 28).

Regression tests verifying that all prompts contain required instructions
for context awareness, dedup, quality standards, and output format.
"""

from app.prompts.artifact_sync import (
    ANALYZE_ADVISE_SYSTEM_PROMPT,
    ARTIFACT_SYNC_SYSTEM_PROMPT,
    INPUT_TYPE_DETECTION_PROMPT,
)
from app.prompts.lpd_prompts import (
    CONTENT_GATE_SYSTEM_PROMPT,
    INTAKE_EXTRACTION_PROMPT,
    LOG_SESSION_SYSTEM_PROMPT,
)

# ============================================================
# EXTRACT PROMPT REGRESSION
# ============================================================


class TestExtractPromptRegression:
    """Verify extract prompt retains all required instructions."""

    def test_has_dedup_instructions(self):
        assert "Avoid duplicates" in ARTIFACT_SYNC_SYSTEM_PROMPT
        assert "already exists" in ARTIFACT_SYNC_SYSTEM_PROMPT

    def test_has_context_section(self):
        assert "## Project Context" in ARTIFACT_SYNC_SYSTEM_PROMPT
        assert "Connect the dots" in ARTIFACT_SYNC_SYSTEM_PROMPT

    def test_has_contradiction_handling(self):
        assert "Flag contradictions" in ARTIFACT_SYNC_SYSTEM_PROMPT
        assert "change_type" in ARTIFACT_SYNC_SYSTEM_PROMPT

    def test_has_quality_standard(self):
        assert "standalone test" in ARTIFACT_SYNC_SYSTEM_PROMPT
        assert "BAD:" in ARTIFACT_SYNC_SYSTEM_PROMPT
        assert "GOOD:" in ARTIFACT_SYNC_SYSTEM_PROMPT

    def test_has_anti_placeholder_rule(self):
        assert "Never use placeholder text" in ARTIFACT_SYNC_SYSTEM_PROMPT
        assert "[Insert X]" in ARTIFACT_SYNC_SYSTEM_PROMPT

    def test_has_json_output_format(self):
        assert "JSON array" in ARTIFACT_SYNC_SYSTEM_PROMPT
        assert "artifact_type" in ARTIFACT_SYNC_SYSTEM_PROMPT
        assert "proposed_text" in ARTIFACT_SYNC_SYSTEM_PROMPT

    def test_has_valid_section_names(self):
        assert "Risks" in ARTIFACT_SYNC_SYSTEM_PROMPT
        assert "Accomplishments" in ARTIFACT_SYNC_SYSTEM_PROMPT
        assert "Action Items" in ARTIFACT_SYNC_SYSTEM_PROMPT


# ============================================================
# ANALYZE PROMPT REGRESSION
# ============================================================


class TestAnalyzePromptRegression:
    """Verify analyze prompt retains all required instructions."""

    def test_has_context_section(self):
        assert "## Project Context" in ANALYZE_ADVISE_SYSTEM_PROMPT

    def test_has_gap_detection(self):
        assert "Flag gaps" in ANALYZE_ADVISE_SYSTEM_PROMPT

    def test_has_contradiction_handling(self):
        assert "Identify contradictions" in ANALYZE_ADVISE_SYSTEM_PROMPT

    def test_has_alignment_acknowledgment(self):
        assert "Acknowledge alignment" in ANALYZE_ADVISE_SYSTEM_PROMPT

    def test_has_json_output_format(self):
        assert "JSON" in ANALYZE_ADVISE_SYSTEM_PROMPT
        assert "summary" in ANALYZE_ADVISE_SYSTEM_PROMPT
        assert "items" in ANALYZE_ADVISE_SYSTEM_PROMPT

    def test_has_category_definitions(self):
        assert "strength" in ANALYZE_ADVISE_SYSTEM_PROMPT
        assert "observation" in ANALYZE_ADVISE_SYSTEM_PROMPT
        assert "gap" in ANALYZE_ADVISE_SYSTEM_PROMPT
        assert "recommendation" in ANALYZE_ADVISE_SYSTEM_PROMPT

    def test_has_anti_placeholder_rule(self):
        assert "Never use placeholder text" in ANALYZE_ADVISE_SYSTEM_PROMPT


# ============================================================
# LOG SESSION PROMPT REGRESSION
# ============================================================


class TestLogSessionPromptRegression:
    """Verify log session prompt retains all required instructions."""

    def test_has_context_section(self):
        assert "## Project Context" in LOG_SESSION_SYSTEM_PROMPT

    def test_has_dedup_instructions(self):
        assert "Avoid duplicates" in LOG_SESSION_SYSTEM_PROMPT
        assert "already" in LOG_SESSION_SYSTEM_PROMPT

    def test_has_contradiction_handling(self):
        assert "Flag contradictions" in LOG_SESSION_SYSTEM_PROMPT

    def test_has_json_output_format(self):
        assert "JSON" in LOG_SESSION_SYSTEM_PROMPT
        assert "session_summary" in LOG_SESSION_SYSTEM_PROMPT
        assert "lpd_updates" in LOG_SESSION_SYSTEM_PROMPT
        assert "artifact_suggestions" in LOG_SESSION_SYSTEM_PROMPT

    def test_has_valid_lpd_sections(self):
        assert "Overview" in LOG_SESSION_SYSTEM_PROMPT
        assert "Stakeholders" in LOG_SESSION_SYSTEM_PROMPT
        assert "Risks" in LOG_SESSION_SYSTEM_PROMPT
        assert "Decisions" in LOG_SESSION_SYSTEM_PROMPT
        assert "Open Questions" in LOG_SESSION_SYSTEM_PROMPT

    def test_excludes_recent_context(self):
        """Recent Context section should not be suggested — it's auto-managed."""
        assert "Do NOT use" in LOG_SESSION_SYSTEM_PROMPT
        assert "Recent Context" in LOG_SESSION_SYSTEM_PROMPT

    def test_prioritizes_lpd_over_artifacts(self):
        assert "Prioritize LPD updates over artifact suggestions" in LOG_SESSION_SYSTEM_PROMPT

    def test_has_anti_placeholder_rule(self):
        assert "Never use placeholder text" in LOG_SESSION_SYSTEM_PROMPT
        assert "[Insert X]" in LOG_SESSION_SYSTEM_PROMPT


# ============================================================
# INTAKE PROMPT REGRESSION
# ============================================================


class TestIntakePromptRegression:
    """Verify intake prompt retains all required instructions."""

    def test_has_all_six_categories(self):
        assert "overview" in INTAKE_EXTRACTION_PROMPT
        assert "stakeholders" in INTAKE_EXTRACTION_PROMPT
        assert "timeline" in INTAKE_EXTRACTION_PROMPT
        assert "risks" in INTAKE_EXTRACTION_PROMPT
        assert "decisions" in INTAKE_EXTRACTION_PROMPT
        assert "open_questions" in INTAKE_EXTRACTION_PROMPT

    def test_has_json_output_format(self):
        assert "JSON" in INTAKE_EXTRACTION_PROMPT
        assert '""' in INTAKE_EXTRACTION_PROMPT  # empty string instruction

    def test_has_extraction_guidelines(self):
        assert "Extract facts" in INTAKE_EXTRACTION_PROMPT
        assert "Preserve specifics" in INTAKE_EXTRACTION_PROMPT

    def test_has_anti_placeholder_rule(self):
        assert "Never use placeholder text" in INTAKE_EXTRACTION_PROMPT

    def test_stakeholders_must_be_named_individuals(self):
        """Stakeholder instruction requires named people, not processes or categories."""
        assert "Named individuals" in INTAKE_EXTRACTION_PROMPT
        assert "do NOT include project names" in INTAKE_EXTRACTION_PROMPT

    def test_has_example(self):
        assert "Example" in INTAKE_EXTRACTION_PROMPT
        assert "Project Falcon" in INTAKE_EXTRACTION_PROMPT


# ============================================================
# INPUT CLASSIFICATION PROMPT REGRESSION
# ============================================================


class TestInputClassificationRegression:
    def test_has_all_valid_types(self):
        assert "meeting_notes" in INPUT_TYPE_DETECTION_PROMPT
        assert "status_update" in INPUT_TYPE_DETECTION_PROMPT
        assert "transcript" in INPUT_TYPE_DETECTION_PROMPT
        assert "general_text" in INPUT_TYPE_DETECTION_PROMPT

    def test_requests_single_label(self):
        assert "ONLY the classification label" in INPUT_TYPE_DETECTION_PROMPT


# ============================================================
# CONTENT GATE PROMPT REGRESSION
# ============================================================


class TestContentGatePromptRegression:
    """Verify content gate prompt retains all required instructions."""

    def test_has_four_classifications(self):
        assert "new" in CONTENT_GATE_SYSTEM_PROMPT
        assert "duplicate" in CONTENT_GATE_SYSTEM_PROMPT
        assert "update" in CONTENT_GATE_SYSTEM_PROMPT
        assert "contradiction" in CONTENT_GATE_SYSTEM_PROMPT

    def test_has_json_output_format(self):
        assert "JSON" in CONTENT_GATE_SYSTEM_PROMPT
        assert "index" in CONTENT_GATE_SYSTEM_PROMPT
        assert "classification" in CONTENT_GATE_SYSTEM_PROMPT
        assert "reason" in CONTENT_GATE_SYSTEM_PROMPT

    def test_has_input_format(self):
        assert "existing_content" in CONTENT_GATE_SYSTEM_PROMPT
        assert "proposed_content" in CONTENT_GATE_SYSTEM_PROMPT

    def test_has_semantic_comparison_guideline(self):
        assert "meaning" in CONTENT_GATE_SYSTEM_PROMPT
        assert "wording" in CONTENT_GATE_SYSTEM_PROMPT

    def test_has_safety_preferences(self):
        """Ambiguous cases should prefer safer classifications."""
        assert "contradiction" in CONTENT_GATE_SYSTEM_PROMPT
        assert "update" in CONTENT_GATE_SYSTEM_PROMPT

    def test_has_empty_content_rule(self):
        """Empty existing_content should always classify as new."""
        assert "empty" in CONTENT_GATE_SYSTEM_PROMPT.lower()
        assert '"new"' in CONTENT_GATE_SYSTEM_PROMPT

    def test_has_anti_placeholder_rule(self):
        assert "Never use placeholder text" in CONTENT_GATE_SYSTEM_PROMPT
