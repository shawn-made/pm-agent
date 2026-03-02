"""VPMA Artifact Sync — Core pipeline for text → suggestions.

Flow:
1. Classify input type (meeting notes, status update, transcript, general)
2. Anonymize PII via Privacy Proxy
3. Fetch LPD project context, anonymize it, and prepend to prompt
4. Send anonymized text to LLM with artifact sync prompt
5. Parse LLM response into structured suggestions
6. Reidentify PII in suggestions
7. Log session to database
8. Return suggestions to caller
"""

import json
import logging

from app.models.schemas import (
    AnalysisItem,
    ArtifactSyncResponse,
    LPDUpdate,
    LPDUpdateClassification,
    SessionCreate,
    Suggestion,
)
from app.prompts.artifact_sync import (
    ANALYZE_ADVISE_SYSTEM_PROMPT,
    ARTIFACT_SYNC_SYSTEM_PROMPT,
    INPUT_TYPE_DETECTION_PROMPT,
)
from app.prompts.lpd_prompts import LOG_SESSION_SYSTEM_PROMPT
from app.services.crud import create_session, get_setting
from app.services.llm_client import LLMClient, LLMError, Provider, create_client
from app.services.lpd_manager import (
    append_to_section,
    generate_session_summary,
    get_context_for_injection,
    log_session_summary,
    lpd_exists,
)
from app.services.privacy_proxy import anonymize, reidentify

logger = logging.getLogger(__name__)


async def _get_llm_client() -> LLMClient:
    """Get the configured LLM client based on settings."""
    provider_str = await get_setting("llm_provider") or "gemini"
    provider = Provider(provider_str)

    # Get API key from settings (overrides .env if set)
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


async def classify_input(text: str, client: LLMClient) -> str:
    """Classify the input type using LLM.

    Returns one of: "meeting_notes", "status_update", "transcript", "general_text"
    """
    try:
        result = await client.call(
            system_prompt=INPUT_TYPE_DETECTION_PROMPT,
            user_prompt=text[:500],  # Only need the beginning for classification
            max_tokens=256,
        )
        if not result:
            logger.warning("Input classification returned empty, defaulting to general_text")
            return "general_text"
        classification = result.strip().lower().replace('"', "").replace("'", "")
        valid_types = {"meeting_notes", "status_update", "transcript", "general_text"}
        return classification if classification in valid_types else "general_text"
    except LLMError:
        logger.warning("Input classification failed, defaulting to general_text")
        return "general_text"


def _parse_suggestions(llm_response: str) -> list[Suggestion]:
    """Parse the LLM response into a list of Suggestion objects.

    The LLM should return a JSON array, but we handle common issues:
    - Markdown code fences around JSON
    - Extra text before/after the JSON
    """
    text = llm_response.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        # Remove opening fence (possibly with language hint)
        first_newline = text.index("\n")
        text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[:-3].rstrip()

    # Find the JSON array
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        logger.warning("No JSON array found in LLM response")
        return []

    json_str = text[start : end + 1]

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse LLM response as JSON: %s", e)
        return []

    suggestions = []
    for item in data:
        try:
            suggestions.append(Suggestion(**item))
        except Exception as e:
            logger.warning("Skipping malformed suggestion: %s", e)
            continue

    return suggestions


def _parse_analysis(llm_response: str) -> tuple[list[AnalysisItem], str | None]:
    """Parse the LLM response into analysis items and a summary.

    The LLM should return a JSON object with "summary" and "items" keys.
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
        logger.warning("No JSON object found in LLM analysis response")
        return [], None

    json_str = text[start : end + 1]

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse LLM analysis response as JSON: %s", e)
        return [], None

    summary = data.get("summary")
    items = []
    for item in data.get("items", []):
        try:
            items.append(AnalysisItem(**item))
        except Exception as e:
            logger.warning("Skipping malformed analysis item: %s", e)
            continue

    return items, summary


def _parse_log_session(
    llm_response: str,
) -> tuple[str | None, list[LPDUpdate], list[Suggestion]]:
    """Parse the LLM response from log_session mode.

    Returns:
        Tuple of (session_summary, lpd_updates, artifact_suggestions).
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
        logger.warning("No JSON object found in log_session response")
        return None, [], []

    json_str = text[start : end + 1]

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse log_session response as JSON: %s", e)
        return None, [], []

    session_summary = data.get("session_summary")

    lpd_updates = []
    for item in data.get("lpd_updates", []):
        try:
            lpd_updates.append(
                LPDUpdate(
                    section=item["section"],
                    content=item["content"],
                )
            )
        except (KeyError, Exception) as e:
            logger.warning("Skipping malformed LPD update: %s", e)
            continue

    suggestions = []
    for item in data.get("artifact_suggestions", []):
        try:
            suggestions.append(Suggestion(**item))
        except Exception as e:
            logger.warning("Skipping malformed artifact suggestion: %s", e)
            continue

    return session_summary, lpd_updates, suggestions


async def run_artifact_sync(
    text: str,
    project_id: str = "default",
    mode: str = "extract",
) -> ArtifactSyncResponse:
    """Run the full artifact sync pipeline.

    Args:
        text: User input (meeting notes, status update, etc.)
        project_id: Which project context to use.
        mode: 'extract' for Extract & Route, 'analyze' for Analyze & Advise,
              'log_session' for Log Session Bridge.

    Returns:
        ArtifactSyncResponse with suggestions or analysis, input type, and session info.

    Raises:
        LLMError: If the LLM call fails.
    """
    # Validate mode — fall back to extract for unknown values
    if mode not in ("extract", "analyze", "log_session"):
        logger.warning("Unknown mode '%s', defaulting to extract", mode)
        mode = "extract"

    client = await _get_llm_client()
    custom_terms = await _get_custom_terms()

    # Step 1: Classify input type
    input_type = await classify_input(text, client)

    # Step 2: Anonymize PII
    anon_result = await anonymize(text, custom_terms=custom_terms)

    # Step 3: Fetch and anonymize LPD project context (if available)
    context_block = ""
    context_pii_count = 0
    lpd_context = await get_context_for_injection(project_id)
    if lpd_context:
        # Anonymize only the content (the heading "## Project Context" is structural
        # and should not pass through NER to avoid false positive mangling)
        context_body = lpd_context.split("\n", 1)[1] if "\n" in lpd_context else lpd_context
        context_anon = await anonymize(context_body, custom_terms=custom_terms)
        context_block = "## Project Context\n" + context_anon.anonymized_text + "\n\n"
        context_pii_count = len(context_anon.entities)

    # Step 4: Call LLM with mode-appropriate prompt
    user_prompt = f"{context_block}[Input type: {input_type}]\n\n{anon_result.anonymized_text}"
    if mode == "analyze":
        system_prompt = ANALYZE_ADVISE_SYSTEM_PROMPT
    elif mode == "log_session":
        system_prompt = LOG_SESSION_SYSTEM_PROMPT
    else:
        system_prompt = ARTIFACT_SYNC_SYSTEM_PROMPT
    llm_response = await client.call(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    # Step 5 & 6: Parse and reidentify based on mode
    suggestions = []
    analysis_items = []
    analysis_summary = None
    content_gate_active = True
    lpd_updates = []
    parsed_session_summary = None  # From log_session LLM response (not the lpd_manager function)

    if mode == "analyze":
        analysis_items, analysis_summary = _parse_analysis(llm_response)
        for i, item in enumerate(analysis_items):
            analysis_items[i] = item.model_copy(
                update={
                    "title": await reidentify(item.title),
                    "detail": await reidentify(item.detail),
                }
            )
        if analysis_summary:
            analysis_summary = await reidentify(analysis_summary)
    elif mode == "log_session":
        parsed_session_summary, lpd_updates, suggestions = _parse_log_session(llm_response)
        # Reidentify PII in log session results
        if parsed_session_summary:
            parsed_session_summary = await reidentify(parsed_session_summary)
        for i, update in enumerate(lpd_updates):
            lpd_updates[i] = update.model_copy(update={"content": await reidentify(update.content)})
        for i, suggestion in enumerate(suggestions):
            suggestions[i] = suggestion.model_copy(
                update={
                    "proposed_text": await reidentify(suggestion.proposed_text),
                    "reasoning": await reidentify(suggestion.reasoning),
                }
            )
        # Content quality gate: classify updates before applying
        from app.services.content_gate import (
            AUTO_APPLY_CLASSIFICATIONS,
            classify_lpd_updates,
        )

        content_gate_active = True
        if lpd_updates and await lpd_exists(project_id):
            lpd_updates, content_gate_active = await classify_lpd_updates(
                project_id=project_id,
                lpd_updates=lpd_updates,
                client=client,
                custom_terms=custom_terms,
            )
            # Only apply updates classified as new or update
            for update in lpd_updates:
                if (
                    update.classification
                    and update.classification.classification in AUTO_APPLY_CLASSIFICATIONS
                ):
                    await append_to_section(project_id, update.section, update.content)
        elif lpd_updates:
            # No LPD yet — mark all as new (nothing to compare against)
            lpd_updates = [
                update.model_copy(
                    update={
                        "classification": LPDUpdateClassification(
                            classification="new", reason="No existing project hub"
                        )
                    }
                )
                for update in lpd_updates
            ]
    else:
        suggestions = _parse_suggestions(llm_response)
        for i, suggestion in enumerate(suggestions):
            suggestions[i] = suggestion.model_copy(
                update={
                    "proposed_text": await reidentify(suggestion.proposed_text),
                    "reasoning": await reidentify(suggestion.reasoning),
                }
            )

    # Step 7: Log session
    tab_labels = {
        "extract": "artifact_sync",
        "analyze": "artifact_sync_analyze",
        "log_session": "artifact_sync_log_session",
    }
    tab_label = tab_labels.get(mode, "artifact_sync")
    session = await create_session(
        SessionCreate(
            project_id=project_id,
            tab_used=tab_label,
            user_input=text[:1000],
            agent_output=llm_response[:2000],
            tokens_used=client.estimate_tokens(text) + client.estimate_tokens(llm_response),
            llm_model=getattr(client, "model", None),
        )
    )

    # Step 8: Generate and log session summary for LPD Recent Context
    # For log_session, prefer the LLM-generated summary; fall back to template
    if mode == "log_session" and parsed_session_summary:
        summary_text = parsed_session_summary
    else:
        summary_text = generate_session_summary(
            suggestions=suggestions,
            analysis_items=analysis_items,
            input_type=input_type,
            mode=mode,
        )
    await log_session_summary(
        project_id=project_id,
        session_id=session.session_id,
        summary=summary_text,
        entities=json.dumps(
            {
                "mode": mode,
                "input_type": input_type,
                "suggestion_count": len(suggestions),
                "analysis_count": len(analysis_items),
                "lpd_update_count": len(lpd_updates),
            }
        ),
    )

    return ArtifactSyncResponse(
        suggestions=suggestions,
        analysis=analysis_items,
        analysis_summary=analysis_summary,
        lpd_updates=lpd_updates,
        session_summary=parsed_session_summary,
        input_type=input_type,
        session_id=session.session_id,
        pii_detected=len(anon_result.entities) + context_pii_count,
        mode=mode,
        content_gate_active=content_gate_active if mode == "log_session" else True,
    )
