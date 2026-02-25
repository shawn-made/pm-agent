"""VPMA API Routes."""

import re

from fastapi import APIRouter, HTTPException

from app.models.schemas import ArtifactSyncRequest, ArtifactSyncResponse, Suggestion
from app.services.artifact_manager import (
    ArtifactType,
    get_or_create_artifact,
    read_artifact_content,
    write_artifact_content,
)
from app.services.artifact_sync import run_artifact_sync
from app.services.crud import get_all_settings, upsert_setting
from app.services.llm_client import LLMError

router = APIRouter()


def _insert_into_section(content: str, section: str, proposed_text: str) -> str:
    """Insert proposed_text into the correct ## section of a markdown artifact.

    Finds the ``## section`` heading and appends the text at the end of that
    section (before the next ``## `` heading).  Falls back to end-of-file
    append if the section heading isn't found.
    """
    pattern = re.compile(r"^## " + re.escape(section) + r"\s*$", re.MULTILINE | re.IGNORECASE)
    match = pattern.search(content)

    if not match:
        # Section not found — fallback to end-of-file append
        return content.rstrip() + "\n\n" + proposed_text + "\n"

    # Find the next ## heading after our section
    rest = content[match.end():]
    next_heading = re.search(r"^## ", rest, re.MULTILINE)

    if next_heading:
        insert_pos = match.end() + next_heading.start()
        before = content[:insert_pos].rstrip()
        after = content[insert_pos:]
        return before + "\n\n" + proposed_text + "\n\n" + after
    else:
        # Last section — append at end
        return content.rstrip() + "\n\n" + proposed_text + "\n"


@router.get("/health")
async def health_check():
    """Backend health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


# ============================================================
# ARTIFACT SYNC
# ============================================================


@router.post("/artifact-sync", response_model=ArtifactSyncResponse)
async def artifact_sync(request: ArtifactSyncRequest):
    """Main flow: text → anonymize → LLM → suggestions.

    Accepts user text (meeting notes, transcripts, updates) and returns
    suggested updates to PM artifacts (RAID Log, Status Report, Meeting Notes).
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text input is required")

    try:
        result = await run_artifact_sync(
            text=request.text,
            project_id=request.project_id,
            mode=request.mode,
        )
        return result
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))


# ============================================================
# ARTIFACTS
# ============================================================


@router.post("/artifacts/{artifact_id}/apply")
async def apply_suggestion(artifact_id: str, suggestion: Suggestion):
    """Apply a suggestion to an artifact stored in ~/VPMA/artifacts/.

    Reads the current artifact content, inserts the suggestion's proposed text
    into the matching ``## section``, and writes back.  Skips duplicates.
    """
    content = await read_artifact_content(artifact_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Artifact not found")

    # Dedup guard — skip if this exact text is already in the artifact
    if suggestion.proposed_text.strip() in content:
        return {"status": "duplicate", "artifact_id": artifact_id}

    updated = _insert_into_section(content, suggestion.section, suggestion.proposed_text)

    success = await write_artifact_content(artifact_id, updated)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to write artifact")

    return {"status": "applied", "artifact_id": artifact_id}


@router.post("/artifacts/apply")
async def apply_suggestion_by_type(suggestion: Suggestion, project_id: str = "default"):
    """Apply a suggestion by artifact type — creates the artifact if needed.

    This is the convenience endpoint used by the frontend. It resolves the
    artifact_type to a file on disk, creating it from a template if it doesn't
    exist yet, then inserts the suggestion into the correct section.
    Skips duplicates.
    """
    type_map = {
        "raid log": ArtifactType.RAID_LOG,
        "status report": ArtifactType.STATUS_REPORT,
        "meeting notes": ArtifactType.MEETING_NOTES,
    }
    artifact_type = type_map.get(suggestion.artifact_type.lower().strip())
    if not artifact_type:
        raise HTTPException(status_code=400, detail=f"Unknown artifact type: {suggestion.artifact_type}")

    artifact = await get_or_create_artifact(project_id, artifact_type)

    content = await read_artifact_content(artifact.artifact_id)
    if content is None:
        raise HTTPException(status_code=500, detail="Failed to read artifact after creation")

    # Dedup guard — skip if this exact text is already in the artifact
    if suggestion.proposed_text.strip() in content:
        return {"status": "duplicate", "artifact_id": artifact.artifact_id, "artifact_type": suggestion.artifact_type}

    updated = _insert_into_section(content, suggestion.section, suggestion.proposed_text)

    success = await write_artifact_content(artifact.artifact_id, updated)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to write artifact")

    return {"status": "applied", "artifact_id": artifact.artifact_id, "artifact_type": suggestion.artifact_type}


# ============================================================
# SETTINGS
# ============================================================


@router.get("/settings")
async def get_settings():
    """Retrieve all current settings."""
    settings = await get_all_settings()
    # Mask API keys in response (show last 4 chars only)
    masked = {}
    for key, value in settings.items():
        if "api_key" in key and value:
            masked[key] = "****" + value[-4:] if len(value) > 4 else "****"
        else:
            masked[key] = value
    return {"settings": masked}


@router.put("/settings")
async def update_settings(settings: dict):
    """Update settings — API keys, LLM provider, sensitive terms.

    Accepts a flat dictionary of key-value pairs.
    Example: {"llm_provider": "claude", "anthropic_api_key": "sk-..."}
    """
    allowed_keys = {
        "llm_provider",
        "anthropic_api_key",
        "google_ai_api_key",
        "sensitive_terms",
    }

    updated = {}
    for key, value in settings.items():
        if key not in allowed_keys:
            continue
        if value is not None:
            await upsert_setting(key, str(value))
            updated[key] = key if "api_key" in key else value

    return {"status": "saved", "updated": list(updated.keys())}
