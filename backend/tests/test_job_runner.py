"""Tests for the job queue system (Task 57 — Session-Based Polling)."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from app.main import app
from app.services.crud import (
    cleanup_expired_jobs,
    count_running_jobs,
    create_job,
    get_job,
    mark_stale_jobs_failed,
    update_job_status,
)
from app.services.database import get_db, init_db
from app.services.job_runner import _JOB_HANDLERS, VALID_JOB_TYPES, execute_job
from httpx import ASGITransport, AsyncClient


@pytest.fixture(autouse=True)
async def setup_db(tmp_path, monkeypatch):
    """Use a temporary database for each test."""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.database.DB_PATH", db_path)
    monkeypatch.setattr("app.services.database.VPMA_DIR", tmp_path)
    await init_db()

    # Also seed the default project
    db = await get_db()
    try:
        await db.execute(
            "INSERT OR IGNORE INTO projects (project_id, project_name) VALUES ('default', 'Default')"
        )
        await db.commit()
    finally:
        await db.close()


# ============================================================
# CRUD TESTS
# ============================================================


class TestJobCRUD:
    """Test job CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_and_get_job(self):
        job = await create_job("job-1", "default", "artifact_sync", '{"text": "hello"}')
        assert job["job_id"] == "job-1"
        assert job["status"] == "pending"
        assert job["job_type"] == "artifact_sync"

        fetched = await get_job("job-1")
        assert fetched is not None
        assert fetched["job_id"] == "job-1"

    @pytest.mark.asyncio
    async def test_get_job_not_found(self):
        result = await get_job("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_job_to_running(self):
        await create_job("job-2", "default", "deep_strategy", "{}")
        await update_job_status("job-2", "running")
        job = await get_job("job-2")
        assert job["status"] == "running"
        assert job["started_at"] is not None

    @pytest.mark.asyncio
    async def test_update_job_to_completed(self):
        await create_job("job-3", "default", "artifact_sync", "{}")
        await update_job_status("job-3", "completed", result_json='{"suggestions": []}')
        job = await get_job("job-3")
        assert job["status"] == "completed"
        assert job["completed_at"] is not None
        assert json.loads(job["result_json"]) == {"suggestions": []}

    @pytest.mark.asyncio
    async def test_update_job_to_failed(self):
        await create_job("job-4", "default", "artifact_sync", "{}")
        await update_job_status("job-4", "failed", error_message="LLM error")
        job = await get_job("job-4")
        assert job["status"] == "failed"
        assert job["error_message"] == "LLM error"

    @pytest.mark.asyncio
    async def test_count_running_jobs(self):
        await create_job("job-5", "default", "artifact_sync", "{}")
        await create_job("job-6", "default", "deep_strategy", "{}")
        await update_job_status("job-5", "running")

        count = await count_running_jobs("default")
        assert count == 2  # job-5 is running, job-6 is pending

        await update_job_status("job-6", "completed", result_json="{}")
        count = await count_running_jobs("default")
        assert count == 1

    @pytest.mark.asyncio
    async def test_mark_stale_jobs_failed(self):
        await create_job("stale-1", "default", "deep_strategy", "{}")
        await update_job_status("stale-1", "running")
        await create_job("stale-2", "default", "artifact_sync", "{}")
        # stale-2 is pending, stale-1 is running

        count = await mark_stale_jobs_failed()
        assert count == 2

        job1 = await get_job("stale-1")
        assert job1["status"] == "failed"
        assert "Server restarted" in job1["error_message"]

        job2 = await get_job("stale-2")
        assert job2["status"] == "failed"

    @pytest.mark.asyncio
    async def test_cleanup_expired_jobs(self):
        await create_job("old-1", "default", "artifact_sync", "{}")
        await update_job_status("old-1", "completed", result_json="{}")

        # Manually backdate the created_at
        db = await get_db()
        try:
            await db.execute(
                "UPDATE jobs SET created_at = datetime('now', '-48 hours') WHERE job_id = 'old-1'"
            )
            await db.commit()
        finally:
            await db.close()

        count = await cleanup_expired_jobs(max_age_hours=24)
        assert count == 1
        assert await get_job("old-1") is None

    @pytest.mark.asyncio
    async def test_cleanup_does_not_delete_recent_jobs(self):
        await create_job("recent-1", "default", "artifact_sync", "{}")
        await update_job_status("recent-1", "completed", result_json="{}")

        count = await cleanup_expired_jobs(max_age_hours=24)
        assert count == 0
        assert await get_job("recent-1") is not None


# ============================================================
# JOB RUNNER TESTS
# ============================================================


class TestJobRunner:
    """Test the execute_job function."""

    @pytest.mark.asyncio
    async def test_execute_job_artifact_sync(self):
        payload = {
            "text": "We decided to use PostgreSQL",
            "project_id": "default",
            "mode": "extract",
        }
        await create_job("exec-1", "default", "artifact_sync", json.dumps(payload))

        mock_fn = AsyncMock(return_value='{"suggestions": [], "session_id": "s1"}')

        with patch("app.services.job_runner._run_artifact_sync", mock_fn):
            await execute_job("exec-1")

        job = await get_job("exec-1")
        assert job["status"] == "completed"
        assert job["result_json"] is not None

    @pytest.mark.asyncio
    async def test_execute_job_unknown_type(self):
        await create_job("exec-bad", "default", "unknown_type", "{}")
        await execute_job("exec-bad")

        job = await get_job("exec-bad")
        assert job["status"] == "failed"
        assert "Unknown job type" in job["error_message"]

    @pytest.mark.asyncio
    async def test_execute_job_not_found(self):
        # Should not raise, just log
        await execute_job("nonexistent-job")

    @pytest.mark.asyncio
    async def test_execute_job_handles_exception(self):
        payload = {"text": "test", "project_id": "default", "mode": "extract"}
        await create_job("exec-err", "default", "artifact_sync", json.dumps(payload))

        failing_handler = AsyncMock(side_effect=RuntimeError("LLM crashed"))
        with patch.dict(_JOB_HANDLERS, {"artifact_sync": failing_handler}):
            await execute_job("exec-err")

        job = await get_job("exec-err")
        assert job["status"] == "failed"
        assert "LLM crashed" in job["error_message"]

    def test_valid_job_types(self):
        assert "artifact_sync" in VALID_JOB_TYPES
        assert "deep_strategy" in VALID_JOB_TYPES
        assert "risk_prediction" in VALID_JOB_TYPES


# ============================================================
# API ENDPOINT TESTS
# ============================================================


class TestJobAPI:
    """Test the job queue API endpoints."""

    @pytest.fixture
    def client(self):
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    @pytest.mark.asyncio
    async def test_submit_job(self, client):
        # Mock launch_job to prevent actual execution
        with patch("app.services.job_runner.launch_job"):
            resp = await client.post(
                "/api/jobs",
                json={
                    "job_type": "artifact_sync",
                    "project_id": "default",
                    "payload": {"text": "test", "mode": "extract"},
                },
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "job_id" in data
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_submit_job_invalid_type(self, client):
        resp = await client.post(
            "/api/jobs",
            json={"job_type": "invalid", "project_id": "default", "payload": {}},
        )
        assert resp.status_code == 400
        assert "Unknown job type" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_submit_job_concurrency_limit(self, client):
        # Create 2 pending jobs
        await create_job("limit-1", "default", "artifact_sync", "{}")
        await create_job("limit-2", "default", "deep_strategy", "{}")

        with patch("app.services.job_runner.launch_job"):
            resp = await client.post(
                "/api/jobs",
                json={
                    "job_type": "artifact_sync",
                    "project_id": "default",
                    "payload": {"text": "test", "mode": "extract"},
                },
            )
        assert resp.status_code == 429
        assert "Too many concurrent jobs" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_job_status_pending(self, client):
        await create_job("status-1", "default", "artifact_sync", "{}")
        resp = await client.get("/api/jobs/status-1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "pending"
        assert data["result"] is None

    @pytest.mark.asyncio
    async def test_get_job_status_completed(self, client):
        await create_job("status-2", "default", "artifact_sync", "{}")
        await update_job_status("status-2", "completed", result_json='{"suggestions": []}')

        resp = await client.get("/api/jobs/status-2")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert data["result"] == {"suggestions": []}

    @pytest.mark.asyncio
    async def test_get_job_status_not_found(self, client):
        resp = await client.get("/api/jobs/nonexistent")
        assert resp.status_code == 404
