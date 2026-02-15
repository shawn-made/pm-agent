"""VPMA Pydantic Models — Data shapes for all database tables."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

# --- Projects ---


class ProjectCreate(BaseModel):
    project_id: Optional[str] = None
    project_name: str
    landscape_config: str = "{}"


class Project(BaseModel):
    project_id: str
    project_name: str
    created_at: datetime
    landscape_config: str


# --- Artifacts ---


class ArtifactCreate(BaseModel):
    artifact_id: Optional[str] = None
    project_id: str
    artifact_type: str  # "RAID Log", "Status Report", "Meeting Notes"
    file_path: str


class Artifact(BaseModel):
    artifact_id: str
    project_id: str
    artifact_type: str
    file_path: str
    last_updated: datetime


# --- Artifact Versions ---


class ArtifactVersionCreate(BaseModel):
    version_id: Optional[str] = None
    artifact_id: str
    version_number: int
    content_snapshot: Optional[str] = None
    session_id: Optional[str] = None


class ArtifactVersion(BaseModel):
    version_id: str
    artifact_id: str
    version_number: int
    content_snapshot: Optional[str]
    created_at: datetime
    session_id: Optional[str]


# --- Sessions ---


class SessionCreate(BaseModel):
    session_id: Optional[str] = None
    project_id: str
    tab_used: Optional[str] = None
    user_input: Optional[str] = None
    agent_output: Optional[str] = None
    persona_used: Optional[str] = None
    tokens_used: int = 0
    llm_model: Optional[str] = None


class Session(BaseModel):
    session_id: str
    project_id: str
    timestamp: datetime
    tab_used: Optional[str]
    user_input: Optional[str]
    agent_output: Optional[str]
    persona_used: Optional[str]
    tokens_used: int
    llm_model: Optional[str]


# --- PII Vault ---


class PIIMapping(BaseModel):
    token: str
    original_value: str
    entity_type: str
    first_seen: Optional[datetime] = None


# --- Settings ---


class Setting(BaseModel):
    key: str
    value: str
    updated_at: Optional[datetime] = None


# --- Artifact Sync ---


class Suggestion(BaseModel):
    """A single suggestion for updating a PM artifact."""

    artifact_type: str  # "RAID Log", "Status Report", "Meeting Notes"
    change_type: str  # "add" or "update"
    section: str  # e.g., "Risks", "Action Items", "Accomplishments"
    proposed_text: str  # The suggested content
    confidence: float  # 0.0-1.0
    reasoning: str  # Why this suggestion was made


class ArtifactSyncRequest(BaseModel):
    """Request body for the artifact sync endpoint."""

    text: str
    project_id: str = "default"


class ArtifactSyncResponse(BaseModel):
    """Response from the artifact sync endpoint."""

    suggestions: list[Suggestion]
    input_type: str  # "meeting_notes", "status_update", "transcript", "general_text"
    session_id: str
    pii_detected: int  # Number of PII entities found and anonymized
