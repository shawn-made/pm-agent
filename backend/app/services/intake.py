"""VPMA In-Flight Project Intake — bulk import existing PM files into the LPD.

Processes one or more existing PM documents (meeting notes, status reports, project
plans, RAID logs) through an LLM to extract structured entities, presents them as a
draft for human review, and applies approved sections to the LPD.

Key design decisions:
- Per-file processing: one LLM call per file (D18)
- Draft review before commit: user approves what goes into the LPD
- Conflicts are flagged, not auto-resolved
- Privacy proxy applied to all content before LLM
"""

import json
import logging

from app.models.schemas import (
    INTAKE_FIELD_TO_LPD_SECTION,
    IntakeConflict,
    IntakeDraft,
    IntakeExtraction,
    IntakeFile,
)
from app.prompts.lpd_prompts import INTAKE_EXTRACTION_PROMPT
from app.services.crud import get_setting
from app.services.llm_client import LLMClient, Provider, create_client
from app.services.lpd_manager import (
    append_to_section,
    get_full_lpd,
    initialize_lpd,
    lpd_exists,
)
from app.services.privacy_proxy import anonymize, reidentify

logger = logging.getLogger(__name__)


async def _get_llm_client() -> LLMClient:
    """Get the configured LLM client based on settings."""
    provider_str = await get_setting("llm_provider") or "gemini"
    provider = Provider(provider_str)

    if provider == Provider.CLAUDE:
        api_key = await get_setting("anthropic_api_key")
        return create_client(provider, api_key=api_key) if api_key else create_client(provider)
    elif provider == Provider.GEMINI:
        api_key = await get_setting("google_ai_api_key")
        return create_client(provider, api_key=api_key) if api_key else create_client(provider)
    else:
        return create_client(provider)


async def _get_custom_terms() -> list[str]:
    """Load custom sensitive terms from settings."""
    terms_str = await get_setting("sensitive_terms")
    if not terms_str:
        return []
    return [t.strip() for t in terms_str.replace("\n", ",").split(",") if t.strip()]


def _parse_extraction(llm_response: str, source_file: str) -> IntakeExtraction:
    """Parse the LLM response into an IntakeExtraction.

    Handles code fences, extra text, and malformed JSON gracefully.
    """
    text = llm_response.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        first_newline = text.index("\n")
        text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[:-3].rstrip()

    # Find the JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        logger.warning("No JSON object found in intake extraction response for %s", source_file)
        return IntakeExtraction(source_file=source_file)

    json_str = text[start : end + 1]

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse intake extraction JSON for %s: %s", source_file, e)
        return IntakeExtraction(source_file=source_file)

    return IntakeExtraction(
        source_file=source_file,
        overview=data.get("overview", ""),
        stakeholders=data.get("stakeholders", ""),
        timeline=data.get("timeline", ""),
        risks=data.get("risks", ""),
        decisions=data.get("decisions", ""),
        open_questions=data.get("open_questions", ""),
    )


async def process_intake_file(
    content: str,
    filename: str,
    custom_terms: list[str] | None = None,
    client: LLMClient | None = None,
) -> tuple[IntakeExtraction, int]:
    """Process a single file through the intake pipeline.

    Args:
        content: File text content.
        filename: Name of the source file.
        custom_terms: Custom sensitive terms for anonymization.
        client: LLM client (created if not provided).

    Returns:
        Tuple of (extraction, pii_count).
    """
    if client is None:
        client = await _get_llm_client()
    if custom_terms is None:
        custom_terms = await _get_custom_terms()

    # Anonymize content before sending to LLM
    anon_result = await anonymize(content, custom_terms=custom_terms)

    # LLM extraction
    user_prompt = f"[Source file: {filename}]\n\n{anon_result.anonymized_text}"
    llm_response = await client.call(
        system_prompt=INTAKE_EXTRACTION_PROMPT,
        user_prompt=user_prompt,
    )

    # Parse extraction
    extraction = _parse_extraction(llm_response, filename)

    # Reidentify PII in extracted fields
    extraction = IntakeExtraction(
        source_file=extraction.source_file,
        overview=await reidentify(extraction.overview) if extraction.overview else "",
        stakeholders=await reidentify(extraction.stakeholders) if extraction.stakeholders else "",
        timeline=await reidentify(extraction.timeline) if extraction.timeline else "",
        risks=await reidentify(extraction.risks) if extraction.risks else "",
        decisions=await reidentify(extraction.decisions) if extraction.decisions else "",
        open_questions=await reidentify(extraction.open_questions)
        if extraction.open_questions
        else "",
    )

    return extraction, len(anon_result.entities)


async def generate_intake_draft(
    files: list[IntakeFile],
    project_id: str,
) -> IntakeDraft:
    """Process multiple files and generate a draft for review.

    Args:
        files: List of files to process.
        project_id: Target project for the LPD.

    Returns:
        IntakeDraft with per-file extractions, combined proposals, and conflicts.
    """
    client = await _get_llm_client()
    custom_terms = await _get_custom_terms()

    extractions: list[IntakeExtraction] = []
    total_pii = 0

    for file in files:
        extraction, pii_count = await process_intake_file(
            content=file.content,
            filename=file.filename,
            custom_terms=custom_terms,
            client=client,
        )
        extractions.append(extraction)
        total_pii += pii_count

    # Combine extractions into proposed sections
    proposed_sections: dict[str, str] = {}
    for field_name, section_name in INTAKE_FIELD_TO_LPD_SECTION.items():
        parts = []
        for ext in extractions:
            value = getattr(ext, field_name, "")
            if value.strip():
                parts.append(value.strip())
        if parts:
            proposed_sections[section_name] = "\n".join(parts)

    # Detect conflicts with existing LPD content
    conflicts: list[IntakeConflict] = []
    if await lpd_exists(project_id):
        existing_lpd = await get_full_lpd(project_id)
        for field_name, section_name in INTAKE_FIELD_TO_LPD_SECTION.items():
            existing_content = existing_lpd.get(section_name, "").strip()
            if not existing_content:
                continue

            # Check each extraction for this field
            for ext in extractions:
                proposed = getattr(ext, field_name, "").strip()
                if not proposed:
                    continue

                # Flag as conflict if the section already has content
                conflicts.append(
                    IntakeConflict(
                        section=section_name,
                        existing=existing_content,
                        proposed=proposed,
                        source_file=ext.source_file,
                    )
                )

    return IntakeDraft(
        extractions=extractions,
        proposed_sections=proposed_sections,
        conflicts=conflicts,
        pii_detected=total_pii,
    )


async def apply_intake_draft(
    project_id: str,
    proposed_sections: dict[str, str],
    approved_sections: list[str],
) -> tuple[list[str], list[str]]:
    """Apply approved intake sections to the LPD.

    Initializes the LPD if it doesn't exist. Appends approved content
    to existing sections (does not replace).

    Args:
        project_id: Target project.
        proposed_sections: Section name → proposed content from the draft.
        approved_sections: List of section names the user approved.

    Returns:
        Tuple of (sections_updated, sections_skipped).
    """
    # Ensure LPD exists
    if not await lpd_exists(project_id):
        await initialize_lpd(project_id)

    updated = []
    skipped = []

    for section_name, content in proposed_sections.items():
        if section_name in approved_sections:
            success = await append_to_section(project_id, section_name, content)
            if success:
                updated.append(section_name)
            else:
                logger.warning(
                    "Failed to apply intake to section '%s' for project '%s'",
                    section_name,
                    project_id,
                )
                skipped.append(section_name)
        else:
            skipped.append(section_name)

    logger.info(
        "Intake applied for project '%s': %d updated, %d skipped",
        project_id,
        len(updated),
        len(skipped),
    )
    return updated, skipped
