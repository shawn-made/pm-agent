"""VPMA Morning Briefing Service — AI-generated project briefing (Task 59).

Gathers LPD sections, staleness data, cached risk/strategy results, and
session summaries, then synthesizes a focused PM briefing via LLM.

Flow:
1. Fetch LPD sections + staleness data
2. Fetch cached risk prediction + deep strategy results (latest sessions)
3. Fetch recent session summaries
4. Anonymize all content via Privacy Proxy
5. LLM call with BRIEFING_SYSTEM_PROMPT
6. Parse response into BriefingResponse
7. Reidentify PII in outputs
8. Log session + cache result
"""

import json
import logging
from datetime import datetime, timezone

from app.models.schemas import (
    BriefingAttentionItem,
    BriefingContradiction,
    BriefingResponse,
    BriefingUpcomingDate,
    SessionCreate,
)
from app.prompts.briefing_prompts import BRIEFING_SYSTEM_PROMPT
from app.services.artifact_sync import get_custom_terms, get_llm_client
from app.services.crud import create_session, get_sessions_by_project
from app.services.lpd_manager import get_full_lpd, get_section_staleness
from app.services.privacy_proxy import anonymize, reidentify

logger = logging.getLogger(__name__)

# Briefing cache TTL in hours
BRIEFING_CACHE_TTL_HOURS = 4


def _build_lpd_block(sections: dict[str, str]) -> str:
    """Format LPD sections as labeled text blocks for LLM input."""
    blocks = []
    for name, content in sections.items():
        blocks.append(f"--- Section: {name} ---\n{content or '(empty)'}\n--- End: {name} ---")
    return "\n\n".join(blocks)


def _build_staleness_block(staleness: list[dict]) -> str:
    """Format staleness data as a readable table for LLM input."""
    lines = ["Section | Days Since Update | Has Content"]
    lines.append("---|---|---")
    for entry in staleness:
        days = entry.get("days_since_update", "unknown")
        has_content = "Yes" if entry.get("has_content") else "No"
        lines.append(f"{entry.get('section_name', '?')} | {days} | {has_content}")
    return "\n".join(lines)


def _build_cached_results_block(sessions: list) -> str:
    """Extract cached risk prediction and deep strategy results from recent sessions."""
    blocks = []

    for session in sessions:
        if not session.agent_output:
            continue

        tab = session.tab_used or ""

        if tab == "risk_prediction":
            blocks.append(
                f"## Cached Risk Prediction (from {session.timestamp})\n{session.agent_output}"
            )
        elif tab == "deep_strategy":
            blocks.append(
                f"## Cached Document Consistency (from {session.timestamp})\n{session.agent_output}"
            )

        if len(blocks) >= 2:
            break

    return "\n\n".join(blocks) if blocks else "(No cached analysis results available)"


def _build_activity_block(sessions: list) -> str:
    """Build a recent activity summary from session summaries."""
    lines = []
    for session in sessions[:5]:
        tab = session.tab_used or "unknown"
        ts = session.timestamp
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        date_str = ts.strftime("%Y-%m-%d") if hasattr(ts, "strftime") else str(ts)[:10]
        summary = (session.user_input or "")[:100]
        lines.append(f"- {date_str} [{tab}]: {summary}")
    return "\n".join(lines) if lines else "(No recent activity)"


def _strip_code_fences(text: str) -> str:
    """Strip markdown code fences from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.index("\n") if "\n" in text else len(text)
        text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[:-3].rstrip()
    return text


def _parse_briefing(llm_response: str) -> dict:
    """Parse LLM response JSON into briefing components."""
    text = _strip_code_fences(llm_response)

    # Find JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        logger.warning("No valid JSON object in briefing response")
        return {}

    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse briefing JSON: %s", e)
        return {}


async def _get_cached_briefing(project_id: str) -> BriefingResponse | None:
    """Check for a recent cached briefing within the TTL."""
    sessions = await get_sessions_by_project(project_id, limit=5)

    for session in sessions:
        if session.tab_used != "briefing":
            continue
        if not session.agent_output:
            continue

        # Check freshness
        ts = session.timestamp
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        age_hours = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
        if age_hours > BRIEFING_CACHE_TTL_HOURS:
            continue

        # Parse cached result
        try:
            data = json.loads(session.agent_output)
            return BriefingResponse(**data)
        except (json.JSONDecodeError, Exception) as e:
            logger.debug("Failed to parse cached briefing: %s", e)
            continue

    return None


async def generate_briefing(
    project_id: str = "default",
    force_refresh: bool = False,
) -> BriefingResponse:
    """Generate an AI project briefing from all available project data.

    Args:
        project_id: Project scope.
        force_refresh: If True, skip cache and regenerate.

    Returns:
        BriefingResponse with attention items, dates, contradictions, and next action.

    Raises:
        LLMError: If the LLM call fails.
    """
    # Check cache first (unless force refresh)
    if not force_refresh:
        cached = await _get_cached_briefing(project_id)
        if cached:
            logger.info("Returning cached briefing for project %s", project_id)
            return cached

    client = await get_llm_client()
    custom_terms = await get_custom_terms()

    # Fetch project data
    sections = await get_full_lpd(project_id)
    staleness = await get_section_staleness(project_id)
    recent_sessions = await get_sessions_by_project(project_id, limit=10)

    if not sections:
        return BriefingResponse(
            attention_items=[],
            upcoming_dates=[],
            contradictions=[],
            suggested_next_action="No project data yet. Start by importing files on the Import tab or adding content to your Knowledge Base.",
            generated_at=datetime.now(timezone.utc).isoformat(),
            session_id="",
            from_cache=False,
        )

    # Anonymize LPD content
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
    lpd_block = _build_lpd_block(anon_sections)
    staleness_block = _build_staleness_block(staleness)
    cached_results_block = _build_cached_results_block(recent_sessions)
    activity_block = _build_activity_block(recent_sessions)

    user_prompt = (
        f"## Living Project Document\n\n{lpd_block}\n\n"
        f"## Section Staleness\n\n{staleness_block}\n\n"
        f"## Recent Activity\n\n{activity_block}\n\n"
        f"## Cached Analysis Results\n\n{cached_results_block}"
    )

    # LLM call
    logger.info("Generating briefing for project %s", project_id)
    llm_response = await client.call(
        system_prompt=BRIEFING_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=4096,
    )

    # Parse response
    parsed = _parse_briefing(llm_response)

    # Build typed objects
    attention_items = []
    for item in parsed.get("attention_items", []):
        try:
            attention_items.append(BriefingAttentionItem(**item))
        except Exception as e:
            logger.warning("Skipping malformed attention item: %s", e)

    upcoming_dates = []
    for item in parsed.get("upcoming_dates", []):
        try:
            upcoming_dates.append(BriefingUpcomingDate(**item))
        except Exception as e:
            logger.warning("Skipping malformed upcoming date: %s", e)

    contradictions = []
    for item in parsed.get("contradictions", []):
        try:
            contradictions.append(BriefingContradiction(**item))
        except Exception as e:
            logger.warning("Skipping malformed contradiction: %s", e)

    suggested_next_action = parsed.get(
        "suggested_next_action", "Review your project Knowledge Base."
    )

    # Reidentify PII in outputs
    for i, item in enumerate(attention_items):
        attention_items[i] = item.model_copy(
            update={
                "title": await reidentify(item.title),
                "detail": await reidentify(item.detail),
            }
        )
    for i, item in enumerate(upcoming_dates):
        upcoming_dates[i] = item.model_copy(
            update={"description": await reidentify(item.description)}
        )
    for i, item in enumerate(contradictions):
        contradictions[i] = item.model_copy(
            update={
                "description": await reidentify(item.description),
                "suggested_resolution": await reidentify(item.suggested_resolution),
            }
        )
    suggested_next_action = await reidentify(suggested_next_action)

    generated_at = datetime.now(timezone.utc).isoformat()

    # Build response
    response = BriefingResponse(
        attention_items=attention_items,
        upcoming_dates=upcoming_dates,
        contradictions=contradictions,
        suggested_next_action=suggested_next_action,
        generated_at=generated_at,
        session_id="",  # Will be set after session logging
        from_cache=False,
    )

    # Log session + cache the result
    session = await create_session(
        SessionCreate(
            project_id=project_id,
            tab_used="briefing",
            user_input=f"Briefing: {len(sections)} LPD sections, {len(staleness)} staleness entries",
            agent_output=response.model_dump_json(),
            tokens_used=client.estimate_tokens(llm_response),
            llm_model=getattr(client, "model", None),
        )
    )

    response.session_id = session.session_id
    return response
