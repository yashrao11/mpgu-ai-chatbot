# MPGU Smart Assistant — Placement Edition

A bilingual (English + Russian) university support chatbot built for interview demos and rapid MVP showcasing.

This version is designed to be **reliable in live interviews**:
- Works with **Hugging Face API** when token is available.
- Gracefully falls back to a **knowledge-base intent engine** when API is missing/fails.
- Exposes conversation metadata (`source`, `intent`, `confidence`, `language`) to demonstrate engineering depth.

---

## ✨ Highlights

- Hybrid response pipeline (AI + deterministic fallback)
- Bilingual support (English/Russian)
- FastAPI backend with typed schemas
- Session-based chat history endpoints
- Frontend with quick prompts and metadata badges
- Clear health and diagnostics endpoints

---

## 🧱 Tech Stack

### Backend
- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- Requests
- python-dotenv

### Frontend
- HTML + CSS + Vanilla JavaScript

### AI Layer
- Hugging Face Inference API (`google/flan-t5-base`)
- Local knowledge base (`backend/data/knowledge_base.json`)

---

## 📁 Project Structure

```text
mpgu_chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app + middleware + health
│   │   ├── config.py                # Env config
│   │   ├── schemas.py               # Pydantic request/response models
│   │   ├── routes/
│   │   │   └── chat.py              # Chat + history routes
│   │   └── services/
│   │       └── chat_engine.py       # Hybrid response engine
│   ├── data/
│   │   └── knowledge_base.json      # Intent keywords and bilingual replies
│   ├── requirements.txt
│   └── run.py                       # Local runner
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── styles.css
├── README.md
└── PROJECT_POSITIONING_GUIDE.md
```

---

## 🧠 Response Pipeline

1. User sends message from frontend.
2. Backend tries Hugging Face inference (if token configured).
3. If unavailable/low reliability, backend answers from intent knowledge base.
4. Backend returns response + metadata:
   - `source`: `hugging_face` or `knowledge_base` / `knowledge_fallback`
   - `intent`
   - `confidence`
   - `language`

This gives you strong talking points for reliability and fallback design in interviews.

---

## 🔌 API Endpoints

Base URL: `http://localhost:5000`

### `GET /`
Service info.

### `GET /health`
Health endpoint with version/provider mode.

### `POST /api/v1/chat`
Chat endpoint.

**Request**
```json
{
  "message": "How do I register for courses?",
  "user_id": "user_abc123"
}
```

**Response**
```json
{
  "reply": "Course registration flow: ...",
  "message_id": 3241,
  "user_id": "user_abc123",
  "source": "knowledge_base",
  "intent": "course_registration",
  "confidence": 0.73,
  "language": "en"
}
```

### `GET /api/v1/chat/history/{user_id}`
Returns in-memory conversation history for a user.

### `DELETE /api/v1/chat/history/{user_id}`
Clears a user chat session.

---

## 🚀 Quick Start (Local)

## 1) Backend

```bash
cd mpgu_chatbot/backend
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
HUGGING_FACE_TOKEN=your_token_here
SECRET_KEY=change-me
REQUEST_TIMEOUT_SECONDS=15
```

Run backend:

```bash
python run.py
```

## 2) Frontend

Open second terminal:

```bash
cd mpgu_chatbot/frontend
python -m http.server 3000
```

Open `http://localhost:3000`

---

## ✅ Demo Script (for Interview)

1. Ask: “How can I apply for admission?”
2. Ask: “Контакты МПГУ”
3. Show metadata badges (`source/intent/language/confidence`).
4. Disable/remove token and demonstrate graceful fallback still works.
5. Clear chat history with `Clear` button and show fresh session.

---

## 🧪 Validation Commands

```bash
# from repo root
python -m compileall mpgu_chatbot/backend/app

# optional smoke run (from backend dir)
PYTHONPATH=. python - <<'PY'
from app.services.chat_engine import chat_engine
print(chat_engine.process('How to register for courses?', 'demo_user'))
PY
```

---

## ⚠️ Current Constraints

- History is in-memory (resets on restart)
- No auth/roles yet
- No database or dashboard analytics yet
- Knowledge base is static JSON (not RAG/vector search yet)

---

## 📌 Production Upgrade Path

- Add persistent DB (PostgreSQL)
- Add JWT auth + role-based access
- Add request logging + metrics
- Add Redis session/rate limiting
- Add RAG over official university docs
- Dockerize + deploy to cloud

---

## 🪪 Portfolio Positioning Line

> “Built a bilingual hybrid AI assistant with deterministic fallback and metadata-rich responses for reliable university support workflows in interview/demo conditions.”

---

## License

No license file is currently included. Add one (MIT/Apache-2.0) before public distribution.
