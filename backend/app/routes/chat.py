from dataclasses import asdict
from fastapi import APIRouter, HTTPException

from app.schemas import ChatHistoryResponse, ChatMessage, ChatReply, ClearHistoryResponse
from app.services.chat_engine import chat_engine

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatReply)
async def chat_endpoint(msg: ChatMessage):
    user_message = msg.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    result = chat_engine.process(user_message, msg.user_id)
    payload = asdict(result)
    payload["confidence"] = round(payload["confidence"], 2)
    return ChatReply(**payload)


@router.get("/chat/history/{user_id}", response_model=ChatHistoryResponse)
async def chat_history(user_id: str):
    history = chat_engine.history(user_id)
    return {
        "user_id": user_id,
        "messages": history,
        "count": len(history),
    }


@router.delete("/chat/history/{user_id}", response_model=ClearHistoryResponse)
async def clear_chat_history(user_id: str):
    chat_engine.reset(user_id)
    return {"status": "cleared", "user_id": user_id}