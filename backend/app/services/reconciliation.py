"""VPMA Cross-Section LPD Reconciliation Engine (D39).

Detects cross-section impacts within the Living Project Document:
- Decisions that resolve Open Questions
- Timeline changes that contradict stated Decisions
- New information that supersedes older entries
- Stakeholder changes that require updates to Risks/Decisions

Flow:
1. Fetch full LPD (all 7 sections)
2. Anonymize all section content via Privacy Proxy
3. Single LLM call with CROSS_SECTION_RECONCILIATION_PROMPT
4. Parse response → list of CrossSectionImpact
5. Reidentify PII in outputs
6. Log session to database
"""

import json
import logging

from app.models.schemas import (
    CrossSectionImpact,
    ReconciliationResponse,
    SessionCreate,
)
from app.prompts.lpd_prompts import CROSS_SECTION_RECONCILIATION_PROMPT
from app.services.artifact_sync import get_custom_terms, get_llm_client
from app.services.crud import create_session
from app.services.lpd_manager import get_full_lpd
from app.services.privacy_proxy import anonymize, reidentify

logger = logging.getLogger(__name__)


def _build_section_block(sections: dict[str, str]) -> str:
    """Format LPD sections as labeled text blocks for LLM input."""
    blocks = []
    for name, content in sections.items():
        blocks.append(f"--- Section: {name} ---\n{content or '(empty)'}\n--- End: {name} ---")
    return "\n\n".join(blocks)


def _strip_code_fences(text: str) -> str:
    """Strip markdown code fences from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.index("\n") if "\n" in text else len(text)
        text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[:-3].rstrip()
    return text


def _parse_impacts(llm_response: str) -> list[CrossSectionImpact]:
    """Parse LLM response into CrossSectionImpact objects."""
    text = _strip_code_fences(llm_response)
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        logger.warning("No valid JSON array in reconciliation response")
        return []

    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse reconciliation JSON: %s", e)
        return []

    results = []
    for item in data:
        try:
            results.append(CrossSectionImpact(**item))
        except Exception as e:
            logger.warning("Skipping malformed cross-section impact: %s", e)
    return results


async def reconcile_lpd_sections(
    project_id: str = "default",
) -> ReconciliationResponse:
    """Run cross-section LPD reconciliation.

    Args:
        project_id: Project scope for LPD and session logging.

    Returns:
        ReconciliationResponse with detected cross-section impacts.

    Raises:
        LLMError: If the LLM call fails.
    """
    client = await get_llm_client()
    custom_terms = await get_custom_terms()

    # Fetch full LPD
    sections = await get_full_lpd(project_id)

    if not sections:
        return ReconciliationResponse(
            impacts=[],
            sections_analyzed=0,
            pii_detected=0,
            session_id="",
        )

    # Anonymize all section content
    total_pii = 0
    anon_sections = {}
    for name, content in sections.items():
        if content:
            anon_result = await anonymize(content, custom_terms=custom_terms)
            anon_sections[name] = anon_result.anonymized_text
            total_pii += len(anon_result.entities)
        else:
            anon_sections[name] = ""

    # Build LLM prompt
    section_block = _build_section_block(anon_sections)
    user_prompt = f"## LPD Sections\n\n{section_block}"

    # LLM call
    logger.info("Running cross-section reconciliation for project %s", project_id)
    llm_response = await client.call(
        system_prompt=CROSS_SECTION_RECONCILIATION_PROMPT,
        user_prompt=user_prompt,
        max_tokens=4096,
    )

    # Parse impacts
    impacts = _parse_impacts(llm_response)

    # Reidentify PII in outputs
    for i, impact in enumerate(impacts):
        impacts[i] = impact.model_copy(
            update={
                "description": await reidentify(impact.description),
                "suggested_action": await reidentify(impact.suggested_action),
                "source_excerpt": await reidentify(impact.source_excerpt),
                "target_excerpt": await reidentify(impact.target_excerpt),
            }
        )

    # Count non-empty sections analyzed
    sections_analyzed = sum(1 for c in sections.values() if c and c.strip())

    # Log session
    session = await create_session(
        SessionCreate(
            project_id=project_id,
            tab_used="reconciliation",
            user_input=f"Reconciliation: {sections_analyzed} LPD sections analyzed",
            agent_output=f"Found {len(impacts)} cross-section impacts",
            tokens_used=client.estimate_tokens(llm_response),
            llm_model=getattr(client, "model", None),
        )
    )

    return ReconciliationResponse(
        impacts=impacts,
        sections_analyzed=sections_analyzed,
        pii_detected=total_pii,
        session_id=session.session_id,
    )
