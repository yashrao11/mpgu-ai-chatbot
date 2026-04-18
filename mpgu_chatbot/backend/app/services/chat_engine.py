import json
import logging
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

    def _openai_response(self, message: str, context: list[dict[str, str]]) -> str | None:
        if not Config.OPENAI_API_KEY:
            return None

        context_window = context[-6:]
        input_messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "You are MPGU Smart Assistant. Be concise, practical, and answer in the same language "
                    "as the user. Prefer step-by-step instructions for academic workflows."
                ),
            }
        ]
        for turn in context_window:
            role = "assistant" if turn["role"] == "assistant" else "user"
            input_messages.append({"role": role, "content": turn["text"]})
        input_messages.append({"role": "user", "content": message})

        headers = {
            "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": Config.OPENAI_MODEL,
            "input": input_messages,
            "max_output_tokens": 260,
        }

        try:
            response = requests.post(
                Config.OPENAI_API_URL,
                headers=headers,
                json=payload,
                timeout=Config.REQUEST_TIMEOUT_SECONDS,
            )
            if response.status_code != 200:
                logger.warning("OpenAI API returned %s", response.status_code)
                return None

            body = response.json()
            if isinstance(body, dict):
                if body.get("output_text"):
                    return str(body["output_text"]).strip() or None

                output_items = body.get("output", [])
                for item in output_items:
                    if item.get("type") == "message":
                        for part in item.get("content", []):
                            if part.get("type") in {"output_text", "text"} and part.get("text"):
                                return str(part["text"]).strip() or None
            return None
        except requests.RequestException:
            logger.exception("OpenAI request failed")
            return None
        except (ValueError, KeyError, TypeError):
            logger.exception("OpenAI response parse failed")
            return None

    def _gemini_response(self, message: str, context: list[dict[str, str]]) -> str | None:
        if not Config.GEMINI_API_KEY:
            return None

        recent_turns = context[-6:]
        conversation_lines = []
        for turn in recent_turns:
            prefix = "Assistant" if turn["role"] == "assistant" else "User"
            conversation_lines.append(f"{prefix}: {turn['text']}")
        conversation_lines.append(f"User: {message}")

        prompt = (
            "You are MPGU Smart Assistant. Keep answers clear, concise, and practical. "
            "Respond in the same language as the user's last question.\n\n"
            "Conversation:\n"
            + "\n".join(conversation_lines)
        )

        url = Config.GEMINI_API_URL_TEMPLATE.format(
            model=Config.GEMINI_MODEL,
            api_key=Config.GEMINI_API_KEY,
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 260
            }
        }

        try:
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=Config.REQUEST_TIMEOUT_SECONDS,
            )
            if response.status_code != 200:
                logger.warning("Gemini API returned %s", response.status_code)
                return None

            body = response.json()
            candidates = body.get("candidates", [])
            if not candidates:
                return None
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                return None
            text = parts[0].get("text", "")
            return str(text).strip() or None
        except requests.RequestException:
            logger.exception("Gemini request failed")
            return None
        except (ValueError, KeyError, TypeError):
            logger.exception("Gemini response parse failed")
            return None

    def process(self, message: str, user_id: str) -> ChatResult:
        language = self.detect_language(message)
        session = self.sessions.setdefault(user_id, [])

        ai_reply = None
        source = ""

        if Config.AI_PROVIDER in {"auto", "gemini"}:
            ai_reply = self._gemini_response(message, session)
            if ai_reply:
                source = "gemini"

        if not ai_reply and Config.AI_PROVIDER in {"auto", "openai"}:
            ai_reply = self._openai_response(message, session)
            if ai_reply:
                source = "openai"

        if not ai_reply and Config.AI_PROVIDER in {"auto", "huggingface"}:
            ai_reply = self._hugging_face_response(message, language, session)
            if ai_reply:
                source = "hugging_face"

        if ai_reply:
            result = ChatResult(
                reply=ai_reply,
                source=source,
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
