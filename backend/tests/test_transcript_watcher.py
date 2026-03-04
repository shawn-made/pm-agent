"""Tests for VPMA Transcript Watcher (Task 35).

Tests that:
1. TranscriptWatcher lifecycle (start/stop/status)
2. Single file processing via process_file
3. Settings integration (watch folder, mode)
4. Manifest tracking prevents reprocessing
5. Graceful error handling
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.transcript_watcher import TranscriptWatcher, get_transcript_watcher

# ============================================================
# WATCHER LIFECYCLE
# ============================================================


class TestWatcherLifecycle:
    def test_initial_state(self):
        """Watcher starts in stopped state."""
        watcher = TranscriptWatcher()
        assert watcher.is_running is False
        assert watcher.watch_folder is None
        assert watcher.mode == "extract"

    @pytest.mark.asyncio
    async def test_start_with_valid_folder(self, tmp_path):
        """Watcher starts successfully with a valid folder."""
        watcher = TranscriptWatcher()
        started = await watcher.start(str(tmp_path), mode="extract")
        assert started is True
        assert watcher.is_running is True
        assert watcher.watch_folder == str(tmp_path)
        await watcher.stop()

    @pytest.mark.asyncio
    async def test_start_with_invalid_folder(self):
        """Watcher rejects invalid (non-existent) folder."""
        watcher = TranscriptWatcher()
        started = await watcher.start("/nonexistent/path", mode="extract")
        assert started is False
        assert watcher.is_running is False

    @pytest.mark.asyncio
    async def test_double_start_rejected(self, tmp_path):
        """Cannot start watcher twice."""
        watcher = TranscriptWatcher()
        await watcher.start(str(tmp_path))
        started_again = await watcher.start(str(tmp_path))
        assert started_again is False
        await watcher.stop()

    @pytest.mark.asyncio
    async def test_stop(self, tmp_path):
        """Watcher stops cleanly."""
        watcher = TranscriptWatcher()
        await watcher.start(str(tmp_path))
        stopped = await watcher.stop()
        assert stopped is True
        assert watcher.is_running is False

    @pytest.mark.asyncio
    async def test_stop_when_not_running(self):
        """Stopping a non-running watcher returns False."""
        watcher = TranscriptWatcher()
        stopped = await watcher.stop()
        assert stopped is False

    @pytest.mark.asyncio
    async def test_status_while_running(self, tmp_path):
        """Status dict includes running state and configuration."""
        watcher = TranscriptWatcher()
        await watcher.start(str(tmp_path), mode="log_session", project_id="proj1")
        status = watcher.status()
        assert status["running"] is True
        assert status["watch_folder"] == str(tmp_path)
        assert status["mode"] == "log_session"
        assert status["project_id"] == "proj1"
        assert "files_processed" in status
        assert "recent_files" in status
        await watcher.stop()

    @pytest.mark.asyncio
    async def test_status_while_stopped(self):
        """Status dict shows not running when stopped."""
        watcher = TranscriptWatcher()
        status = watcher.status()
        assert status["running"] is False

    @pytest.mark.asyncio
    async def test_invalid_mode_defaults_to_extract(self, tmp_path):
        """Invalid mode falls back to 'extract'."""
        watcher = TranscriptWatcher()
        await watcher.start(str(tmp_path), mode="invalid_mode")
        assert watcher.mode == "extract"
        await watcher.stop()


# ============================================================
# FILE PROCESSING
# ============================================================


class TestFileProcessing:
    @pytest.mark.asyncio
    async def test_process_vtt_file(self, tmp_path, monkeypatch):
        """Processing a VTT file calls run_artifact_sync."""
        vtt_file = tmp_path / "meeting.vtt"
        vtt_file.write_text(
            "WEBVTT\n\n00:00:01.000 --> 00:00:05.000\n<v Alice>Sprint review notes for Q3.</v>\n"
        )

        # Mock run_artifact_sync
        mock_result = MagicMock()
        mock_result.suggestions = [MagicMock()]
        mock_result.session_id = "sess-123"
        mock_result.lpd_updates = []

        mock_sync = AsyncMock(return_value=mock_result)
        monkeypatch.setattr("app.services.transcript_watcher.run_artifact_sync", mock_sync)

        watcher = TranscriptWatcher()
        result = await watcher.process_file(str(vtt_file))

        assert result["status"] == "processed"
        assert result["suggestion_count"] == 1
        assert result["session_id"] == "sess-123"

    @pytest.mark.asyncio
    async def test_process_empty_file(self, tmp_path):
        """Empty transcript files are skipped."""
        vtt_file = tmp_path / "empty.vtt"
        vtt_file.write_text("WEBVTT\n\n")

        watcher = TranscriptWatcher()
        result = await watcher.process_file(str(vtt_file))
        assert result["status"] == "skipped"
        assert "Empty" in result["reason"]

    @pytest.mark.asyncio
    async def test_process_missing_file(self):
        """Missing file returns error result."""
        watcher = TranscriptWatcher()
        result = await watcher.process_file("/nonexistent/file.vtt")
        assert result["status"] == "error"
        assert "not found" in result["reason"].lower()

    @pytest.mark.asyncio
    async def test_process_unsupported_format(self, tmp_path):
        """Unsupported file format returns error result."""
        pdf_file = tmp_path / "file.pdf"
        pdf_file.write_text("fake pdf content")

        watcher = TranscriptWatcher()
        result = await watcher.process_file(str(pdf_file))
        assert result["status"] == "error"
        assert "Unsupported" in result["reason"]

    @pytest.mark.asyncio
    async def test_process_log_session_mode(self, tmp_path, monkeypatch):
        """Log session mode includes lpd_update_count in result."""
        vtt_file = tmp_path / "meeting.vtt"
        vtt_file.write_text("WEBVTT\n\n00:00:01.000 --> 00:00:05.000\nDiscussion notes.\n")

        mock_result = MagicMock()
        mock_result.suggestions = []
        mock_result.session_id = "sess-456"
        mock_result.lpd_updates = [MagicMock(), MagicMock()]

        mock_sync = AsyncMock(return_value=mock_result)
        monkeypatch.setattr("app.services.transcript_watcher.run_artifact_sync", mock_sync)

        watcher = TranscriptWatcher()
        watcher._mode = "log_session"
        result = await watcher.process_file(str(vtt_file))

        assert result["status"] == "processed"
        assert result["lpd_update_count"] == 2


# ============================================================
# MANIFEST TRACKING
# ============================================================


class TestManifest:
    @pytest.mark.asyncio
    async def test_manifest_created(self, tmp_path, monkeypatch):
        """Processing a file creates/updates the manifest."""
        vtt_file = tmp_path / "meeting.vtt"
        vtt_file.write_text("WEBVTT\n\n00:00:01.000 --> 00:00:05.000\nHello.\n")

        mock_result = MagicMock()
        mock_result.suggestions = []
        mock_result.session_id = "sess-789"
        mock_result.lpd_updates = []

        mock_sync = AsyncMock(return_value=mock_result)
        monkeypatch.setattr("app.services.transcript_watcher.run_artifact_sync", mock_sync)

        watcher = TranscriptWatcher()
        watcher._manifest_path = tmp_path / "transcript_manifest.json"
        await watcher.process_file(str(vtt_file))

        assert watcher._manifest_path.exists()
        manifest = json.loads(watcher._manifest_path.read_text())
        assert str(vtt_file) in manifest

    @pytest.mark.asyncio
    async def test_manifest_loaded_on_start(self, tmp_path):
        """Existing manifest is loaded when watcher starts."""
        manifest = {
            "/some/file.vtt": {"processed_at": "2026-01-01T00:00:00Z", "status": "processed"}
        }
        manifest_path = tmp_path / "transcript_manifest.json"
        manifest_path.write_text(json.dumps(manifest))

        watcher = TranscriptWatcher()
        await watcher.start(str(tmp_path))
        assert len(watcher._manifest) == 1
        await watcher.stop()


# ============================================================
# RECENT FILES
# ============================================================


class TestRecentFiles:
    @pytest.mark.asyncio
    async def test_recent_files_tracked(self, tmp_path, monkeypatch):
        """Processed files appear in recent_files list."""
        vtt_file = tmp_path / "meeting.vtt"
        vtt_file.write_text("WEBVTT\n\n00:00:01.000 --> 00:00:05.000\nContent.\n")

        mock_result = MagicMock()
        mock_result.suggestions = []
        mock_result.session_id = "sess-1"
        mock_result.lpd_updates = []

        monkeypatch.setattr(
            "app.services.transcript_watcher.run_artifact_sync",
            AsyncMock(return_value=mock_result),
        )

        watcher = TranscriptWatcher()
        await watcher.process_file(str(vtt_file))

        assert len(watcher.recent_files) == 1
        assert watcher.recent_files[0]["file"] == "meeting.vtt"
        assert watcher.recent_files[0]["status"] == "processed"


# ============================================================
# SINGLETON
# ============================================================


class TestSingleton:
    def test_get_transcript_watcher_returns_same_instance(self):
        """get_transcript_watcher returns the same singleton."""
        w1 = get_transcript_watcher()
        w2 = get_transcript_watcher()
        assert w1 is w2


# ============================================================
# API ENDPOINT SMOKE TESTS
# ============================================================


class TestTranscriptWatcherAPI:
    @pytest.mark.asyncio
    async def test_status_endpoint(self):
        """GET /api/transcript-watcher/status returns status dict."""
        from app.main import app
        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/transcript-watcher/status")

        assert response.status_code == 200
        data = response.json()
        assert "running" in data
        assert "watch_folder" in data

    @pytest.mark.asyncio
    async def test_start_without_config(self):
        """POST /api/transcript-watcher/start fails without configured folder."""
        from app.main import app
        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/transcript-watcher/start")

        assert response.status_code == 400
        assert "transcript_watch_folder" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_stop_when_not_running(self):
        """POST /api/transcript-watcher/stop fails when not running."""
        from app.main import app
        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/transcript-watcher/stop")

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_process_missing_path(self):
        """POST /api/transcript-watcher/process fails without file_path."""
        from app.main import app
        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/transcript-watcher/process", json={})

        assert response.status_code == 400
        assert "file_path" in response.json()["detail"]
