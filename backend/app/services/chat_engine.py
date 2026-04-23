import json
import logging
<<<<<<< ours
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import requests

from ..config import Config

logger = logging.getLogger("mpgu_chatbot.chat_engine")
=======
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from app.config import Config

logger = logging.getLogger(__name__)
>>>>>>> theirs


@dataclass
class ChatResult:
    reply: str
<<<<<<< ours
    message_id: int
    user_id: str
=======
>>>>>>> theirs
    source: str
    intent: str
    confidence: float
    language: str
<<<<<<< ours


@dataclass
class IntentMatch:
    intent_id: str
    confidence: float
    hits: int
    strong_match: bool
=======
    provider_attempted: str
    provider_status: str
    fallback_reason: str | None = None
>>>>>>> theirs


class ChatEngine:
    def __init__(self) -> None:
        self.knowledge_base = self._load_knowledge_base()
        self.sessions: dict[str, list[dict[str, str]]] = {}

    @staticmethod
<<<<<<< ours
    def _coerce_responses(value: Any) -> list[str]:
        if isinstance(value, str):
            cleaned = value.strip()
            return [cleaned] if cleaned else []
        if isinstance(value, list):
            return [item.strip() for item in value if isinstance(item, str) and item.strip()]
        return []

    def _normalize_knowledge_base(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        normalized_intents: list[dict[str, Any]] = []
        for intent in raw_data.get("intents", []):
            responses = intent.get("responses", {})
            use_nested_responses = isinstance(responses, dict) and bool(responses)
            normalized_intents.append(
                {
                    "id": intent.get("id", "fallback"),
                    "keywords": intent.get("keywords", []),
                    "responses": {
                        "en": self._coerce_responses(
                            responses.get("en") if use_nested_responses else intent.get("response_en")
                        ),
                        "ru": self._coerce_responses(
                            responses.get("ru") if use_nested_responses else intent.get("response_ru")
                        ),
                    },
                }
            )

        fallback = raw_data.get("fallback", {})
        normalized_fallback = {
            "en": self._coerce_responses(fallback.get("en")),
            "ru": self._coerce_responses(fallback.get("ru")),
        }

        return {
            "intents": normalized_intents,
            "fallback": normalized_fallback,
        }

    def _load_knowledge_base(self) -> dict[str, Any]:
        kb_path = Path(__file__).resolve().parents[2] / "data" / "knowledge_base.json"
        with kb_path.open("r", encoding="utf-8") as fp:
            raw_data = json.load(fp)
        return self._normalize_knowledge_base(raw_data)
=======
    def _load_knowledge_base() -> dict[str, Any]:
        kb_path = Path(__file__).resolve().parents[2] / "data" / "knowledge_base.json"
        with kb_path.open("r", encoding="utf-8") as fp:
            return json.load(fp)
>>>>>>> theirs

    @staticmethod
    def detect_language(text: str) -> str:
        russian_chars = len(re.findall(r"[а-яА-ЯёЁ]", text))
        return "ru" if russian_chars > max(1, len(text)) * 0.2 else "en"

    @staticmethod
    def _tokenize(text: str) -> list[str]:
<<<<<<< ours
        return re.findall(r"\b\w+\b", text.lower())

    def _keyword_hits(self, message: str, intent_id: str, keywords: list[str]) -> tuple[int, int]:
        message_l = message.lower()
        words = self._tokenize(message_l)
        word_set = set(words)

        hits = 0
        strong_hits = 0

        for keyword in keywords:
            keyword_l = keyword.lower().strip()
            if not keyword_l:
                continue

            if " " in keyword_l:
                if keyword_l in message_l:
                    hits += 1
                    strong_hits += 1
                continue

            exact_word_match = keyword_l in word_set
            prefix_match = any(word.startswith(keyword_l) for word in words) if len(keyword_l) >= 4 else False

            if intent_id == "greeting":
                if exact_word_match:
                    hits += 1
                    strong_hits += 1
                continue

            if exact_word_match:
                hits += 1
                strong_hits += 1
            elif prefix_match:
                hits += 1

        return hits, strong_hits

    def _match_intent(self, message: str) -> IntentMatch:
        words = self._tokenize(message)
        best_match = IntentMatch(intent_id="fallback", confidence=0.0, hits=0, strong_match=False)

        for intent in self.knowledge_base.get("intents", []):
            intent_id = intent.get("id", "fallback")
            hits, strong_hits = self._keyword_hits(message, intent_id, intent.get("keywords", []))
            if hits == 0:
                continue

            if intent_id == "greeting":
                confidence = 0.25 + (0.2 * strong_hits)
                strong_match = strong_hits > 0 and len(words) <= 5
            else:
                confidence = min(0.95, 0.4 + (0.25 * strong_hits) + (0.1 * max(0, hits - strong_hits)))
                strong_match = strong_hits > 0

            current = IntentMatch(
                intent_id=intent_id,
                confidence=confidence,
                hits=hits,
                strong_match=strong_match,
            )
            if (
                current.confidence > best_match.confidence
                or (
                    current.confidence == best_match.confidence
                    and current.hits > best_match.hits
                )
            ):
                best_match = current

        if best_match.intent_id == "greeting" and not best_match.strong_match:
            return IntentMatch(intent_id="fallback", confidence=0.0, hits=0, strong_match=False)

        return best_match

    @staticmethod
    def _is_open_ended_question(message: str) -> bool:
        lowered = message.lower().strip()
        starters = (
            "explain",
            "what is",
            "what's",
            "tell me",
            "describe",
            "how does",
            "why does",
            "compare",
        )
        return lowered.startswith(starters)

    def _should_use_knowledge_base_first(self, message: str, intent_match: IntentMatch) -> bool:
        if intent_match.intent_id == "fallback":
            return False

        if intent_match.intent_id == "greeting":
            return intent_match.strong_match

        if self._is_open_ended_question(message):
            return False

        return intent_match.strong_match and intent_match.confidence >= 0.65

    def _pick_localized_reply(self, responses: dict[str, list[str]], language: str) -> str | None:
        candidates = responses.get(language) or responses.get("en") or []
        return random.choice(candidates) if candidates else None

    def _get_kb_reply(self, intent_id: str, language: str) -> str:
        for intent in self.knowledge_base.get("intents", []):
            if intent.get("id") == intent_id:
                reply = self._pick_localized_reply(intent.get("responses", {}), language)
                if reply:
                    return reply

        fallback = self.knowledge_base.get("fallback", {})
        reply = self._pick_localized_reply(fallback, language)
        if reply:
            return reply

        return "I can help with admissions, courses, schedules, tutors, exams, and contacts."

    @staticmethod
    def _build_system_prompt() -> str:
        return (
            "You are MPGU Smart Assistant, a university support chatbot for Moscow Pedagogical "
            "State University. Answer clearly, briefly, and helpfully. If the user asks a general "
            "question unrelated to MPGU, still answer helpfully in simple language. "
            "If the user writes in Russian, answer in Russian. If in English, answer in English."
        )

    @staticmethod
    def _safe_preview(value: Any, limit: int = 400) -> str:
        if isinstance(value, str):
            text = value
        else:
            try:
                text = json.dumps(value, ensure_ascii=False)
            except (TypeError, ValueError):
                text = str(value)
        compact = re.sub(r"\s+", " ", text).strip()
        return compact[:limit]

    @staticmethod
    def _extract_gemini_error(data: Any) -> str:
        if not isinstance(data, dict):
            return "non-json error response"

        error = data.get("error")
        if not isinstance(error, dict):
            return "unknown gemini error"

        status = error.get("status", "UNKNOWN_STATUS")
        message = error.get("message", "No error message returned")
        return f"{status}: {message}"

    @staticmethod
    def _extract_gemini_text(data: Any) -> str | None:
        if not isinstance(data, dict):
            return None

        candidates = data.get("candidates", [])
        if not candidates:
            return None

        parts = candidates[0].get("content", {}).get("parts", [])
        text_parts = [part.get("text", "").strip() for part in parts if part.get("text")]
        final_text = "\n".join(part for part in text_parts if part)
        return final_text or None

    @staticmethod
    def _build_gemini_url() -> str:
        template = Config.GEMINI_API_URL_TEMPLATE
        if "{api_key}" in template:
            return template.format(model=Config.GEMINI_MODEL, api_key=Config.GEMINI_API_KEY)
        return template.format(model=Config.GEMINI_MODEL)

    def _try_gemini(self, message: str) -> str | None:
        if not Config.GEMINI_API_KEY:
            logger.info("Gemini skipped | reason=no_api_key")
            return None

        url = self._build_gemini_url()
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": Config.GEMINI_API_KEY,
        }
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": f"{self._build_system_prompt()}\n\nUser message: {message}"
                        }
                    ]
                }
            ]
        }

        try:
            logger.info(
                "Gemini request attempt | model=%s | prompt_chars=%s",
                Config.GEMINI_MODEL,
                len(message),
            )
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=Config.REQUEST_TIMEOUT_SECONDS,
            )
        except requests.Timeout:
            logger.warning(
                "Gemini request failed | reason=timeout | timeout_seconds=%s",
                Config.REQUEST_TIMEOUT_SECONDS,
            )
            return None
        except requests.RequestException as exc:
            logger.warning("Gemini request failed | reason=request_exception | error=%s", exc)
            return None

        logger.info("Gemini response received | status_code=%s", response.status_code)

        try:
            data = response.json()
        except ValueError:
            logger.warning(
                "Gemini response parse failed | status_code=%s | body_preview=%s",
                response.status_code,
                self._safe_preview(response.text),
            )
            return None

        if not response.ok:
            logger.warning(
                "Gemini request failed | status_code=%s | error=%s",
                response.status_code,
                self._extract_gemini_error(data),
            )
            return None

        final_text = self._extract_gemini_text(data)
        if not final_text:
            logger.warning(
                "Gemini response parse failed | status_code=%s | body_preview=%s",
                response.status_code,
                self._safe_preview(data),
            )
            return None

        logger.info("Gemini response parsed successfully | chars=%s", len(final_text))
        return final_text

    def _try_openai(self, message: str) -> str | None:
        if not Config.OPENAI_API_KEY:
            return None

        payload = {
            "model": Config.OPENAI_MODEL,
            "input": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": self._build_system_prompt(),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": message,
                        }
                    ],
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                Config.OPENAI_API_URL,
                headers=headers,
                json=payload,
                timeout=Config.REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError):
            return None

        output_text = data.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        for item in data.get("output", []):
            for content in item.get("content", []):
                text = content.get("text")
                if isinstance(text, str) and text.strip():
                    return text.strip()
        return None

    def _try_huggingface(self, message: str) -> str | None:
        if not Config.HUGGING_FACE_TOKEN:
            return None

        headers = {
            "Authorization": f"Bearer {Config.HUGGING_FACE_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": f"{self._build_system_prompt()}\n\nUser message: {message}",
            "options": {"wait_for_model": True},
        }

        try:
            response = requests.post(
                Config.HUGGING_FACE_API_URL,
                headers=headers,
                json=payload,
                timeout=Config.REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError):
            return None

        if isinstance(data, list):
            for item in data:
                text = item.get("generated_text")
                if isinstance(text, str) and text.strip():
                    return text.strip()
        if isinstance(data, dict):
            text = data.get("generated_text")
            if isinstance(text, str) and text.strip():
                return text.strip()
        return None

    def _provider_attempts(self) -> list[tuple[str, Callable[[str], str | None]]]:
        providers: dict[str, Callable[[str], str | None]] = {
            "gemini": self._try_gemini,
            "openai": self._try_openai,
            "huggingface": self._try_huggingface,
        }

        if Config.AI_PROVIDER == "auto":
            return [(name, providers[name]) for name in ("gemini", "openai", "huggingface")]
        if Config.AI_PROVIDER == "knowledge":
            return []
        return [(Config.AI_PROVIDER, providers[Config.AI_PROVIDER])]

    def _append_history(self, user_id: str, role: str, content: str) -> None:
        self.sessions.setdefault(user_id, []).append({"role": role, "content": content})
        if len(self.sessions[user_id]) > 20:
            self.sessions[user_id] = self.sessions[user_id][-20:]

    def _fallback_result(self, message: str, user_id: str, language: str, intent_match: IntentMatch) -> ChatResult:
        if intent_match.intent_id != "fallback":
            reply = self._get_kb_reply(intent_match.intent_id, language)
            source = "knowledge_base"
            intent_id = intent_match.intent_id
            confidence = intent_match.confidence
            fallback_reason = f"matched_intent:{intent_id}"
        else:
            reply = self._get_kb_reply("fallback", language)
            source = "knowledge_fallback"
            intent_id = "fallback"
            confidence = 0.35
            fallback_reason = "no_domain_intent_match"

        logger.info(
            "Fallback response selected | source=%s | intent=%s | reason=%s",
            source,
            intent_id,
            fallback_reason,
        )

        self._append_history(user_id, "user", message)
        self._append_history(user_id, "assistant", reply)

        return ChatResult(
            reply=reply,
            message_id=random.randint(1000, 9999),
            user_id=user_id,
            source=source,
            intent=intent_id,
            confidence=confidence,
            language=language,
        )

    def process(self, message: str, user_id: str) -> ChatResult:
        language = self.detect_language(message)
        intent_match = self._match_intent(message)
        logger.info(
            "Processing chat request | user_id=%s | language=%s | intent_candidate=%s | intent_confidence=%.2f | kb_first=%s",
            user_id,
            language,
            intent_match.intent_id,
            intent_match.confidence,
            self._should_use_knowledge_base_first(message, intent_match),
        )

        if self._should_use_knowledge_base_first(message, intent_match):
            logger.info(
                "Knowledge base selected before provider call | intent=%s | confidence=%.2f",
                intent_match.intent_id,
                intent_match.confidence,
            )
            return self._fallback_result(message, user_id, language, intent_match)

        for provider_name, handler in self._provider_attempts():
            logger.info("Attempting provider | provider=%s", provider_name)
            provider_reply = handler(message)
            if provider_reply:
                logger.info("Provider succeeded | provider=%s", provider_name)
                self._append_history(user_id, "user", message)
                self._append_history(user_id, "assistant", provider_reply)
                return ChatResult(
                    reply=provider_reply,
                    message_id=random.randint(1000, 9999),
                    user_id=user_id,
                    source=provider_name,
                    intent="ai_response",
                    confidence=0.95,
                    language=language,
                )
            logger.info("Provider returned no reply | provider=%s", provider_name)

        return self._fallback_result(message, user_id, language, intent_match)

    def history(self, user_id: str) -> list[dict[str, str]]:
        return list(self.sessions.get(user_id, []))

    def clear_history(self, user_id: str) -> None:
=======
        return re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9]+", text.lower())

    def _intent_score(self, message: str, keywords: list[str]) -> float:
        tokens = self._tokenize(message)
        token_set = set(tokens)
        text_lower = message.lower()

        score = 0.0
        for raw_keyword in keywords:
            keyword = raw_keyword.lower().strip()
            if not keyword:
                continue

            if " " in keyword:
                if keyword in text_lower:
                    score += 1.0
                continue

            if keyword in token_set:
                score += 1.0
                continue

            # limited stem-like match only for longer keywords to avoid false hits like "hi" in "machine"
            if len(keyword) >= 5 and any(tok.startswith(keyword) for tok in tokens):
                score += 0.6

        return score

    def _match_intent(self, message: str) -> tuple[str, float]:
        best_intent = "fallback"
        best_score = 0.0

        for intent in self.knowledge_base["intents"]:
            score = self._intent_score(message, intent["keywords"])
            if score > best_score:
                best_score = score
                best_intent = intent["id"]

        return best_intent, best_score

    @staticmethod
    def _is_strong_domain_intent(score: float) -> bool:
        return score >= 1.0

    def _build_kb_result(self, intent_id: str, language: str, confidence: float) -> ChatResult:
        intent_obj = next(item for item in self.knowledge_base["intents"] if item["id"] == intent_id)
        response_key = "response_ru" if language == "ru" else "response_en"
        return ChatResult(
            reply=intent_obj[response_key],
            source="knowledge_base",
            intent=intent_id,
            confidence=confidence,
            language=language,
            provider_attempted="none",
            provider_status="not_attempted",
            fallback_reason="domain_intent",
        )

    def _build_fallback_result(self, language: str, intent_id: str, reason: str, provider_status: str) -> ChatResult:
        if intent_id != "fallback":
            intent_obj = next(item for item in self.knowledge_base["intents"] if item["id"] == intent_id)
            response_key = "response_ru" if language == "ru" else "response_en"
            reply = intent_obj[response_key]
            source = "knowledge_base"
            confidence = 0.62
        else:
            reply = self.knowledge_base["fallback"][language]
            source = "knowledge_fallback"
            confidence = 0.35

        return ChatResult(
            reply=reply,
            source=source,
            intent=intent_id,
            confidence=confidence,
            language=language,
            provider_attempted="gemini",
            provider_status=provider_status,
            fallback_reason=reason,
        )

    def _gemini_response(self, message: str, context: list[dict[str, str]]) -> tuple[str, str | None, str | None]:
        """Returns: (provider_status, reply, fallback_reason)."""

        if not Config.GEMINI_API_KEY:
            logger.warning("Gemini key missing; skipping provider call")
            return "request_failed", None, "gemini_key_missing"

        recent_turns = context[-6:]
        conversation_lines = []
        for turn in recent_turns:
            prefix = "Assistant" if turn["role"] == "assistant" else "User"
            conversation_lines.append(f"{prefix}: {turn['text']}")
        conversation_lines.append(f"User: {message}")

        prompt = (
            "You are MPGU Smart Assistant for a university LMS support demo. "
            "Give clear and concise answers, using bullet points when useful. "
            "Answer in the same language as the user.\n\n"
            "Conversation:\n"
            + "\n".join(conversation_lines)
        )

        url = Config.GEMINI_API_URL_TEMPLATE.format(
            model=Config.GEMINI_MODEL,
            api_key=Config.GEMINI_API_KEY,
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 280,
            },
        }

        logger.info("Gemini request started | model=%s", Config.GEMINI_MODEL)
        try:
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=Config.REQUEST_TIMEOUT_SECONDS,
            )
            logger.info("Gemini response status | status_code=%s", response.status_code)

            if response.status_code == 429:
                logger.warning("Gemini quota exceeded or rate limited")
                return "quota_exceeded", None, "gemini_429"
            if response.status_code >= 400:
                logger.warning("Gemini request failed | status_code=%s", response.status_code)
                return "request_failed", None, f"gemini_http_{response.status_code}"

            body = response.json()
            candidates = body.get("candidates", [])
            if not candidates:
                logger.warning("Gemini parse failed | no candidates")
                return "parse_failed", None, "gemini_no_candidates"

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                logger.warning("Gemini parse failed | no parts")
                return "parse_failed", None, "gemini_no_parts"

            text = str(parts[0].get("text", "")).strip()
            if not text:
                logger.warning("Gemini parse failed | empty text")
                return "parse_failed", None, "gemini_empty_text"

            logger.info("Gemini parse success")
            return "ok", text, None

        except requests.RequestException:
            logger.exception("Gemini request failed due to network/request error")
            return "request_failed", None, "gemini_request_exception"
        except (ValueError, KeyError, TypeError):
            logger.exception("Gemini response parse failed due to unexpected shape")
            return "parse_failed", None, "gemini_parse_exception"

    def process(self, message: str, user_id: str) -> ChatResult:
        language = self.detect_language(message)
        session = self.sessions.setdefault(user_id, [])

        intent_id, intent_score = self._match_intent(message)
        strong_domain_intent = self._is_strong_domain_intent(intent_score)

        if strong_domain_intent and intent_id != "fallback":
            logger.info("Using knowledge base due to strong domain intent | intent=%s score=%.2f", intent_id, intent_score)
            result = self._build_kb_result(intent_id, language, min(0.9, 0.55 + intent_score * 0.1))
        else:
            provider_status, gemini_reply, fallback_reason = self._gemini_response(message, session)
            if provider_status == "ok" and gemini_reply:
                result = ChatResult(
                    reply=gemini_reply,
                    source="gemini",
                    intent="general_query",
                    confidence=0.9,
                    language=language,
                    provider_attempted="gemini",
                    provider_status="ok",
                    fallback_reason=None,
                )
            else:
                logger.info(
                    "Falling back after Gemini failure | status=%s reason=%s intent=%s score=%.2f",
                    provider_status,
                    fallback_reason,
                    intent_id,
                    intent_score,
                )
                fallback_intent = intent_id if intent_id != "fallback" else "fallback"
                result = self._build_fallback_result(
                    language=language,
                    intent_id=fallback_intent,
                    reason=fallback_reason or "gemini_failed",
                    provider_status=provider_status,
                )

        session.append({"role": "user", "text": message})
        session.append({"role": "assistant", "text": result.reply})
        if len(session) > 20:
            self.sessions[user_id] = session[-20:]

        return result

    def history(self, user_id: str) -> list[dict[str, str]]:
        return self.sessions.get(user_id, [])

    def reset(self, user_id: str) -> None:
>>>>>>> theirs
        self.sessions.pop(user_id, None)


chat_engine = ChatEngine()
