# MPGU Smart Assistant (AI Chatbot)

A bilingual (English + Russian) chatbot prototype for Moscow Pedagogical State University (MPGU) student support workflows.

It is designed as a **hybrid assistant**:
- Uses Hugging Face Inference API when available.
- Falls back to deterministic domain responses for reliability.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [How Response Generation Works](#how-response-generation-works)
- [API Documentation](#api-documentation)
- [Setup Guide (Local)](#setup-guide-local)
- [Run Frontend and Backend Together](#run-frontend-and-backend-together)
- [Configuration](#configuration)
- [Testing and Validation](#testing-and-validation)
- [Known Limitations](#known-limitations)
- [Production Hardening Roadmap](#production-hardening-roadmap)
- [Interview/Portfolio Positioning](#interviewportfolio-positioning)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project is an MVP chatbot for university-related support queries such as:
- course registration
- schedules
- tutor/teacher discovery
- university contact/help information
- basic platform navigation guidance

The assistant supports both English and Russian input and includes resilience mechanisms to avoid complete failure if external AI is unavailable.

---

## Features

- ✅ Bilingual interaction (English/Russian)
- ✅ FastAPI backend with clean REST endpoint
- ✅ Frontend chat UI with:
  - connection status indicator
  - typing indicator
  - user/bot message history in session
- ✅ Hybrid response generation:
  - Hugging Face model inference
  - smart-response fallback from curated domain intents
- ✅ Health endpoints for backend availability checks
- ✅ CORS-enabled for local frontend/backend development

---

## Tech Stack

### Backend
- Python
- FastAPI
- Uvicorn
- Pydantic
- Requests
- python-dotenv

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript

### AI
- Hugging Face Inference API (`google/flan-t5-base` configured)
- Rule-based fallback intent map and response templates

---

## Project Structure

```text
mpgu_chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entrypoint
│   │   ├── config.py            # Env + model + CORS config
│   │   └── routes/
│   │       └── chat.py          # Chat endpoint + response engine
│   ├── requirements.txt
│   └── run.py                   # Convenience server runner
├── frontend/
│   ├── index.html               # Chat UI structure
│   ├── styles.css               # UI styling
│   └── script.js                # Client logic + API calls
└── PROJECT_POSITIONING_GUIDE.md # Interview positioning notes
```

---

## Architecture

```mermaid
flowchart LR
    U[User] --> F[Frontend Chat UI\nHTML/CSS/JS]
    F -->|POST /api/v1/chat| B[FastAPI Backend]
    B -->|try external inference| HF[Hugging Face API]
    HF -->|response or failure| B
    B -->|fallback if needed| SR[Smart Response Engine\n(intent + templates)]
    B --> F
    F --> U
```

### Service boundaries
- Frontend communicates with backend via REST.
- Backend manages language detection, intent mapping, external AI call, fallback strategy.
- External dependency is optional at runtime due to fallback architecture.

---

## How Response Generation Works

1. User sends message to backend (`POST /api/v1/chat`).
2. Backend sanitizes and validates input.
3. For non-trivial messages, backend attempts Hugging Face API.
4. If model result is unavailable/weak/error, backend falls back to curated smart responses.
5. Response payload includes reply + metadata (`message_id`, `user_id`, `api_used`).

This approach balances quality and reliability during prototype phase.

---

## API Documentation

### Base URL (local)
`http://localhost:5000`

### `GET /`
Service root and metadata.

**Example response:**
```json
{
  "status": "running",
  "service": "MPGU AI Chatbot",
  "version": "4.0.0",
  "ai_provider": "Hugging Face"
}
```

### `GET /health`
Health check endpoint.

**Example response:**
```json
{
  "status": "healthy",
  "service": "MPGU Chatbot API",
  "ai_provider": "Hugging Face"
}
```

### `POST /api/v1/chat`
Main chat endpoint.

**Request body:**
```json
{
  "message": "How do I register for courses?",
  "user_id": "user_123"
}
```

**Successful response:**
```json
{
  "reply": "Course registration is done through ...",
  "message_id": 4721,
  "user_id": "user_123",
  "api_used": "Hugging Face AI"
}
```

**Validation error example:**
- If message is empty/whitespace, backend returns status code `400` with appropriate detail.

---

## Setup Guide (Local)

## Prerequisites
- Python 3.10+
- pip
- (Optional) Hugging Face API token

## 1) Clone and enter project
```bash
git clone <your-repo-url>
cd <your-repo-root>/mpgu_chatbot
```

## 2) Backend setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows PowerShell

pip install -r requirements.txt
```

## 3) Environment variables
Create `.env` inside `backend/`:

```env
HUGGING_FACE_TOKEN=your_token_here
SECRET_KEY=change-this-in-real-deployments
```

> If `HUGGING_FACE_TOKEN` is missing, the app still works using fallback responses.

## 4) Run backend
```bash
python run.py
```
Backend starts at: `http://localhost:5000`

## 5) Run frontend
In a second terminal:
```bash
cd <your-repo-root>/mpgu_chatbot/frontend
python -m http.server 3000
```
Open: `http://localhost:3000`

---

## Run Frontend and Backend Together

### Terminal A
```bash
cd mpgu_chatbot/backend
source .venv/bin/activate
python run.py
```

### Terminal B
```bash
cd mpgu_chatbot/frontend
python -m http.server 3000
```

### Verify
- Backend health: `http://localhost:5000/health`
- Frontend: `http://localhost:3000`

---

## Configuration

Defined in `backend/app/config.py`:
- `HUGGING_FACE_TOKEN`
- `HUGGING_FACE_API_URL`
- `SECRET_KEY`
- `ALLOWED_ORIGINS`

Adjust `ALLOWED_ORIGINS` if you host frontend/backend on different domains in future.

---

## Testing and Validation

Current lightweight checks:

```bash
# Compile backend modules
python -m compileall app

# Optional quick import smoke test
PYTHONPATH=. python - <<'PY'
from app.routes.chat import get_smart_response
print(get_smart_response('hello'))
PY
```

Recommended next step: add `pytest` with
- endpoint test (`/api/v1/chat`)
- fallback behavior test
- language detection test

---

## Known Limitations

- Prototype status: not production deployed.
- Intent mapping is rule-based and finite.
- No authentication/authorization.
- No persistent database for chat history/analytics.
- Limited observability (no structured logs/metrics dashboards).

---

## Production Hardening Roadmap

- Add automated tests (`pytest`, CI)
- Add persistent storage (SQLite/PostgreSQL)
- Add auth (JWT/OAuth)
- Add logging + monitoring (request IDs, latency, fallback rate)
- Add containerization (Docker)
- Add retrieval-based answer grounding from curated knowledge docs

---

## Interview/Portfolio Positioning

You can describe this as:

> “A bilingual international university-support chatbot MVP using FastAPI + JavaScript, designed with a resilient hybrid response strategy (external LLM + deterministic fallback) for uptime and cost control in early-stage deployment.”

Suggested talking points:
- Reliability tradeoffs in AI products
- Error handling and graceful degradation
- API contract design and frontend integration
- Roadmap from MVP to production

---

## Troubleshooting

### Frontend shows “Cannot connect to backend”
- Ensure backend is running on port `5000`.
- Verify `http://localhost:5000/health` in browser.
- Check CORS origins in `config.py`.

### AI replies always from fallback
- Confirm `HUGGING_FACE_TOKEN` is set in `backend/.env`.
- Check outbound network/API quota.
- Inspect backend console for request errors/timeouts.

### Import issues (`No module named app`)
- Run backend commands from `mpgu_chatbot/backend` directory.
- Or set `PYTHONPATH` accordingly.

---

## Contributing

Contributions are welcome. A good first PR:
1. Add tests for `/api/v1/chat`.
2. Add `.env.example` and onboarding notes.
3. Improve intent mapping and response quality.

---

## License

No license file is currently included in this repository. Add a `LICENSE` (e.g., MIT) before public distribution.
