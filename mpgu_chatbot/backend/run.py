#!/usr/bin/env python3
"""Local runner for MPGU Smart Assistant backend."""

import os
import sys

import uvicorn

from app.config import Config, validate_config


def main() -> None:
    try:
        print("🎓 MPGU Smart Assistant - Gemini Demo")
        print("=" * 56)
        print(f"📁 Working directory: {os.getcwd()}")
        print("🔍 Validating configuration...")
        validate_config()
        print("✅ Configuration validated successfully")
        print(f"🌐 API base: http://localhost:{Config.API_PORT}")
        print(f"🔗 Health: http://localhost:{Config.API_PORT}/health")
        print(f"💬 Chat: http://localhost:{Config.API_PORT}/api/v1/chat")
        print(f"🗂️ History: http://localhost:{Config.API_PORT}/api/v1/chat/history/{{user_id}}")
        print("🤖 Provider: Gemini only (knowledge fallback enabled)")
        print("=" * 56)

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