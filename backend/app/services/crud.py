"""VPMA CRUD Operations — Database query functions for all tables."""

import uuid
from typing import Optional

from app.models.schemas import (
    Artifact,
    ArtifactCreate,
    ArtifactVersion,
    ArtifactVersionCreate,
    LPDSection,
    LPDSectionCreate,
    LPDSessionSummary,
    LPDSessionSummaryCreate,
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
        cursor = await db.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,))
        row = await cursor.fetchone()
        return Project(**dict(row))
    finally:
        await db.close()


async def get_project(project_id: str) -> Optional[Project]:
    """Get a project by ID. Returns None if not found."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,))
        row = await cursor.fetchone()
        return Project(**dict(row)) if row else None
    finally:
        await db.close()


async def list_projects() -> list[Project]:
    """List all projects."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM projects ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [Project(**dict(row)) for row in rows]
    finally:
        await db.close()


async def ensure_default_project() -> Project:
    """Create the default project if it doesn't exist. Returns it."""
    existing = await get_project("default")
    if existing:
        return existing
    return await create_project(ProjectCreate(project_id="default", project_name="My Project"))


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
        cursor = await db.execute("SELECT * FROM artifacts WHERE artifact_id = ?", (artifact_id,))
        row = await cursor.fetchone()
        return Artifact(**dict(row))
    finally:
        await db.close()


async def get_artifact(artifact_id: str) -> Optional[Artifact]:
    """Get artifact by ID."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM artifacts WHERE artifact_id = ?", (artifact_id,))
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


async def get_artifact_by_type(project_id: str, artifact_type: str) -> Optional[Artifact]:
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
        cursor = await db.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = await cursor.fetchone()
        return Session(**dict(row))
    finally:
        await db.close()


async def get_session(session_id: str) -> Optional[Session]:
    """Get a session by ID."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = await cursor.fetchone()
        return Session(**dict(row)) if row else None
    finally:
        await db.close()


async def get_sessions_by_project(project_id: str, limit: int = 10) -> list[Session]:
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


async def store_pii_mapping(token: str, original_value: str, entity_type: str) -> PIIMapping:
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
        cursor = await db.execute("SELECT * FROM pii_vault WHERE token = ?", (token,))
        row = await cursor.fetchone()
        return PIIMapping(**dict(row))
    finally:
        await db.close()


async def get_pii_mapping(token: str) -> Optional[PIIMapping]:
    """Look up a PII mapping by token."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM pii_vault WHERE token = ?", (token,))
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
        cursor = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
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
        cursor = await db.execute("SELECT * FROM settings WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return Setting(**dict(row))
    finally:
        await db.close()


# ============================================================
# LPD SECTIONS
# ============================================================


async def create_lpd_section(data: LPDSectionCreate) -> LPDSection:
    """Create a single LPD section row."""
    section_id = data.section_id or str(uuid.uuid4())
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO lpd_sections
               (section_id, project_id, section_name, content, section_order)
               VALUES (?, ?, ?, ?, ?)""",
            (section_id, data.project_id, data.section_name, data.content, data.section_order),
        )
        await db.commit()
        cursor = await db.execute("SELECT * FROM lpd_sections WHERE section_id = ?", (section_id,))
        row = await cursor.fetchone()
        return LPDSection(**dict(row))
    finally:
        await db.close()


async def get_lpd_sections(project_id: str) -> list[LPDSection]:
    """Get all LPD sections for a project, ordered by section_order."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM lpd_sections WHERE project_id = ? ORDER BY section_order",
            (project_id,),
        )
        rows = await cursor.fetchall()
        return [LPDSection(**dict(row)) for row in rows]
    finally:
        await db.close()


async def get_lpd_section(project_id: str, section_name: str) -> Optional[LPDSection]:
    """Get a specific LPD section by project and name."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM lpd_sections WHERE project_id = ? AND section_name = ?",
            (project_id, section_name),
        )
        row = await cursor.fetchone()
        return LPDSection(**dict(row)) if row else None
    finally:
        await db.close()


async def update_lpd_section_content(
    project_id: str, section_name: str, content: str
) -> Optional[LPDSection]:
    """Replace the content of an LPD section. Updates the updated_at timestamp."""
    db = await get_db()
    try:
        await db.execute(
            """UPDATE lpd_sections
               SET content = ?, updated_at = CURRENT_TIMESTAMP
               WHERE project_id = ? AND section_name = ?""",
            (content, project_id, section_name),
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT * FROM lpd_sections WHERE project_id = ? AND section_name = ?",
            (project_id, section_name),
        )
        row = await cursor.fetchone()
        return LPDSection(**dict(row)) if row else None
    finally:
        await db.close()


async def verify_lpd_section(project_id: str, section_name: str) -> Optional[LPDSection]:
    """Mark an LPD section as verified (human confirmed accuracy)."""
    db = await get_db()
    try:
        await db.execute(
            """UPDATE lpd_sections
               SET verified_at = CURRENT_TIMESTAMP
               WHERE project_id = ? AND section_name = ?""",
            (project_id, section_name),
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT * FROM lpd_sections WHERE project_id = ? AND section_name = ?",
            (project_id, section_name),
        )
        row = await cursor.fetchone()
        return LPDSection(**dict(row)) if row else None
    finally:
        await db.close()


async def lpd_exists(project_id: str) -> bool:
    """Check whether an LPD has been initialized for a project."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM lpd_sections WHERE project_id = ?",
            (project_id,),
        )
        row = await cursor.fetchone()
        return row["cnt"] > 0
    finally:
        await db.close()


# ============================================================
# LPD SESSION SUMMARIES
# ============================================================


async def create_lpd_session_summary(data: LPDSessionSummaryCreate) -> LPDSessionSummary:
    """Record a session summary for the LPD."""
    summary_id = data.summary_id or str(uuid.uuid4())
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO lpd_session_summaries
               (summary_id, project_id, session_id, summary_text, entities_extracted)
               VALUES (?, ?, ?, ?, ?)""",
            (
                summary_id,
                data.project_id,
                data.session_id,
                data.summary_text,
                data.entities_extracted,
            ),
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT * FROM lpd_session_summaries WHERE summary_id = ?", (summary_id,)
        )
        row = await cursor.fetchone()
        return LPDSessionSummary(**dict(row))
    finally:
        await db.close()


async def get_recent_session_summaries(project_id: str, limit: int = 10) -> list[LPDSessionSummary]:
    """Get the most recent session summaries for a project."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT * FROM lpd_session_summaries
               WHERE project_id = ?
               ORDER BY created_at DESC, rowid DESC LIMIT ?""",
            (project_id, limit),
        )
        rows = await cursor.fetchall()
        return [LPDSessionSummary(**dict(row)) for row in rows]
    finally:
        await db.close()


async def get_session_summary_count(project_id: str) -> int:
    """Get total number of session summaries for a project."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM lpd_session_summaries WHERE project_id = ?",
            (project_id,),
        )
        row = await cursor.fetchone()
        return row["cnt"]
    finally:
        await db.close()


# ============================================================
# JOBS (Task 57 — Session-Based Polling)
# ============================================================


async def create_job(job_id: str, project_id: str, job_type: str, request_json: str) -> dict:
    """Insert a new job record."""
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO jobs (job_id, project_id, job_type, status, request_json)
               VALUES (?, ?, ?, 'pending', ?)""",
            (job_id, project_id, job_type, request_json),
        )
        await db.commit()
        cursor = await db.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        row = await cursor.fetchone()
        return dict(row)
    finally:
        await db.close()


async def get_job(job_id: str) -> Optional[dict]:
    """Get a job by ID."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def update_job_status(
    job_id: str,
    status: str,
    *,
    result_json: Optional[str] = None,
    error_message: Optional[str] = None,
) -> None:
    """Update a job's status and optional result/error fields."""
    db = await get_db()
    try:
        if status == "running":
            await db.execute(
                "UPDATE jobs SET status = ?, started_at = CURRENT_TIMESTAMP WHERE job_id = ?",
                (status, job_id),
            )
        elif status in ("completed", "failed"):
            await db.execute(
                """UPDATE jobs SET status = ?, result_json = ?, error_message = ?,
                   completed_at = CURRENT_TIMESTAMP WHERE job_id = ?""",
                (status, result_json, error_message, job_id),
            )
        else:
            await db.execute(
                "UPDATE jobs SET status = ? WHERE job_id = ?",
                (status, job_id),
            )
        await db.commit()
    finally:
        await db.close()


async def count_running_jobs(project_id: str) -> int:
    """Count jobs in 'pending' or 'running' state for a project."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM jobs WHERE project_id = ? AND status IN ('pending', 'running')",
            (project_id,),
        )
        row = await cursor.fetchone()
        return row["cnt"]
    finally:
        await db.close()


async def mark_stale_jobs_failed() -> int:
    """Mark any jobs stuck in 'running' or 'pending' as failed (called on startup)."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """UPDATE jobs SET status = 'failed',
               error_message = 'Server restarted during processing',
               completed_at = CURRENT_TIMESTAMP
               WHERE status IN ('pending', 'running')"""
        )
        await db.commit()
        return cursor.rowcount
    finally:
        await db.close()


async def cleanup_expired_jobs(max_age_hours: int = 24) -> int:
    """Delete completed/failed jobs older than max_age_hours."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """DELETE FROM jobs
               WHERE status IN ('completed', 'failed')
               AND created_at < datetime('now', ? || ' hours')""",
            (f"-{max_age_hours}",),
        )
        await db.commit()
        return cursor.rowcount
    finally:
        await db.close()
