"""Tests for VPMA API Endpoints (Task 12)."""

from unittest.mock import AsyncMock

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def async_client():
    """Create an async HTTP client for testing."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        async with async_client as client:
            response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestSettingsEndpoints:
    @pytest.mark.asyncio
    async def test_get_settings_empty(self, async_client):
        async with async_client as client:
            response = await client.get("/api/settings")
        assert response.status_code == 200
        data = response.json()
        assert "settings" in data

    @pytest.mark.asyncio
    async def test_put_settings(self, async_client):
        async with async_client as client:
            response = await client.put(
                "/api/settings",
                json={"llm_provider": "claude", "sensitive_terms": "ProjectX,ClientY"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "saved"
        assert "llm_provider" in data["updated"]

    @pytest.mark.asyncio
    async def test_put_settings_masks_api_keys(self, async_client):
        async with async_client as client:
            # Save an API key
            await client.put(
                "/api/settings",
                json={"anthropic_api_key": "sk-test-key-12345678"},
            )
            # Retrieve settings — key should be masked
            response = await client.get("/api/settings")
        data = response.json()
        key_value = data["settings"].get("anthropic_api_key", "")
        assert "sk-test" not in key_value
        assert key_value.startswith("****")

    @pytest.mark.asyncio
    async def test_put_settings_ignores_unknown_keys(self, async_client):
        async with async_client as client:
            response = await client.put(
                "/api/settings",
                json={"unknown_key": "value", "llm_provider": "gemini"},
            )
        data = response.json()
        assert "unknown_key" not in data["updated"]
        assert "llm_provider" in data["updated"]


class TestArtifactSyncEndpoint:
    @pytest.mark.asyncio
    async def test_empty_text_returns_400(self, async_client):
        async with async_client as client:
            response = await client.post(
                "/api/artifact-sync",
                json={"text": "   "},
            )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_artifact_sync_success(self, async_client, monkeypatch):
        """Artifact sync returns suggestions with mocked LLM."""
        from app.models.schemas import ArtifactSyncResponse

        mock_response = ArtifactSyncResponse(
            suggestions=[],
            input_type="general_text",
            session_id="test-session-id",
            pii_detected=0,
        )

        monkeypatch.setattr(
            "app.api.routes.run_artifact_sync",
            AsyncMock(return_value=mock_response),
        )

        async with async_client as client:
            response = await client.post(
                "/api/artifact-sync",
                json={"text": "Project update: everything is on track."},
            )

        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert "session_id" in data

    @pytest.mark.asyncio
    async def test_artifact_sync_llm_error_returns_502(self, async_client, monkeypatch):
        """LLM errors return 502."""
        from app.services.llm_client import LLMError

        monkeypatch.setattr(
            "app.api.routes.run_artifact_sync",
            AsyncMock(side_effect=LLMError("API key invalid")),
        )

        async with async_client as client:
            response = await client.post(
                "/api/artifact-sync",
                json={"text": "Some meeting notes."},
            )

        assert response.status_code == 502


class TestApplyEndpoint:
    @pytest.mark.asyncio
    async def test_apply_not_found(self, async_client):
        async with async_client as client:
            response = await client.post(
                "/api/artifacts/nonexistent/apply",
                json={
                    "artifact_type": "RAID Log",
                    "change_type": "add",
                    "section": "Risks",
                    "proposed_text": "New risk",
                    "confidence": 0.9,
                    "reasoning": "Test",
                },
            )
        assert response.status_code == 404
