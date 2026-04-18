# MPGU Smart Assistant — Placement Edition

A bilingual (English + Russian) university support chatbot built for interview demos and rapid MVP showcasing.

This version is designed to be **reliable in live interviews**:
- Works with **Gemini API**, **OpenAI API**, or **Hugging Face API** when token is available.
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
- Gemini API (`gemini-2.5-flash` by default)
- OpenAI Responses API (`gpt-5.2` by default)
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
2. Backend tries Gemini first (default in `auto` mode), then OpenAI, then Hugging Face.
3. If unavailable/low reliability, backend answers from intent knowledge base.
4. Backend returns response + metadata:
   - `source`: `gemini`, `openai`, `hugging_face`, `knowledge_base`, or `knowledge_fallback`
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
AI_PROVIDER=auto
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.2
HUGGING_FACE_TOKEN=your_huggingface_token
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

## 🏆 Which API is best for placements?

For your interview demo, use this order:

1. **Gemini (`gemini-2.5-flash`)** for speed + quality balance in demos.
2. **OpenAI (`gpt-5.2`)** as strong secondary option.
3. **Hugging Face** as additional backup.
4. **Knowledge fallback** for guaranteed offline reliability.

In this project, set:

```env
AI_PROVIDER=auto
```

`auto` tries Gemini first, then OpenAI, then Hugging Face, then fallback.

If you want forced mode:

```env
AI_PROVIDER=gemini
# or
AI_PROVIDER=openai
# or
AI_PROVIDER=huggingface
# or
AI_PROVIDER=knowledge
```

---

## 🔐 How to get Gemini API key (detailed)

1. Open Google AI Studio: https://aistudio.google.com/  
2. Create an API key for Gemini and copy it.  
3. Never paste key in frontend/client files. Keep it in backend `.env` only.  
4. Ensure your Google Cloud/project billing/quota is configured for your usage.  
5. Add key in `backend/.env`:

```env
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-2.5-flash
AI_PROVIDER=gemini
```

6. Restart backend and verify:
   - `GET /health` should show provider mode.
   - Responses will show `source: gemini` when Gemini is used.

---

## ☁️ Run when project is only on GitHub (no local files)

### Option A (Recommended): GitHub Codespaces

1. Open your GitHub repository page.
2. Click **Code → Codespaces → Create codespace on branch**.
3. In terminal:
   ```bash
   cd mpgu_chatbot/backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Create `backend/.env` with your API keys.
5. Start backend:
   ```bash
   python run.py
   ```
6. In second terminal:
   ```bash
   cd mpgu_chatbot/frontend
   python -m http.server 3000
   ```
7. Use forwarded ports in Codespaces (3000 and 5000) and open the UI.

### Option B: Local clone from GitHub

```bash
git clone <your-github-repo-url>
cd <repo>/mpgu_chatbot
```

Then run the same backend/frontend steps from this README.

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
