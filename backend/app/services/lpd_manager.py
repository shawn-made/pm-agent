"""VPMA LPD Manager — Living Project Document operations.

The LPD is a persistent knowledge base that accumulates project context across sessions.
It is separate from the Phase 0 artifact system (D17). The database is source of truth;
a Markdown file is rendered as a write-through cache for human readability.

Key design decisions:
- Section-based storage, not a single file (D16)
- Separate system from artifacts (D17)
- 7 fixed sections with independent staleness tracking
- Recent Context section is auto-pruned to ~1500 tokens
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

from app.models.schemas import (
    LPD_SECTION_NAMES,
    LPD_SECTIONS,
    LPDSection,
    LPDSectionCreate,
    LPDSessionSummaryCreate,
)
from app.services.crud import (
    create_lpd_section,
    create_lpd_session_summary,
    get_lpd_section,
    get_lpd_sections,
    get_recent_session_summaries,
    lpd_exists,
    update_lpd_section_content,
)
from app.services.database import VPMA_DIR

logger = logging.getLogger(__name__)

# Where LPD markdown files are cached
LPD_DIR = VPMA_DIR / "artifacts"

# Mapping from artifact section names (lowercase) to LPD section names.
# When a suggestion is applied to an artifact, this determines which LPD
# section receives the return-path update.
ARTIFACT_SECTION_TO_LPD: dict[str, str] = {
    "risks": "Risks",
    "decisions": "Decisions",
    "action items": "Open Questions",
    "accomplishments": "Overview",
    "blockers": "Risks",
}

# Approximate token budget for Recent Context section
RECENT_CONTEXT_TOKEN_BUDGET = 1500

# Approximate token budget for full context injection
CONTEXT_INJECTION_TOKEN_BUDGET = 4000

# Rough chars-per-token estimate (conservative for English)
CHARS_PER_TOKEN = 4


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English text."""
    return len(text) // CHARS_PER_TOKEN


async def initialize_lpd(project_id: str) -> list[LPDSection]:
    """Create all 7 LPD sections from the fixed template. Idempotent.

    If sections already exist for this project, returns them without modification.

    Returns:
        List of all LPD sections for the project.
    """
    if await lpd_exists(project_id):
        return await get_lpd_sections(project_id)

    sections = []
    for section_def in LPD_SECTIONS:
        section = await create_lpd_section(
            LPDSectionCreate(
                project_id=project_id,
                section_name=section_def["name"],
                content="",
                section_order=section_def["order"],
            )
        )
        sections.append(section)

    # Write the initial Markdown file
    await _sync_markdown(project_id, sections)

    logger.info("Initialized LPD for project '%s' with %d sections", project_id, len(sections))
    return sections


async def get_full_lpd(project_id: str) -> dict[str, str]:
    """Get the full LPD as a dict of section_name → content.

    Returns:
        Dict mapping section names to their content. Empty dict if LPD not initialized.
    """
    sections = await get_lpd_sections(project_id)
    return {s.section_name: s.content for s in sections}


async def render_lpd_markdown(project_id: str) -> str:
    """Render the full LPD as a Markdown document.

    Returns:
        Complete Markdown string with all sections.
    """
    sections = await get_lpd_sections(project_id)
    if not sections:
        return ""

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Living Project Document",
        "",
        f"**Project**: {project_id}",
        f"**Last Updated**: {now}",
        "",
    ]

    for section in sections:
        lines.append(f"## {section.section_name}")
        lines.append("")
        if section.content:
            lines.append(section.content)
        else:
            lines.append(f"_No {section.section_name.lower()} recorded yet._")
        lines.append("")

    return "\n".join(lines)


async def update_section(project_id: str, section_name: str, content: str) -> bool:
    """Replace the content of an LPD section entirely.

    Also syncs the Markdown file to disk.

    Returns:
        True if the update succeeded, False if section not found.
    """
    if section_name not in LPD_SECTION_NAMES:
        logger.warning("Invalid LPD section name: %s", section_name)
        return False

    result = await update_lpd_section_content(project_id, section_name, content)
    if result is None:
        return False

    await _sync_markdown_from_db(project_id)
    return True


async def append_to_section(project_id: str, section_name: str, text: str) -> bool:
    """Append text to an existing LPD section.

    Adds the text on a new line after existing content.

    Returns:
        True if successful, False if section not found.
    """
    if section_name not in LPD_SECTION_NAMES:
        logger.warning("Invalid LPD section name: %s", section_name)
        return False

    section = await get_lpd_section(project_id, section_name)
    if section is None:
        return False

    if section.content:
        new_content = section.content + "\n" + text
    else:
        new_content = text

    result = await update_lpd_section_content(project_id, section_name, new_content)
    if result is None:
        return False

    await _sync_markdown_from_db(project_id)
    return True


async def log_session_summary(
    project_id: str,
    session_id: str | None,
    summary: str,
    entities: str = "{}",
) -> None:
    """Record a session summary and rebuild the Recent Context section.

    Args:
        project_id: Project this session belongs to.
        session_id: Optional link to the sync session record.
        summary: Brief text describing what happened in this session.
        entities: JSON string of extracted entities (decisions, risks, etc.)
    """
    await create_lpd_session_summary(
        LPDSessionSummaryCreate(
            project_id=project_id,
            session_id=session_id,
            summary_text=summary,
            entities_extracted=entities,
        )
    )

    # Rebuild Recent Context from recent summaries
    await _rebuild_recent_context(project_id)


async def get_context_for_injection(
    project_id: str, max_tokens: int = CONTEXT_INJECTION_TOKEN_BUDGET
) -> str:
    """Assemble LPD context for injection into LLM prompts.

    Selects sections within the token budget, prioritizing:
    1. Overview (always included if available)
    2. Recent Context (most relevant for current work)
    3. Remaining sections in order, truncated if needed

    Args:
        project_id: Project to get context for.
        max_tokens: Maximum approximate token budget.

    Returns:
        Assembled context string, or empty string if no LPD exists.
    """
    if not await lpd_exists(project_id):
        return ""

    sections = await get_lpd_sections(project_id)
    if not sections:
        return ""

    # Build section content, filtering empty sections
    section_texts = {}
    for section in sections:
        if section.content.strip():
            section_texts[section.section_name] = section.content

    if not section_texts:
        return ""

    # Priority order for inclusion
    priority_order = [
        "Overview",
        "Recent Context",
        "Risks",
        "Decisions",
        "Open Questions",
        "Stakeholders",
        "Timeline & Milestones",
    ]

    lines = ["## Project Context"]
    current_tokens = _estimate_tokens(lines[0])

    for name in priority_order:
        if name not in section_texts:
            continue

        content = section_texts[name]
        section_block = f"\n### {name}\n{content}"
        section_tokens = _estimate_tokens(section_block)

        if current_tokens + section_tokens > max_tokens:
            # Try to include a truncated version
            remaining_chars = (max_tokens - current_tokens) * CHARS_PER_TOKEN
            if remaining_chars > 100:
                truncated = content[:remaining_chars] + "..."
                lines.append(f"\n### {name}\n{truncated}")
            break

        lines.append(section_block)
        current_tokens += section_tokens

    return "\n".join(lines)


async def get_section_staleness(project_id: str) -> list[dict]:
    """Get staleness information for each LPD section.

    Returns a list of dicts with section_name, updated_at, verified_at,
    and days_since_update for each section.
    """
    sections = await get_lpd_sections(project_id)
    now = datetime.now(timezone.utc)
    result = []

    for section in sections:
        updated_at = section.updated_at
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)

        days_since_update = (now - updated_at).days

        verified_at = section.verified_at
        days_since_verified = None
        if verified_at:
            if isinstance(verified_at, str):
                verified_at = datetime.fromisoformat(verified_at)
            if verified_at.tzinfo is None:
                verified_at = verified_at.replace(tzinfo=timezone.utc)
            days_since_verified = (now - verified_at).days

        result.append(
            {
                "section_name": section.section_name,
                "updated_at": str(section.updated_at),
                "verified_at": str(section.verified_at) if section.verified_at else None,
                "days_since_update": days_since_update,
                "days_since_verified": days_since_verified,
                "has_content": bool(section.content.strip()),
            }
        )

    return result


async def update_lpd_from_suggestion(
    project_id: str,
    artifact_section: str,
    proposed_text: str,
) -> bool:
    """Update the LPD based on an applied artifact suggestion (return path).

    Maps the artifact section to the corresponding LPD section and appends
    the proposed text. Does nothing if the LPD is not initialized or the
    artifact section has no LPD mapping.

    Args:
        project_id: Project to update.
        artifact_section: The section name from the suggestion (e.g., "Risks", "Action Items").
        proposed_text: The text that was applied to the artifact.

    Returns:
        True if the LPD was updated, False if skipped (no LPD, no mapping, or error).
    """
    if not await lpd_exists(project_id):
        return False

    lpd_section = ARTIFACT_SECTION_TO_LPD.get(artifact_section.lower().strip())
    if not lpd_section:
        logger.debug(
            "No LPD mapping for artifact section '%s', skipping return path",
            artifact_section,
        )
        return False

    # Check for duplicate — don't append if the text is already present
    section = await get_lpd_section(project_id, lpd_section)
    if section and proposed_text.strip() in section.content:
        logger.debug("Duplicate text in LPD section '%s', skipping", lpd_section)
        return False

    result = await append_to_section(project_id, lpd_section, proposed_text)
    if result:
        logger.info(
            "Return path: applied '%s' → LPD '%s' for project '%s'",
            artifact_section,
            lpd_section,
            project_id,
        )
    return result


def generate_session_summary(
    suggestions: list,
    analysis_items: list | None = None,
    input_type: str = "general_text",
    mode: str = "extract",
) -> str:
    """Generate a template-based session summary (no LLM call).

    Produces a one-line summary describing what happened in this sync session.

    Args:
        suggestions: List of Suggestion objects from extract mode.
        analysis_items: List of AnalysisItem objects from analyze mode.
        input_type: Classified input type (e.g., "meeting_notes").
        mode: Pipeline mode ("extract" or "analyze").

    Returns:
        A brief summary string suitable for the Recent Context section.
    """
    input_label = input_type.replace("_", " ")

    if mode == "analyze":
        count = len(analysis_items) if analysis_items else 0
        return f"Analyzed {input_label}: {count} observation(s) generated."

    if not suggestions:
        return f"Processed {input_label}: no suggestions generated."

    # Group suggestions by artifact type
    by_type: dict[str, int] = {}
    for s in suggestions:
        by_type[s.artifact_type] = by_type.get(s.artifact_type, 0) + 1

    parts = [f"{count} {atype}" for atype, count in sorted(by_type.items())]
    return f"Extracted from {input_label}: {', '.join(parts)}."


# ============================================================
# Internal helpers
# ============================================================


async def _rebuild_recent_context(project_id: str) -> None:
    """Rebuild the Recent Context section from session summaries.

    Fetches recent summaries and assembles them into the section,
    pruning to stay within RECENT_CONTEXT_TOKEN_BUDGET.
    """
    summaries = await get_recent_session_summaries(project_id, limit=20)
    if not summaries:
        return

    lines = []
    current_tokens = 0

    for summary in summaries:
        created = summary.created_at
        if isinstance(created, str):
            created = datetime.fromisoformat(created)
        date_str = created.strftime("%Y-%m-%d")
        line = f"- **{date_str}**: {summary.summary_text}"
        line_tokens = _estimate_tokens(line)

        if current_tokens + line_tokens > RECENT_CONTEXT_TOKEN_BUDGET:
            break

        lines.append(line)
        current_tokens += line_tokens

    content = "\n".join(lines) if lines else ""
    await update_lpd_section_content(project_id, "Recent Context", content)

    # Sync the markdown cache so file-based readers (e.g., Claude Code) see fresh data
    await _sync_markdown_from_db(project_id)


async def _sync_markdown_from_db(project_id: str) -> None:
    """Re-read sections from DB and write the Markdown file."""
    sections = await get_lpd_sections(project_id)
    await _sync_markdown(project_id, sections)


async def _sync_markdown(project_id: str, sections: list[LPDSection]) -> None:
    """Write the LPD Markdown file to disk (write-through cache)."""
    LPD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = _lpd_file_path(project_id)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Living Project Document",
        "",
        f"**Project**: {project_id}",
        f"**Last Updated**: {now}",
        "",
    ]

    for section in sections:
        lines.append(f"## {section.section_name}")
        lines.append("")
        if section.content:
            lines.append(section.content)
        else:
            lines.append(f"_No {section.section_name.lower()} recorded yet._")
        lines.append("")

    file_path.write_text("\n".join(lines))
    logger.debug("Synced LPD Markdown to %s", file_path)


def _lpd_file_path(project_id: str) -> Path:
    """Get the file path for a project's LPD Markdown cache."""
    import re

    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", project_id)
    return LPD_DIR / f"{safe_id}_lpd.md"
