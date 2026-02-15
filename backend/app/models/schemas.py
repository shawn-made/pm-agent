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
    file_path: str = Field(..., description="Path to the Markdown file in ~/VPMA/artifacts/")


class Artifact(BaseModel):
    artifact_id: str = Field(..., description="Unique artifact identifier (UUID)")
    project_id: str = Field(..., description="Parent project ID")
    artifact_type: str = Field(
        ..., description="Artifact type: 'RAID Log', 'Status Report', or 'Meeting Notes'"
    )
    file_path: str = Field(..., description="Path to the Markdown file in ~/VPMA/artifacts/")
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


class ArtifactSyncRequest(BaseModel):
    """Request body for the artifact sync endpoint."""

    text: str = Field(
        ..., description="Raw user input (meeting notes, transcript, or project update)"
    )
    project_id: str = Field("default", description="Project scope for the sync operation")


class ArtifactSyncResponse(BaseModel):
    """Response from the artifact sync endpoint."""

    suggestions: list[Suggestion] = Field(
        ..., description="List of suggested artifact updates"
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
