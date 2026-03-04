"""VPMA AI Risk Prediction — Identify missing risks from project health analysis.

Flow:
1. Fetch full LPD, staleness data, and RAID Log content
2. Anonymize all content via Privacy Proxy
3. LLM call with RISK_PREDICTION_PROMPT
4. Parse response into PredictedRisk objects
5. Reidentify PII in outputs
6. Log session to database
"""

import json
import logging

from app.models.schemas import (
    PredictedRisk,
    RiskPredictionResponse,
    SessionCreate,
)
from app.prompts.risk_prediction_prompts import RISK_PREDICTION_PROMPT
from app.services.artifact_sync import get_custom_terms, get_llm_client
from app.services.crud import create_session
from app.services.lpd_manager import get_full_lpd, get_section_staleness
from app.services.privacy_proxy import anonymize, reidentify

logger = logging.getLogger(__name__)


def _build_lpd_block(sections: dict[str, str]) -> str:
    """Format LPD sections as labeled text blocks for LLM input."""
    blocks = []
    for name, content in sections.items():
        blocks.append(f"--- Section: {name} ---\n{content or '(empty)'}\n--- End: {name} ---")
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


def _parse_predictions(llm_response: str) -> list[PredictedRisk]:
    """Parse LLM response into PredictedRisk objects."""
    text = _strip_code_fences(llm_response)
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        logger.warning("No valid JSON array in risk prediction response")
        return []

    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse risk prediction JSON: %s", e)
        return []

    results = []
    for item in data:
        try:
            results.append(PredictedRisk(**item))
        except Exception as e:
            logger.warning("Skipping malformed risk prediction: %s", e)
    return results


def _assess_project_health(
    sections: dict[str, str],
    staleness: list[dict],
    predictions: list[PredictedRisk],
) -> str:
    """Compute a simple project health assessment."""
    stale_count = sum(1 for s in staleness if s.get("days_since_update", 0) >= 14)
    empty_count = sum(1 for content in sections.values() if not content or not content.strip())
    high_risks = sum(1 for p in predictions if p.severity == "high")

    if high_risks >= 3 or stale_count >= 4:
        return "at_risk"
    if high_risks >= 1 or stale_count >= 2 or empty_count >= 3:
        return "needs_attention"
    return "healthy"


async def predict_risks(
    project_id: str = "default",
) -> RiskPredictionResponse:
    """Run AI risk prediction based on LPD state.

    Args:
        project_id: Project scope for LPD and session logging.

    Returns:
        RiskPredictionResponse with predicted risks and health assessment.

    Raises:
        LLMError: If the LLM call fails.
    """
    client = await get_llm_client()
    custom_terms = await get_custom_terms()

    # Fetch LPD data
    sections = await get_full_lpd(project_id)
    staleness = await get_section_staleness(project_id)

    if not sections:
        return RiskPredictionResponse(
            predictions=[],
            project_health="unknown",
            pii_detected=0,
            session_id="",
        )

    # Fetch RAID Log content if available
    raid_content = ""
    try:
        from app.services.artifact_manager import read_artifact_content
        from app.services.crud import get_artifact_by_type

        raid_artifact = await get_artifact_by_type(project_id, "raid_log")
        if raid_artifact:
            raid_content = await read_artifact_content(raid_artifact.artifact_id) or ""
    except Exception:
        logger.debug("No RAID Log found for project %s", project_id)

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

    anon_raid = ""
    if raid_content:
        raid_anon = await anonymize(raid_content, custom_terms=custom_terms)
        anon_raid = raid_anon.anonymized_text
        total_pii += len(raid_anon.entities)

    # Build LLM prompt
    lpd_block = _build_lpd_block(anon_sections)
    staleness_block = _build_staleness_block(staleness)

    user_prompt = f"## Living Project Document\n\n{lpd_block}\n\n"
    if anon_raid:
        user_prompt += f"## Current RAID Log\n\n{anon_raid}\n\n"
    else:
        user_prompt += "## Current RAID Log\n\n(No RAID Log exists yet)\n\n"
    user_prompt += f"## Section Staleness\n\n{staleness_block}"

    # LLM call
    logger.info("Running AI risk prediction for project %s", project_id)
    llm_response = await client.call(
        system_prompt=RISK_PREDICTION_PROMPT,
        user_prompt=user_prompt,
        max_tokens=4096,
    )

    # Parse predictions
    predictions = _parse_predictions(llm_response)

    # Reidentify PII in outputs
    for i, pred in enumerate(predictions):
        predictions[i] = pred.model_copy(
            update={
                "description": await reidentify(pred.description),
                "evidence": await reidentify(pred.evidence),
                "suggested_raid_entry": await reidentify(pred.suggested_raid_entry),
            }
        )

    # Assess project health
    project_health = _assess_project_health(sections, staleness, predictions)

    # Log session
    session = await create_session(
        SessionCreate(
            project_id=project_id,
            tab_used="risk_prediction",
            user_input=f"Risk prediction: {len(sections)} LPD sections analyzed",
            agent_output=f"Found {len(predictions)} predicted risks",
            tokens_used=client.estimate_tokens(llm_response),
            llm_model=getattr(client, "model", None),
        )
    )

    return RiskPredictionResponse(
        predictions=predictions,
        project_health=project_health,
        pii_detected=total_pii,
        session_id=session.session_id,
    )
