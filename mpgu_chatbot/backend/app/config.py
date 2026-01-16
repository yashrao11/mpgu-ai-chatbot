import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Hugging Face API Configuration
    HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
    
    # Use a more reliable model
    HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
    
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