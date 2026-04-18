"""Compatibility launcher for legacy scripts.

This file keeps backward compatibility for users running `python app.py`.
It simply starts the FastAPI application defined in `app.main`.
"""

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info",
    )
