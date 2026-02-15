"""VPMA Artifact Manager — Types, templates, and file operations.

Artifact content lives as Markdown files in ~/VPMA/artifacts/.
SQLite stores metadata only (timestamps, references, type).

Supported artifact types:
- RAID Log: Risks, Assumptions, Issues, Dependencies
- Status Report: Summary, accomplishments, blockers
- Meeting Notes: Attendees, discussion, action items
"""

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from app.models.schemas import Artifact, ArtifactCreate
from app.services.crud import (
    create_artifact,
    get_artifact,
    get_artifact_by_type,
    get_artifacts_by_project,
    update_artifact_timestamp,
)
from app.services.database import VPMA_DIR

# Where artifact markdown files live
ARTIFACTS_DIR = VPMA_DIR / "artifacts"

# Where templates live (in the repo)
TEMPLATES_DIR = Path(__file__).parent.parent / "prompts" / "templates"


class ArtifactType(str, Enum):
    """Supported artifact types for Phase 0."""

    RAID_LOG = "RAID Log"
    STATUS_REPORT = "Status Report"
    MEETING_NOTES = "Meeting Notes"


# Map artifact types to their template filenames
_TEMPLATE_FILES = {
    ArtifactType.RAID_LOG: "raid_log.md",
    ArtifactType.STATUS_REPORT: "status_report.md",
    ArtifactType.MEETING_NOTES: "meeting_notes.md",
}


def load_template(artifact_type: ArtifactType) -> str:
    """Load the Markdown template for an artifact type.

    Args:
        artifact_type: Which type of artifact template to load.

    Returns:
        Template content as a string.

    Raises:
        FileNotFoundError: If the template file doesn't exist.
    """
    filename = _TEMPLATE_FILES[artifact_type]
    template_path = TEMPLATES_DIR / filename
    return template_path.read_text()


def _safe_filename(name: str) -> str:
    """Sanitize a string for use in a filename (prevent path traversal)."""
    import re

    return re.sub(r"[^a-zA-Z0-9_-]", "_", name)


def _artifact_filename(project_id: str, artifact_type: ArtifactType) -> str:
    """Generate a consistent filename for an artifact.

    Format: {project_id}_{type_slug}.md
    Example: default_raid-log.md
    """
    safe_id = _safe_filename(project_id)
    slug = artifact_type.value.lower().replace(" ", "-")
    return f"{safe_id}_{slug}.md"


async def get_or_create_artifact(
    project_id: str,
    artifact_type: ArtifactType,
) -> Artifact:
    """Get an existing artifact or create one with a template.

    Creates both the SQLite metadata record and the Markdown file
    on disk if they don't exist yet.

    Args:
        project_id: Project this artifact belongs to.
        artifact_type: Type of artifact.

    Returns:
        The Artifact metadata record.
    """
    # Check if metadata exists
    existing = await get_artifact_by_type(project_id, artifact_type.value)
    if existing:
        return existing

    # Create the markdown file from template
    filename = _artifact_filename(project_id, artifact_type)
    file_path = ARTIFACTS_DIR / filename

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        template = load_template(artifact_type)
        # Fill in basic template variables
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        content = template.replace("{{project_name}}", project_id)
        content = content.replace("{{last_updated}}", now)
        content = content.replace("{{date}}", now)
        content = content.replace("{{period}}", "Current")
        content = content.replace("{{attendees}}", "")
        file_path.write_text(content)

    # Create metadata record
    artifact = await create_artifact(
        ArtifactCreate(
            project_id=project_id,
            artifact_type=artifact_type.value,
            file_path=str(file_path),
        )
    )
    return artifact


async def read_artifact_content(artifact_id: str) -> str | None:
    """Read the Markdown content of an artifact from disk.

    Args:
        artifact_id: The artifact's database ID.

    Returns:
        File content as string, or None if artifact/file not found.
    """
    artifact = await get_artifact(artifact_id)
    if not artifact:
        return None

    file_path = Path(artifact.file_path).resolve()
    if not str(file_path).startswith(str(ARTIFACTS_DIR.resolve())):
        return None  # Path traversal attempt

    if not file_path.exists():
        return None

    return file_path.read_text()


async def write_artifact_content(artifact_id: str, content: str) -> bool:
    """Write updated content to an artifact's Markdown file.

    Also updates the last_updated timestamp in SQLite.

    Args:
        artifact_id: The artifact's database ID.
        content: New Markdown content to write.

    Returns:
        True if successful, False if artifact not found.
    """
    artifact = await get_artifact(artifact_id)
    if not artifact:
        return False

    file_path = Path(artifact.file_path).resolve()
    if not str(file_path).startswith(str(ARTIFACTS_DIR.resolve())):
        return False  # Path traversal attempt

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)

    await update_artifact_timestamp(artifact_id)
    return True


async def list_project_artifacts(project_id: str) -> list[Artifact]:
    """List all artifacts for a project.

    Args:
        project_id: The project ID.

    Returns:
        List of Artifact metadata records.
    """
    return await get_artifacts_by_project(project_id)
