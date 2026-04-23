#!/usr/bin/env python3
<<<<<<< ours
"""Runner for the MPGU Smart Assistant backend."""
=======
"""Local runner for MPGU Smart Assistant backend."""
>>>>>>> theirs

import os
import sys

import uvicorn

<<<<<<< ours
from app.config import Config, validate_config
=======
from app.config import validate_config
>>>>>>> theirs


def main() -> None:
    try:
<<<<<<< ours
        print("🎓 MPGU Smart Assistant")
        print("🎓 MPGU Smart Assistant - Placement Edition")
        print("=" * 50)
        print(f"📁 Working directory: {os.getcwd()}")

        # Validate configuration
        print("🔍 Validating configuration...")
        validate_config()

        print("🚀 Starting MPGU Chatbot server...")
        print(f"🌐 Server URL: http://localhost:{Config.API_PORT}")
        print(f"🔗 Health check: http://localhost:{Config.API_PORT}/health")
        print(f"💬 Chat endpoint: http://localhost:{Config.API_PORT}/api/v1/chat")
        print(f"🗂️ History endpoint: http://localhost:{Config.API_PORT}/api/v1/chat/history/{{user_id}}")
        print("🤖 AI System: Gemini/OpenAI/Hugging Face with knowledge-base fallback")
        print("⏹️  Press Ctrl+C to stop the server")
        print("=" * 50)
=======
        print("🎓 MPGU Smart Assistant - Gemini Demo")
        print("=" * 56)
        print(f"📁 Working directory: {os.getcwd()}")
        print("🔍 Validating configuration...")
        validate_config()
        print("✅ Configuration validated successfully")
        print("🌐 API base: http://localhost:5000")
        print("🔗 Health: http://localhost:5000/health")
        print("💬 Chat: http://localhost:5000/api/v1/chat")
        print("🗂️ History: http://localhost:5000/api/v1/chat/history/{user_id}")
        print("🤖 Provider: Gemini only (knowledge fallback enabled)")
        print("=" * 56)
>>>>>>> theirs

        uvicorn.run(
            "app.main:app",
            host=Config.API_HOST,
            port=Config.API_PORT,
            reload=True,
            log_level="info",
        )

    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as exc:
        print(f"❌ Failed to start server: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
