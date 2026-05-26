from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=800)
    user_id: str = Field(default="anonymous", min_length=1, max_length=80)


class ChatReply(BaseModel):
    reply: str
    message_id: int
    user_id: str
    source: Literal["groq", "knowledge_base", "knowledge_fallback"]
    intent: str
    confidence: float
    language: Literal["en", "ru"]
    provider_attempted: Literal["groq", "none"]
    provider_status: Literal["ok", "quota_exceeded", "request_failed", "parse_failed", "not_attempted"]
    fallback_reason: str | None = None


class HealthResponse(BaseModel):
    status: Literal["healthy", "running"]
    service: str
    version: str
    ai_provider: str


class ChatHistoryResponse(BaseModel):
    user_id: str
    messages: list[dict[str, str]]
    count: int


class ClearHistoryResponse(BaseModel):
    status: Literal["cleared"]
    user_id: str