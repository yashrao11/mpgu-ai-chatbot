from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Config
from app.routes.chat import router as chat_router
from app.schemas import HealthResponse

# Create FastAPI app
app = FastAPI(
    title="MPGU AI Chatbot API",
    description="Hybrid AI assistant API for university support (MPGU) with resilient fallback responses",
    version="5.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(chat_router, prefix="/api/v1")

# Health check endpoint
@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        status="running",
        service="MPGU AI Chatbot",
        version="5.0.0",
        ai_provider=f"{Config.AI_PROVIDER} (gemini/openai/huggingface/knowledge supported)",
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="MPGU Chatbot API",
        version="5.0.0",
        ai_provider=f"{Config.AI_PROVIDER} (gemini/openai/huggingface/knowledge supported)",
    )

# This allows running with: python -m app.main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
