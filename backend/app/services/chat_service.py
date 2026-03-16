"""VPMA Chat Service — Multi-turn conversational PM assistant (Task 60).

Implements the conversational API from docs/conversational_api_design.md.
Each conversation is project-scoped with LPD context injection, privacy
proxy, and structured suggestion extraction.

Flow:
1. Create or retrieve conversation
2. Build prompt: system + LPD context + conversation history + user message
3. Anonymize user message via Privacy Proxy
4. LLM call
5. Parse response: extract text, suggestions, LPD section references
6. Reidentify PII in response
7. Store messages in DB
8. Auto-generate title after first exchange
9. Log session
"""

import json
import logging
import uuid

from app.models.schemas import (
    ChatResponse,
    SessionCreate,
    Suggestion,
)
from app.prompts.chat_prompts import CHAT_SYSTEM_PROMPT, CHAT_TITLE_PROMPT
from app.services.artifact_sync import get_custom_terms, get_llm_client
from app.services.crud import (
    add_conversation_message,
    create_conversation,
    create_session,
    delete_conversation,
    get_conversation,
    get_conversation_messages,
    get_conversations_by_project,
    update_conversation,
)
from app.services.lpd_manager import get_context_for_injection
from app.services.privacy_proxy import anonymize, reidentify

logger = logging.getLogger(__name__)

# Max messages to include in full (older messages get truncated)
MAX_HISTORY_MESSAGES = 10


def _parse_response(llm_response: str) -> tuple[str, list[Suggestion], list[str]]:
    """Parse an LLM response into text, suggestions, and LPD section refs.

    Returns:
        (response_text, suggestions, lpd_sections_referenced)
    """
    text = llm_response
    suggestions = []
    lpd_refs = []

    # Extract LPD refs
    if "---LPD_REFS---" in text:
        parts = text.split("---LPD_REFS---", 1)
        text = parts[0].rstrip()
        refs_str = parts[1].strip()
        # Strip code fences if present
        if refs_str.startswith("```"):
            refs_str = refs_str.split("\n", 1)[1] if "\n" in refs_str else refs_str
        if refs_str.endswith("```"):
            refs_str = refs_str[:-3].rstrip()
        try:
            parsed_refs = json.loads(refs_str)
            if isinstance(parsed_refs, list):
                lpd_refs = [str(r) for r in parsed_refs]
        except (json.JSONDecodeError, ValueError):
            logger.debug("Failed to parse LPD refs: %s", refs_str[:100])

    # Extract suggestions
    if "---SUGGESTIONS---" in text:
        parts = text.split("---SUGGESTIONS---", 1)
        text = parts[0].rstrip()
        sugg_str = parts[1].strip()
        # Strip code fences
        if sugg_str.startswith("```"):
            sugg_str = sugg_str.split("\n", 1)[1] if "\n" in sugg_str else sugg_str
        if sugg_str.endswith("```"):
            sugg_str = sugg_str[:-3].rstrip()
        try:
            start = sugg_str.find("[")
            end = sugg_str.rfind("]")
            if start != -1 and end != -1:
                parsed = json.loads(sugg_str[start : end + 1])
                for item in parsed:
                    try:
                        suggestions.append(Suggestion(**item))
                    except Exception as e:
                        logger.debug("Skipping malformed suggestion: %s", e)
        except (json.JSONDecodeError, ValueError):
            logger.debug("Failed to parse suggestions: %s", sugg_str[:100])

    return text.strip(), suggestions, lpd_refs


def _build_history_prompt(messages: list[dict]) -> str:
    """Build conversation history for the LLM prompt."""
    if not messages:
        return ""

    # Take the most recent messages
    recent = messages[-MAX_HISTORY_MESSAGES:]
    lines = []
    for msg in recent:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        # Truncate long messages in history
        if len(content) > 500:
            content = content[:497] + "..."
        lines.append(f"{'User' if role == 'user' else 'Assistant'}: {content}")

    return "\n\n".join(lines)


async def _generate_title(client, message: str) -> str:
    """Generate a short conversation title from the first user message."""
    try:
        prompt = CHAT_TITLE_PROMPT.format(message=message[:200])
        title = await client.call(
            system_prompt="You are a title generator. Return only the title.",
            user_prompt=prompt,
            max_tokens=50,
        )
        # Clean up — remove quotes, limit length
        title = title.strip().strip('"').strip("'")
        if len(title) > 60:
            title = title[:57] + "..."
        return title
    except Exception:
        # Fallback: first N chars of user message
        fallback = message[:40].strip()
        if len(message) > 40:
            fallback += "..."
        return fallback


async def send_chat_message(
    project_id: str,
    message: str,
    conversation_id: str | None = None,
    include_lpd_context: bool = True,
    include_artifacts: bool = False,
) -> ChatResponse:
    """Send a message and get a response in a conversation.

    Args:
        project_id: Project scope.
        message: User's message text.
        conversation_id: Existing conversation ID, or None to start new.
        include_lpd_context: Whether to inject LPD context.
        include_artifacts: Whether to include artifact content.

    Returns:
        ChatResponse with response text, suggestions, and metadata.

    Raises:
        LLMError: If the LLM call fails.
    """
    client = await get_llm_client()
    custom_terms = await get_custom_terms()

    # Create or retrieve conversation
    is_new = conversation_id is None
    if is_new:
        conversation_id = str(uuid.uuid4())
        await create_conversation(conversation_id, project_id, mode="chat")

    # Get conversation history
    history = []
    if not is_new:
        history_rows = await get_conversation_messages(conversation_id, limit=MAX_HISTORY_MESSAGES)
        history = history_rows

    # Build system prompt with LPD context
    system_prompt = CHAT_SYSTEM_PROMPT

    if include_lpd_context:
        lpd_context = await get_context_for_injection(project_id)
        if lpd_context:
            system_prompt += f"\n\n## Current Project Context\n\n{lpd_context}"

    if include_artifacts:
        from app.services.artifact_manager import list_project_artifacts, read_artifact_content

        artifacts = await list_project_artifacts(project_id)
        artifact_parts = []
        for artifact in artifacts:
            content = await read_artifact_content(artifact.artifact_id)
            if content and content.strip():
                name = artifact.artifact_type.replace("_", " ").title()
                artifact_parts.append(f"### {name}\n{content.strip()}")
        if artifact_parts:
            system_prompt += "\n\n## Current Artifacts\n\n" + "\n\n".join(artifact_parts)

    # Build the user prompt
    history_prompt = _build_history_prompt(history)

    # Anonymize user message
    anon_result = await anonymize(message, custom_terms=custom_terms)
    anon_message = anon_result.anonymized_text
    total_pii = len(anon_result.entities)

    user_prompt_parts = []
    if history_prompt:
        user_prompt_parts.append(f"## Conversation History\n\n{history_prompt}")
    user_prompt_parts.append(f"## Current Message\n\n{anon_message}")
    user_prompt = "\n\n".join(user_prompt_parts)

    # LLM call
    llm_response = await client.call(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=4096,
    )

    # Parse response
    response_text, suggestions, lpd_refs = _parse_response(llm_response)

    # Reidentify PII
    response_text = await reidentify(response_text)
    for i, sugg in enumerate(suggestions):
        suggestions[i] = sugg.model_copy(
            update={
                "proposed_text": await reidentify(sugg.proposed_text),
                "reasoning": await reidentify(sugg.reasoning),
            }
        )

    # Store messages
    user_msg_id = str(uuid.uuid4())
    assistant_msg_id = str(uuid.uuid4())
    token_count = client.estimate_tokens(llm_response)

    await add_conversation_message(
        message_id=user_msg_id,
        conversation_id=conversation_id,
        role="user",
        content=message,  # Store original (not anonymized) for user display
    )

    await add_conversation_message(
        message_id=assistant_msg_id,
        conversation_id=conversation_id,
        role="assistant",
        content=response_text,
        suggestions_json=json.dumps([s.model_dump() for s in suggestions]),
        lpd_sections_json=json.dumps(lpd_refs),
        token_count=token_count,
    )

    # Update conversation metadata
    title_update = None
    if is_new:
        title_update = await _generate_title(client, message)
    await update_conversation(conversation_id, title=title_update)

    # Log session
    session = await create_session(
        SessionCreate(
            project_id=project_id,
            tab_used="chat",
            user_input=message[:200],
            agent_output=response_text[:500],
            tokens_used=token_count,
            llm_model=getattr(client, "model", None),
        )
    )

    return ChatResponse(
        conversation_id=conversation_id,
        message_id=assistant_msg_id,
        response=response_text,
        suggestions=suggestions,
        lpd_sections_referenced=lpd_refs,
        session_id=session.session_id,
        pii_detected=total_pii,
        token_count=token_count,
    )


async def get_conversations(project_id: str) -> list[dict]:
    """List conversations for a project."""
    rows = await get_conversations_by_project(project_id)
    return [
        {
            "conversation_id": row["conversation_id"],
            "title": row.get("title"),
            "mode": row.get("mode", "chat"),
            "created_at": str(row["created_at"]),
            "last_message_at": str(row["last_message_at"]),
            "message_count": row["message_count"],
        }
        for row in rows
    ]


async def get_conversation_history(project_id: str, conversation_id: str) -> dict | None:
    """Get full conversation with message history."""
    conv = await get_conversation(conversation_id)
    if not conv or conv["project_id"] != project_id:
        return None

    messages_rows = await get_conversation_messages(conversation_id)
    messages = []
    for row in messages_rows:
        msg = {
            "message_id": row["message_id"],
            "role": row["role"],
            "content": row["content"],
            "timestamp": str(row["created_at"]),
        }
        # Parse JSON fields for assistant messages
        if row["role"] == "assistant":
            try:
                msg["suggestions"] = json.loads(row.get("suggestions_json") or "[]")
            except json.JSONDecodeError:
                msg["suggestions"] = []
            try:
                msg["lpd_sections_referenced"] = json.loads(row.get("lpd_sections_json") or "[]")
            except json.JSONDecodeError:
                msg["lpd_sections_referenced"] = []
        messages.append(msg)

    return {
        "conversation_id": conversation_id,
        "title": conv.get("title"),
        "mode": conv.get("mode", "chat"),
        "messages": messages,
    }


async def remove_conversation(project_id: str, conversation_id: str) -> bool:
    """Delete a conversation (validates project ownership)."""
    conv = await get_conversation(conversation_id)
    if not conv or conv["project_id"] != project_id:
        return False
    return await delete_conversation(conversation_id)
