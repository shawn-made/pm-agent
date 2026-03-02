"""Tests for VPMA In-Flight Project Intake (Task 26).

Tests that:
1. Single file intake extracts entities correctly
2. Multi-file intake combines extractions
3. Conflicts with existing LPD content are detected
4. Draft apply updates the LPD for approved sections only
5. Privacy proxy is applied to intake content
6. API endpoints work correctly
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.models.schemas import (
    INTAKE_FIELD_TO_LPD_SECTION,
    IntakeFile,
)
from app.services.intake import (
    _parse_extraction,
    apply_intake_draft,
    generate_intake_draft,
    process_intake_file,
)
from app.services.lpd_manager import get_full_lpd, initialize_lpd, update_section

PROJECT_ID = "default"


# ============================================================
# HELPERS
# ============================================================


def _extraction_json(
    overview="",
    stakeholders="",
    timeline="",
    risks="",
    decisions="",
    open_questions="",
) -> str:
    return json.dumps(
        {
            "overview": overview,
            "stakeholders": stakeholders,
            "timeline": timeline,
            "risks": risks,
            "decisions": decisions,
            "open_questions": open_questions,
        }
    )


def _patch_intake_llm(monkeypatch, responses: list[str]):
    """Patch the LLM client for intake. Responses are returned in order."""
    call_count = [0]

    async def mock_call(system_prompt, user_prompt, max_tokens=4096):
        idx = call_count[0]
        call_count[0] += 1
        if idx < len(responses):
            return responses[idx]
        return _extraction_json()

    client = MagicMock()
    client.call = mock_call
    client.estimate_tokens = MagicMock(return_value=50)
    client.model = "mock"
    monkeypatch.setattr(
        "app.services.intake._get_llm_client",
        AsyncMock(return_value=client),
    )
    return client


# ============================================================
# _parse_extraction
# ============================================================


class TestParseExtraction:
    def test_valid_json(self):
        response = _extraction_json(
            overview="Project Falcon redesign.",
            risks="- Budget risk.",
        )
        result = _parse_extraction(response, "notes.md")
        assert result.source_file == "notes.md"
        assert result.overview == "Project Falcon redesign."
        assert result.risks == "- Budget risk."
        assert result.stakeholders == ""

    def test_json_with_code_fences(self):
        response = "```json\n" + _extraction_json(overview="Test.") + "\n```"
        result = _parse_extraction(response, "file.md")
        assert result.overview == "Test."

    def test_malformed_json_returns_empty(self):
        result = _parse_extraction("not json at all", "bad.md")
        assert result.source_file == "bad.md"
        assert result.overview == ""

    def test_partial_keys(self):
        result = _parse_extraction('{"overview": "Partial", "risks": "- Risk"}', "partial.md")
        assert result.overview == "Partial"
        assert result.risks == "- Risk"
        assert result.decisions == ""

    def test_extra_text_around_json(self):
        response = (
            "Here is the extraction:\n" + _extraction_json(decisions="- Chose React.") + "\nDone."
        )
        result = _parse_extraction(response, "file.md")
        assert result.decisions == "- Chose React."


# ============================================================
# process_intake_file
# ============================================================


class TestProcessIntakeFile:
    @pytest.mark.asyncio
    async def test_single_file_extraction(self, monkeypatch):
        response = _extraction_json(
            overview="Acme Corp portal redesign.",
            risks="- Timeline risk if vendor delays.",
            stakeholders="- Alice — PM\n- Bob — Dev Lead",
        )
        _patch_intake_llm(monkeypatch, [response])

        extraction, pii_count = await process_intake_file(
            content="Some project notes about the portal redesign.",
            filename="kickoff_notes.md",
        )

        assert extraction.source_file == "kickoff_notes.md"
        assert "portal redesign" in extraction.overview
        assert "Timeline risk" in extraction.risks
        assert pii_count == 0  # No PII in test input

    @pytest.mark.asyncio
    async def test_pii_anonymized_before_llm(self, monkeypatch):
        """Verify PII in content is anonymized before sending to LLM."""
        call_args = []

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            call_args.append(user_prompt)
            return _extraction_json()

        client = MagicMock()
        client.call = mock_call
        client.estimate_tokens = MagicMock(return_value=50)
        client.model = "mock"
        monkeypatch.setattr(
            "app.services.intake._get_llm_client",
            AsyncMock(return_value=client),
        )

        await process_intake_file(
            content="Contact alice@example.com for details.",
            filename="contacts.md",
        )

        # The email should be anonymized in the LLM call
        assert "alice@example.com" not in call_args[0]
        assert "<EMAIL_" in call_args[0]


# ============================================================
# generate_intake_draft
# ============================================================


class TestGenerateIntakeDraft:
    @pytest.mark.asyncio
    async def test_single_file_draft(self, monkeypatch):
        response = _extraction_json(
            overview="Project Falcon — mobile app.",
            risks="- API performance risk.",
        )
        _patch_intake_llm(monkeypatch, [response])

        draft = await generate_intake_draft(
            files=[IntakeFile(filename="plan.md", content="Project plan content.")],
            project_id=PROJECT_ID,
        )

        assert len(draft.extractions) == 1
        assert "Overview" in draft.proposed_sections
        assert "Risks" in draft.proposed_sections
        assert "Project Falcon" in draft.proposed_sections["Overview"]
        assert len(draft.conflicts) == 0

    @pytest.mark.asyncio
    async def test_multi_file_combines_extractions(self, monkeypatch):
        responses = [
            _extraction_json(
                overview="Project Alpha — Phase 1.",
                stakeholders="- Sarah — PM",
            ),
            _extraction_json(
                risks="- Budget overrun risk.",
                stakeholders="- Mike — Tech Lead",
            ),
        ]
        _patch_intake_llm(monkeypatch, responses)

        draft = await generate_intake_draft(
            files=[
                IntakeFile(filename="plan.md", content="Plan content."),
                IntakeFile(filename="risks.md", content="Risk content."),
            ],
            project_id=PROJECT_ID,
        )

        assert len(draft.extractions) == 2
        # Stakeholders should combine both files
        assert "Sarah" in draft.proposed_sections["Stakeholders"]
        assert "Mike" in draft.proposed_sections["Stakeholders"]
        # Overview from first file, Risks from second
        assert "Overview" in draft.proposed_sections
        assert "Risks" in draft.proposed_sections

    @pytest.mark.asyncio
    async def test_conflicts_detected_with_existing_lpd(self, monkeypatch):
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Risks", "- Existing timeline risk.")

        response = _extraction_json(risks="- New budget risk from intake.")
        _patch_intake_llm(monkeypatch, [response])

        draft = await generate_intake_draft(
            files=[IntakeFile(filename="update.md", content="Update content.")],
            project_id=PROJECT_ID,
        )

        assert len(draft.conflicts) == 1
        assert draft.conflicts[0].section == "Risks"
        assert "Existing timeline risk" in draft.conflicts[0].existing
        assert "New budget risk" in draft.conflicts[0].proposed
        assert draft.conflicts[0].source_file == "update.md"

    @pytest.mark.asyncio
    async def test_no_conflicts_when_no_lpd(self, monkeypatch):
        response = _extraction_json(risks="- Some risk.")
        _patch_intake_llm(monkeypatch, [response])

        draft = await generate_intake_draft(
            files=[IntakeFile(filename="file.md", content="Content.")],
            project_id=PROJECT_ID,
        )

        assert len(draft.conflicts) == 0

    @pytest.mark.asyncio
    async def test_empty_extractions_not_in_proposed(self, monkeypatch):
        response = _extraction_json(overview="Only overview.")
        _patch_intake_llm(monkeypatch, [response])

        draft = await generate_intake_draft(
            files=[IntakeFile(filename="file.md", content="Content.")],
            project_id=PROJECT_ID,
        )

        assert "Overview" in draft.proposed_sections
        assert "Risks" not in draft.proposed_sections
        assert "Decisions" not in draft.proposed_sections

    @pytest.mark.asyncio
    async def test_pii_count_accumulated(self, monkeypatch):
        response = _extraction_json(overview="Project info.")
        _patch_intake_llm(monkeypatch, [response, response])

        draft = await generate_intake_draft(
            files=[
                IntakeFile(
                    filename="f1.md",
                    content="Contact alice@example.com for info.",
                ),
                IntakeFile(
                    filename="f2.md",
                    content="Call bob@example.com for support.",
                ),
            ],
            project_id=PROJECT_ID,
        )

        # Each file has at least 1 PII entity (email)
        assert draft.pii_detected >= 2


# ============================================================
# apply_intake_draft
# ============================================================


class TestApplyIntakeDraft:
    @pytest.mark.asyncio
    async def test_apply_all_sections(self):
        proposed = {
            "Overview": "Project Falcon — mobile app.",
            "Risks": "- API risk.",
        }
        updated, skipped = await apply_intake_draft(PROJECT_ID, proposed, ["Overview", "Risks"])

        assert set(updated) == {"Overview", "Risks"}
        assert skipped == []

        lpd = await get_full_lpd(PROJECT_ID)
        assert "Project Falcon" in lpd["Overview"]
        assert "API risk" in lpd["Risks"]

    @pytest.mark.asyncio
    async def test_apply_partial_sections(self):
        proposed = {
            "Overview": "Project info.",
            "Risks": "- Risk A.",
            "Decisions": "- Decision D1.",
        }
        updated, skipped = await apply_intake_draft(PROJECT_ID, proposed, ["Overview", "Decisions"])

        assert "Overview" in updated
        assert "Decisions" in updated
        assert "Risks" in skipped

        lpd = await get_full_lpd(PROJECT_ID)
        assert "Project info" in lpd["Overview"]
        assert "Decision D1" in lpd["Decisions"]
        assert lpd["Risks"] == ""  # Not approved, not applied

    @pytest.mark.asyncio
    async def test_apply_initializes_lpd_if_needed(self):
        """LPD is created automatically if it doesn't exist."""
        proposed = {"Overview": "New project."}
        updated, skipped = await apply_intake_draft(PROJECT_ID, proposed, ["Overview"])

        assert "Overview" in updated
        lpd = await get_full_lpd(PROJECT_ID)
        assert "New project" in lpd["Overview"]

    @pytest.mark.asyncio
    async def test_apply_appends_to_existing_content(self):
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Risks", "- Existing risk.")

        proposed = {"Risks": "- New risk from intake."}
        await apply_intake_draft(PROJECT_ID, proposed, ["Risks"])

        lpd = await get_full_lpd(PROJECT_ID)
        assert "Existing risk" in lpd["Risks"]
        assert "New risk from intake" in lpd["Risks"]


# ============================================================
# INTAKE_FIELD_TO_LPD_SECTION constant
# ============================================================


class TestFieldToSectionMapping:
    def test_all_six_fields_mapped(self):
        assert len(INTAKE_FIELD_TO_LPD_SECTION) == 6
        assert INTAKE_FIELD_TO_LPD_SECTION["overview"] == "Overview"
        assert INTAKE_FIELD_TO_LPD_SECTION["stakeholders"] == "Stakeholders"
        assert INTAKE_FIELD_TO_LPD_SECTION["timeline"] == "Timeline & Milestones"
        assert INTAKE_FIELD_TO_LPD_SECTION["risks"] == "Risks"
        assert INTAKE_FIELD_TO_LPD_SECTION["decisions"] == "Decisions"
        assert INTAKE_FIELD_TO_LPD_SECTION["open_questions"] == "Open Questions"


# ============================================================
# API ENDPOINTS
# ============================================================


class TestIntakeAPIEndpoints:
    @pytest.mark.asyncio
    async def test_preview_endpoint(self, monkeypatch):
        from app.main import app
        from httpx import ASGITransport, AsyncClient

        response_json = _extraction_json(
            overview="API project.",
            risks="- Latency risk.",
        )
        _patch_intake_llm(monkeypatch, [response_json])

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/lpd/{PROJECT_ID}/intake/preview",
                json={"files": [{"filename": "notes.md", "content": "Project notes."}]},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["extractions"]) == 1
        assert "Overview" in data["proposed_sections"]

    @pytest.mark.asyncio
    async def test_preview_empty_files_returns_400(self):
        from app.main import app
        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/lpd/{PROJECT_ID}/intake/preview",
                json={"files": []},
            )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_preview_empty_content_returns_400(self):
        from app.main import app
        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/lpd/{PROJECT_ID}/intake/preview",
                json={"files": [{"filename": "empty.md", "content": "  "}]},
            )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_apply_endpoint(self):
        from app.main import app
        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/lpd/{PROJECT_ID}/intake/apply",
                json={
                    "proposed_sections": {
                        "Overview": "Test project overview.",
                        "Risks": "- Test risk.",
                    },
                    "approved_sections": ["Overview"],
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "Overview" in data["sections_updated"]
        assert "Risks" in data["sections_skipped"]

    @pytest.mark.asyncio
    async def test_apply_no_approved_returns_400(self):
        from app.main import app
        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/lpd/{PROJECT_ID}/intake/apply",
                json={
                    "proposed_sections": {"Overview": "Content."},
                    "approved_sections": [],
                },
            )

        assert response.status_code == 400


# ============================================================
# PROMPT VERIFICATION
# ============================================================


class TestIntakePrompt:
    def test_prompt_has_required_sections(self):
        from app.prompts.lpd_prompts import INTAKE_EXTRACTION_PROMPT

        assert "overview" in INTAKE_EXTRACTION_PROMPT
        assert "stakeholders" in INTAKE_EXTRACTION_PROMPT
        assert "timeline" in INTAKE_EXTRACTION_PROMPT
        assert "risks" in INTAKE_EXTRACTION_PROMPT
        assert "decisions" in INTAKE_EXTRACTION_PROMPT
        assert "open_questions" in INTAKE_EXTRACTION_PROMPT

    def test_prompt_requests_json_output(self):
        from app.prompts.lpd_prompts import INTAKE_EXTRACTION_PROMPT

        assert "JSON" in INTAKE_EXTRACTION_PROMPT
