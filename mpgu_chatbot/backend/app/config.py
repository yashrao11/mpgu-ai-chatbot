import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Hugging Face API Configuration
    HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
    
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
    model = Config.HUGGING_FACE_API_URL.rsplit("/", maxsplit=1)[-1]
    token_status = "set" if Config.HUGGING_FACE_TOKEN else "not set (fallback mode)"
    print(f"✅ MPGU Chatbot configuration validated | model={model} | token={token_status}")
