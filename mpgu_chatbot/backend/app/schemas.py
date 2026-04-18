from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=800)
    user_id: str = Field(default="anonymous", min_length=1, max_length=80)


class ChatReply(BaseModel):
    reply: str
    message_id: int
    user_id: str
    source: str
    intent: str
    confidence: float
    language: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    ai_provider: str
