"""Tests for VPMA LPD API Endpoints (Task 29).

Tests the LPD-specific REST endpoints:
- GET /lpd/{project_id}/sections
- PUT /lpd/{project_id}/sections/{section_name}
- POST /lpd/{project_id}/initialize
- GET /lpd/{project_id}/staleness
- GET /lpd/{project_id}/markdown
- POST /lpd/{project_id}/sections/{section_name}/verify
"""

import pytest
from app.main import app
from app.services.lpd_manager import get_full_lpd, initialize_lpd, update_section
from httpx import ASGITransport, AsyncClient

PROJECT_ID = "default"


# ============================================================
# INITIALIZE
# ============================================================


class TestInitializeEndpoint:
    @pytest.mark.asyncio
    async def test_initialize_creates_sections(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/api/lpd/{PROJECT_ID}/initialize")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "initialized"
        assert data["section_count"] == 7
        assert "Overview" in data["sections"]
        assert "Risks" in data["sections"]
        assert "Recent Context" in data["sections"]

    @pytest.mark.asyncio
    async def test_initialize_idempotent(self):
        await initialize_lpd(PROJECT_ID)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/api/lpd/{PROJECT_ID}/initialize")

        assert response.status_code == 200
        assert response.json()["section_count"] == 7


# ============================================================
# GET SECTIONS
# ============================================================


class TestGetSectionsEndpoint:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_lpd(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/lpd/{PROJECT_ID}/sections")

        assert response.status_code == 200
        assert response.json()["sections"] == {}

    @pytest.mark.asyncio
    async def test_returns_sections_after_init(self):
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Overview", "Project Falcon — mobile app.")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/lpd/{PROJECT_ID}/sections")

        assert response.status_code == 200
        sections = response.json()["sections"]
        assert "Overview" in sections
        assert "Project Falcon" in sections["Overview"]
        assert "Risks" in sections  # Empty but present


# ============================================================
# UPDATE SECTION
# ============================================================


class TestUpdateSectionEndpoint:
    @pytest.mark.asyncio
    async def test_update_section_content(self):
        await initialize_lpd(PROJECT_ID)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                f"/api/lpd/{PROJECT_ID}/sections/Risks",
                json={"content": "- API performance risk."},
            )

        assert response.status_code == 200
        assert response.json()["status"] == "updated"

        lpd = await get_full_lpd(PROJECT_ID)
        assert "API performance risk" in lpd["Risks"]

    @pytest.mark.asyncio
    async def test_update_invalid_section_returns_404(self):
        await initialize_lpd(PROJECT_ID)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                f"/api/lpd/{PROJECT_ID}/sections/NonExistent",
                json={"content": "content"},
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_missing_content_returns_400(self):
        await initialize_lpd(PROJECT_ID)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                f"/api/lpd/{PROJECT_ID}/sections/Risks",
                json={},
            )

        assert response.status_code == 400


# ============================================================
# STALENESS
# ============================================================


class TestStalenessEndpoint:
    @pytest.mark.asyncio
    async def test_staleness_returns_metrics(self):
        await initialize_lpd(PROJECT_ID)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/lpd/{PROJECT_ID}/staleness")

        assert response.status_code == 200
        data = response.json()["staleness"]
        assert len(data) == 7
        names = [s["section_name"] for s in data]
        assert "Overview" in names
        assert "Risks" in names

    @pytest.mark.asyncio
    async def test_staleness_empty_when_no_lpd(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/lpd/{PROJECT_ID}/staleness")

        assert response.status_code == 200
        assert response.json()["staleness"] == []


# ============================================================
# MARKDOWN
# ============================================================


class TestMarkdownEndpoint:
    @pytest.mark.asyncio
    async def test_returns_markdown(self):
        await initialize_lpd(PROJECT_ID)
        await update_section(PROJECT_ID, "Overview", "Project Falcon — mobile app.")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/lpd/{PROJECT_ID}/markdown")

        assert response.status_code == 200
        md = response.json()["markdown"]
        assert "# Living Project Document" in md
        assert "## Overview" in md
        assert "Project Falcon" in md

    @pytest.mark.asyncio
    async def test_markdown_404_when_no_lpd(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/lpd/{PROJECT_ID}/markdown")

        assert response.status_code == 404


# ============================================================
# VERIFY
# ============================================================


class TestVerifyEndpoint:
    @pytest.mark.asyncio
    async def test_verify_section(self):
        await initialize_lpd(PROJECT_ID)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/api/lpd/{PROJECT_ID}/sections/Risks/verify")

        assert response.status_code == 200
        assert response.json()["status"] == "verified"

    @pytest.mark.asyncio
    async def test_verify_invalid_section_returns_404(self):
        await initialize_lpd(PROJECT_ID)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/api/lpd/{PROJECT_ID}/sections/NonExistent/verify")

        assert response.status_code == 404
