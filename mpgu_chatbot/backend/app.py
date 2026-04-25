"""Compatibility launcher for legacy scripts."""

import uvicorn

from app.config import Config


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True,
        log_level="info",
    )