import json
import logging
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from app.config import Config
from rag.retriever import retriever

logger = logging.getLogger("mpgu_chatbot.chat_engine")


@dataclass
class ChatResult:
    reply: str
    message_id: int
    user_id: str
    source: str
    intent: str
    confidence: float
    language: str
    provider_attempted: str
    provider_status: str
    fallback_reason: str | None = None


class ChatEngine:

    def __init__(self) -> None:

        self.knowledge_base = (
            self._load_knowledge_base()
        )

        self.sessions: dict[
            str,
            list[dict[str, str]]
        ] = {}

    @staticmethod
    def _coerce_responses(
        value: Any
    ) -> list[str]:

        if isinstance(value, str):

            cleaned = value.strip()

            return [cleaned] if cleaned else []

        if isinstance(value, list):

            return [
                item.strip()
                for item in value
                if isinstance(item, str)
                and item.strip()
            ]

        return []

    def _normalize_knowledge_base(
        self,
        raw_data: dict[str, Any]
    ) -> dict[str, Any]:

        normalized_intents = []

        for intent in raw_data.get(
            "intents",
            []
        ):

            responses = intent.get(
                "responses",
                {}
            )

            use_nested = (
                isinstance(responses, dict)
                and bool(responses)
            )

            normalized_intents.append(
                {
                    "id": intent.get(
                        "id",
                        "fallback"
                    ),

                    "keywords": intent.get(
                        "keywords",
                        []
                    ),

                    "responses": {

                        "en": (
                            self._coerce_responses(
                                responses.get("en")
                                if use_nested
                                else intent.get(
                                    "response_en"
                                )
                            )
                        ),

                        "ru": (
                            self._coerce_responses(
                                responses.get("ru")
                                if use_nested
                                else intent.get(
                                    "response_ru"
                                )
                            )
                        ),
                    },
                }
            )

        fallback = raw_data.get(
            "fallback",
            {}
        )

        return {
            "intents": normalized_intents,

            "fallback": {

                "en": (
                    self._coerce_responses(
                        fallback.get("en")
                    )
                ),

                "ru": (
                    self._coerce_responses(
                        fallback.get("ru")
                    )
                ),
            },
        }

    def _load_knowledge_base(
        self
    ) -> dict[str, Any]:

        kb_path = (
            Path(__file__)
            .resolve()
            .parents[2]
            / "data"
            / "knowledge_base.json"
        )

        with kb_path.open(
            "r",
            encoding="utf-8"
        ) as fp:

            return (
                self._normalize_knowledge_base(
                    json.load(fp)
                )
            )

    @staticmethod
    def detect_language(
        text: str
    ) -> str:

        russian_chars = len(
            re.findall(
                r"[а-яА-ЯёЁ]",
                text
            )
        )

        return (
            "ru"
            if russian_chars >
            max(1, len(text)) * 0.2
            else "en"
        )

    @staticmethod
    def _tokenize(
        text: str
    ) -> list[str]:

        return re.findall(
            r"[a-zA-Zа-яА-ЯёЁ0-9]+",
            text.lower()
        )

    def _intent_score(
        self,
        message: str,
        intent_id: str,
        keywords: list[str]
    ) -> float:

        tokens = self._tokenize(
            message
        )

        token_set = set(tokens)

        text_lower = message.lower()

        score = 0.0

        for raw_keyword in keywords:

            keyword = (
                raw_keyword
                .lower()
                .strip()
            )

            if not keyword:
                continue

            if " " in keyword:

                if keyword in text_lower:
                    score += 1.0

                continue

            if intent_id == "greeting":

                if keyword in token_set:
                    score += 1.0

                continue

            if keyword in token_set:

                score += 1.0

            elif (
                len(keyword) >= 5
                and any(
                    tok.startswith(keyword)
                    for tok in tokens
                )
            ):

                score += 0.6

        return score

    def _match_intent(
        self,
        message: str
    ) -> tuple[str, float]:

        best_intent = "fallback"

        best_score = 0.0

        for intent in (
            self.knowledge_base["intents"]
        ):

            intent_id = intent["id"]

            score = self._intent_score(
                message,
                intent_id,
                intent["keywords"]
            )

            if score > best_score:

                best_score = score

                best_intent = intent_id

        tokens = self._tokenize(
            message
        )

        if (
            best_intent == "greeting"
            and len(tokens) > 5
        ):

            return "fallback", 0.0

        return best_intent, best_score

    def _pick_response(
        self,
        intent_id: str,
        language: str
    ) -> str:

        for intent in (
            self.knowledge_base["intents"]
        ):

            if intent["id"] == intent_id:

                candidates = (
                    intent["responses"]
                    .get(language)

                    or

                    intent["responses"]
                    .get("en")

                    or []
                )

                if candidates:

                    return random.choice(
                        candidates
                    )

        fallback_candidates = (

            self.knowledge_base["fallback"]
            .get(language)

            or

            self.knowledge_base["fallback"]
            .get("en")

            or [
                (
                    "I can help with admissions, "
                    "courses, schedules, tutors, "
                    "exams, and contacts."
                )
            ]
        )

        return random.choice(
            fallback_candidates
        )

    def _build_kb_result(
        self,
        user_id: str,
        language: str,
        intent_id: str,
        confidence: float
    ) -> ChatResult:

        return ChatResult(

            reply=self._pick_response(
                intent_id,
                language
            ),

            message_id=random.randint(
                1000,
                9999
            ),

            user_id=user_id,

            source="knowledge_base",

            intent=intent_id,

            confidence=confidence,

            language=language,

            provider_attempted="none",

            provider_status="not_attempted",

            fallback_reason="domain_intent",
        )

    def _build_fallback_result(
        self,
        user_id: str,
        language: str,
        intent_id: str,
        provider_status: str,
        fallback_reason: str,
    ) -> ChatResult:

        return ChatResult(

            reply=self._pick_response(
                intent_id,
                language
            ),

            message_id=random.randint(
                1000,
                9999
            ),

            user_id=user_id,

            source="knowledge_fallback",

            intent=intent_id,

            confidence=0.35,

            language=language,

            provider_attempted="groq",

            provider_status=provider_status,

            fallback_reason=fallback_reason,
        )

    def _groq_response(
        self,
        message: str,
        context: list[dict[str, str]],
        retrieved_chunks: list[dict]
    ) -> tuple[
        str,
        str | None,
        str | None
    ]:

        if not Config.GROQ_API_KEY:

            logger.warning(
                "Groq key missing"
            )

            return (
                "request_failed",
                None,
                "groq_key_missing"
            )

        retrieved_context = ""

        for idx, chunk in enumerate(
            retrieved_chunks,
            start=1
        ):

            retrieved_context += (

                f"\nDOCUMENT {idx}\n"

                f"Source: "
                f"{chunk['source']}\n\n"

                f"{chunk['text']}\n\n"
            )

        messages = [
            {
                "role": "system",

                "content": (

                    "You are MPGU Smart Assistant.\n\n"

                    "Answer ONLY using the "
                    "provided university context.\n\n"

                    "If information is not found, "
                    "say you do not have enough "
                    "official information.\n\n"

                    "Give concise and accurate "
                    "answers.\n\n"

                    "Answer in the same language "
                    "as the user.\n\n"

                    f"MPGU CONTEXT:\n"
                    f"{retrieved_context}"
                ),
            }
        ]

        for turn in context[-6:]:

            role = (
                "assistant"
                if turn["role"] == "assistant"
                else "user"
            )

            messages.append(
                {
                    "role": role,
                    "content": turn["text"]
                }
            )

        messages.append(
            {
                "role": "user",
                "content": message
            }
        )

        payload = {

            "model": Config.GROQ_MODEL,

            "messages": messages,

            "temperature": 0.3,

            "max_tokens": 600,
        }

        headers = {

            "Authorization": (
                f"Bearer "
                f"{Config.GROQ_API_KEY}"
            ),

            "Content-Type":
                "application/json",
        }

        try:

            response = requests.post(

                Config.GROQ_API_URL_TEMPLATE,

                headers=headers,

                json=payload,

                timeout=(
                    Config
                    .REQUEST_TIMEOUT_SECONDS
                ),
            )

            if response.status_code == 429:

                return (
                    "quota_exceeded",
                    None,
                    "groq_429"
                )

            if response.status_code >= 400:

                return (
                    "request_failed",
                    None,
                    (
                        f"groq_http_"
                        f"{response.status_code}"
                    )
                )

            body = response.json()

            choices = body.get(
                "choices",
                []
            )

            if not choices:

                return (
                    "parse_failed",
                    None,
                    "groq_no_choices"
                )

            content = (
                choices[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )

            if not content:

                return (
                    "parse_failed",
                    None,
                    "groq_empty_content"
                )

            return (
                "ok",
                content,
                None
            )

        except requests.RequestException:

            logger.exception(
                "Groq request failed"
            )

            return (
                "request_failed",
                None,
                "groq_request_exception"
            )

        except (
            ValueError,
            KeyError,
            TypeError
        ):

            logger.exception(
                "Groq parse failed"
            )

            return (
                "parse_failed",
                None,
                "groq_parse_exception"
            )

    def process(
        self,
        message: str,
        user_id: str
    ) -> ChatResult:

        language = self.detect_language(
            message
        )

        session = self.sessions.setdefault(
            user_id,
            []
        )

        intent_id, intent_score = (
            self._match_intent(message)
        )

        # ONLY greetings use KB
        if intent_id == "greeting":

            result = self._build_kb_result(

                user_id=user_id,

                language=language,

                intent_id=intent_id,

                confidence=0.95,
            )

        else:

            # RAG Retrieval
            retrieved_chunks = (
                retriever.search(message)
            )

            # Send chunks to Groq
            provider_status, groq_reply, fallback_reason = (
                self._groq_response(
                    message,
                    session,
                    retrieved_chunks
                )
            )

            # Successful response
            if (
                provider_status == "ok"
                and groq_reply
            ):

                result = ChatResult(

                    reply=groq_reply,

                    message_id=random.randint(
                        1000,
                        9999
                    ),

                    user_id=user_id,

                    source="rag",

                    intent=intent_id,

                    confidence=0.92,

                    language=language,

                    provider_attempted="groq",

                    provider_status="ok",

                    fallback_reason=None,
                )

            # Fallback response
            else:

                result = (
                    self._build_fallback_result(
                        user_id=user_id,

                        language=language,

                        intent_id="fallback",

                        provider_status=(
                            provider_status
                        ),

                        fallback_reason=(
                            fallback_reason
                            or "groq_failed"
                        ),
                    )
                )

        # Save conversation
        session.append(
            {
                "role": "user",
                "text": message
            }
        )

        session.append(
            {
                "role": "assistant",
                "text": result.reply
            }
        )

        # Keep latest 20 messages
        if len(session) > 20:

            self.sessions[user_id] = (
                session[-20:]
            )

        return result

    def history(
        self,
        user_id: str
    ) -> list[dict[str, str]]:

        return self.sessions.get(
            user_id,
            []
        )

    def reset(
        self,
        user_id: str
    ) -> None:

        self.sessions.pop(
            user_id,
            None
        )


chat_engine = ChatEngine()