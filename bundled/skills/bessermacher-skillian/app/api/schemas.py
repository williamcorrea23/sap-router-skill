"""API request and response schemas."""

from enum import StrEnum

from pydantic import BaseModel, Field

# Health & Info


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    environment: str
    llm_provider: str
    llm_model: str
    skills_count: int
    tools_count: int
    knowledge_documents: int
    business_db_healthy: bool | None


class SkillInfo(BaseModel):
    """Skill information."""

    name: str
    description: str
    tools: list[dict]
    knowledge_paths: list[str]


class SkillsResponse(BaseModel):
    """List of skills response."""

    skills: list[SkillInfo]


# Chat


class ChatRequest(BaseModel):
    """Chat request body."""

    message: str = Field(min_length=1, max_length=10000)
    session_id: str | None = Field(
        default=None,
        description="Optional session ID for conversation continuity",
    )


class ToolCall(BaseModel):
    """Tool call information."""

    tool: str
    args: dict
    result: str
    duration_seconds: float | None = None


class ChatResponse(BaseModel):
    """Chat response body."""

    response: str
    tool_calls: list[ToolCall] = []
    session_id: str | None = None
    finished: bool = True
    timing: dict | None = None


# Knowledge/RAG


class SearchRequest(BaseModel):
    """Knowledge search request."""

    query: str = Field(min_length=1, max_length=1000)
    k: int = Field(default=4, ge=1, le=20)
    skill_filter: str | None = None


class SearchResult(BaseModel):
    """Single search result."""

    content: str
    source: str
    skill: str
    score: float | None = None


class SearchResponse(BaseModel):
    """Knowledge search response."""

    results: list[SearchResult]
    query: str
    count: int


class IngestResponse(BaseModel):
    """Knowledge ingestion response."""

    status: str
    chunks_ingested: int
    by_skill: dict[str, int]


# Sessions


class SessionInfo(BaseModel):
    """Session information."""

    session_id: str
    message_count: int
    created_at: str


class SessionListResponse(BaseModel):
    """List of sessions."""

    sessions: list[SessionInfo]


# Errors


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: str | None = None
    code: str | None = None


# Streaming


class StreamEventType(StrEnum):
    """Types of events emitted during streaming."""

    THINKING = "thinking"
    LLM_RESPONSE = "llm_response"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    TEXT_DELTA = "text_delta"
    DONE = "done"
    ERROR = "error"
