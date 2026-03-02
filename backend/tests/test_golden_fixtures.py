"""Golden fixture tests — validate API response schemas with zero API calls.

These tests load pre-captured golden responses from live Gemini API runs
and validate that they conform to VPMA's Pydantic models and structural
invariants. No LLM or network calls are made — pure schema validation.

Test categories:
1. Pydantic model parsing — every golden response deserializes cleanly
2. Mode-specific invariants — extract has suggestions, analyze has analysis, etc.
3. Content gate classifications — log_session fixtures have correct gate behavior
4. Intake structure — proposed_sections, conflicts, extractions all present
5. Cross-fixture consistency — shared fields (pii_detected, session_id) always present

Run time: <1 second. These parse JSON, they don't execute app code.
"""

import json
from pathlib import Path

import pytest
from app.models.schemas import (
    AnalysisItem,
    ArtifactSyncResponse,
    IntakeConflict,
    IntakeDraft,
    IntakeExtraction,
    LPDUpdate,
    LPDUpdateClassification,
    Suggestion,
)

pytestmark = pytest.mark.smoke  # Fast enough for pre-commit gate

# ---------------------------------------------------------------------------
# Fixture paths
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent / "fixtures"
INPUTS_DIR = FIXTURES_DIR / "inputs"
GOLDEN_DIR = FIXTURES_DIR / "golden_responses"

# All 10 golden response files grouped by mode
EXTRACT_FIXTURES = ["extract_meeting_notes", "extract_status_update", "extract_transcript"]
ANALYZE_FIXTURES = ["analyze_draft_doc", "analyze_rough_plan"]
LOG_SESSION_FIXTURES = ["log_session_new", "log_session_duplicate", "log_session_contradiction"]
INTAKE_FIXTURES = ["intake_charter", "intake_status_report"]

ARTIFACT_SYNC_FIXTURES = EXTRACT_FIXTURES + ANALYZE_FIXTURES + LOG_SESSION_FIXTURES
ALL_FIXTURES = ARTIFACT_SYNC_FIXTURES + INTAKE_FIXTURES


def _load_golden(name: str) -> dict:
    """Load a golden response JSON file by fixture name."""
    path = GOLDEN_DIR / f"{name}.json"
    assert path.exists(), f"Golden fixture not found: {path}"
    return json.loads(path.read_text())


# ---------------------------------------------------------------------------
# Helpers: valid enum values from the Pydantic models
# ---------------------------------------------------------------------------

VALID_ARTIFACT_TYPES = {"RAID Log", "Status Report", "Meeting Notes"}
VALID_CHANGE_TYPES = {"add", "update"}
VALID_INPUT_TYPES = {"meeting_notes", "status_update", "transcript", "general_text"}
VALID_ANALYSIS_CATEGORIES = {"observation", "recommendation", "gap", "strength"}
VALID_ANALYSIS_PRIORITIES = {"high", "medium", "low"}
VALID_GATE_CLASSIFICATIONS = {"new", "duplicate", "update", "contradiction"}
VALID_LPD_SECTIONS = {
    "Overview",
    "Stakeholders",
    "Timeline & Milestones",
    "Risks",
    "Decisions",
    "Open Questions",
    "Recent Context",
}


# ===================================================================
# 1. PYDANTIC MODEL PARSING — every fixture deserializes cleanly
# ===================================================================


class TestArtifactSyncModelParsing:
    """Every artifact-sync golden response parses into ArtifactSyncResponse."""

    @pytest.mark.parametrize("fixture_name", ARTIFACT_SYNC_FIXTURES)
    def test_parses_to_response_model(self, fixture_name):
        data = _load_golden(fixture_name)
        response = ArtifactSyncResponse(**data)
        assert response.session_id  # Always present, non-empty
        assert response.pii_detected >= 0

    @pytest.mark.parametrize("fixture_name", EXTRACT_FIXTURES)
    def test_extract_suggestions_parse(self, fixture_name):
        data = _load_golden(fixture_name)
        for s in data["suggestions"]:
            Suggestion(**s)

    @pytest.mark.parametrize("fixture_name", ANALYZE_FIXTURES)
    def test_analyze_items_parse(self, fixture_name):
        data = _load_golden(fixture_name)
        for item in data["analysis"]:
            AnalysisItem(**item)

    @pytest.mark.parametrize("fixture_name", LOG_SESSION_FIXTURES)
    def test_log_session_updates_parse(self, fixture_name):
        data = _load_golden(fixture_name)
        for u in data["lpd_updates"]:
            update = LPDUpdate(**u)
            if update.classification:
                LPDUpdateClassification(**u["classification"])


class TestIntakeModelParsing:
    """Every intake golden response parses into IntakeDraft."""

    @pytest.mark.parametrize("fixture_name", INTAKE_FIXTURES)
    def test_parses_to_intake_draft(self, fixture_name):
        data = _load_golden(fixture_name)
        draft = IntakeDraft(**data)
        assert draft.pii_detected >= 0

    @pytest.mark.parametrize("fixture_name", INTAKE_FIXTURES)
    def test_extractions_parse(self, fixture_name):
        data = _load_golden(fixture_name)
        for ext in data["extractions"]:
            IntakeExtraction(**ext)

    @pytest.mark.parametrize("fixture_name", INTAKE_FIXTURES)
    def test_conflicts_parse(self, fixture_name):
        data = _load_golden(fixture_name)
        for c in data["conflicts"]:
            IntakeConflict(**c)


# ===================================================================
# 2. MODE-SPECIFIC STRUCTURAL INVARIANTS
# ===================================================================


class TestExtractInvariants:
    """Extract mode: suggestions present, no analysis, no lpd_updates."""

    @pytest.mark.parametrize("fixture_name", EXTRACT_FIXTURES)
    def test_has_suggestions(self, fixture_name):
        data = _load_golden(fixture_name)
        assert len(data["suggestions"]) > 0, "Extract mode must produce suggestions"

    @pytest.mark.parametrize("fixture_name", EXTRACT_FIXTURES)
    def test_no_analysis(self, fixture_name):
        data = _load_golden(fixture_name)
        assert data["analysis"] == [], "Extract mode should not produce analysis items"

    @pytest.mark.parametrize("fixture_name", EXTRACT_FIXTURES)
    def test_no_lpd_updates(self, fixture_name):
        data = _load_golden(fixture_name)
        assert data["lpd_updates"] == [], "Extract mode should not produce LPD updates"

    @pytest.mark.parametrize("fixture_name", EXTRACT_FIXTURES)
    def test_mode_is_extract(self, fixture_name):
        data = _load_golden(fixture_name)
        assert data["mode"] == "extract"

    @pytest.mark.parametrize("fixture_name", EXTRACT_FIXTURES)
    def test_suggestion_fields(self, fixture_name):
        """Each suggestion has required fields with valid values.

        Note: artifact_type is str in the Pydantic model (not an enum), so
        LLM-hallucinated types like 'Open Questions' are schema-valid even
        though the UI only renders RAID Log / Status Report / Meeting Notes.
        """
        data = _load_golden(fixture_name)
        for s in data["suggestions"]:
            assert len(s["artifact_type"]) > 0
            assert s["change_type"] in VALID_CHANGE_TYPES, (
                f"Invalid change_type: {s['change_type']}"
            )
            assert 0.0 <= s["confidence"] <= 1.0, f"Confidence out of range: {s['confidence']}"
            assert len(s["proposed_text"]) > 0
            assert len(s["reasoning"]) > 0
            assert len(s["section"]) > 0

    @pytest.mark.parametrize("fixture_name", EXTRACT_FIXTURES)
    def test_input_type_valid(self, fixture_name):
        data = _load_golden(fixture_name)
        assert data["input_type"] in VALID_INPUT_TYPES


class TestAnalyzeInvariants:
    """Analyze mode: analysis items present, summary present, no suggestions/lpd_updates."""

    @pytest.mark.parametrize("fixture_name", ANALYZE_FIXTURES)
    def test_has_analysis_items(self, fixture_name):
        data = _load_golden(fixture_name)
        assert len(data["analysis"]) > 0, "Analyze mode must produce analysis items"

    @pytest.mark.parametrize("fixture_name", ANALYZE_FIXTURES)
    def test_has_summary(self, fixture_name):
        data = _load_golden(fixture_name)
        assert data["analysis_summary"] is not None
        assert len(data["analysis_summary"]) > 0

    @pytest.mark.parametrize("fixture_name", ANALYZE_FIXTURES)
    def test_no_suggestions(self, fixture_name):
        data = _load_golden(fixture_name)
        assert data["suggestions"] == [], "Analyze mode should not produce suggestions"

    @pytest.mark.parametrize("fixture_name", ANALYZE_FIXTURES)
    def test_no_lpd_updates(self, fixture_name):
        data = _load_golden(fixture_name)
        assert data["lpd_updates"] == [], "Analyze mode should not produce LPD updates"

    @pytest.mark.parametrize("fixture_name", ANALYZE_FIXTURES)
    def test_mode_is_analyze(self, fixture_name):
        data = _load_golden(fixture_name)
        assert data["mode"] == "analyze"

    @pytest.mark.parametrize("fixture_name", ANALYZE_FIXTURES)
    def test_analysis_item_fields(self, fixture_name):
        """Each analysis item has valid category, title, detail, priority."""
        data = _load_golden(fixture_name)
        for item in data["analysis"]:
            assert item["category"] in VALID_ANALYSIS_CATEGORIES, (
                f"Invalid category: {item['category']}"
            )
            assert item["priority"] in VALID_ANALYSIS_PRIORITIES, (
                f"Invalid priority: {item['priority']}"
            )
            assert len(item["title"]) > 0
            assert len(item["detail"]) > 0


class TestLogSessionInvariants:
    """Log session mode: lpd_updates present, session_summary present, suggestions optional."""

    @pytest.mark.parametrize("fixture_name", LOG_SESSION_FIXTURES)
    def test_has_lpd_updates(self, fixture_name):
        data = _load_golden(fixture_name)
        assert len(data["lpd_updates"]) > 0, "Log session must produce LPD updates"

    @pytest.mark.parametrize("fixture_name", LOG_SESSION_FIXTURES)
    def test_has_session_summary(self, fixture_name):
        data = _load_golden(fixture_name)
        assert data["session_summary"] is not None
        assert len(data["session_summary"]) > 0

    @pytest.mark.parametrize("fixture_name", LOG_SESSION_FIXTURES)
    def test_mode_is_log_session(self, fixture_name):
        data = _load_golden(fixture_name)
        assert data["mode"] == "log_session"

    @pytest.mark.parametrize("fixture_name", LOG_SESSION_FIXTURES)
    def test_lpd_update_fields(self, fixture_name):
        """Each LPD update has valid section, non-empty content, source."""
        data = _load_golden(fixture_name)
        for u in data["lpd_updates"]:
            assert u["section"] in VALID_LPD_SECTIONS, f"Invalid LPD section: {u['section']}"
            assert len(u["content"]) > 0
            assert u["source"] == "log_session"

    @pytest.mark.parametrize("fixture_name", LOG_SESSION_FIXTURES)
    def test_no_analysis(self, fixture_name):
        data = _load_golden(fixture_name)
        assert data["analysis"] == [], "Log session should not produce analysis items"


class TestIntakeInvariants:
    """Intake mode: extractions, proposed_sections, and conflicts present."""

    @pytest.mark.parametrize("fixture_name", INTAKE_FIXTURES)
    def test_has_extractions(self, fixture_name):
        data = _load_golden(fixture_name)
        assert len(data["extractions"]) > 0, "Intake must produce extractions"

    @pytest.mark.parametrize("fixture_name", INTAKE_FIXTURES)
    def test_has_proposed_sections(self, fixture_name):
        data = _load_golden(fixture_name)
        assert len(data["proposed_sections"]) > 0, "Intake must propose sections"

    @pytest.mark.parametrize("fixture_name", INTAKE_FIXTURES)
    def test_proposed_section_names_valid(self, fixture_name):
        """All proposed section names are valid LPD section names."""
        data = _load_golden(fixture_name)
        for section_name in data["proposed_sections"]:
            assert section_name in VALID_LPD_SECTIONS, (
                f"Invalid section in proposed_sections: {section_name}"
            )

    @pytest.mark.parametrize("fixture_name", INTAKE_FIXTURES)
    def test_extraction_fields(self, fixture_name):
        """Each extraction has source_file and at least some content fields."""
        data = _load_golden(fixture_name)
        content_fields = [
            "overview",
            "stakeholders",
            "timeline",
            "risks",
            "decisions",
            "open_questions",
        ]
        for ext in data["extractions"]:
            assert len(ext["source_file"]) > 0
            # At least one content field should be non-empty
            has_content = any(ext.get(f, "") for f in content_fields)
            assert has_content, f"Extraction from {ext['source_file']} has no content"

    @pytest.mark.parametrize("fixture_name", INTAKE_FIXTURES)
    def test_conflict_fields(self, fixture_name):
        """Each conflict has section, existing, proposed, and source_file."""
        data = _load_golden(fixture_name)
        for c in data["conflicts"]:
            assert c["section"] in VALID_LPD_SECTIONS, (
                f"Invalid section in conflict: {c['section']}"
            )
            assert len(c["existing"]) > 0
            assert len(c["proposed"]) > 0
            assert len(c["source_file"]) > 0


# ===================================================================
# 3. CONTENT GATE CLASSIFICATIONS
# ===================================================================


class TestContentGateClassifications:
    """Log session fixtures exercise the content quality gate correctly."""

    @pytest.mark.parametrize("fixture_name", LOG_SESSION_FIXTURES)
    def test_content_gate_active(self, fixture_name):
        """Content gate should be active for all log session fixtures."""
        data = _load_golden(fixture_name)
        assert data["content_gate_active"] is True

    @pytest.mark.parametrize("fixture_name", LOG_SESSION_FIXTURES)
    def test_all_updates_classified(self, fixture_name):
        """Every LPD update has a classification when the gate is active."""
        data = _load_golden(fixture_name)
        for u in data["lpd_updates"]:
            assert u["classification"] is not None, (
                f"LPD update to {u['section']} missing classification"
            )
            assert u["classification"]["classification"] in VALID_GATE_CLASSIFICATIONS
            assert len(u["classification"]["reason"]) > 0

    def test_new_session_all_new(self):
        """log_session_new: all updates should be classified as 'new'."""
        data = _load_golden("log_session_new")
        classifications = [u["classification"]["classification"] for u in data["lpd_updates"]]
        assert all(c == "new" for c in classifications), (
            f"Expected all 'new', got: {classifications}"
        )

    def test_duplicate_session_no_new(self):
        """log_session_duplicate: no updates should be classified as 'new'."""
        data = _load_golden("log_session_duplicate")
        classifications = [u["classification"]["classification"] for u in data["lpd_updates"]]
        # Duplicate session should detect overlap — updates should be 'duplicate' or 'update'
        assert all(c != "new" for c in classifications), (
            f"Expected no 'new' in duplicate session, got: {classifications}"
        )

    def test_contradiction_session_has_contradictions(self):
        """log_session_contradiction: at least one update classified as 'contradiction'."""
        data = _load_golden("log_session_contradiction")
        classifications = [u["classification"]["classification"] for u in data["lpd_updates"]]
        assert "contradiction" in classifications, (
            f"Expected at least one 'contradiction', got: {classifications}"
        )

    def test_contradiction_count(self):
        """log_session_contradiction: majority of updates are contradictions."""
        data = _load_golden("log_session_contradiction")
        classifications = [u["classification"]["classification"] for u in data["lpd_updates"]]
        contradiction_count = classifications.count("contradiction")
        assert contradiction_count >= 2, (
            f"Expected at least 2 contradictions, got {contradiction_count}: {classifications}"
        )


# ===================================================================
# 4. CROSS-FIXTURE CONSISTENCY
# ===================================================================


class TestCrossFixtureConsistency:
    """Shared invariants across all fixtures."""

    @pytest.mark.parametrize("fixture_name", ARTIFACT_SYNC_FIXTURES)
    def test_session_id_is_uuid_format(self, fixture_name):
        """session_id should look like a UUID (contains hyphens, 36 chars)."""
        data = _load_golden(fixture_name)
        sid = data["session_id"]
        assert len(sid) == 36
        assert sid.count("-") == 4

    @pytest.mark.parametrize("fixture_name", ARTIFACT_SYNC_FIXTURES)
    def test_pii_detected_positive(self, fixture_name):
        """All fixtures should have detected some PII (they contain names)."""
        data = _load_golden(fixture_name)
        assert data["pii_detected"] > 0, "Expected PII detection in fixtures with names"

    @pytest.mark.parametrize("fixture_name", INTAKE_FIXTURES)
    def test_intake_pii_detected_positive(self, fixture_name):
        data = _load_golden(fixture_name)
        assert data["pii_detected"] > 0

    @pytest.mark.parametrize("fixture_name", ARTIFACT_SYNC_FIXTURES)
    def test_content_gate_field_present(self, fixture_name):
        """content_gate_active field exists on all artifact sync responses."""
        data = _load_golden(fixture_name)
        assert "content_gate_active" in data


# ===================================================================
# 5. INPUT FIXTURES EXIST AND ARE NON-EMPTY
# ===================================================================


class TestInputFixturesExist:
    """Verify all input fixture files exist and are non-trivial."""

    INPUT_FIXTURES = [
        "extract_meeting_notes",
        "extract_status_update",
        "extract_transcript",
        "analyze_draft_doc",
        "analyze_rough_plan",
        "log_session_new",
        "log_session_duplicate",
        "log_session_contradiction",
        "intake_charter",
        "intake_status_report",
    ]

    @pytest.mark.parametrize("fixture_name", INPUT_FIXTURES)
    def test_input_file_exists(self, fixture_name):
        path = INPUTS_DIR / f"{fixture_name}.txt"
        assert path.exists(), f"Input fixture not found: {path}"

    @pytest.mark.parametrize("fixture_name", INPUT_FIXTURES)
    def test_input_file_non_empty(self, fixture_name):
        path = INPUTS_DIR / f"{fixture_name}.txt"
        content = path.read_text()
        assert len(content.strip()) > 50, f"Input fixture too short ({len(content)} chars): {path}"

    @pytest.mark.parametrize("fixture_name", INPUT_FIXTURES)
    def test_golden_response_exists(self, fixture_name):
        path = GOLDEN_DIR / f"{fixture_name}.json"
        assert path.exists(), f"Golden response not found: {path}"

    @pytest.mark.parametrize("fixture_name", INPUT_FIXTURES)
    def test_golden_response_valid_json(self, fixture_name):
        path = GOLDEN_DIR / f"{fixture_name}.json"
        data = json.loads(path.read_text())
        assert isinstance(data, dict)


# ===================================================================
# 6. PII SAFETY — no real names leak into fixtures
# ===================================================================


class TestPIISafety:
    """Verify no real names or identifying info leaked into committed fixtures.

    Input fixtures are checked strictly — we fully control their content.
    Golden responses are NOT checked for system names because they were
    captured from a live session whose LPD had accumulated content from
    prior runs (including privacy proxy tokens and LPD conflict quotes).
    Cleaning golden responses would require rewriting LLM output, which
    defeats their purpose as real-world schema validation fixtures.
    """

    # Known real names that must NOT appear in input fixtures
    FORBIDDEN_STRINGS = [
        "Colleague",  # Real system name → should be LegacySIS
        "PowerCampus",  # Real system name → should be CampusPro
        "Informer",  # Real system name → should be ReportHub
        "StarRez",  # Real system name → should be HousingDB
        "PowerFAIDS",  # Real system name → should be FinAidSys
        "Snowflake",  # Real system name → should be DataCloud
        "Tableau",  # Real system name → should be VizBoard
        "SnapLogic",  # Real system name → should be PipelineTool
        "Snowpipe",  # Real system name → should be DataPipe
        "Workday Student",  # Real system name → should be NextGenSIS
        "Salesforce",  # Real system name → should be CRMPlatform
        "TargetX",  # Real system name → should be AdmitTrack
    ]

    INPUT_FIXTURE_NAMES = [
        "extract_meeting_notes",
        "extract_status_update",
        "extract_transcript",
        "analyze_draft_doc",
        "analyze_rough_plan",
        "log_session_new",
        "log_session_duplicate",
        "log_session_contradiction",
        "intake_charter",
        "intake_status_report",
    ]

    @pytest.mark.parametrize("fixture_name", INPUT_FIXTURE_NAMES)
    def test_no_real_system_names_in_inputs(self, fixture_name):
        """Input fixtures must not contain real system/product names."""
        path = INPUTS_DIR / f"{fixture_name}.txt"
        content = path.read_text()
        for forbidden in self.FORBIDDEN_STRINGS:
            assert forbidden not in content, (
                f"Real name '{forbidden}' found in input fixture: {fixture_name}"
            )
