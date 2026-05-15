from pydantic import BaseModel, Field


class ResolveTicketRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    text: str = ""
    image_base64: str | None = None
    log_snippet: str | None = None


class StoreAnswerRequest(BaseModel):
    question_text: str = Field(min_length=1)
    classification: str = "MANUAL"
    suggested_steps: list[str] = Field(default_factory=list)
    deep_answer: str | None = None
