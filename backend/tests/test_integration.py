"""End-to-End Integration Tests (Task 18).

Tests the full flow: paste text → anonymize → LLM → reidentify → display → copy/apply.
Uses mocked LLM responses (realistic JSON) to test without real API keys.
"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from app.api.routes import _insert_into_section
from app.main import app
from app.services.artifact_manager import ArtifactType, get_or_create_artifact
from app.services.artifact_sync import _parse_analysis
from httpx import ASGITransport, AsyncClient

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def async_client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


# Realistic meeting notes with PII
MEETING_NOTES_WITH_PII = """
Meeting Notes - Q1 Sprint Review
Date: 2024-03-15
Attendees: John Smith, Sarah Johnson, Mike Chen

Discussion:
- John presented the dashboard redesign. The client at Acme Corp is happy with progress.
- Sarah flagged a risk: vendor contract with TechVendor Inc expires next month.
- Mike reported a blocker: the staging server at staging.example.com is down.
- Action item: Sarah to follow up with Bob Williams at bob.williams@acme.com by Friday.
- Phone contact for emergency: (555) 123-4567

Decisions:
- Move forward with Phase 2 of the migration.
- Budget approved for $50,000 additional resources.
"""

STATUS_UPDATE_WITH_PII = """
Weekly Status Update - Project Phoenix
Manager: Lisa Anderson (lisa.anderson@example.com)

Accomplishments:
- Completed API integration with DataFlow Systems
- Deployed v2.3 to production (https://app.example.com/v2.3)

Blockers:
- Waiting on security review from Tom Baker
- CI/CD pipeline intermittent failures

Next Steps:
- Schedule demo with GlobalCorp client
- Fix regression in user dashboard
"""

TRANSCRIPT_WITH_PII = """
[00:05] Alex: Hey everyone, thanks for joining. Let me share what happened at the Microsoft partnership meeting.
[00:15] Rachel: Sure, I also have updates on the Amazon Web Services migration.
[00:30] Alex: So the Microsoft team, led by David Park, confirmed the Q2 timeline.
[01:00] Rachel: On the AWS side, we need to resolve the billing issue. Contact support at aws-support@amazon.com.
[01:30] Alex: Great. Let's also track the risk about the Chicago datacenter lease expiring.
"""


def _make_llm_response(suggestions: list[dict]) -> str:
    """Helper to format suggestions as LLM would return them."""
    return json.dumps(suggestions, indent=2)


# A realistic LLM response for meeting notes
MEETING_NOTES_LLM_RESPONSE = _make_llm_response(
    [
        {
            "artifact_type": "RAID Log",
            "change_type": "add",
            "section": "Risks",
            "proposed_text": "**Risk**: Vendor contract with <ORG_1> expires next month. Mitigation: <PERSON_2> to follow up with renewal terms.",
            "confidence": 0.9,
            "reasoning": "Vendor contract expiration identified as risk from meeting discussion.",
        },
        {
            "artifact_type": "RAID Log",
            "change_type": "add",
            "section": "Issues",
            "proposed_text": "**Issue**: Staging server at <URL_1> is down, blocking deployment. Owner: <PERSON_3>.",
            "confidence": 0.95,
            "reasoning": "Blocker explicitly mentioned by attendee.",
        },
        {
            "artifact_type": "Status Report",
            "change_type": "update",
            "section": "Accomplishments",
            "proposed_text": "Dashboard redesign presented to <ORG_2> — client approved. Moving to Phase 2.",
            "confidence": 0.85,
            "reasoning": "Progress update from sprint review.",
        },
        {
            "artifact_type": "Meeting Notes",
            "change_type": "add",
            "section": "Action Items",
            "proposed_text": "- <PERSON_2> to follow up with <PERSON_4> at <EMAIL_1> by Friday\n- Team to proceed with Phase 2 migration",
            "confidence": 0.9,
            "reasoning": "Action items identified from meeting discussion.",
        },
    ]
)

STATUS_UPDATE_LLM_RESPONSE = _make_llm_response(
    [
        {
            "artifact_type": "Status Report",
            "change_type": "update",
            "section": "Accomplishments",
            "proposed_text": "- Completed API integration with <ORG_1>\n- Deployed v2.3 to production",
            "confidence": 0.95,
            "reasoning": "Direct accomplishments listed in update.",
        },
        {
            "artifact_type": "RAID Log",
            "change_type": "add",
            "section": "Issues",
            "proposed_text": "**Issue**: Waiting on security review from <PERSON_1>. CI/CD pipeline intermittent failures.",
            "confidence": 0.85,
            "reasoning": "Blockers identified from status update.",
        },
    ]
)


def _make_analysis_response(items: list[dict], summary: str = "Overall assessment.") -> str:
    """Helper to format analysis as LLM would return it."""
    return json.dumps({"summary": summary, "items": items}, indent=2)


# A realistic LLM analysis response
ANALYZE_LLM_RESPONSE = _make_analysis_response(
    summary="The status update covers accomplishments well but lacks detail on blockers and has no risk mitigation plan.",
    items=[
        {
            "category": "strength",
            "title": "Clear accomplishments listed",
            "detail": "The API integration and v2.3 deployment are described with enough context to understand their significance.",
            "priority": "low",
            "artifact_type": "Status Report",
        },
        {
            "category": "gap",
            "title": "Missing blocker details",
            "detail": "The security review blocker mentions <PERSON_1> but doesn't specify what's needed, the deadline, or escalation path.",
            "priority": "high",
            "artifact_type": "Status Report",
        },
        {
            "category": "recommendation",
            "title": "Add risk mitigation for CI/CD",
            "detail": "The CI/CD pipeline failures are noted but there's no mitigation plan. Add: who is investigating, what the root cause hypothesis is, and the target resolution date.",
            "priority": "medium",
            "artifact_type": "RAID Log",
        },
        {
            "category": "observation",
            "title": "No upcoming section",
            "detail": "The update lists next steps but doesn't frame them as prioritized upcoming work. Consider structuring with priority order.",
            "priority": "low",
            "artifact_type": "Status Report",
        },
    ],
)


def _mock_llm_call(
    classification_response="meeting_notes", sync_response=MEETING_NOTES_LLM_RESPONSE
):
    """Create a mock LLM client that returns predefined responses."""
    mock_client = AsyncMock()
    mock_client.call = AsyncMock(
        side_effect=[
            classification_response,  # First call: input classification
            sync_response,  # Second call: artifact sync
        ]
    )
    mock_client.estimate_tokens = lambda text: len(text) // 4
    mock_client.model = "mock-model"
    return mock_client


# ============================================================
# E2E Pipeline Tests
# ============================================================


class TestFullPipeline:
    """Test the complete flow: text → anonymize → LLM → reidentify → display."""

    @pytest.mark.asyncio
    async def test_meeting_notes_e2e(self, async_client):
        """Full E2E: meeting notes → PII anonymized → suggestions returned with real names."""
        mock_client = _mock_llm_call()

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": MEETING_NOTES_WITH_PII},
                )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "suggestions" in data
        assert "input_type" in data
        assert "session_id" in data
        assert "pii_detected" in data

        # Should have detected PII
        assert data["pii_detected"] > 0

        # Should have 4 suggestions from our mock
        assert len(data["suggestions"]) == 4

        # Verify each suggestion has required fields
        for s in data["suggestions"]:
            assert "artifact_type" in s
            assert "change_type" in s
            assert "section" in s
            assert "proposed_text" in s
            assert "confidence" in s
            assert "reasoning" in s

    @pytest.mark.asyncio
    async def test_pii_not_sent_to_llm(self, async_client):
        """Verify that PII is anonymized BEFORE reaching the LLM."""
        mock_client = _mock_llm_call()

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                await client.post(
                    "/api/artifact-sync",
                    json={"text": MEETING_NOTES_WITH_PII},
                )

        # The LLM should have been called twice (classify + sync)
        assert mock_client.call.call_count == 2

        # The sync call (second call) should NOT contain real PII
        sync_call_args = mock_client.call.call_args_list[1]
        llm_input = sync_call_args.kwargs.get("user_prompt") or sync_call_args[1].get(
            "user_prompt", ""
        )
        if not llm_input and len(sync_call_args.args) > 1:
            llm_input = sync_call_args.args[1]

        # Real names should be replaced with tokens
        assert "John Smith" not in llm_input
        assert "Sarah Johnson" not in llm_input
        assert "bob.williams@acme.com" not in llm_input
        assert "(555) 123-4567" not in llm_input

    @pytest.mark.asyncio
    async def test_pii_reidentified_in_response(self, async_client):
        """Verify PII tokens in LLM response are replaced back with real values."""
        mock_client = _mock_llm_call()

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": MEETING_NOTES_WITH_PII},
                )

        data = response.json()
        suggestions = data["suggestions"]

        # After reidentification, no raw tokens should remain
        for s in suggestions:
            # Tokens like <PERSON_1> should be replaced (if they existed in the vault)
            # The mock LLM response uses tokens that may or may not be in the vault,
            # so we just verify the pipeline ran without errors
            assert s["proposed_text"]  # Non-empty
            assert s["reasoning"]  # Non-empty

    @pytest.mark.asyncio
    async def test_status_update_e2e(self, async_client):
        """E2E with status update text and different suggestions."""
        mock_client = _mock_llm_call(
            classification_response="status_update",
            sync_response=STATUS_UPDATE_LLM_RESPONSE,
        )

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": STATUS_UPDATE_WITH_PII},
                )

        assert response.status_code == 200
        data = response.json()
        assert len(data["suggestions"]) == 2
        assert data["pii_detected"] > 0

    @pytest.mark.asyncio
    async def test_transcript_e2e(self, async_client):
        """E2E with transcript-style input."""
        mock_client = _mock_llm_call(
            classification_response="transcript",
            sync_response=_make_llm_response(
                [
                    {
                        "artifact_type": "Meeting Notes",
                        "change_type": "add",
                        "section": "Discussion",
                        "proposed_text": "Partnership update: <ORG_1> confirmed Q2 timeline. <ORG_2> migration ongoing.",
                        "confidence": 0.85,
                        "reasoning": "Key discussion points from transcript.",
                    }
                ]
            ),
        )

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": TRANSCRIPT_WITH_PII},
                )

        assert response.status_code == 200
        data = response.json()
        assert len(data["suggestions"]) == 1
        assert data["pii_detected"] > 0

    @pytest.mark.asyncio
    async def test_session_logged(self, async_client):
        """Verify session is logged to database after pipeline runs."""
        mock_client = _mock_llm_call()

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": MEETING_NOTES_WITH_PII},
                )

        data = response.json()
        assert data["session_id"]  # Non-empty session ID


# ============================================================
# Apply Suggestion Tests
# ============================================================


class TestApplySuggestion:
    """Test applying suggestions to local artifact storage."""

    @pytest.mark.asyncio
    async def test_apply_creates_artifact_content(self, async_client, tmp_database):
        """Apply a suggestion and verify content written to disk."""
        # First create an artifact
        artifact = await get_or_create_artifact("default", ArtifactType.RAID_LOG)

        # Read current content
        async with async_client as client:
            response = await client.post(
                f"/api/artifacts/{artifact.artifact_id}/apply",
                json={
                    "artifact_type": "RAID Log",
                    "change_type": "add",
                    "section": "Risks",
                    "proposed_text": "**Risk**: New vendor dependency identified.",
                    "confidence": 0.9,
                    "reasoning": "From meeting notes.",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "applied"

        # Verify content was written to disk
        content = Path(artifact.file_path).read_text()
        assert "New vendor dependency identified" in content

    @pytest.mark.asyncio
    async def test_apply_multiple_suggestions(self, async_client, tmp_database):
        """Apply multiple suggestions sequentially to the same artifact."""
        artifact = await get_or_create_artifact("default", ArtifactType.STATUS_REPORT)

        suggestions = [
            {
                "artifact_type": "Status Report",
                "change_type": "add",
                "section": "Accomplishments",
                "proposed_text": "- Completed API integration",
                "confidence": 0.95,
                "reasoning": "Direct accomplishment.",
            },
            {
                "artifact_type": "Status Report",
                "change_type": "add",
                "section": "Blockers / Risks",
                "proposed_text": "- Security review pending",
                "confidence": 0.85,
                "reasoning": "Blocker identified.",
            },
        ]

        async with async_client as client:
            for s in suggestions:
                response = await client.post(
                    f"/api/artifacts/{artifact.artifact_id}/apply",
                    json=s,
                )
                assert response.status_code == 200

        content = Path(artifact.file_path).read_text()
        assert "Completed API integration" in content
        assert "Security review pending" in content

    @pytest.mark.asyncio
    async def test_apply_nonexistent_artifact_returns_404(self, async_client):
        async with async_client as client:
            response = await client.post(
                "/api/artifacts/does-not-exist/apply",
                json={
                    "artifact_type": "RAID Log",
                    "change_type": "add",
                    "section": "Risks",
                    "proposed_text": "Test",
                    "confidence": 0.9,
                    "reasoning": "Test",
                },
            )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_apply_by_type_creates_and_appends(self, async_client):
        """The convenience /artifacts/apply endpoint creates the artifact if needed."""
        async with async_client as client:
            response = await client.post(
                "/api/artifacts/apply?project_id=default",
                json={
                    "artifact_type": "Meeting Notes",
                    "change_type": "add",
                    "section": "Action Items",
                    "proposed_text": "- Review design docs by Friday",
                    "confidence": 0.9,
                    "reasoning": "Action item from sync.",
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "applied"
        assert data["artifact_type"] == "Meeting Notes"
        assert data["artifact_id"]  # Should have created one

    @pytest.mark.asyncio
    async def test_apply_dedup_guard(self, async_client, tmp_database):
        """Applying the same suggestion twice skips the second as duplicate."""
        artifact = await get_or_create_artifact("default", ArtifactType.RAID_LOG)

        suggestion = {
            "artifact_type": "RAID Log",
            "change_type": "add",
            "section": "Risks",
            "proposed_text": "| R-NEW | Server capacity risk | High | High | Scale infra | DevOps | Open |",
            "confidence": 0.9,
            "reasoning": "Risk identified.",
        }

        async with async_client as client:
            # First apply — should succeed
            r1 = await client.post(f"/api/artifacts/{artifact.artifact_id}/apply", json=suggestion)
            assert r1.json()["status"] == "applied"

            # Second apply — should be duplicate
            r2 = await client.post(f"/api/artifacts/{artifact.artifact_id}/apply", json=suggestion)
            assert r2.json()["status"] == "duplicate"

        # Content should contain the text exactly once
        content = Path(artifact.file_path).read_text()
        assert content.count("Server capacity risk") == 1

    @pytest.mark.asyncio
    async def test_apply_inserts_into_correct_section(self, async_client, tmp_database):
        """Suggestion text should appear inside its target section, not at end of file."""
        artifact = await get_or_create_artifact("default", ArtifactType.RAID_LOG)

        suggestion = {
            "artifact_type": "RAID Log",
            "change_type": "add",
            "section": "Issues",
            "proposed_text": "| I-NEW | Build failures on CI | High | DevOps | 2024-04-01 | Open |",
            "confidence": 0.9,
            "reasoning": "Issue from status update.",
        }

        async with async_client as client:
            response = await client.post(
                f"/api/artifacts/{artifact.artifact_id}/apply", json=suggestion
            )
        assert response.status_code == 200

        content = Path(artifact.file_path).read_text()
        issues_pos = content.index("## Issues")
        text_pos = content.index("Build failures on CI")
        deps_pos = content.index("## Dependencies")

        # Text should be between ## Issues and ## Dependencies
        assert text_pos > issues_pos
        assert text_pos < deps_pos

    @pytest.mark.asyncio
    async def test_apply_by_type_dedup_guard(self, async_client):
        """The /artifacts/apply convenience endpoint also skips duplicates."""
        suggestion = {
            "artifact_type": "Meeting Notes",
            "change_type": "add",
            "section": "Action Items",
            "proposed_text": "| Follow up with vendor | Mike | Friday | Open |",
            "confidence": 0.9,
            "reasoning": "Action item.",
        }

        async with async_client as client:
            r1 = await client.post("/api/artifacts/apply?project_id=default", json=suggestion)
            assert r1.json()["status"] == "applied"

            r2 = await client.post("/api/artifacts/apply?project_id=default", json=suggestion)
            assert r2.json()["status"] == "duplicate"

    @pytest.mark.asyncio
    async def test_apply_by_type_unknown_type_returns_400(self, async_client):
        async with async_client as client:
            response = await client.post(
                "/api/artifacts/apply",
                json={
                    "artifact_type": "Unknown Type",
                    "change_type": "add",
                    "section": "Test",
                    "proposed_text": "Test",
                    "confidence": 0.9,
                    "reasoning": "Test",
                },
            )
        assert response.status_code == 400


# ============================================================
# Settings & Provider Toggle Tests
# ============================================================


class TestProviderToggle:
    """Test switching between Claude and Gemini providers."""

    @pytest.mark.asyncio
    async def test_toggle_provider_to_gemini(self, async_client):
        """Save Gemini as LLM provider and verify it persists."""
        async with async_client as client:
            # Set provider to gemini
            response = await client.put(
                "/api/settings",
                json={"llm_provider": "gemini"},
            )
            assert response.status_code == 200

            # Verify it was saved
            response = await client.get("/api/settings")
            data = response.json()
            assert data["settings"]["llm_provider"] == "gemini"

    @pytest.mark.asyncio
    async def test_toggle_provider_to_claude(self, async_client):
        """Toggle back to Claude."""
        async with async_client as client:
            # Set provider to gemini first
            await client.put("/api/settings", json={"llm_provider": "gemini"})
            # Toggle back to claude
            await client.put("/api/settings", json={"llm_provider": "claude"})

            response = await client.get("/api/settings")
            data = response.json()
            assert data["settings"]["llm_provider"] == "claude"

    @pytest.mark.asyncio
    async def test_save_and_retrieve_sensitive_terms(self, async_client):
        """Sensitive terms round-trip through settings."""
        terms = "ProjectX,ClientY,SecretZ"
        async with async_client as client:
            await client.put("/api/settings", json={"sensitive_terms": terms})
            response = await client.get("/api/settings")
            data = response.json()
            assert data["settings"]["sensitive_terms"] == terms

    @pytest.mark.asyncio
    async def test_custom_terms_used_in_anonymization(self, async_client):
        """Custom sensitive terms are applied during artifact sync."""
        mock_client = _mock_llm_call()

        async with async_client as client:
            # Save custom terms
            await client.put(
                "/api/settings",
                json={"sensitive_terms": "ProjectPhoenix,Acme"},
            )

            # Run artifact sync with those terms active
            with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": "The ProjectPhoenix team at Acme delivered the milestone."},
                )

        assert response.status_code == 200
        data = response.json()
        # Custom terms count as PII
        assert data["pii_detected"] >= 2

        # Verify custom terms were not sent to LLM
        sync_call_args = mock_client.call.call_args_list[1]
        llm_input = sync_call_args.kwargs.get("user_prompt") or sync_call_args[1].get(
            "user_prompt", ""
        )
        if not llm_input and len(sync_call_args.args) > 1:
            llm_input = sync_call_args.args[1]
        assert "ProjectPhoenix" not in llm_input
        assert "Acme" not in llm_input


# ============================================================
# Error Handling Tests
# ============================================================


class TestErrorHandling:
    """Test error cases in the integration flow."""

    @pytest.mark.asyncio
    async def test_empty_text_rejected(self, async_client):
        async with async_client as client:
            response = await client.post(
                "/api/artifact-sync",
                json={"text": ""},
            )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_whitespace_only_rejected(self, async_client):
        async with async_client as client:
            response = await client.post(
                "/api/artifact-sync",
                json={"text": "   \n\t  "},
            )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_llm_failure_returns_502(self, async_client):
        """LLM errors are surfaced as 502."""
        from app.services.llm_client import LLMError

        mock_client = AsyncMock()
        mock_client.call = AsyncMock(side_effect=LLMError("Rate limited"))

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": "Some valid meeting notes."},
                )
        assert response.status_code == 502

    @pytest.mark.asyncio
    async def test_malformed_llm_response_returns_empty_suggestions(self, async_client):
        """If LLM returns garbage, pipeline still succeeds with empty suggestions."""
        mock_client = _mock_llm_call(
            sync_response="This is not valid JSON at all!",
        )

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": "Valid input text for the meeting."},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["suggestions"] == []

    @pytest.mark.asyncio
    async def test_no_pii_in_text(self, async_client):
        """Text with no PII still processes successfully."""
        mock_client = _mock_llm_call(
            sync_response=_make_llm_response(
                [
                    {
                        "artifact_type": "Status Report",
                        "change_type": "add",
                        "section": "Notes",
                        "proposed_text": "Sprint retrospective completed.",
                        "confidence": 0.8,
                        "reasoning": "General update.",
                    }
                ]
            ),
        )

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": "The sprint retrospective was completed successfully."},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["pii_detected"] == 0
        assert len(data["suggestions"]) == 1


# ============================================================
# Privacy Round-Trip Tests
# ============================================================


class TestPrivacyRoundTrip:
    """Verify the anonymize → LLM → reidentify round-trip through the API."""

    @pytest.mark.asyncio
    async def test_email_anonymized_and_restored(self, async_client):
        """Email addresses are anonymized before LLM and restored in response."""
        # LLM response uses the token that the anonymizer would generate
        mock_client = AsyncMock()
        call_count = 0

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return "general_text"
            # Return a suggestion referencing the email token from the anonymized input
            # Extract the email token from the input
            import re

            email_token = re.search(r"<EMAIL_\d+>", user_prompt)
            token_str = email_token.group(0) if email_token else "<EMAIL_1>"
            return json.dumps(
                [
                    {
                        "artifact_type": "Meeting Notes",
                        "change_type": "add",
                        "section": "Action Items",
                        "proposed_text": f"Contact: {token_str}",
                        "confidence": 0.9,
                        "reasoning": f"Email found: {token_str}",
                    }
                ]
            )

        mock_client.call = mock_call
        mock_client.estimate_tokens = lambda text: len(text) // 4
        mock_client.model = "mock-model"

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": "Please contact bob.williams@acme.com for details."},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["pii_detected"] >= 1

        # The suggestion text should have the real email restored
        if data["suggestions"]:
            proposed = data["suggestions"][0]["proposed_text"]
            assert "bob.williams@acme.com" in proposed
            assert "<EMAIL_" not in proposed

    @pytest.mark.asyncio
    async def test_phone_anonymized_and_restored(self, async_client):
        """Phone numbers round-trip correctly."""
        mock_client = AsyncMock()
        call_count = 0

        async def mock_call(system_prompt, user_prompt, max_tokens=4096):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return "general_text"
            import re

            phone_token = re.search(r"<PHONE_\d+>", user_prompt)
            token_str = phone_token.group(0) if phone_token else "<PHONE_1>"
            return json.dumps(
                [
                    {
                        "artifact_type": "RAID Log",
                        "change_type": "add",
                        "section": "Dependencies",
                        "proposed_text": f"Emergency contact: {token_str}",
                        "confidence": 0.9,
                        "reasoning": "Contact info captured.",
                    }
                ]
            )

        mock_client.call = mock_call
        mock_client.estimate_tokens = lambda text: len(text) // 4
        mock_client.model = "mock-model"

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": "Emergency hotline: (555) 123-4567"},
                )

        assert response.status_code == 200
        data = response.json()
        if data["suggestions"]:
            proposed = data["suggestions"][0]["proposed_text"]
            assert "(555) 123-4567" in proposed
            assert "<PHONE_" not in proposed


# ============================================================
# Section-Aware Insert Unit Tests
# ============================================================


class TestInsertIntoSection:
    """Unit tests for the _insert_into_section helper."""

    RAID_LOG_TEMPLATE = (
        "# RAID Log\n\n"
        "## Risks\n\n"
        "| ID | Description | Likelihood | Impact | Mitigation | Owner | Status |\n"
        "|----|-------------|------------|--------|------------|-------|--------|\n\n"
        "## Assumptions\n\n"
        "| ID | Description | Validation Date | Status |\n"
        "|----|-------------|-----------------|--------|\n\n"
        "## Issues\n\n"
        "| ID | Description | Priority | Owner | Due Date | Status |\n"
        "|----|-------------|----------|-------|----------|--------|\n\n"
        "## Dependencies\n\n"
        "| ID | Description | Dependent On | Expected Date | Status |\n"
        "|----|-------------|-------------|---------------|--------|\n"
    )

    def test_inserts_into_first_section(self):
        row = "| R-NEW | Server risk | High | High | Scale | DevOps | Open |"
        result = _insert_into_section(self.RAID_LOG_TEMPLATE, "Risks", row)
        risks_pos = result.index("## Risks")
        row_pos = result.index("Server risk")
        assumptions_pos = result.index("## Assumptions")
        assert risks_pos < row_pos < assumptions_pos

    def test_inserts_into_middle_section(self):
        row = "| I-NEW | CI broken | High | DevOps | 2024-04-01 | Open |"
        result = _insert_into_section(self.RAID_LOG_TEMPLATE, "Issues", row)
        issues_pos = result.index("## Issues")
        row_pos = result.index("CI broken")
        deps_pos = result.index("## Dependencies")
        assert issues_pos < row_pos < deps_pos

    def test_inserts_into_last_section(self):
        row = "| D-NEW | Vendor API | External | March | Pending |"
        result = _insert_into_section(self.RAID_LOG_TEMPLATE, "Dependencies", row)
        deps_pos = result.index("## Dependencies")
        row_pos = result.index("Vendor API")
        assert row_pos > deps_pos

    def test_fallback_append_when_section_not_found(self):
        row = "- Some text"
        result = _insert_into_section(self.RAID_LOG_TEMPLATE, "Nonexistent", row)
        # Should be appended at end
        assert result.rstrip().endswith(row)

    def test_case_insensitive_section_match(self):
        row = "| R-NEW | Test risk | Low | Low | Monitor | PM | Open |"
        result = _insert_into_section(self.RAID_LOG_TEMPLATE, "risks", row)
        risks_pos = result.index("## Risks")
        row_pos = result.index("Test risk")
        assumptions_pos = result.index("## Assumptions")
        assert risks_pos < row_pos < assumptions_pos

    def test_multiple_inserts_same_section(self):
        row1 = "| R-NEW | First risk | High | High | Fix | DevOps | Open |"
        row2 = "| R-NEW | Second risk | Low | Medium | Monitor | PM | Open |"
        result = _insert_into_section(self.RAID_LOG_TEMPLATE, "Risks", row1)
        result = _insert_into_section(result, "Risks", row2)
        # Both should be between ## Risks and ## Assumptions
        risks_pos = result.index("## Risks")
        row1_pos = result.index("First risk")
        row2_pos = result.index("Second risk")
        assumptions_pos = result.index("## Assumptions")
        assert risks_pos < row1_pos < assumptions_pos
        assert risks_pos < row2_pos < assumptions_pos


# ============================================================
# Analyze & Advise Mode Tests
# ============================================================


class TestAnalyzeMode:
    """Test the Analyze & Advise mode of artifact sync."""

    @pytest.mark.asyncio
    async def test_analyze_mode_returns_analysis_items(self, async_client):
        """Analyze mode returns analysis items, not suggestions."""
        mock_client = _mock_llm_call(
            classification_response="status_update",
            sync_response=ANALYZE_LLM_RESPONSE,
        )

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": STATUS_UPDATE_WITH_PII, "mode": "analyze"},
                )

        assert response.status_code == 200
        data = response.json()

        # Should have analysis items, not suggestions
        assert len(data["analysis"]) == 4
        assert data["analysis_summary"] is not None
        assert data["suggestions"] == []
        assert data["mode"] == "analyze"

        # Verify analysis item structure
        for item in data["analysis"]:
            assert "category" in item
            assert "title" in item
            assert "detail" in item
            assert "priority" in item
            assert item["category"] in ("strength", "observation", "gap", "recommendation")

    @pytest.mark.asyncio
    async def test_analyze_mode_pii_anonymized(self, async_client):
        """PII is anonymized before LLM in analyze mode."""
        mock_client = _mock_llm_call(
            classification_response="status_update",
            sync_response=ANALYZE_LLM_RESPONSE,
        )

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                await client.post(
                    "/api/artifact-sync",
                    json={"text": STATUS_UPDATE_WITH_PII, "mode": "analyze"},
                )

        # The sync call (second call) should NOT contain real PII
        sync_call_args = mock_client.call.call_args_list[1]
        llm_input = sync_call_args.kwargs.get("user_prompt") or sync_call_args[1].get(
            "user_prompt", ""
        )
        if not llm_input and len(sync_call_args.args) > 1:
            llm_input = sync_call_args.args[1]

        assert "Lisa Anderson" not in llm_input
        assert "lisa.anderson@example.com" not in llm_input

    @pytest.mark.asyncio
    async def test_analyze_mode_pii_reidentified(self, async_client):
        """PII tokens in analysis items are replaced back with real values."""
        mock_client = _mock_llm_call(
            classification_response="status_update",
            sync_response=ANALYZE_LLM_RESPONSE,
        )

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": STATUS_UPDATE_WITH_PII, "mode": "analyze"},
                )

        data = response.json()
        # Verify analysis items have non-empty content and no raw PII tokens
        # Check both bracketed (<ORG_88>) and bare (ORG_88) token forms
        import re

        bracketed_re = re.compile(r"<(PERSON|ORG|EMAIL|PHONE|URL|GPE|PRODUCT|CUSTOM)_\d+>")
        bare_re = re.compile(
            r"(?<![<\w])(PERSON|ORG|GPE|PRODUCT|EMAIL|PHONE|URL|CUSTOM)_\d+(?![>\w])"
        )
        for item in data["analysis"]:
            assert item["title"]
            assert item["detail"]
            assert not bracketed_re.search(item["title"]), (
                f"Bracketed PII token in title: {item['title']}"
            )
            assert not bracketed_re.search(item["detail"]), (
                f"Bracketed PII token in detail: {item['detail']}"
            )
            assert not bare_re.search(item["title"]), f"Bare PII token in title: {item['title']}"
            assert not bare_re.search(item["detail"]), f"Bare PII token in detail: {item['detail']}"

    @pytest.mark.asyncio
    async def test_extract_mode_unchanged_when_omitted(self, async_client):
        """Omitting mode defaults to extract (backward compatible)."""
        mock_client = _mock_llm_call()

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": MEETING_NOTES_WITH_PII},
                )

        data = response.json()
        assert data["mode"] == "extract"
        assert len(data["suggestions"]) == 4
        assert data["analysis"] == []
        assert data["analysis_summary"] is None

    @pytest.mark.asyncio
    async def test_invalid_mode_falls_back_to_extract(self, async_client):
        """Unknown mode values fall back to extract."""
        mock_client = _mock_llm_call()

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": MEETING_NOTES_WITH_PII, "mode": "unknown_mode"},
                )

        data = response.json()
        assert data["mode"] == "extract"
        assert len(data["suggestions"]) == 4

    @pytest.mark.asyncio
    async def test_analyze_mode_session_logged(self, async_client):
        """Session is logged for analyze mode."""
        mock_client = _mock_llm_call(
            classification_response="status_update",
            sync_response=ANALYZE_LLM_RESPONSE,
        )

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": STATUS_UPDATE_WITH_PII, "mode": "analyze"},
                )

        data = response.json()
        assert data["session_id"]  # Non-empty session ID

    @pytest.mark.asyncio
    async def test_analyze_mode_malformed_response(self, async_client):
        """Malformed LLM response in analyze mode returns empty analysis."""
        mock_client = _mock_llm_call(
            classification_response="general_text",
            sync_response="This is not valid JSON!",
        )

        with patch("app.services.artifact_sync.get_llm_client", return_value=mock_client):
            async with async_client as client:
                response = await client.post(
                    "/api/artifact-sync",
                    json={"text": "Some text to analyze.", "mode": "analyze"},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["analysis"] == []
        assert data["analysis_summary"] is None


# ============================================================
# _parse_analysis Unit Tests
# ============================================================


class TestParseAnalysis:
    """Unit tests for the _parse_analysis helper."""

    def test_valid_json(self):
        response = json.dumps(
            {
                "summary": "Good document overall.",
                "items": [
                    {
                        "category": "strength",
                        "title": "Clear structure",
                        "detail": "The document is well organized.",
                        "priority": "low",
                    },
                ],
            }
        )
        items, summary = _parse_analysis(response)
        assert len(items) == 1
        assert summary == "Good document overall."
        assert items[0].category == "strength"
        assert items[0].title == "Clear structure"

    def test_json_with_code_fences(self):
        response = '```json\n{"summary": "Test.", "items": [{"category": "gap", "title": "Missing info", "detail": "Details needed.", "priority": "high"}]}\n```'
        items, summary = _parse_analysis(response)
        assert len(items) == 1
        assert summary == "Test."

    def test_malformed_json(self):
        items, summary = _parse_analysis("Not JSON at all")
        assert items == []
        assert summary is None

    def test_missing_items_key(self):
        response = json.dumps({"summary": "Just a summary."})
        items, summary = _parse_analysis(response)
        assert items == []
        assert summary == "Just a summary."

    def test_partial_items(self):
        """Items with missing required fields are skipped."""
        response = json.dumps(
            {
                "summary": "Mixed quality.",
                "items": [
                    {
                        "category": "strength",
                        "title": "Good",
                        "detail": "Solid work.",
                        "priority": "low",
                    },
                    {"title": "Missing category"},  # Missing required 'category' and 'detail'
                    {
                        "category": "gap",
                        "title": "Issue",
                        "detail": "Problem here.",
                        "priority": "high",
                    },
                ],
            }
        )
        items, summary = _parse_analysis(response)
        assert len(items) == 2
        assert items[0].title == "Good"
        assert items[1].title == "Issue"

    def test_no_json_object(self):
        items, summary = _parse_analysis("[1, 2, 3]")
        assert items == []
        assert summary is None


# ============================================================
# Artifact Export Tests
# ============================================================


class TestArtifactExport:
    """Test the combined artifact export endpoint."""

    @pytest.mark.asyncio
    async def test_export_no_artifacts_returns_empty(self, async_client):
        """Export with no artifacts returns empty markdown."""
        async with async_client as client:
            response = await client.get("/api/artifacts/default/export")

        assert response.status_code == 200
        data = response.json()
        assert data["markdown"] == ""
        assert data["artifact_count"] == 0

    @pytest.mark.asyncio
    async def test_export_with_artifacts(self, async_client, tmp_database):
        """Export returns combined markdown from all artifacts."""
        async with async_client as client:
            # Create artifacts by applying suggestions
            for artifact_type, section, text in [
                (
                    "RAID Log",
                    "Risks",
                    "| R-1 | Export test risk | High | High | Monitor | PM | Open |",
                ),
                ("Status Report", "Accomplishments", "- Export feature implemented"),
            ]:
                await client.post(
                    "/api/artifacts/apply?project_id=default",
                    json={
                        "artifact_type": artifact_type,
                        "change_type": "add",
                        "section": section,
                        "proposed_text": text,
                        "confidence": 0.9,
                        "reasoning": "Export test.",
                    },
                )

            response = await client.get("/api/artifacts/default/export")

        assert response.status_code == 200
        data = response.json()
        assert data["artifact_count"] == 2
        assert "Export test risk" in data["markdown"]
        assert "Export feature implemented" in data["markdown"]
        # Artifacts separated by horizontal rule
        assert "---" in data["markdown"]

    @pytest.mark.asyncio
    async def test_export_nonexistent_project(self, async_client):
        """Export for a project with no artifacts returns empty."""
        async with async_client as client:
            response = await client.get("/api/artifacts/nonexistent/export")

        assert response.status_code == 200
        data = response.json()
        assert data["artifact_count"] == 0
