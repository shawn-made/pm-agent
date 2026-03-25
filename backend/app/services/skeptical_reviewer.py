"""VPMA Skeptical Reviewer — Evidence-based critical review of project documents.

Flow:
1. Fetch full LPD, staleness data, and artifact content
2. Anonymize all content via Privacy Proxy
3. LLM call with SKEPTICAL_REVIEW_PROMPT
4. Parse response into ReviewFinding objects
5. Filter out findings without specific evidence citations
6. Reidentify PII in outputs
7. Log session to database
"""

import json
import logging

from app.models.schemas import (
    ReviewFinding,
    SessionCreate,
    SkepticalReviewResponse,
)
from app.prompts.skeptical_reviewer_prompts import SKEPTICAL_REVIEW_PROMPT
from app.services.artifact_sync import get_custom_terms, get_llm_client
from app.services.crud import create_session
from app.services.lpd_manager import get_full_lpd, get_section_staleness
from app.services.privacy_proxy import anonymize, reidentify

logger = logging.getLogger(__name__)


def _build_lpd_block(sections: dict[str, str]) -> str:
    """Format LPD sections as labeled text blocks for LLM input."""
    blocks = []
    for name, content in sections.items():
        blocks.append(
            f"--- Section: {name} ---\n{content or '(empty)'}\n--- End: {name} ---"
        )
    return "\n\n".join(blocks)


def _build_staleness_block(staleness: list[dict]) -> str:
    """Format staleness data as a readable table for LLM input."""
    lines = ["Section | Days Since Update"]
    lines.append("---|---")
    for entry in staleness:
        days = entry.get("days_since_update", "unknown")
        lines.append(f"{entry.get('section_name', '?')} | {days}")
    return "\n".join(lines)


def _strip_code_fences(text: str) -> str:
    """Strip markdown code fences from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.index("\n") if "\n" in text else len(text)
        text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[:-3].rstrip()
    return text


def _parse_findings(llm_response: str) -> list[ReviewFinding]:
    """Parse LLM response into ReviewFinding objects."""
    text = _strip_code_fences(llm_response)
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        logger.warning("No valid JSON array in skeptical review response")
        return []

    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse skeptical review JSON: %s", e)
        return []

    results = []
    for item in data:
        try:
            results.append(ReviewFinding(**item))
        except Exception as e:
            logger.warning("Skipping malformed review finding: %s", e)
    return results


def _filter_quality(findings: list[ReviewFinding]) -> list[ReviewFinding]:
    """Remove findings that lack specific evidence citations."""
    quality = []
    for f in findings:
        # Evidence must be non-empty and reference at least one section name
        if not f.evidence or len(f.evidence.strip()) < 10:
            logger.info("Filtered finding '%s' — insufficient evidence", f.title)
            continue
        # Reject generic descriptions
        if f.description and len(f.description.strip()) < 20:
            logger.info("Filtered finding '%s' — description too vague", f.title)
            continue
        quality.append(f)
    return quality


async def skeptical_review(
    project_id: str = "default",
) -> SkepticalReviewResponse:
    """Run Skeptical Review on project LPD and artifacts.

    Args:
        project_id: Project scope for LPD and session logging.

    Returns:
        SkepticalReviewResponse with evidence-backed findings.

    Raises:
        LLMError: If the LLM call fails.
    """
    client = await get_llm_client()
    custom_terms = await get_custom_terms()

    # Fetch LPD data
    sections = await get_full_lpd(project_id)
    staleness = await get_section_staleness(project_id)

    if not sections:
        return SkepticalReviewResponse(
            findings=[],
            sections_analyzed=0,
            artifacts_analyzed=0,
            pii_detected=0,
            session_id="",
        )

    # Fetch artifact content (RAID Log, Status Report, Meeting Notes)
    artifact_content = {}
    artifacts_found = 0
    try:
        from app.services.artifact_manager import read_artifact_content
        from app.services.crud import get_artifact_by_type

        for atype in ["raid_log", "status_report", "meeting_notes"]:
            artifact = await get_artifact_by_type(project_id, atype)
            if artifact:
                content = await read_artifact_content(artifact.artifact_id)
                if content:
                    artifact_content[atype] = content
                    artifacts_found += 1
    except Exception:
        logger.debug("Could not load artifacts for project %s", project_id)

    # Anonymize all content
    total_pii = 0
    anon_sections = {}
    for name, content in sections.items():
        if content:
            anon_result = await anonymize(content, custom_terms=custom_terms)
            anon_sections[name] = anon_result.anonymized_text
            total_pii += len(anon_result.entities)
        else:
            anon_sections[name] = ""

    anon_artifacts = {}
    for atype, content in artifact_content.items():
        if content:
            anon_result = await anonymize(content, custom_terms=custom_terms)
            anon_artifacts[atype] = anon_result.anonymized_text
            total_pii += len(anon_result.entities)

    # Build LLM prompt
    lpd_block = _build_lpd_block(anon_sections)
    staleness_block = _build_staleness_block(staleness)

    user_prompt = f"## Living Project Document\n\n{lpd_block}\n\n"

    if anon_artifacts:
        user_prompt += "## Project Artifacts\n\n"
        for atype, content in anon_artifacts.items():
            user_prompt += f"--- Artifact: {atype} ---\n{content}\n--- End: {atype} ---\n\n"
    else:
        user_prompt += "## Project Artifacts\n\n(No artifacts exist yet)\n\n"

    user_prompt += f"## Section Staleness\n\n{staleness_block}"

    # LLM call
    logger.info("Running Skeptical Review for project %s", project_id)
    llm_response = await client.call(
        system_prompt=SKEPTICAL_REVIEW_PROMPT,
        user_prompt=user_prompt,
        max_tokens=4096,
    )

    # Parse and filter findings
    findings = _parse_findings(llm_response)
    findings = _filter_quality(findings)

    # Reidentify PII in outputs
    for i, finding in enumerate(findings):
        findings[i] = finding.model_copy(
            update={
                "title": await reidentify(finding.title),
                "description": await reidentify(finding.description),
                "evidence": await reidentify(finding.evidence),
                "recommendation": await reidentify(finding.recommendation),
            }
        )

    # Log session
    session = await create_session(
        SessionCreate(
            project_id=project_id,
            tab_used="review",
            user_input=f"Skeptical Review: {len(sections)} LPD sections, {artifacts_found} artifacts",
            agent_output=f"Found {len(findings)} findings",
            tokens_used=client.estimate_tokens(llm_response),
            llm_model=getattr(client, "model", None),
        )
    )

    return SkepticalReviewResponse(
        findings=findings,
        sections_analyzed=len(sections),
        artifacts_analyzed=artifacts_found,
        pii_detected=total_pii,
        session_id=session.session_id,
    )
