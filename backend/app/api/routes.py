"""VPMA API Routes."""

import re
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ArtifactSyncRequest,
    ArtifactSyncResponse,
    DeepStrategyApplyRequest,
    DeepStrategyApplyResponse,
    DeepStrategyRequest,
    DeepStrategyResponse,
    IntakeApplyRequest,
    IntakeApplyResponse,
    IntakeDraft,
    IntakePreviewRequest,
    ReconciliationResponse,
    RiskPredictionResponse,
    Suggestion,
)
from app.services.artifact_manager import (
    ArtifactType,
    get_or_create_artifact,
    read_artifact_content,
    write_artifact_content,
)
from app.services.artifact_sync import get_custom_terms, get_llm_client, run_artifact_sync
from app.services.crud import get_all_settings, get_setting, upsert_setting, verify_lpd_section
from app.services.deep_strategy import apply_deep_strategy_updates, run_deep_strategy
from app.services.intake import apply_intake_draft, generate_intake_draft
from app.services.llm_client import LLMError
from app.services.llm_ollama import check_ollama_status
from app.services.lpd_manager import (
    get_full_lpd,
    get_section_staleness,
    initialize_lpd,
    render_lpd_markdown,
    update_lpd_from_suggestion,
    update_section,
)
from app.services.reconciliation import reconcile_lpd_sections
from app.services.risk_prediction import predict_risks
from app.services.transcript_watcher import get_transcript_watcher

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
    rest = content[match.end() :]
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
    return {"status": "ok", "version": "0.4.0"}


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
        raise HTTPException(
            status_code=400, detail=f"Unknown artifact type: {suggestion.artifact_type}"
        )

    artifact = await get_or_create_artifact(project_id, artifact_type)

    content = await read_artifact_content(artifact.artifact_id)
    if content is None:
        raise HTTPException(status_code=500, detail="Failed to read artifact after creation")

    # Dedup guard — skip if this exact text is already in the artifact
    if suggestion.proposed_text.strip() in content:
        return {
            "status": "duplicate",
            "artifact_id": artifact.artifact_id,
            "artifact_type": suggestion.artifact_type,
        }

    updated = _insert_into_section(content, suggestion.section, suggestion.proposed_text)

    success = await write_artifact_content(artifact.artifact_id, updated)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to write artifact")

    # Return path: update LPD with the applied suggestion content
    # Uses content gate for semantic dedup when LLM is available (D40)
    try:
        client = await get_llm_client()
        custom_terms = await get_custom_terms()
    except Exception:
        client = None
        custom_terms = None

    lpd_result = await update_lpd_from_suggestion(
        project_id=project_id,
        artifact_section=suggestion.section,
        proposed_text=suggestion.proposed_text,
        client=client,
        custom_terms=custom_terms,
    )

    response = {
        "status": "applied",
        "artifact_id": artifact.artifact_id,
        "artifact_type": suggestion.artifact_type,
        "lpd_updated": lpd_result.get("updated", False),
    }
    # Include change details when LPD was updated
    if lpd_result.get("updated"):
        response["lpd_change"] = {
            "section": lpd_result["section"],
            "content_added": lpd_result["content_added"],
        }
    return response


@router.get("/artifacts/{project_id}/export")
async def export_artifacts(project_id: str):
    """Export all artifacts for a project as combined Markdown.

    Returns the content of all existing artifacts (RAID Log, Status Report,
    Meeting Notes) concatenated into a single Markdown document.
    """
    from app.services.artifact_manager import list_project_artifacts

    artifacts = await list_project_artifacts(project_id)

    if not artifacts:
        return {"markdown": "", "artifact_count": 0}

    parts = []
    for artifact in artifacts:
        content = await read_artifact_content(artifact.artifact_id)
        if content and content.strip():
            parts.append(content.strip())

    combined = "\n\n---\n\n".join(parts)

    return {"markdown": combined, "artifact_count": len(parts)}


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
        "ollama_base_url",
        "ollama_model",
        "sensitive_terms",
        "transcript_watch_folder",
        "transcript_auto_mode",
    }

    updated = {}
    for key, value in settings.items():
        if key not in allowed_keys:
            continue
        if value is not None:
            await upsert_setting(key, str(value))
            updated[key] = key if "api_key" in key else value

    return {"status": "saved", "updated": list(updated.keys())}


@router.get("/settings/ollama-status")
async def ollama_status():
    """Check Ollama connectivity and list available models."""
    base_url = await get_setting("ollama_base_url")
    result = await check_ollama_status(base_url or None)
    return result


# ============================================================
# LPD INTAKE
# ============================================================


@router.post("/lpd/{project_id}/intake/preview", response_model=IntakeDraft)
async def intake_preview(project_id: str, request: IntakePreviewRequest):
    """Process intake files and return a draft for review.

    Each file is processed individually through the LLM (one call per file).
    Returns a draft with per-file extractions, combined proposals per LPD section,
    and any conflicts with existing LPD content.
    """
    if not request.files:
        raise HTTPException(status_code=400, detail="At least one file is required")

    for f in request.files:
        if not f.content.strip():
            raise HTTPException(
                status_code=400,
                detail=f"File '{f.filename}' has no content",
            )

    try:
        draft = await generate_intake_draft(request.files, project_id)
        return draft
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/lpd/{project_id}/intake/apply", response_model=IntakeApplyResponse)
async def intake_apply(project_id: str, request: IntakeApplyRequest):
    """Apply approved intake sections to the LPD.

    Takes the proposed_sections from the preview draft and applies only
    the sections in approved_sections. Initializes the LPD if needed.
    """
    if not request.approved_sections:
        raise HTTPException(status_code=400, detail="At least one section must be approved")

    updated, skipped = await apply_intake_draft(
        project_id=project_id,
        proposed_sections=request.proposed_sections,
        approved_sections=request.approved_sections,
    )

    return IntakeApplyResponse(sections_updated=updated, sections_skipped=skipped)


# ============================================================
# LPD (Living Project Document)
# ============================================================


@router.get("/lpd/{project_id}/sections")
async def get_lpd_sections_endpoint(project_id: str):
    """Get all LPD sections for a project.

    Returns a dict mapping section names to their content, plus raw section
    metadata. If no LPD exists, returns an empty dict.
    """
    sections = await get_full_lpd(project_id)
    return {"sections": sections}


@router.put("/lpd/{project_id}/sections/{section_name}")
async def update_lpd_section(project_id: str, section_name: str, body: dict):
    """Update an LPD section's content.

    Expects JSON body with a "content" key.
    """
    content = body.get("content")
    if content is None:
        raise HTTPException(status_code=400, detail="Missing 'content' in request body")

    success = await update_section(project_id, section_name, content)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Section '{section_name}' not found or invalid",
        )
    return {"status": "updated", "section": section_name}


@router.post("/lpd/{project_id}/initialize")
async def initialize_lpd_endpoint(project_id: str):
    """Initialize a new LPD for a project (idempotent).

    Creates all 7 sections with empty content. If the LPD already exists,
    returns the existing sections without modification.
    """
    sections = await initialize_lpd(project_id)
    return {
        "status": "initialized",
        "section_count": len(sections),
        "sections": [s.section_name for s in sections],
    }


@router.get("/lpd/{project_id}/staleness")
async def get_lpd_staleness_endpoint(project_id: str):
    """Get staleness information for each LPD section.

    Returns per-section timestamps and days-since-update metrics.
    """
    staleness = await get_section_staleness(project_id)
    return {"staleness": staleness}


@router.get("/lpd/{project_id}/markdown")
async def get_lpd_markdown(project_id: str):
    """Render the full LPD as a Markdown document."""
    md = await render_lpd_markdown(project_id)
    if not md:
        raise HTTPException(status_code=404, detail="No LPD found for this project")
    return {"markdown": md}


@router.post("/lpd/{project_id}/sections/{section_name}/verify")
async def verify_lpd_section_endpoint(project_id: str, section_name: str):
    """Mark a section as verified (human-reviewed and accurate)."""
    result = await verify_lpd_section(project_id, section_name)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Section '{section_name}' not found",
        )
    return {"status": "verified", "section": section_name}


# ============================================================
# TRANSCRIPT WATCHER
# ============================================================


@router.get("/transcript-watcher/status")
async def transcript_watcher_status():
    """Get the current transcript watcher status."""
    watcher = get_transcript_watcher()
    return watcher.status()


@router.post("/transcript-watcher/start")
async def transcript_watcher_start(
    project_id: str = "default",
):
    """Start the transcript file watcher.

    Uses the configured watch folder and mode from settings.
    Falls back to defaults if not configured.
    """
    watch_folder = await get_setting("transcript_watch_folder")
    if not watch_folder:
        raise HTTPException(
            status_code=400,
            detail="No transcript_watch_folder configured. Set it in Settings first.",
        )

    mode = await get_setting("transcript_auto_mode") or "extract"

    watcher = get_transcript_watcher()
    started = await watcher.start(
        watch_folder=watch_folder,
        mode=mode,
        project_id=project_id,
    )

    if not started:
        if watcher.is_running:
            raise HTTPException(status_code=409, detail="Watcher is already running")
        raise HTTPException(status_code=400, detail="Failed to start watcher (invalid folder?)")

    return {"status": "started", **watcher.status()}


@router.post("/transcript-watcher/stop")
async def transcript_watcher_stop():
    """Stop the transcript file watcher."""
    watcher = get_transcript_watcher()
    stopped = await watcher.stop()
    if not stopped:
        raise HTTPException(status_code=409, detail="Watcher is not running")
    return {"status": "stopped"}


# ============================================================
# DEEP STRATEGY
# ============================================================


@router.post("/deep-strategy/analyze", response_model=DeepStrategyResponse)
async def deep_strategy_analyze(request: DeepStrategyRequest):
    """Run 4-pass Deep Strategy analysis on uploaded artifacts.

    Accepts 2+ artifacts with name, content, and priority. Runs dependency
    graph construction, inconsistency detection, proposed updates, and
    cross-validation. Returns all results with summary statistics.
    """
    if len(request.artifacts) < 2:
        raise HTTPException(
            status_code=400, detail="At least 2 artifacts are required for Deep Strategy analysis"
        )

    try:
        result = await run_deep_strategy(
            artifacts=request.artifacts,
            project_id=request.project_id,
        )
        return result
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/deep-strategy/apply", response_model=DeepStrategyApplyResponse)
async def deep_strategy_apply(request: DeepStrategyApplyRequest):
    """Apply selected Deep Strategy updates to artifacts.

    VPMA-managed artifacts (RAID Log, Status Report, Meeting Notes) are
    written directly. Other artifacts are returned for copy-to-clipboard.
    """
    if not request.updates:
        raise HTTPException(status_code=400, detail="At least one update is required")

    result = await apply_deep_strategy_updates(request)
    return result


# ============================================================
# RISK PREDICTION
# ============================================================


@router.post("/risk-prediction/{project_id}", response_model=RiskPredictionResponse)
async def risk_prediction(project_id: str):
    """Run AI risk prediction based on project LPD state.

    Analyzes the full Living Project Document, RAID Log, and section
    staleness data to identify risks that are not yet tracked.
    """
    try:
        result = await predict_risks(project_id=project_id)
        return result
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))


# ============================================================
# LPD RECONCILIATION
# ============================================================


@router.post("/lpd/{project_id}/reconcile", response_model=ReconciliationResponse)
async def lpd_reconcile(project_id: str):
    """Run cross-section LPD reconciliation.

    Detects cross-section impacts: decisions resolving questions,
    timeline contradictions, superseded information, and required updates.
    """
    try:
        result = await reconcile_lpd_sections(project_id=project_id)
        return result
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/transcript-watcher/process")
async def transcript_watcher_process(body: dict):
    """Process a single transcript file manually (one-off).

    Expects JSON body with a "file_path" key.
    """
    file_path = body.get("file_path")
    if not file_path:
        raise HTTPException(status_code=400, detail="Missing 'file_path' in request body")

    watcher = get_transcript_watcher()
    result = await watcher.process_file(file_path)
    return result


@router.post("/transcript-watcher/upload")
async def transcript_watcher_upload(body: dict):
    """Process an uploaded transcript file (content provided directly).

    Accepts JSON body with "filename" and "content" keys.
    Used by the drag-and-drop UI where the browser reads the file.
    """
    import os
    import tempfile

    filename = body.get("filename", "")
    content = body.get("content", "")
    if not content or not content.strip():
        raise HTTPException(status_code=400, detail="Missing or empty 'content' in request body")

    suffix = os.path.splitext(filename)[1].lower() if filename else ".txt"
    if suffix not in {".vtt", ".srt", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Accepted: .vtt, .srt, .txt",
        )

    # Write to a temp file and process through the watcher pipeline
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, prefix="vpma_upload_", delete=False
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        watcher = get_transcript_watcher()
        result = await watcher.process_file(tmp_path)
        # Override the file name to show the original filename
        result["file"] = filename or f"upload{suffix}"
        return result
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


@router.get("/transcript-watcher/results")
async def transcript_watcher_results():
    """Get recent transcript processing results with full sync data.

    Returns the last 10 processed files with their full artifact sync
    results (suggestions, LPD updates, etc.) for frontend display.
    """
    watcher = get_transcript_watcher()
    return {"results": watcher.recent_files}


# ============================================================
# FOLDER BROWSER
# ============================================================


@router.get("/settings/browse-folders")
async def browse_folders(path: str = None):
    """Browse directories for folder selection (e.g., transcript watch folder).

    Security constraints:
    - Only lists subdirectories (no files)
    - Skips hidden directories (starting with .)
    - Restricts browsing to within the user's home directory
    - Does not follow symlinks
    """
    home = Path.home()

    if path:
        target = Path(path).resolve()
    else:
        target = home

    # Security: must be within home directory
    try:
        target.relative_to(home)
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Cannot browse outside home directory",
        )

    if not target.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found")

    # List subdirectories (skip hidden, skip symlinks)
    directories = []
    try:
        for entry in sorted(target.iterdir()):
            if entry.name.startswith("."):
                continue
            if entry.is_symlink():
                continue
            if entry.is_dir():
                directories.append(
                    {
                        "name": entry.name,
                        "path": str(entry),
                    }
                )
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")

    parent_path = str(target.parent) if target != home else None

    return {
        "current_path": str(target),
        "parent_path": parent_path,
        "directories": directories,
    }
