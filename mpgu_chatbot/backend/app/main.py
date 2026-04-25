from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Config, configure_logging
from app.routes.chat import router as chat_router
from app.schemas import HealthResponse

configure_logging()

app = FastAPI(
    title=Config.APP_NAME,
    description="Gemini-first chatbot API with local knowledge fallback",
    version=Config.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True,
        log_level="info",
    )