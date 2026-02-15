"""VPMA CRUD Operations — Database query functions for all tables."""

import uuid
from typing import Optional

from app.models.schemas import (
    Artifact,
    ArtifactCreate,
    ArtifactVersion,
    ArtifactVersionCreate,
    PIIMapping,
    Project,
    ProjectCreate,
    Session,
    SessionCreate,
    Setting,
)
from app.services.database import get_db


# ============================================================
# PROJECTS
# ============================================================


async def create_project(data: ProjectCreate) -> Project:
    """Create a new project. Auto-generates project_id if not provided."""
    project_id = data.project_id or str(uuid.uuid4())
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO projects (project_id, project_name, landscape_config) VALUES (?, ?, ?)",
            (project_id, data.project_name, data.landscape_config),
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT * FROM projects WHERE project_id = ?", (project_id,)
        )
        row = await cursor.fetchone()
        return Project(**dict(row))
    finally:
        await db.close()


async def get_project(project_id: str) -> Optional[Project]:
    """Get a project by ID. Returns None if not found."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM projects WHERE project_id = ?", (project_id,)
        )
        row = await cursor.fetchone()
        return Project(**dict(row)) if row else None
    finally:
        await db.close()


async def list_projects() -> list[Project]:
    """List all projects."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM projects ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
        return [Project(**dict(row)) for row in rows]
    finally:
        await db.close()


async def ensure_default_project() -> Project:
    """Create the default project if it doesn't exist. Returns it."""
    existing = await get_project("default")
    if existing:
        return existing
    return await create_project(
        ProjectCreate(project_id="default", project_name="My Project")
    )


# ============================================================
# ARTIFACTS
# ============================================================


async def create_artifact(data: ArtifactCreate) -> Artifact:
    """Create artifact metadata record."""
    artifact_id = data.artifact_id or str(uuid.uuid4())
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO artifacts (artifact_id, project_id, artifact_type, file_path) VALUES (?, ?, ?, ?)",
            (artifact_id, data.project_id, data.artifact_type, data.file_path),
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT * FROM artifacts WHERE artifact_id = ?", (artifact_id,)
        )
        row = await cursor.fetchone()
        return Artifact(**dict(row))
    finally:
        await db.close()


async def get_artifact(artifact_id: str) -> Optional[Artifact]:
    """Get artifact by ID."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM artifacts WHERE artifact_id = ?", (artifact_id,)
        )
        row = await cursor.fetchone()
        return Artifact(**dict(row)) if row else None
    finally:
        await db.close()


async def get_artifacts_by_project(project_id: str) -> list[Artifact]:
    """List all artifacts for a project."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM artifacts WHERE project_id = ? ORDER BY last_updated DESC",
            (project_id,),
        )
        rows = await cursor.fetchall()
        return [Artifact(**dict(row)) for row in rows]
    finally:
        await db.close()


async def get_artifact_by_type(
    project_id: str, artifact_type: str
) -> Optional[Artifact]:
    """Find a specific artifact type within a project."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM artifacts WHERE project_id = ? AND artifact_type = ?",
            (project_id, artifact_type),
        )
        row = await cursor.fetchone()
        return Artifact(**dict(row)) if row else None
    finally:
        await db.close()


async def update_artifact_timestamp(artifact_id: str) -> None:
    """Update the last_updated timestamp for an artifact."""
    db = await get_db()
    try:
        await db.execute(
            "UPDATE artifacts SET last_updated = CURRENT_TIMESTAMP WHERE artifact_id = ?",
            (artifact_id,),
        )
        await db.commit()
    finally:
        await db.close()


# ============================================================
# ARTIFACT VERSIONS
# ============================================================


async def create_artifact_version(data: ArtifactVersionCreate) -> ArtifactVersion:
    """Create a version snapshot for an artifact."""
    version_id = data.version_id or str(uuid.uuid4())
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO artifact_versions
               (version_id, artifact_id, version_number, content_snapshot, session_id)
               VALUES (?, ?, ?, ?, ?)""",
            (
                version_id,
                data.artifact_id,
                data.version_number,
                data.content_snapshot,
                data.session_id,
            ),
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT * FROM artifact_versions WHERE version_id = ?", (version_id,)
        )
        row = await cursor.fetchone()
        return ArtifactVersion(**dict(row))
    finally:
        await db.close()


async def get_artifact_versions(artifact_id: str) -> list[ArtifactVersion]:
    """List all versions for an artifact, newest first."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT * FROM artifact_versions
               WHERE artifact_id = ? ORDER BY version_number DESC""",
            (artifact_id,),
        )
        rows = await cursor.fetchall()
        return [ArtifactVersion(**dict(row)) for row in rows]
    finally:
        await db.close()


async def get_latest_version_number(artifact_id: str) -> int:
    """Get the highest version number for an artifact. Returns 0 if no versions."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT MAX(version_number) as max_ver FROM artifact_versions WHERE artifact_id = ?",
            (artifact_id,),
        )
        row = await cursor.fetchone()
        return (row["max_ver"] or 0) if row else 0
    finally:
        await db.close()


# ============================================================
# SESSIONS
# ============================================================


async def create_session(data: SessionCreate) -> Session:
    """Log a new sync session."""
    session_id = data.session_id or str(uuid.uuid4())
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO sessions
               (session_id, project_id, tab_used, user_input, agent_output,
                persona_used, tokens_used, llm_model)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id,
                data.project_id,
                data.tab_used,
                data.user_input,
                data.agent_output,
                data.persona_used,
                data.tokens_used,
                data.llm_model,
            ),
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        )
        row = await cursor.fetchone()
        return Session(**dict(row))
    finally:
        await db.close()


async def get_session(session_id: str) -> Optional[Session]:
    """Get a session by ID."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        )
        row = await cursor.fetchone()
        return Session(**dict(row)) if row else None
    finally:
        await db.close()


async def get_sessions_by_project(
    project_id: str, limit: int = 10
) -> list[Session]:
    """Get recent sessions for a project (for context assembly)."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT * FROM sessions WHERE project_id = ?
               ORDER BY timestamp DESC LIMIT ?""",
            (project_id, limit),
        )
        rows = await cursor.fetchall()
        return [Session(**dict(row)) for row in rows]
    finally:
        await db.close()


# ============================================================
# PII VAULT
# ============================================================


async def store_pii_mapping(
    token: str, original_value: str, entity_type: str
) -> PIIMapping:
    """Store or update a PII token mapping. Preserves first_seen on re-insert."""
    db = await get_db()
    try:
        await db.execute(
            """INSERT OR REPLACE INTO pii_vault (token, original_value, entity_type, first_seen)
               VALUES (?, ?, ?, COALESCE(
                   (SELECT first_seen FROM pii_vault WHERE token = ?),
                   CURRENT_TIMESTAMP
               ))""",
            (token, original_value, entity_type, token),
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT * FROM pii_vault WHERE token = ?", (token,)
        )
        row = await cursor.fetchone()
        return PIIMapping(**dict(row))
    finally:
        await db.close()


async def get_pii_mapping(token: str) -> Optional[PIIMapping]:
    """Look up a PII mapping by token."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM pii_vault WHERE token = ?", (token,)
        )
        row = await cursor.fetchone()
        return PIIMapping(**dict(row)) if row else None
    finally:
        await db.close()


async def get_all_pii_mappings() -> list[PIIMapping]:
    """Load the entire PII vault (for building in-memory lookup)."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM pii_vault")
        rows = await cursor.fetchall()
        return [PIIMapping(**dict(row)) for row in rows]
    finally:
        await db.close()


async def lookup_pii_by_original(original_value: str) -> Optional[PIIMapping]:
    """Check if a value already has a token (for consistency across sessions)."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM pii_vault WHERE original_value = ?", (original_value,)
        )
        row = await cursor.fetchone()
        return PIIMapping(**dict(row)) if row else None
    finally:
        await db.close()


# ============================================================
# SETTINGS
# ============================================================


async def get_setting(key: str) -> Optional[str]:
    """Get a single setting value by key. Returns None if not found."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        )
        row = await cursor.fetchone()
        return row["value"] if row else None
    finally:
        await db.close()


async def get_all_settings() -> dict[str, str]:
    """Get all settings as a key-value dict."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT key, value FROM settings")
        rows = await cursor.fetchall()
        return {row["key"]: row["value"] for row in rows}
    finally:
        await db.close()


async def upsert_setting(key: str, value: str) -> Setting:
    """Insert or update a setting."""
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO settings (key, value, updated_at)
               VALUES (?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP""",
            (key, value, value),
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT * FROM settings WHERE key = ?", (key,)
        )
        row = await cursor.fetchone()
        return Setting(**dict(row))
    finally:
        await db.close()
