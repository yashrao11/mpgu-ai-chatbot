# MPGU LMS Chatbot – Project Positioning Guide (for Interviews)

This document helps you explain this project as an **international academic product prototype** and improve it quickly for placements (Morgan Stanley and others).

## 1) What this project is

You built a **bilingual AI assistant prototype** for MPGU (Moscow Pedagogical State University) LMS workflows.

### Core idea
- Students ask questions in English or Russian.
- Backend routes queries to:
  1. Hugging Face inference API (when available), and
  2. a deterministic smart-response fallback for reliability.
- Frontend provides a chat UX with connection health checks and status indicator.

### Current architecture
- **Frontend:** plain HTML/CSS/JavaScript single-page chat UI.
- **Backend:** FastAPI app with REST endpoint `/api/v1/chat`.
- **AI strategy:** hybrid (external model + local intent/keyword fallback).

---

## 2) Technologies used (what to say in interviews)

### Confirmed stack from code
- **Python 3**
- **FastAPI** for API service
- **Uvicorn** ASGI server
- **Pydantic** request schema validation
- **Requests** for external API calls
- **python-dotenv** for configuration
- **Vanilla HTML/CSS/JS** frontend

### Key engineering concepts demonstrated
- API design (`POST /chat`, health endpoints)
- CORS configuration for local frontend/backend split
- Fault tolerance (fallback logic when AI API is unavailable)
- Bilingual intent routing (English + Russian)
- Client-side state + optimistic UI patterns (typing indicator, connection status)

---

## 3) What you were trying to build (one-line + two-line versions)

### 1-line pitch
"I built a bilingual AI support assistant for an international university LMS to handle common student workflows with resilient fallback behavior."

### 2-line pitch
"The goal was to reduce repeated support questions (courses, schedule, contacts, tutors) by adding a lightweight chatbot integrated with LMS context. Since external AI can fail or be costly, I designed a hybrid architecture: model API when available, deterministic domain responses as fallback."

---

## 4) Honest project status (say this clearly)

Use this wording:

- "This is a **working prototype / pre-production MVP**."
- "It was developed as part of an international academic collaboration context."
- "Deployment, observability, and auth were not completed yet, but architecture and core conversational flow are implemented."

This sounds mature and honest.

---

## 5) Minimal-time improvements that make it stand out

Prioritize these in order.

## Tier A (1–2 days): interview-impact essentials
1. **Add README with architecture diagram + setup + API contract**
2. **Add sample test script** (`pytest` for one happy path + one fallback path)
3. **Add `.env.example` and clean config docs**
4. **Record a 60–90 second demo video** of chatbot flow

## Tier B (2–4 days): product maturity signal
1. Add **conversation logging** (local JSON or SQLite)
2. Add **simple analytics endpoint** (question category counts)
3. Add **Dockerfile + docker-compose**
4. Add **language selector** in UI (auto + manual)

## Tier C (4–7 days): strong differentiator
1. Replace keyword map with **embedding-based retrieval** over FAQ docs
2. Add **source-grounded answers** (show source links)
3. Add **basic authentication** (student/admin roles)

---

## 6) Morgan Stanley–style interview framing

Focus on engineering rigor, not just chatbot hype.

### STAR-style story template
- **Situation:** International university needed scalable student support in bilingual context.
- **Task:** Build low-cost assistant prototype with high uptime.
- **Action:** Designed FastAPI backend, intent fallback, bilingual mapping, and frontend chat UX.
- **Result:** Working MVP that handles common queries with graceful degradation when AI endpoint fails.

### Strong technical talking points
- Why hybrid > pure LLM in early-stage systems (cost, reliability, latency)
- How you handled error/fallback to avoid total failure
- What metrics you would track in production (latency, fallback rate, resolution rate)
- Tradeoffs of rule-based vs model-driven intent handling

---

## 7) 7-day rapid execution plan

### Day 1
- README + architecture + setup cleanup
- `.env.example` + run instructions

### Day 2
- Unit tests for routing/fallback
- Linting + formatting setup

### Day 3
- Logging for conversations
- Basic analytics endpoint

### Day 4
- Dockerize app
- Smoke-test script

### Day 5
- UI polish + empty/error/loading states
- Add project screenshots in docs

### Day 6
- Demo recording + interview bullet points

### Day 7
- Mock interview rehearsal using your STAR story

---

## 8) What to learn first (fast, practical sequence)

1. **FastAPI fundamentals** (routing, models, validation)
2. **HTTP/API basics** (status codes, payloads, timeouts)
3. **Prompt + fallback architecture** patterns
4. **Testing basics** in Python (`pytest`)
5. **Docker fundamentals** for consistent execution

If you can do only one deep learning item: learn **retrieval-augmented FAQ answering** with embeddings.

---

## 9) CV bullet upgrades (replace vague lines)

Use measurable, engineering-focused bullets like:

- "Built a bilingual (English/Russian) AI assistant prototype for university LMS support using FastAPI and JavaScript."
- "Implemented hybrid response pipeline combining Hugging Face inference with deterministic fallback to improve reliability."
- "Designed REST endpoints and frontend chat workflow with health checks, status indicators, and user-session handling."
- "Defined roadmap for production hardening: tests, logging, analytics, containerization, and deployment."

---

## 10) Red flags to avoid in interviews

- Don’t claim production deployment if not deployed.
- Don’t claim advanced NLP if it is mostly keyword-intent mapping.
- Don’t hide limitations; explain roadmap and tradeoffs confidently.

Honesty + clarity + roadmap = strong impression.
