# Conversational API Design (D46)

**Date**: 2026-03-03
**Phase**: 2A (design only — implementation in Phase 2B/3)
**Relates to**: D36 (dual-tool architecture), D15 (hybrid workflow bridge)

## Problem Statement

VPMA currently operates in a paste-and-process model: user submits text, LLM processes it, results appear as suggestion cards. There is no way to have a multi-turn conversation where the LLM can ask follow-up questions, the user can refine requests, or context accumulates within a conversation session.

D36 established that VPMA will evolve into a dual-mode tool: structured UI (current) + freeform chat panel. This document defines the API shape for the chat/conversational interface.

## Design Principles

1. **LPD-aware**: Every conversation message can access the project's LPD context, same as artifact sync does today.
2. **Session-scoped**: Conversations are multi-turn within a session, with message history maintained.
3. **Privacy-first**: All user messages pass through the Privacy Proxy before reaching the LLM. Responses are reidentified before returning to the user.
4. **Action-capable**: The LLM can suggest artifact updates or LPD changes as structured side-effects within a conversational response, not just plain text.
5. **Project-scoped**: Every conversation belongs to a project (same `project_id` pattern used everywhere).

## API Endpoints

### `POST /api/chat/{project_id}`
Start or continue a conversation.

**Request** (`ChatRequest`):
```json
{
  "message": "What are the biggest risks in the project right now?",
  "conversation_id": "conv-uuid-123",  // null for new conversation
  "include_lpd_context": true,         // default true
  "include_artifacts": false            // default false — include artifact content
}
```

**Response** (`ChatResponse`):
```json
{
  "conversation_id": "conv-uuid-123",
  "message_id": "msg-uuid-456",
  "response": "Based on your project document, the three main risks are...",
  "suggestions": [
    {
      "artifact_type": "RAID Log",
      "change_type": "add",
      "section": "Risks",
      "proposed_text": "Risk: Vendor delivery timeline uncertainty...",
      "confidence": 0.85,
      "reasoning": "Identified from conversation context"
    }
  ],
  "lpd_sections_referenced": ["Risks", "Timeline & Milestones"],
  "session_id": "sess-uuid-789",
  "pii_detected": 2,
  "token_count": 1847
}
```

### `GET /api/chat/{project_id}/conversations`
List conversations for a project.

**Response**:
```json
{
  "conversations": [
    {
      "conversation_id": "conv-uuid-123",
      "title": "Risk Assessment Discussion",
      "created_at": "2026-03-03T10:00:00Z",
      "last_message_at": "2026-03-03T10:15:00Z",
      "message_count": 6
    }
  ]
}
```

### `GET /api/chat/{project_id}/conversations/{conversation_id}`
Get full conversation history.

**Response**:
```json
{
  "conversation_id": "conv-uuid-123",
  "title": "Risk Assessment Discussion",
  "messages": [
    {
      "message_id": "msg-uuid-001",
      "role": "user",
      "content": "What are the biggest risks?",
      "timestamp": "2026-03-03T10:00:00Z"
    },
    {
      "message_id": "msg-uuid-002",
      "role": "assistant",
      "content": "Based on your project document...",
      "suggestions": [...],
      "timestamp": "2026-03-03T10:00:03Z"
    }
  ]
}
```

### `DELETE /api/chat/{project_id}/conversations/{conversation_id}`
Delete a conversation and all its messages.

## Pydantic Models

```python
class ConversationMessage(BaseModel):
    message_id: str
    conversation_id: str
    role: str  # "user" or "assistant"
    content: str
    suggestions: list[Suggestion] = []
    lpd_sections_referenced: list[str] = []
    timestamp: datetime
    token_count: int = 0

class ConversationSession(BaseModel):
    conversation_id: str
    project_id: str
    title: str | None = None
    created_at: datetime
    last_message_at: datetime
    message_count: int = 0

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None  # null = new conversation
    include_lpd_context: bool = True
    include_artifacts: bool = False

class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    response: str
    suggestions: list[Suggestion] = []
    lpd_sections_referenced: list[str] = []
    session_id: str
    pii_detected: int = 0
    token_count: int = 0
```

## Database Tables

### `conversations`
```sql
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

### `conversation_messages`
```sql
CREATE TABLE IF NOT EXISTS conversation_messages (
    message_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    suggestions_json TEXT DEFAULT '[]',
    lpd_sections_json TEXT DEFAULT '[]',
    token_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);
```

## LLM Integration Flow

```
User message
  → Privacy Proxy anonymize()
  → Build prompt:
      - System prompt (conversational PM assistant persona)
      - LPD context (if include_lpd_context=true)
      - Artifact content (if include_artifacts=true)
      - Conversation history (prior messages in this conversation)
      - Current user message
  → LLM call (via abstract client — Claude/Gemini/Ollama)
  → Parse response:
      - Extract plain text response
      - Extract any structured suggestions (JSON within response)
  → Privacy Proxy reidentify()
  → Save message pair to DB
  → Return ChatResponse
```

## Context Window Management

Conversation history grows with each turn. Strategy:

1. **Recent window**: Include the last N messages in full (default N=10).
2. **Summary rollup**: When history exceeds the window, summarize older messages into a brief context paragraph. Store the summary on the conversation record.
3. **LPD token budget**: Same approach as artifact sync — cap LPD context at ~2000 tokens, selecting most relevant sections based on the user's message.

## Auto-Title Generation

New conversations start with `title=null`. After the first assistant response, generate a title from the conversation content (similar to how ChatGPT auto-titles). This can be done with a lightweight LLM call or simple heuristic (first user message, truncated).

## Relationship to Existing Features

- **Artifact Sync**: Chat can produce the same `Suggestion` objects. Apply flow is identical — reuses `applySuggestionByType`.
- **Log Session**: A conversation could end with a "save session" action that behaves like Log Session mode — summarizing the conversation and updating the LPD.
- **Privacy Proxy**: Same flow. User messages are anonymized, responses are reidentified.
- **Content Gate**: LPD updates from chat suggestions go through the same content quality gate (dedup, contradiction detection).

## Implementation Phases

1. **Phase 2A** (this task): Design doc + Pydantic models only. No implementation.
2. **Phase 2B or 3**: Backend implementation — DB tables, chat service, LLM prompt template.
3. **Phase 3**: Frontend — embedded chat panel in the UI, conversation list, message history.

## Open Questions

- **Streaming**: Should chat responses stream token-by-token? Improves perceived latency but adds SSE/WebSocket complexity. Recommendation: defer streaming to a polish phase; start with request/response.
- **Conversation archiving**: How long to retain conversations? Recommendation: keep indefinitely (local data, no storage concern), add optional "archive" status.
- **Cross-conversation context**: Should the LLM see summaries of prior conversations? Recommendation: not initially — LPD serves as the persistent memory. Add if users request it.
