#!/usr/bin/env python3
"""Local runner for MPGU Smart Assistant backend."""

import os
import sys
import uvicorn

from app.config import validate_config


def main() -> None:

    try:

        print("🎓 MPGU Smart Assistant")
        print("=" * 56)

        print(f"📁 Working directory: {os.getcwd()}")

        print("🔍 Validating configuration...")

        validate_config()

        print("✅ Configuration validated successfully")

        print("🌐 API base: http://127.0.0.1:5000")
        print("🔗 Health: http://127.0.0.1:5000/health")
        print("💬 Chat: http://127.0.0.1:5000/api/v1/chat")
        print("🗂️ History: http://127.0.0.1:5000/api/v1/chat/history/{user_id}")

        print("🤖 Provider: Groq only (RAG enabled)")

        print("=" * 56)

        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=5000,
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