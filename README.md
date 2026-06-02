# MPGU Smart Assistant

A bilingual university assistant for **Moscow Pedagogical State University (MPGU)** built as a full **Retrieval-Augmented Generation (RAG)** system.

This project combines:

* **official MPGU website crawling**
* **PDF ingestion**
* **text chunking**
* **vector embeddings**
* **semantic search with ChromaDB**
* **Groq-based answer generation**
* **FastAPI backend**
* **HTML/CSS/JavaScript frontend**

The result is a university support chatbot that can answer questions about admissions, international students, programs, faculty structure, contacts, and related MPGU information using official source material.

---

## What this project demonstrates

This repository is designed to show a complete modern AI workflow, not just a simple chatbot.

It demonstrates:

* how to collect data from a live university website
* how to extract text from PDFs
* how to turn documents into chunks
* how to convert chunks into embeddings
* how to store and search embeddings in a vector database
* how to retrieve relevant context for a user query
* how to pass that context to an LLM
* how to return a grounded answer through an API

---

## Key idea

The chatbot does **not** rely only on hardcoded answers.

Instead, it uses a two-layer knowledge system:

1. **Static fallback knowledge**

   * used for greetings and safe fallback behavior
   * stored in `data/knowledge_base.json`

2. **RAG knowledge layer**

   * built from MPGU website pages and PDFs
   * stored as embeddings in ChromaDB
   * used for most factual questions

That means the assistant can answer from official MPGU content rather than only from prewritten responses.

---

## Project highlights

* Bilingual support: English and Russian
* Official MPGU website crawler
* PDF ingestion pipeline
* Semantic retrieval using embeddings
* ChromaDB vector store
* Groq LLM integration
* FastAPI backend with typed schemas
* Chat history endpoints
* Conversation memory during runtime
* Frontend chat interface with metadata badges
* Clean separation of ingestion, retrieval, and generation layers

---

## Architecture overview

### Online chat flow

```text
User
  ↓
Frontend (HTML/CSS/JS)
  ↓ fetch()
FastAPI backend
  ↓
app/routes/chat.py
  ↓
app/services/chat_engine.py
  ↓
rag/retriever.py
  ↓
ChromaDB vector store
  ↓
Relevant chunks
  ↓
Groq LLM
  ↓
Final answer
  ↓
Frontend UI
```

### Offline knowledge-building flow

```text
MPGU website pages / PDFs
  ↓
ingestion/crawler.py / ingestion/pdf_loader.py
  ↓
data/raw/*.txt
  ↓
rag/chunker.py
  ↓
rag/embed_store.py
  ↓
data/vector_store/
```

---

## Tech stack

### Backend

* Python 3.11+
* FastAPI
* Uvicorn
* Pydantic
* Requests
* python-dotenv

### RAG / AI layer

* sentence-transformers
* ChromaDB
* Groq LLM
* PyMuPDF for PDFs

### Web crawling / parsing

* requests
* BeautifulSoup4
* lxml

### Frontend

* HTML
* CSS
* Vanilla JavaScript

---

## Repository structure

```text
mpgu_chatbot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── chat.py
│   │   └── services/
│   │       └── chat_engine.py
│   ├── data/
│   │   ├── knowledge_base.json
│   │   ├── raw/
│   │   ├── processed/
│   │   └── vector_store/
│   ├── ingestion/
│   │   ├── clean_text.py
│   │   ├── crawler.py
│   │   ├── pdf_loader.py
│   │   ├── urls.py
│   │   └── pdfs/
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── embed_store.py
│   │   └── retriever.py
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── styles.css
└── README.md
```

---

## How the system works

### 1. Data collection

The project starts by collecting knowledge from MPGU official sources.

#### Website crawling

The crawler visits MPGU website pages and extracts visible text.

Important pages include:

* homepage
* admissions pages
* structure pages
* education/program pages
* international relations pages
* news and announcements
* contact pages

#### PDF ingestion

PDF files can be placed in:

```text
backend/ingestion/pdfs/
```

The PDF loader extracts text from those PDFs and saves the cleaned output into `backend/data/raw/`.

---

### 2. Raw text storage

All extracted source text is stored as plain `.txt` files in:

```text
backend/data/raw/
```

This folder is the main raw knowledge pool used for chunking.

Both website content and PDF content are normalized into the same format: plain text.

---

### 3. Chunking

The chunker reads every `.txt` file in `data/raw/` and splits the text into smaller overlapping chunks.

This is necessary because:

* large documents are too noisy for retrieval
* embeddings work better on smaller semantic units
* retrieval accuracy improves when each chunk focuses on a smaller topic

The chunking process uses:

* `chunk_size`
* `overlap`

The overlap ensures that important content near chunk boundaries is not lost.

Example:

If the chunk size is `100` and overlap is `10`:

* Chunk 1 covers words `1–100`
* Chunk 2 covers words `91–190`
* Chunk 3 covers words `181–280`

The repeated part between adjacent chunks creates continuity and helps retrieval.

---

### 4. Embeddings

Each chunk is converted into a vector using:

```python
SentenceTransformer("all-MiniLM-L6-v2")
```

This model transforms text into a fixed-size numerical representation.

The model learns semantic meaning, so similar concepts map to nearby points in vector space.

Example:

* “international student application”
* “foreign applicant admission process”

These are different phrases, but they can still be semantically close.

---

### 5. Vector storage with ChromaDB

The chunk vectors, text, and metadata are stored in:

```text
backend/data/vector_store/
```

ChromaDB is used as the vector database.

It stores:

* chunk text
* chunk id
* source filename
* embeddings
* vector index files

This makes semantic search efficient.

---

### 6. Retrieval

When the user asks a question, the retriever:

1. embeds the query
2. searches ChromaDB
3. finds the most similar chunks
4. returns them as context

This is the heart of RAG.

The retriever does not look for exact keyword matches only.
It compares meaning using vectors.

---

### 7. Answer generation

The retrieved chunks are then inserted into the Groq prompt.

Groq receives:

* system instructions
* retrieved MPGU context
* user question
* recent conversation history

Then Groq generates the final answer.

This makes the response grounded in the official knowledge base.

---

## Backend modules

### `run.py`

Local backend launcher.

Responsibilities:

* print startup information
* validate configuration
* start Uvicorn
* load `app.main:app`

---

### `app/main.py`

FastAPI application entry point.

Responsibilities:

* create the FastAPI app
* configure CORS
* register routers
* expose `/` and `/health`

---

### `app/routes/chat.py`

API route layer.

Responsibilities:

* receive chat requests
* call the chat engine
* return typed responses
* support history clearing and history retrieval

Routes:

* `POST /api/v1/chat`
* `GET /api/v1/chat/history/{user_id}`
* `DELETE /api/v1/chat/history/{user_id}`

---

### `app/services/chat_engine.py`

Core orchestration layer.

Responsibilities:

* load static fallback knowledge
* detect language
* maintain session memory
* route between greeting fallback and RAG flow
* call the retriever
* build Groq prompts
* parse Groq responses
* return structured chat results

This file is the central brain of the chatbot.

---

### `app/schemas.py`

Typed request/response models.

Responsibilities:

* validate input JSON
* validate output JSON
* keep the API contract consistent

Typical models:

* `ChatMessage`
* `ChatReply`
* `HealthResponse`
* `ChatHistoryResponse`
* `ClearHistoryResponse`

---

### `app/config.py`

Configuration module.

Responsibilities:

* load `.env`
* store environment variables
* define API host and port
* define Groq settings
* define allowed CORS origins
* configure logging

---

## Ingestion modules

### `ingestion/crawler.py`

Recursive website crawler.

Responsibilities:

* start from MPGU homepage
* discover internal links
* crawl MPGU pages
* extract visible text
* avoid external domains
* save cleaned content locally

---

### `ingestion/web_loader.py`

Website content loader.

Responsibilities:

* fetch website HTML
* parse the page
* remove junk tags
* extract text
* save it as `.txt`

---

### `ingestion/pdf_loader.py`

PDF ingestion script.

Responsibilities:

* read PDFs from `ingestion/pdfs/`
* extract text page by page
* clean extracted text
* write `.txt` files into `data/raw/`

Library used:

* `PyMuPDF` (`fitz`)

---

### `ingestion/clean_text.py`

Text normalization helper.

Responsibilities:

* collapse whitespace
* remove extra lines
* normalize noisy text

---

### `ingestion/urls.py`

Contains starting URL lists or target URLs for crawling.

---

## RAG modules

### `rag/chunker.py`

Reads raw text files and splits them into chunks.

Responsibilities:

* load files from `data/raw/`
* split each file into overlapping chunks
* assign chunk ids
* preserve source filenames

The overlapping strategy preserves boundary context.

---

### `rag/embed_store.py`

Creates and stores embeddings.

Responsibilities:

* load chunked text
* embed each chunk with Sentence Transformers
* initialize ChromaDB
* store documents and embeddings in the vector store

This script creates the semantic index.

---

### `rag/retriever.py`

Semantic retrieval engine.

Responsibilities:

* embed the user query
* search the vector DB
* retrieve the most relevant chunks
* return them with source metadata and distances

---

## Data directories

### `backend/data/raw/`

Plain extracted text from websites and PDFs.

### `backend/data/vector_store/`

ChromaDB persistence directory.

### `backend/data/processed/`

Optional intermediate files or future structured outputs.

### `backend/data/knowledge_base.json`

Static fallback responses and intent-based replies.

---

## Runtime conversation flow

A typical live query goes through this path:

1. User types a question in the frontend.
2. JavaScript sends a `fetch()` request.
3. FastAPI receives the request at `/api/v1/chat`.
4. Pydantic validates the payload.
5. `chat.py` calls `chat_engine.process()`.
6. `chat_engine.py` decides the path.
7. The retriever embeds the query.
8. ChromaDB returns the closest chunks.
9. Those chunks are inserted into a Groq prompt.
10. Groq generates the answer.
11. The backend returns JSON.
12. The frontend displays the answer and metadata.

---

## Semantic retrieval in this project

Semantic search is what makes the chatbot intelligent.

Instead of searching for exact words, the system searches by meaning.

For example, these phrases can all lead to similar results:

* “How do I apply?”
* “What is the admission procedure?”
* “How can foreign students enroll?”
* “Tell me about the application process”

This is possible because the embedding model maps text into a semantic vector space.

---

## Models used in the project

### 1. Embedding model

Used for:

* chunk embeddings
* query embeddings
* semantic retrieval

Model:

```text
all-MiniLM-L6-v2
```

Library:

```text
sentence-transformers
```

---

### 2. Groq LLM

Used for:

* final answer generation
* context-aware response formatting
* conversation-style replies

Model:

```text
llama-3.1-8b-instant
```

Provider:

```text
Groq
```

---

### 3. PDF extraction engine

Used for PDF-to-text conversion.

Library:

```text
PyMuPDF
```

---

### 4. Web parsing tools

Used for crawling and HTML parsing.

Libraries:

* requests
* BeautifulSoup4
* lxml

---

### 5. Vector database

Used for storing and searching embeddings.

Tool:

```text
ChromaDB
```

---

## How to run locally

### 1. Create and activate the virtual environment

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Set environment variables

Create `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
GROQ_API_URL_TEMPLATE=https://api.groq.com/openai/v1/chat/completions
REQUEST_TIMEOUT_SECONDS=20
API_HOST=127.0.0.1
API_PORT=5000
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

---

### 4. Build or refresh the knowledge base

If you add new website pages or PDFs:

```bash
python ingestion/pdf_loader.py
python ingestion/crawler.py
python rag/chunker.py
python rag/embed_store.py
```

If the vector DB becomes incompatible after dependency changes, rebuild it:

```bash
rm -rf data/vector_store
python rag/embed_store.py
```

---

### 5. Start the backend

```bash
python run.py
```

---

### 6. Start the frontend

From the frontend folder:

```bash
python3 -m http.server 8000
```

Open:

```text
http://127.0.0.1:8000
```

---

## API endpoints

### `GET /`

Returns service info.

### `GET /health`

Returns health/status information.

### `POST /api/v1/chat`

Main chat endpoint.

Example request:

```json
{
  "message": "How can international students apply?",
  "user_id": "user_123"
}
```

Example response:

```json
{
  "reply": "...",
  "message_id": 1234,
  "user_id": "user_123",
  "source": "rag",
  "intent": "admission",
  "confidence": 0.92,
  "language": "en",
  "provider_attempted": "groq",
  "provider_status": "ok",
  "fallback_reason": null
}
```

### `GET /api/v1/chat/history/{user_id}`

Returns recent session messages.

### `DELETE /api/v1/chat/history/{user_id}`

Clears conversation history for a user.

---

## Project strengths

* Real RAG architecture
* Official university content ingestion
* Semantic retrieval
* PDF support
* Bilingual response handling
* Typed API design
* Modular backend structure
* Easy extension for more sources
* Good interview/demo value

---

## Current limitations

* Conversation memory is in-process only
* No persistent user authentication yet
* No PostgreSQL/Redis storage yet
* Vector store rebuild is needed after major dependency changes
* Some raw website text may still include navigation/footer noise

---

## Future upgrades

Possible next improvements:

* cleaner page extraction and better crawl filtering
* hybrid retrieval (keyword + vector)
* chunk metadata filtering
* re-ranking layer
* source citation in answers
* persistent chat history database
* Redis caching
* JWT authentication
* rate limiting
* Docker deployment
* cloud deployment
* OCR support for scanned PDFs
* better multilingual retrieval

---

## Interview positioning

This project is a strong portfolio piece because it shows that you can build a complete AI application stack:

* data ingestion
* document processing
* embedding generation
* vector search
* LLM orchestration
* API design
* frontend integration
* graceful fallback handling

A good one-line summary for recruiters:

> Built a FastAPI-based bilingual MPGU assistant with website/PDF ingestion, chunking, embeddings, ChromaDB semantic retrieval, and Groq-powered grounded answers.

---

## License

Add a license before public distribution.

Recommended options:

* MIT
* Apache 2.0

---

## A note on maintenance

Whenever you update the knowledge sources, remember to regenerate embeddings so the chatbot stays in sync with the latest MPGU content.

---

## Final note

This project is no longer a simple chatbot. It is a complete retrieval-based university assistant with a clean architecture that can be extended into a production-grade AI system.
