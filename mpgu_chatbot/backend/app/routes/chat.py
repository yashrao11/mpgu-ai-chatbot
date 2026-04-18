import random

from fastapi import APIRouter, HTTPException

from app.schemas import ChatMessage, ChatReply
from app.services.chat_engine import chat_engine

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatReply)
async def chat_endpoint(msg: ChatMessage):
    user_message = msg.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    result = chat_engine.process(user_message, msg.user_id)
    return ChatReply(
        reply=result.reply,
        message_id=random.randint(1000, 9999),
        user_id=msg.user_id,
        source=result.source,
        intent=result.intent,
        confidence=round(result.confidence, 2),
        language=result.language,
    )


@router.get("/chat/history/{user_id}")
async def chat_history(user_id: str):
    return {
        "user_id": user_id,
        "messages": chat_engine.history(user_id),
        "count": len(chat_engine.history(user_id)),
    }


@router.delete("/chat/history/{user_id}")
async def clear_chat_history(user_id: str):
    chat_engine.reset(user_id)
    return {"status": "cleared", "user_id": user_id}
