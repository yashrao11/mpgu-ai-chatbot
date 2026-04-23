import os
import logging
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
<<<<<<< ours
    BASE_DIR = BASE_DIR
    ENV_PATH = ENV_PATH
    SUPPORTED_AI_PROVIDERS = {"auto", "gemini", "openai", "huggingface", "knowledge"}

    # Provider selection: auto | gemini | openai | huggingface | knowledge
    AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").strip().lower()
    if AI_PROVIDER not in SUPPORTED_AI_PROVIDERS:
        AI_PROVIDER = "auto"
=======
    """Runtime configuration for Gemini-first local demo."""

    APP_NAME = "MPGU Smart Assistant API"
    APP_VERSION = "6.0.0"

    # Gemini-only provider mode for this project.
    AI_PROVIDER = "gemini"
>>>>>>> theirs

    # Gemini API configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GEMINI_API_URL_TEMPLATE = os.getenv(
        "GEMINI_API_URL_TEMPLATE",
<<<<<<< ours
        "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    )

    # OpenAI API configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")
    OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/responses")

    # Hugging Face API configuration
    HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
    HUGGING_FACE_API_URL = os.getenv(
        "HUGGING_FACE_API_URL",
        "https://api-inference.huggingface.co/models/google/flan-t5-base",
    )

    REQUEST_TIMEOUT_SECONDS = max(1, int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15")))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").strip().upper()

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "mpgu-chatbot-working-2024")

    # Server
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "5000"))

    # CORS
    DEFAULT_ALLOWED_ORIGINS = [
=======
        "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
    )

    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))

    # CORS for local demo environments
    ALLOWED_ORIGINS = [
>>>>>>> theirs
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
<<<<<<< ours
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "null",
=======
        "http://localhost:8080",
>>>>>>> theirs
    ]
    ALLOWED_ORIGINS = _split_csv(os.getenv("ALLOWED_ORIGINS")) or DEFAULT_ALLOWED_ORIGINS


def validate_config() -> None:
    hf_model = Config.HUGGING_FACE_API_URL.rsplit("/", maxsplit=1)[-1]
    hf_token_status = "set" if Config.HUGGING_FACE_TOKEN else "not set"
    gemini_key_status = "set" if Config.GEMINI_API_KEY else "not set"
    openai_token_status = "set" if Config.OPENAI_API_KEY else "not set"
    print(
        "✅ MPGU Chatbot configuration validated | "
        f"env={Config.ENV_PATH} | "
        f"provider={Config.AI_PROVIDER} | "
        f"gemini_model={Config.GEMINI_MODEL} | gemini_key={gemini_key_status} | "
        f"openai_model={Config.OPENAI_MODEL} | openai_key={openai_token_status} | "
        f"hf_model={hf_model} | hf_token={hf_token_status} | "
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

<<<<<<< ours
    logger.setLevel(level)
    logger.propagate = False
=======

def validate_config() -> None:
    gemini_key_status = "set" if Config.GEMINI_API_KEY else "not set"
    print(
        "✅ Configuration validated | "
        f"provider={Config.AI_PROVIDER} | "
        f"gemini_model={Config.GEMINI_MODEL} | "
        f"gemini_key={gemini_key_status} | "
        f"timeout={Config.REQUEST_TIMEOUT_SECONDS}s"
    )
>>>>>>> theirs
