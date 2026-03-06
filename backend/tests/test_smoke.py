"""Smoke tests — fast critical-path validation (<10s total).

Run with: pytest -m smoke --timeout=10 -q
These run as a pre-commit gate to catch broken fundamentals before the full suite.
"""

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient

pytestmark = pytest.mark.smoke


@pytest.fixture
def async_client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestAppBoots:
    """Verify the application starts and core endpoints respond."""

    async def test_health_check(self, async_client):
        async with async_client as client:
            resp = await client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    async def test_openapi_spec_loads(self, async_client):
        async with async_client as client:
            resp = await client.get("/openapi.json")
        assert resp.status_code == 200
        assert "paths" in resp.json()


class TestDatabaseInitialized:
    """Verify database schema is in place and queryable."""

    async def test_settings_table_exists(self, async_client):
        async with async_client as client:
            resp = await client.get("/api/settings")
        assert resp.status_code == 200

    async def test_default_project_created(self):
        from app.services.crud import ensure_default_project

        project = await ensure_default_project()
        assert project is not None
        assert project.project_name == "My Project"


class TestCriticalPipelines:
    """Verify core business logic doesn't crash on basic input."""

    async def test_privacy_proxy_anonymize_roundtrip(self):
        from app.services.privacy_proxy import anonymize, reidentify

        text = "Contact john.smith@acme.com about the project."
        anon_result = await anonymize(text)
        assert "john.smith@acme.com" not in anon_result.anonymized_text
        restored = await reidentify(anon_result.anonymized_text)
        assert "john.smith@acme.com" in restored

    async def test_empty_input_rejected(self, async_client):
        async with async_client as client:
            resp = await client.post("/api/artifact-sync", json={"text": "   "})
        assert resp.status_code == 400

    async def test_artifact_types_valid(self):
        from app.services.artifact_manager import ArtifactType

        assert len(ArtifactType) >= 3  # RAID, Status Report, Meeting Notes


class TestLPDCriticalPaths:
    """Verify Phase 1A Living Project Document critical paths."""

    async def test_lpd_initialization(self):
        from app.services.crud import ensure_default_project
        from app.services.lpd_manager import get_full_lpd, initialize_lpd

        project = await ensure_default_project()
        sections = await initialize_lpd(project.project_id)
        assert len(sections) == 7
        lpd = await get_full_lpd(project.project_id)
        assert len(lpd) == 7

    async def test_lpd_context_injection(self):
        from app.services.crud import ensure_default_project
        from app.services.lpd_manager import get_context_for_injection, initialize_lpd

        project = await ensure_default_project()
        await initialize_lpd(project.project_id)
        context = await get_context_for_injection(project.project_id)
        assert isinstance(context, str)

    async def test_lpd_section_update_roundtrip(self):
        from app.services.crud import ensure_default_project
        from app.services.lpd_manager import get_full_lpd, initialize_lpd, update_section

        project = await ensure_default_project()
        await initialize_lpd(project.project_id)
        await update_section(project.project_id, "Overview", "Test project overview content.")
        lpd = await get_full_lpd(project.project_id)
        assert lpd["Overview"] == "Test project overview content."

    async def test_intake_endpoint_reachable(self, async_client):
        async with async_client as client:
            resp = await client.post(
                "/api/lpd/default-project/intake/preview",
                json={"files": []},
            )
        # Empty files should be rejected (400), not crash (500) or missing (404)
        assert resp.status_code in (400, 422)


class TestTranscriptWatcherCriticalPaths:
    """Verify Phase 1B Transcript Watcher critical paths."""

    async def test_watcher_status_endpoint(self, async_client):
        async with async_client as client:
            resp = await client.get("/api/transcript-watcher/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "running" in data

    async def test_vtt_parser_imports(self):
        from app.services.vtt_parser import parse_srt, parse_transcript_file, parse_vtt

        assert callable(parse_vtt)
        assert callable(parse_srt)
        assert callable(parse_transcript_file)

    async def test_vtt_basic_parse(self):
        from app.services.vtt_parser import parse_vtt

        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:05.000\n<v Alice>Hello.</v>\n"
        result = parse_vtt(vtt)
        assert "Alice: Hello." in result


class TestPhase2ACriticalPaths:
    """Verify Phase 2A new critical paths."""

    async def test_export_endpoint_reachable(self, async_client):
        async with async_client as client:
            resp = await client.get("/api/artifacts/default/export")
        assert resp.status_code == 200
        data = resp.json()
        assert "markdown" in data
        assert "artifact_count" in data

    async def test_upload_endpoint_validates(self, async_client):
        async with async_client as client:
            resp = await client.post(
                "/api/transcript-watcher/upload",
                json={"filename": "test.pdf", "content": "hello"},
            )
        assert resp.status_code == 400
        assert "Unsupported" in resp.json()["detail"]

    async def test_watcher_results_endpoint(self, async_client):
        async with async_client as client:
            resp = await client.get("/api/transcript-watcher/results")
        assert resp.status_code == 200
        assert "results" in resp.json()

    async def test_ollama_client_importable(self):
        from app.services.llm_ollama import OllamaClient

        client = OllamaClient()
        assert client.model == "llama3.2"

    async def test_conversational_models_importable(self):
        from app.models.schemas import ChatRequest, ChatResponse, ConversationSession

        req = ChatRequest(message="test")
        assert req.include_lpd_context is True
        assert "response" in ChatResponse.model_fields
        assert "project_id" in ConversationSession.model_fields


class TestDeepStrategyCriticalPaths:
    """Verify Phase 2B Deep Strategy critical paths."""

    async def test_deep_strategy_endpoint_reachable(self, async_client):
        async with async_client as client:
            resp = await client.post(
                "/api/deep-strategy/analyze",
                json={"artifacts": [{"name": "A", "content": "x", "priority": 1}]},
            )
        # Fewer than 2 artifacts should be rejected (400)
        assert resp.status_code == 400

    async def test_available_artifacts_endpoint(self, async_client):
        async with async_client as client:
            resp = await client.get("/api/deep-strategy/available-artifacts/default")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    async def test_deep_strategy_parsers_importable(self):
        from app.services.deep_strategy import (
            _parse_dependency_graph,
            _parse_inconsistencies,
            _parse_proposed_updates,
            _parse_validation,
        )

        assert _parse_dependency_graph("[]") is not None
        assert _parse_inconsistencies("[]") == []
        assert _parse_proposed_updates("[]") == []
        assert _parse_validation("[]") == []


class TestRiskPredictionCriticalPaths:
    """Verify Phase 2B Risk Prediction critical paths."""

    async def test_risk_prediction_endpoint_reachable(self, async_client):
        async with async_client as client:
            resp = await client.post("/api/risk-prediction/smoke-test-project")
        # Should respond (may be 502 if no LLM key, but not 404/500)
        assert resp.status_code in (200, 502)

    async def test_risk_prediction_parsers(self):
        from app.services.risk_prediction import _assess_project_health, _parse_predictions

        assert _parse_predictions("[]") == []
        assert _assess_project_health({}, [], []) == "healthy"


class TestReconciliationCriticalPaths:
    """Verify Phase 2B Cross-Section Reconciliation critical paths."""

    async def test_reconciliation_endpoint_reachable(self, async_client):
        async with async_client as client:
            resp = await client.post("/api/lpd/smoke-test-project/reconcile")
        # Empty LPD should return 200 with empty impacts
        assert resp.status_code in (200, 502)

    async def test_reconciliation_parsers(self):
        from app.services.reconciliation import _build_section_block, _parse_impacts

        assert _parse_impacts("[]") == []
        block = _build_section_block({"A": "content"})
        assert "Section: A" in block


class TestFolderBrowserCriticalPaths:
    """Verify Phase 2B Folder Browser critical paths."""

    async def test_browse_folders_endpoint(self, async_client):
        async with async_client as client:
            resp = await client.get("/api/settings/browse-folders")
        assert resp.status_code == 200
        data = resp.json()
        assert "current_path" in data
        assert "directories" in data
