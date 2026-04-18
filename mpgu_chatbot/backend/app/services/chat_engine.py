import json
import logging
import random
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import requests

from app.config import Config

logger = logging.getLogger(__name__)


@dataclass
class ChatResult:
    reply: str
    source: str
    intent: str
    confidence: float
    language: str


class ChatEngine:
    def __init__(self) -> None:
        self.knowledge_base = self._load_knowledge_base()
        self.sessions: dict[str, list[dict[str, str]]] = {}

    @staticmethod
    def _load_knowledge_base() -> dict[str, Any]:
        kb_path = Path(__file__).resolve().parents[2] / "data" / "knowledge_base.json"
        with kb_path.open("r", encoding="utf-8") as fp:
            return json.load(fp)

    @staticmethod
    def detect_language(text: str) -> str:
        russian_chars = len(re.findall(r"[а-яА-ЯёЁ]", text))
        return "ru" if russian_chars > max(1, len(text)) * 0.2 else "en"

    def _score_intent(self, message: str, keywords: list[str]) -> float:
        message_l = message.lower()
        token_hits = sum(1 for kw in keywords if kw in message_l)
        max_similarity = max((SequenceMatcher(None, kw, message_l).ratio() for kw in keywords), default=0.0)
        return token_hits + max_similarity

    def _match_intent(self, message: str) -> tuple[str, float]:
        best_intent = "fallback"
        best_score = 0.0

        for intent in self.knowledge_base["intents"]:
            score = self._score_intent(message, intent["keywords"])
            if score > best_score:
                best_score = score
                best_intent = intent["id"]

        return best_intent, best_score

    def _knowledge_response(self, message: str, language: str) -> ChatResult:
        intent_id, score = self._match_intent(message)

        if intent_id == "fallback" or score < 0.9:
            fallback = self.knowledge_base["fallback"][language]
            return ChatResult(reply=fallback, source="knowledge_fallback", intent="fallback", confidence=0.35, language=language)

        intent_obj = next(item for item in self.knowledge_base["intents"] if item["id"] == intent_id)
        field = "response_ru" if language == "ru" else "response_en"

        return ChatResult(
            reply=intent_obj[field],
            source="knowledge_base",
            intent=intent_id,
            confidence=min(0.95, 0.45 + score / 4),
            language=language,
        )

    def _hugging_face_response(self, message: str, language: str, context: list[dict[str, str]]) -> str | None:
        if not Config.HUGGING_FACE_TOKEN:
            return None

        context_window = "\n".join([f"{turn['role']}: {turn['text']}" for turn in context[-4:]])
        system_prompt = (
            "You are MPGU Smart Assistant. Provide concise, accurate and structured academic support responses. "
            "Always answer in the same language as the user."
        )
        prompt = (
            f"{system_prompt}\n\n"
            f"Conversation so far:\n{context_window}\n\n"
            f"User question: {message}\n"
            "Assistant answer:"
        )

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 220,
                "temperature": 0.4,
                "return_full_text": False
            }
        }
        headers = {
            "Authorization": f"Bearer {Config.HUGGING_FACE_TOKEN}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                Config.HUGGING_FACE_API_URL,
                headers=headers,
                json=payload,
                timeout=Config.REQUEST_TIMEOUT_SECONDS,
            )
            if response.status_code != 200:
                logger.warning("Hugging Face API returned %s", response.status_code)
                return None

            body = response.json()
            if isinstance(body, list) and body:
                return body[0].get("generated_text", "").strip() or None
            if isinstance(body, dict):
                return body.get("generated_text", "").strip() or None
            return None
        except requests.RequestException:
            logger.exception("Hugging Face request failed")
            return None
        except (ValueError, KeyError, TypeError):
            logger.exception("Hugging Face response parse failed")
            return None

    def process(self, message: str, user_id: str) -> ChatResult:
        language = self.detect_language(message)
        session = self.sessions.setdefault(user_id, [])

        ai_reply = self._hugging_face_response(message, language, session)
        if ai_reply:
            result = ChatResult(
                reply=ai_reply,
                source="hugging_face",
                intent="ai_generated",
                confidence=0.9,
                language=language,
            )
        else:
            result = self._knowledge_response(message, language)

        session.append({"role": "user", "text": message})
        session.append({"role": "assistant", "text": result.reply})
        if len(session) > 20:
            self.sessions[user_id] = session[-20:]

        return result

    def history(self, user_id: str) -> list[dict[str, str]]:
        return self.sessions.get(user_id, [])

    def reset(self, user_id: str) -> None:
        self.sessions.pop(user_id, None)


chat_engine = ChatEngine()
