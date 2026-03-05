"""VPMA Pydantic Models — Data shapes for all database tables."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# --- Projects ---


class ProjectCreate(BaseModel):
    project_id: Optional[str] = Field(None, description="UUID (auto-generated if omitted)")
    project_name: str = Field(..., description="Human-readable project name")
    landscape_config: str = Field("{}", description="JSON string of project landscape config")


class Project(BaseModel):
    project_id: str = Field(..., description="Unique project identifier (UUID)")
    project_name: str = Field(..., description="Human-readable project name")
    created_at: datetime = Field(..., description="When the project was created")
    landscape_config: str = Field(..., description="JSON string of project landscape config")


# --- Artifacts ---


class ArtifactCreate(BaseModel):
    artifact_id: Optional[str] = Field(None, description="UUID (auto-generated if omitted)")
    project_id: str = Field(..., description="Parent project ID")
    artifact_type: str = Field(
        ..., description="Artifact type: 'RAID Log', 'Status Report', or 'Meeting Notes'"
    )
    file_path: str = Field(..., description="Path to the Markdown file in data/artifacts/")


class Artifact(BaseModel):
    artifact_id: str = Field(..., description="Unique artifact identifier (UUID)")
    project_id: str = Field(..., description="Parent project ID")
    artifact_type: str = Field(
        ..., description="Artifact type: 'RAID Log', 'Status Report', or 'Meeting Notes'"
    )
    file_path: str = Field(..., description="Path to the Markdown file in data/artifacts/")
    last_updated: datetime = Field(..., description="Last modification timestamp")


# --- Artifact Versions ---


class ArtifactVersionCreate(BaseModel):
    version_id: Optional[str] = Field(None, description="UUID (auto-generated if omitted)")
    artifact_id: str = Field(..., description="Parent artifact ID")
    version_number: int = Field(..., description="Incremental version number")
    content_snapshot: Optional[str] = Field(
        None, description="Full Markdown content at this version"
    )
    session_id: Optional[str] = Field(None, description="Session that created this version")


class ArtifactVersion(BaseModel):
    version_id: str = Field(..., description="Unique version identifier (UUID)")
    artifact_id: str = Field(..., description="Parent artifact ID")
    version_number: int = Field(..., description="Incremental version number")
    content_snapshot: Optional[str] = Field(
        None, description="Full Markdown content at this version"
    )
    created_at: datetime = Field(..., description="When this version was created")
    session_id: Optional[str] = Field(None, description="Session that created this version")


# --- Sessions ---


class SessionCreate(BaseModel):
    session_id: Optional[str] = Field(None, description="UUID (auto-generated if omitted)")
    project_id: str = Field(..., description="Parent project ID")
    tab_used: Optional[str] = Field(None, description="Which UI tab triggered this session")
    user_input: Optional[str] = Field(None, description="Raw user input text")
    agent_output: Optional[str] = Field(None, description="LLM response JSON")
    persona_used: Optional[str] = Field(None, description="LLM persona/system prompt used")
    tokens_used: int = Field(0, description="Approximate token count for this session")
    llm_model: Optional[str] = Field(None, description="Model ID used (e.g., claude-sonnet-4-5)")


class Session(BaseModel):
    session_id: str = Field(..., description="Unique session identifier (UUID)")
    project_id: str = Field(..., description="Parent project ID")
    timestamp: datetime = Field(..., description="When the session was created")
    tab_used: Optional[str] = Field(None, description="Which UI tab triggered this session")
    user_input: Optional[str] = Field(None, description="Raw user input text")
    agent_output: Optional[str] = Field(None, description="LLM response JSON")
    persona_used: Optional[str] = Field(None, description="LLM persona/system prompt used")
    tokens_used: int = Field(..., description="Approximate token count for this session")
    llm_model: Optional[str] = Field(None, description="Model ID used (e.g., claude-sonnet-4-5)")


# --- PII Vault ---


class PIIMapping(BaseModel):
    token: str = Field(..., description="Anonymized placeholder token (e.g., <PERSON_1>)")
    original_value: str = Field(..., description="Original PII value before anonymization")
    entity_type: str = Field(..., description="PII category: PERSON, ORG, EMAIL, PHONE, etc.")
    first_seen: Optional[datetime] = Field(None, description="When this PII was first detected")


# --- Settings ---


class Setting(BaseModel):
    key: str = Field(..., description="Setting key (e.g., 'llm_provider', 'anthropic_api_key')")
    value: str = Field(..., description="Setting value (API keys are stored encrypted)")
    updated_at: Optional[datetime] = Field(None, description="Last time this setting was changed")


# --- LPD (Living Project Document) ---

# Fixed LPD sections with display order (D16)
LPD_SECTIONS = [
    {"name": "Overview", "order": 1},
    {"name": "Stakeholders", "order": 2},
    {"name": "Timeline & Milestones", "order": 3},
    {"name": "Risks", "order": 4},
    {"name": "Decisions", "order": 5},
    {"name": "Open Questions", "order": 6},
    {"name": "Recent Context", "order": 7},
]

LPD_SECTION_NAMES = [s["name"] for s in LPD_SECTIONS]


class LPDSectionCreate(BaseModel):
    section_id: Optional[str] = Field(None, description="UUID (auto-generated if omitted)")
    project_id: str = Field(..., description="Parent project ID")
    section_name: str = Field(..., description="LPD section name (e.g., 'Overview', 'Risks')")
    content: str = Field("", description="Markdown content for this section")
    section_order: int = Field(..., description="Display order (1-7)")


class LPDSection(BaseModel):
    section_id: str = Field(..., description="Unique section identifier (UUID)")
    project_id: str = Field(..., description="Parent project ID")
    section_name: str = Field(..., description="LPD section name")
    content: str = Field(..., description="Markdown content for this section")
    section_order: int = Field(..., description="Display order (1-7)")
    updated_at: datetime = Field(..., description="Last content modification timestamp")
    verified_at: Optional[datetime] = Field(
        None, description="Last time a human verified this section's accuracy"
    )


class LPDSessionSummaryCreate(BaseModel):
    summary_id: Optional[str] = Field(None, description="UUID (auto-generated if omitted)")
    project_id: str = Field(..., description="Parent project ID")
    session_id: Optional[str] = Field(None, description="Associated sync session ID")
    summary_text: str = Field(..., description="Brief summary of what happened in this session")
    entities_extracted: str = Field(
        "{}", description="JSON string of entities extracted (decisions, risks, actions)"
    )


class LPDSessionSummary(BaseModel):
    summary_id: str = Field(..., description="Unique summary identifier (UUID)")
    project_id: str = Field(..., description="Parent project ID")
    session_id: Optional[str] = Field(None, description="Associated sync session ID")
    summary_text: str = Field(..., description="Brief summary of what happened in this session")
    entities_extracted: str = Field(..., description="JSON string of entities extracted")
    created_at: datetime = Field(..., description="When this summary was created")


# --- Artifact Sync ---


class Suggestion(BaseModel):
    """A single suggestion for updating a PM artifact."""

    artifact_type: str = Field(
        ..., description="Target artifact: 'RAID Log', 'Status Report', or 'Meeting Notes'"
    )
    change_type: str = Field(..., description="'add' for new content or 'update' for modifications")
    section: str = Field(
        ..., description="Target section within the artifact (e.g., 'Risks', 'Action Items')"
    )
    proposed_text: str = Field(..., description="The suggested Markdown content to add or update")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0")
    reasoning: str = Field(..., description="Explanation of why this suggestion was generated")


class AnalysisItem(BaseModel):
    """A single observation or recommendation from Analyze & Advise mode."""

    category: str = Field(..., description="'observation', 'recommendation', 'gap', or 'strength'")
    title: str = Field(..., description="Brief headline for this item")
    detail: str = Field(..., description="Full explanation with context")
    priority: str = Field("medium", description="'high', 'medium', or 'low'")
    artifact_type: Optional[str] = Field(
        None, description="Which artifact this relates to, if applicable"
    )


class ArtifactSyncRequest(BaseModel):
    """Request body for the artifact sync endpoint."""

    text: str = Field(
        ..., description="Raw user input (meeting notes, transcript, or project update)"
    )
    project_id: str = Field("default", description="Project scope for the sync operation")
    mode: str = Field(
        "extract",
        description="'extract' for Extract & Route, 'analyze' for Analyze & Advise, "
        "'log_session' for Log Session Bridge",
    )


class LPDUpdateClassification(BaseModel):
    """Classification result from the content quality gate."""

    classification: str = Field(
        ...,
        description="'new', 'duplicate', 'update', or 'contradiction'",
    )
    reason: str = Field("", description="Brief explanation of why this classification was assigned")


class LPDUpdate(BaseModel):
    """A direct update to an LPD section from log_session mode."""

    section: str = Field(..., description="LPD section name (e.g., 'Risks', 'Decisions')")
    content: str = Field(..., description="Content to append to the section")
    source: str = Field("log_session", description="Where this update came from")
    classification: Optional[LPDUpdateClassification] = Field(
        None, description="Quality gate classification (None if gate was not active)"
    )


class ArtifactSyncResponse(BaseModel):
    """Response from the artifact sync endpoint."""

    suggestions: list[Suggestion] = Field(
        default_factory=list, description="List of suggested artifact updates (extract mode)"
    )
    analysis: list[AnalysisItem] = Field(
        default_factory=list, description="List of analysis items (analyze mode)"
    )
    analysis_summary: Optional[str] = Field(
        None, description="Brief overall assessment (analyze mode only)"
    )
    lpd_updates: list[LPDUpdate] = Field(
        default_factory=list,
        description="Direct LPD updates applied (log_session mode)",
    )
    session_summary: Optional[str] = Field(
        None, description="Session summary text (log_session mode)"
    )
    input_type: str = Field(
        ...,
        description="Classified input type: 'meeting_notes', 'status_update', 'transcript', "
        "or 'general_text'",
    )
    session_id: str = Field(..., description="Unique session ID for this sync operation")
    pii_detected: int = Field(
        ..., description="Number of PII entities found and anonymized in the input"
    )
    mode: str = Field("extract", description="Which mode was used")
    content_gate_active: bool = Field(
        True, description="Whether the content quality gate was applied to LPD updates"
    )


# --- Intake (Task 26) ---


class IntakeFile(BaseModel):
    """A single file submitted for intake processing."""

    filename: str = Field(..., description="Name of the source file")
    content: str = Field(..., description="Text content of the file")


class IntakeExtraction(BaseModel):
    """Entities extracted from a single intake file by the LLM."""

    source_file: str = Field(..., description="Filename this extraction came from")
    overview: str = Field("", description="Project overview information found")
    stakeholders: str = Field("", description="Stakeholders identified")
    timeline: str = Field("", description="Timeline and milestones found")
    risks: str = Field("", description="Risks identified")
    decisions: str = Field("", description="Decisions found")
    open_questions: str = Field("", description="Open questions or action items found")


# Maps IntakeExtraction field names to LPD section names
INTAKE_FIELD_TO_LPD_SECTION: dict[str, str] = {
    "overview": "Overview",
    "stakeholders": "Stakeholders",
    "timeline": "Timeline & Milestones",
    "risks": "Risks",
    "decisions": "Decisions",
    "open_questions": "Open Questions",
}


class IntakeConflict(BaseModel):
    """A conflict between existing LPD content and proposed intake content."""

    section: str = Field(..., description="LPD section name where conflict was detected")
    existing: str = Field(..., description="Current content in the LPD section")
    proposed: str = Field(..., description="Proposed content from the intake file")
    source_file: str = Field(..., description="Filename that proposed the conflicting content")


class IntakeDraft(BaseModel):
    """Preview of what the intake would add to the LPD."""

    extractions: list[IntakeExtraction] = Field(
        default_factory=list, description="Per-file extraction results"
    )
    proposed_sections: dict[str, str] = Field(
        default_factory=dict,
        description="Combined proposed content per LPD section name",
    )
    conflicts: list[IntakeConflict] = Field(
        default_factory=list, description="Detected conflicts with existing LPD content"
    )
    pii_detected: int = Field(0, description="Total PII entities anonymized across all files")


class IntakePreviewRequest(BaseModel):
    """Request body for the intake preview endpoint."""

    files: list[IntakeFile] = Field(..., description="Files to process for intake")


class IntakeApplyRequest(BaseModel):
    """Request body for the intake apply endpoint."""

    proposed_sections: dict[str, str] = Field(
        ..., description="Section name → proposed content (from the preview draft)"
    )
    approved_sections: list[str] = Field(
        ..., description="List of section names the user approved for application"
    )


class IntakeApplyResponse(BaseModel):
    """Response from the intake apply endpoint."""

    sections_updated: list[str] = Field(
        default_factory=list, description="Sections that were updated"
    )
    sections_skipped: list[str] = Field(
        default_factory=list, description="Sections that were not approved"
    )


# --- Conversational API (D46 — design only, implementation Phase 2B/3) ---


class ConversationMessage(BaseModel):
    """A single message in a conversation."""

    message_id: str = Field(..., description="Unique message identifier (UUID)")
    conversation_id: str = Field(..., description="Parent conversation ID")
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text content")
    suggestions: list[Suggestion] = Field(
        default_factory=list, description="Structured suggestions from assistant messages"
    )
    lpd_sections_referenced: list[str] = Field(
        default_factory=list, description="LPD sections referenced in this message"
    )
    timestamp: datetime = Field(..., description="When this message was created")
    token_count: int = Field(0, description="Token count for this message")


class ConversationSession(BaseModel):
    """A multi-turn conversation session."""

    conversation_id: str = Field(..., description="Unique conversation identifier (UUID)")
    project_id: str = Field(..., description="Parent project ID")
    title: Optional[str] = Field(None, description="Auto-generated conversation title")
    created_at: datetime = Field(..., description="When the conversation started")
    last_message_at: datetime = Field(..., description="When the last message was sent")
    message_count: int = Field(0, description="Number of messages in this conversation")


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""

    message: str = Field(..., description="User's message text")
    conversation_id: Optional[str] = Field(
        None, description="Existing conversation ID (null to start new)"
    )
    include_lpd_context: bool = Field(
        True, description="Whether to inject LPD context into the prompt"
    )
    include_artifacts: bool = Field(
        False, description="Whether to include artifact content in the prompt"
    )


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""

    conversation_id: str = Field(..., description="Conversation ID (new or existing)")
    message_id: str = Field(..., description="ID of the assistant's response message")
    response: str = Field(..., description="Assistant's response text")
    suggestions: list[Suggestion] = Field(
        default_factory=list, description="Structured suggestions extracted from the response"
    )
    lpd_sections_referenced: list[str] = Field(
        default_factory=list, description="LPD sections referenced in the response"
    )
    session_id: str = Field(..., description="Sync session ID for tracking")
    pii_detected: int = Field(0, description="Number of PII entities anonymized")
    token_count: int = Field(0, description="Total tokens used for this exchange")
