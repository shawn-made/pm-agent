"""Tests for VPMA CRUD operations."""

import pytest
from app.models.schemas import (
    ArtifactCreate,
    ArtifactVersionCreate,
    ProjectCreate,
    SessionCreate,
)
from app.services.crud import (
    create_artifact,
    create_artifact_version,
    create_project,
    create_session,
    ensure_default_project,
    get_all_pii_mappings,
    get_all_settings,
    get_artifact,
    get_artifact_by_type,
    get_artifact_versions,
    get_artifacts_by_project,
    get_latest_version_number,
    get_pii_mapping,
    get_project,
    get_session,
    get_sessions_by_project,
    get_setting,
    list_projects,
    lookup_pii_by_original,
    store_pii_mapping,
    update_artifact_timestamp,
    upsert_setting,
)

# ============================================================
# PROJECTS
# ============================================================


@pytest.mark.asyncio
async def test_default_project_exists():
    """init_db creates the default project automatically."""
    project = await get_project("default")
    assert project is not None
    assert project.project_name == "My Project"


@pytest.mark.asyncio
async def test_ensure_default_project_idempotent():
    """Calling ensure_default_project twice doesn't error."""
    p1 = await ensure_default_project()
    p2 = await ensure_default_project()
    assert p1.project_id == p2.project_id


@pytest.mark.asyncio
async def test_create_and_get_project():
    project = await create_project(
        ProjectCreate(project_id="proj-1", project_name="Test Project")
    )
    assert project.project_id == "proj-1"
    assert project.project_name == "Test Project"

    fetched = await get_project("proj-1")
    assert fetched is not None
    assert fetched.project_name == "Test Project"


@pytest.mark.asyncio
async def test_create_project_auto_id():
    project = await create_project(ProjectCreate(project_name="Auto ID"))
    assert project.project_id  # should be a UUID string
    assert len(project.project_id) == 36  # UUID format


@pytest.mark.asyncio
async def test_get_project_not_found():
    result = await get_project("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_list_projects():
    await create_project(ProjectCreate(project_id="p1", project_name="First"))
    await create_project(ProjectCreate(project_id="p2", project_name="Second"))
    projects = await list_projects()
    # default + p1 + p2
    assert len(projects) >= 3
    names = {p.project_name for p in projects}
    assert "First" in names
    assert "Second" in names


# ============================================================
# ARTIFACTS
# ============================================================


@pytest.mark.asyncio
async def test_create_and_get_artifact():
    artifact = await create_artifact(
        ArtifactCreate(
            artifact_id="art-1",
            project_id="default",
            artifact_type="RAID Log",
            file_path="~/VPMA/artifacts/raid_log.md",
        )
    )
    assert artifact.artifact_id == "art-1"
    assert artifact.artifact_type == "RAID Log"

    fetched = await get_artifact("art-1")
    assert fetched is not None
    assert fetched.file_path == "~/VPMA/artifacts/raid_log.md"


@pytest.mark.asyncio
async def test_get_artifact_not_found():
    result = await get_artifact("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_get_artifacts_by_project():
    await create_artifact(
        ArtifactCreate(
            project_id="default",
            artifact_type="RAID Log",
            file_path="raid.md",
        )
    )
    await create_artifact(
        ArtifactCreate(
            project_id="default",
            artifact_type="Status Report",
            file_path="status.md",
        )
    )
    artifacts = await get_artifacts_by_project("default")
    assert len(artifacts) == 2


@pytest.mark.asyncio
async def test_get_artifact_by_type():
    await create_artifact(
        ArtifactCreate(
            artifact_id="raid-1",
            project_id="default",
            artifact_type="RAID Log",
            file_path="raid.md",
        )
    )
    found = await get_artifact_by_type("default", "RAID Log")
    assert found is not None
    assert found.artifact_id == "raid-1"

    not_found = await get_artifact_by_type("default", "Meeting Notes")
    assert not_found is None


@pytest.mark.asyncio
async def test_update_artifact_timestamp():
    artifact = await create_artifact(
        ArtifactCreate(
            artifact_id="ts-test",
            project_id="default",
            artifact_type="Status Report",
            file_path="status.md",
        )
    )
    original_ts = artifact.last_updated
    await update_artifact_timestamp("ts-test")
    updated = await get_artifact("ts-test")
    assert updated.last_updated >= original_ts


# ============================================================
# ARTIFACT VERSIONS
# ============================================================


@pytest.mark.asyncio
async def test_create_artifact_version():
    await create_artifact(
        ArtifactCreate(
            artifact_id="ver-art",
            project_id="default",
            artifact_type="RAID Log",
            file_path="raid.md",
        )
    )
    version = await create_artifact_version(
        ArtifactVersionCreate(
            artifact_id="ver-art",
            version_number=1,
            content_snapshot="# RAID Log\n- Risk 1",
        )
    )
    assert version.version_number == 1
    assert version.content_snapshot == "# RAID Log\n- Risk 1"


@pytest.mark.asyncio
async def test_get_artifact_versions():
    await create_artifact(
        ArtifactCreate(
            artifact_id="multi-ver",
            project_id="default",
            artifact_type="RAID Log",
            file_path="raid.md",
        )
    )
    await create_artifact_version(
        ArtifactVersionCreate(artifact_id="multi-ver", version_number=1)
    )
    await create_artifact_version(
        ArtifactVersionCreate(artifact_id="multi-ver", version_number=2)
    )
    versions = await get_artifact_versions("multi-ver")
    assert len(versions) == 2
    assert versions[0].version_number == 2  # newest first


@pytest.mark.asyncio
async def test_get_latest_version_number():
    await create_artifact(
        ArtifactCreate(
            artifact_id="latest-ver",
            project_id="default",
            artifact_type="RAID Log",
            file_path="raid.md",
        )
    )
    assert await get_latest_version_number("latest-ver") == 0

    await create_artifact_version(
        ArtifactVersionCreate(artifact_id="latest-ver", version_number=1)
    )
    assert await get_latest_version_number("latest-ver") == 1

    await create_artifact_version(
        ArtifactVersionCreate(artifact_id="latest-ver", version_number=2)
    )
    assert await get_latest_version_number("latest-ver") == 2


# ============================================================
# SESSIONS
# ============================================================


@pytest.mark.asyncio
async def test_create_and_get_session():
    session = await create_session(
        SessionCreate(
            session_id="sess-1",
            project_id="default",
            tab_used="Artifact Sync",
            user_input="Meeting notes from standup...",
            agent_output='{"suggestions": []}',
            tokens_used=150,
            llm_model="claude-sonnet-4-5-20250929",
        )
    )
    assert session.session_id == "sess-1"
    assert session.tokens_used == 150

    fetched = await get_session("sess-1")
    assert fetched is not None
    assert fetched.tab_used == "Artifact Sync"


@pytest.mark.asyncio
async def test_get_session_not_found():
    result = await get_session("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_get_sessions_by_project():
    for i in range(5):
        await create_session(
            SessionCreate(
                session_id=f"sess-{i}",
                project_id="default",
                user_input=f"Input {i}",
            )
        )
    sessions = await get_sessions_by_project("default", limit=3)
    assert len(sessions) == 3


# ============================================================
# PII VAULT
# ============================================================


@pytest.mark.asyncio
async def test_store_and_get_pii_mapping():
    mapping = await store_pii_mapping("<PERSON_1>", "John Smith", "PERSON")
    assert mapping.token == "<PERSON_1>"
    assert mapping.original_value == "John Smith"
    assert mapping.first_seen is not None

    fetched = await get_pii_mapping("<PERSON_1>")
    assert fetched is not None
    assert fetched.original_value == "John Smith"


@pytest.mark.asyncio
async def test_pii_mapping_not_found():
    result = await get_pii_mapping("<NONEXISTENT>")
    assert result is None


@pytest.mark.asyncio
async def test_store_pii_preserves_first_seen():
    m1 = await store_pii_mapping("<PERSON_1>", "John Smith", "PERSON")
    first_seen_original = m1.first_seen

    # Re-store with updated value — first_seen should be preserved
    m2 = await store_pii_mapping("<PERSON_1>", "Jonathan Smith", "PERSON")
    assert m2.original_value == "Jonathan Smith"
    assert m2.first_seen == first_seen_original


@pytest.mark.asyncio
async def test_get_all_pii_mappings():
    await store_pii_mapping("<PERSON_1>", "Alice", "PERSON")
    await store_pii_mapping("<ORG_1>", "Acme Corp", "ORG")
    await store_pii_mapping("<EMAIL_1>", "alice@example.com", "EMAIL")
    mappings = await get_all_pii_mappings()
    assert len(mappings) == 3


@pytest.mark.asyncio
async def test_lookup_pii_by_original():
    await store_pii_mapping("<PERSON_1>", "Jane Doe", "PERSON")
    found = await lookup_pii_by_original("Jane Doe")
    assert found is not None
    assert found.token == "<PERSON_1>"

    not_found = await lookup_pii_by_original("Unknown Person")
    assert not_found is None


# ============================================================
# SETTINGS
# ============================================================


@pytest.mark.asyncio
async def test_upsert_and_get_setting():
    await upsert_setting("llm_provider", "claude")
    value = await get_setting("llm_provider")
    assert value == "claude"


@pytest.mark.asyncio
async def test_get_setting_not_found():
    result = await get_setting("nonexistent_key")
    assert result is None


@pytest.mark.asyncio
async def test_upsert_setting_updates_existing():
    await upsert_setting("llm_provider", "claude")
    await upsert_setting("llm_provider", "gemini")
    value = await get_setting("llm_provider")
    assert value == "gemini"


@pytest.mark.asyncio
async def test_get_all_settings():
    await upsert_setting("llm_provider", "claude")
    await upsert_setting("api_key", "sk-test-123")
    settings = await get_all_settings()
    assert settings["llm_provider"] == "claude"
    assert settings["api_key"] == "sk-test-123"
