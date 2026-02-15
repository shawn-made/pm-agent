"""VPMA Artifact Sync — Core pipeline for text → suggestions.

Flow:
1. Classify input type (meeting notes, status update, transcript, general)
2. Anonymize PII via Privacy Proxy
3. Send anonymized text to LLM with artifact sync prompt
4. Parse LLM response into structured suggestions
5. Reidentify PII in suggestions
6. Log session to database
7. Return suggestions to caller
"""

import json
import logging
from typing import Optional

from app.models.schemas import (
    ArtifactSyncResponse,
    SessionCreate,
    Suggestion,
)
from app.prompts.artifact_sync import (
    ARTIFACT_SYNC_SYSTEM_PROMPT,
    INPUT_TYPE_DETECTION_PROMPT,
)
from app.services.crud import create_session, get_setting
from app.services.llm_client import LLMClient, LLMError, Provider, create_client
from app.services.privacy_proxy import anonymize, reidentify

logger = logging.getLogger(__name__)


async def _get_llm_client() -> LLMClient:
    """Get the configured LLM client based on settings."""
    provider_str = await get_setting("llm_provider") or "claude"
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
            max_tokens=20,
        )
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


async def run_artifact_sync(
    text: str,
    project_id: str = "default",
) -> ArtifactSyncResponse:
    """Run the full artifact sync pipeline.

    Args:
        text: User input (meeting notes, status update, etc.)
        project_id: Which project context to use.

    Returns:
        ArtifactSyncResponse with suggestions, input type, and session info.

    Raises:
        LLMError: If the LLM call fails.
    """
    client = await _get_llm_client()
    custom_terms = await _get_custom_terms()

    # Step 1: Classify input type
    input_type = await classify_input(text, client)

    # Step 2: Anonymize PII
    anon_result = await anonymize(text, custom_terms=custom_terms)

    # Step 3: Call LLM with anonymized text + input type context
    user_prompt = f"[Input type: {input_type}]\n\n{anon_result.anonymized_text}"
    llm_response = await client.call(
        system_prompt=ARTIFACT_SYNC_SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )

    # Step 4: Parse suggestions
    suggestions = _parse_suggestions(llm_response)

    # Step 5: Reidentify PII in suggestion texts
    for i, suggestion in enumerate(suggestions):
        suggestions[i] = suggestion.model_copy(
            update={
                "proposed_text": await reidentify(suggestion.proposed_text),
                "reasoning": await reidentify(suggestion.reasoning),
            }
        )

    # Step 6: Log session
    session = await create_session(
        SessionCreate(
            project_id=project_id,
            tab_used="artifact_sync",
            user_input=text[:1000],  # Truncate for storage
            agent_output=llm_response[:2000],
            tokens_used=client.estimate_tokens(text) + client.estimate_tokens(llm_response),
            llm_model=getattr(client, "model", None),
        )
    )

    return ArtifactSyncResponse(
        suggestions=suggestions,
        input_type=input_type,
        session_id=session.session_id,
        pii_detected=len(anon_result.entities),
    )
