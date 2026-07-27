from pydantic import BaseModel, Field


class ResolveTicketRequest(BaseModel):
    tenantId: str = Field(default="default-tenant", description="Tenant identifier")
    text: str = Field(default="", description="Ticket body or description")
    imageBase64: str | None = Field(default=None, description="Base64 encoded screenshot image")
    logSnippet: str | None = Field(default=None, description="Log excerpt snippet")
    repoUrl: str | None = Field(default=None, description="Optional GitHub repo URL for context")


class CacheDetail(BaseModel):
    memory_id: str
    similarity: float
    tokens_saved: bool = True


class DeepResolutionDetail(BaseModel):
    poll_path: str
    note: str


class ResolveTicketResponse(BaseModel):
    ticket_id: str | None = None
    latency_ms: int
    classification: str
    confidence: float
    suggested_steps: list[str]
    has_screenshot: bool = False
    ocr_text: str | None = None
    resolution_mode: str  # "cache_hit" | "ml_complete" | "ml_needs_deep"
    cache: CacheDetail | None = None
    deep_resolution: DeepResolutionDetail | None = None


class TicketStatusResponse(BaseModel):
    id: str
    tenant_id: str
    status: str  # "pending" | "deep_resolution_running" | "deep_resolution_finished" | "deep_resolution_error"
    classification: str
    confidence: float
    suggested_steps: list[str]
    deep_result_text: str | None = None
    deep_error: str | None = None
    created_at: str
    updated_at: str


class StoreAnswerRequest(BaseModel):
    question_text: str
    classification: str
    suggested_steps: list[str] = Field(default_factory=list)
    deep_answer: str | None = None


class MemoryStatsResponse(BaseModel):
    count: int
    storage_type: str = "pgvector"
