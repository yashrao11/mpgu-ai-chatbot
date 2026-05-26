import logging
import os
from pathlib import Path

from dotenv import load_dotenv


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)


class Config:
    """Runtime configuration for Groq-based MPGU Smart Assistant backend."""

    BASE_DIR = BASE_DIR
    ENV_PATH = ENV_PATH

    APP_NAME = "MPGU Smart Assistant API"
    APP_VERSION = "6.0.0"

    AI_PROVIDER = "groq"

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    GROQ_API_URL_TEMPLATE = os.getenv(
        "GROQ_API_URL_TEMPLATE",
        "https://api.groq.com/openai/v1/chat/completions",
    )

    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").strip().upper()

    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "5000"))

    DEFAULT_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]
    ALLOWED_ORIGINS = _split_csv(os.getenv("ALLOWED_ORIGINS")) or DEFAULT_ALLOWED_ORIGINS


def validate_config() -> None:
    groq_key_status = "set" if Config.GROQ_API_KEY else "not set"
    print(
        "✅ Configuration validated | "
        f"env={Config.ENV_PATH} | "
        f"provider={Config.AI_PROVIDER} | "
        f"groq_model={Config.GROQ_MODEL} | "
        f"groq_key={groq_key_status} | "
        f"origins={len(Config.ALLOWED_ORIGINS)} | "
        f"log_level={Config.LOG_LEVEL}"
    )


def configure_logging() -> None:
    logger = logging.getLogger("mpgu_chatbot")
    level = getattr(logging, Config.LOG_LEVEL, logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        logger.addHandler(handler)

    logger.setLevel(level)
    logger.propagate = False