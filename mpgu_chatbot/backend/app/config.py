import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Provider selection: auto | gemini | openai | huggingface | knowledge
    AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").lower()

    # Gemini API configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GEMINI_API_URL_TEMPLATE = os.getenv(
        "GEMINI_API_URL_TEMPLATE",
        "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
    )

    # OpenAI API configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")
    OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/responses")

    # Hugging Face API Configuration
    HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
    
    # Use a more reliable model
    # Use a production-grade instruction model
    HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15"))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "mpgu-chatbot-working-2024")
    
    # CORS
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:8080"
    ]

def validate_config():
    print("✅ MPGU Chatbot configuration validated successfully!")
    hf_model = Config.HUGGING_FACE_API_URL.rsplit("/", maxsplit=1)[-1]
    hf_token_status = "set" if Config.HUGGING_FACE_TOKEN else "not set"
    gemini_key_status = "set" if Config.GEMINI_API_KEY else "not set"
    openai_token_status = "set" if Config.OPENAI_API_KEY else "not set"
    print(
        "✅ MPGU Chatbot configuration validated | "
        f"provider={Config.AI_PROVIDER} | "
        f"gemini_model={Config.GEMINI_MODEL} | gemini_key={gemini_key_status} | "
        f"openai_model={Config.OPENAI_MODEL} | openai_key={openai_token_status} | "
        f"hf_model={hf_model} | hf_token={hf_token_status}"
    )
mpgu_chatbot/backend/app/main.py
