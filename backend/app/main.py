import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

<<<<<<< ours
from .config import Config, configure_logging
from .routes.chat import router as chat_router
from .schemas import HealthResponse

configure_logging()
=======
from app.config import Config
from app.routes.chat import router as chat_router
from app.schemas import HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
>>>>>>> theirs

app = FastAPI(
<<<<<<< ours
    title="MPGU AI Chatbot API",
    description="Hybrid AI assistant API for university support (MPGU) with provider fallback and typed responses",
    version="5.0.0"
=======
    title="MPGU Smart Assistant API",
    description="Gemini-first chatbot API with local knowledge fallback",
    version=Config.APP_VERSION,
>>>>>>> theirs
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")

<<<<<<< ours
# Root endpoint
@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        status="running",
        service="MPGU AI Chatbot",
        version="5.0.0",
        ai_provider=f"{Config.AI_PROVIDER} (gemini)",
    )

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="MPGU Chatbot API",
        version="5.0.0",
        ai_provider=f"{Config.AI_PROVIDER} (gemini)",
    )

# Run directly
=======

@app.get("/", response_model=HealthResponse)
async def root() -> HealthResponse:
    return HealthResponse(
        status="running",
        service=Config.APP_NAME,
        version=Config.APP_VERSION,
        ai_provider="gemini_only_with_knowledge_fallback",
    )


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service=Config.APP_NAME,
        version=Config.APP_VERSION,
        ai_provider="gemini_only_with_knowledge_fallback",
    )


>>>>>>> theirs
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True,
<<<<<<< ours
        log_level="info"
=======
        log_level="info",
>>>>>>> theirs
    )
