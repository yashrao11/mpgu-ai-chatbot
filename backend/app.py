"""Compatibility launcher for legacy scripts.

This file keeps backward compatibility for users running `python app.py`.
It simply starts the FastAPI application defined in `app.main`.
"""

import uvicorn

<<<<<<< ours
from app.config import Config

=======
>>>>>>> theirs

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
<<<<<<< ours
        host=Config.API_HOST,
        port=Config.API_PORT,
=======
        host="0.0.0.0",
        port=5000,
>>>>>>> theirs
        reload=True,
        log_level="info",
    )
