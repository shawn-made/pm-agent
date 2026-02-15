"""Tests for VPMA Artifact Manager — Types, templates, file operations (Task 9)."""

import pytest

from app.services.artifact_manager import (
    ARTIFACTS_DIR,
    ArtifactType,
    _artifact_filename,
    get_or_create_artifact,
    list_project_artifacts,
    load_template,
    read_artifact_content,
    write_artifact_content,
)


class TestArtifactType:
    def test_raid_log_value(self):
        assert ArtifactType.RAID_LOG.value == "RAID Log"

    def test_status_report_value(self):
        assert ArtifactType.STATUS_REPORT.value == "Status Report"

    def test_meeting_notes_value(self):
        assert ArtifactType.MEETING_NOTES.value == "Meeting Notes"


class TestTemplates:
    def test_load_raid_log_template(self):
        template = load_template(ArtifactType.RAID_LOG)
        assert "# RAID Log" in template
        assert "Risks" in template
        assert "Assumptions" in template
        assert "Issues" in template
        assert "Dependencies" in template

    def test_load_status_report_template(self):
        template = load_template(ArtifactType.STATUS_REPORT)
        assert "# Status Report" in template
        assert "Accomplishments" in template
        assert "Blockers" in template

    def test_load_meeting_notes_template(self):
        template = load_template(ArtifactType.MEETING_NOTES)
        assert "# Meeting Notes" in template
        assert "Action Items" in template
        assert "Decisions" in template


class TestArtifactFilename:
    def test_raid_log_filename(self):
        result = _artifact_filename("default", ArtifactType.RAID_LOG)
        assert result == "default_raid-log.md"

    def test_status_report_filename(self):
        result = _artifact_filename("myproject", ArtifactType.STATUS_REPORT)
        assert result == "myproject_status-report.md"

    def test_meeting_notes_filename(self):
        result = _artifact_filename("default", ArtifactType.MEETING_NOTES)
        assert result == "default_meeting-notes.md"


class TestGetOrCreateArtifact:
    @pytest.mark.asyncio
    async def test_creates_new_artifact(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "app.services.artifact_manager.ARTIFACTS_DIR", tmp_path
        )
        artifact = await get_or_create_artifact("default", ArtifactType.RAID_LOG)

        assert artifact.project_id == "default"
        assert artifact.artifact_type == "RAID Log"
        assert artifact.file_path.endswith(".md")

    @pytest.mark.asyncio
    async def test_creates_file_on_disk(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "app.services.artifact_manager.ARTIFACTS_DIR", tmp_path
        )
        artifact = await get_or_create_artifact("default", ArtifactType.RAID_LOG)

        from pathlib import Path

        assert Path(artifact.file_path).exists()
        content = Path(artifact.file_path).read_text()
        assert "# RAID Log" in content

    @pytest.mark.asyncio
    async def test_returns_existing_artifact(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "app.services.artifact_manager.ARTIFACTS_DIR", tmp_path
        )
        a1 = await get_or_create_artifact("default", ArtifactType.RAID_LOG)
        a2 = await get_or_create_artifact("default", ArtifactType.RAID_LOG)

        assert a1.artifact_id == a2.artifact_id


class TestReadWriteArtifact:
    @pytest.mark.asyncio
    async def test_read_artifact_content(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "app.services.artifact_manager.ARTIFACTS_DIR", tmp_path
        )
        artifact = await get_or_create_artifact("default", ArtifactType.STATUS_REPORT)
        content = await read_artifact_content(artifact.artifact_id)

        assert content is not None
        assert "# Status Report" in content

    @pytest.mark.asyncio
    async def test_write_artifact_content(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "app.services.artifact_manager.ARTIFACTS_DIR", tmp_path
        )
        artifact = await get_or_create_artifact("default", ArtifactType.MEETING_NOTES)

        new_content = "# Updated Meeting Notes\n\nNew content here."
        success = await write_artifact_content(artifact.artifact_id, new_content)
        assert success is True

        content = await read_artifact_content(artifact.artifact_id)
        assert content == new_content

    @pytest.mark.asyncio
    async def test_read_nonexistent_returns_none(self):
        content = await read_artifact_content("nonexistent-id")
        assert content is None

    @pytest.mark.asyncio
    async def test_write_nonexistent_returns_false(self):
        result = await write_artifact_content("nonexistent-id", "content")
        assert result is False


class TestListProjectArtifacts:
    @pytest.mark.asyncio
    async def test_list_empty(self):
        artifacts = await list_project_artifacts("default")
        assert artifacts == []

    @pytest.mark.asyncio
    async def test_list_after_creation(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "app.services.artifact_manager.ARTIFACTS_DIR", tmp_path
        )
        await get_or_create_artifact("default", ArtifactType.RAID_LOG)
        await get_or_create_artifact("default", ArtifactType.STATUS_REPORT)

        artifacts = await list_project_artifacts("default")
        assert len(artifacts) == 2
        types = {a.artifact_type for a in artifacts}
        assert "RAID Log" in types
        assert "Status Report" in types
