<<<<<<< ours
=======
from typing import Literal

>>>>>>> theirs
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=800)
    user_id: str = Field(default="anonymous", min_length=1, max_length=80)


class ChatReply(BaseModel):
    reply: str
    message_id: int
    user_id: str
<<<<<<< ours
    source: str
    intent: str
    confidence: float
    language: str


class HealthResponse(BaseModel):
    status: str
=======
    source: Literal["gemini", "knowledge_base", "knowledge_fallback"]
    intent: str
    confidence: float
    language: Literal["en", "ru"]
    provider_attempted: Literal["gemini", "none"]
    provider_status: Literal["ok", "quota_exceeded", "request_failed", "parse_failed", "not_attempted"]
    fallback_reason: str | None = None


class HealthResponse(BaseModel):
    status: Literal["healthy", "running"]
>>>>>>> theirs
    service: str
    version: str
    ai_provider: str


<<<<<<< ours
class ChatHistoryEntry(BaseModel):
    role: str
    content: str


class ChatHistoryResponse(BaseModel):
    user_id: str
    messages: list[ChatHistoryEntry]
=======
class ChatHistoryResponse(BaseModel):
    user_id: str
    messages: list[dict[str, str]]
>>>>>>> theirs
    count: int


class ClearHistoryResponse(BaseModel):
<<<<<<< ours
    status: str
=======
    status: Literal["cleared"]
>>>>>>> theirs
    user_id: str
