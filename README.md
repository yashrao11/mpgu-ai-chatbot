````md
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
````

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

Both website content and PDF content are normalized into the same format: plain text.

---

### 3. Chunking

The chunker reads every `.txt` file in `data/raw/` and splits the text into smaller overlapping chunks.

Why this matters:

* improves retrieval accuracy
* avoids large-context noise
* keeps semantic coherence

Example:

If chunk size is 100 and overlap is 10:

* Chunk 1: 1–100
* Chunk 2: 91–190
* Chunk 3: 181–280

---

### 4. Embeddings

Each chunk is converted into a vector using:

```python
SentenceTransformer("all-MiniLM-L6-v2")
```

This model maps semantic meaning into vector space.

Example similarity:

* “admission process”
* “how to apply for university”

---

### 5. Vector storage with ChromaDB

Stored in:

```text
backend/data/vector_store/
```

ChromaDB stores:

* embeddings
* metadata
* chunk text
* document IDs

---

### 6. Retrieval

When a query is received:

1. Query is embedded
2. Compared with stored vectors
3. Top-k similar chunks are retrieved
4. Passed as context

---

### 7. Answer generation

Groq LLM receives:

* system prompt
* retrieved context
* user query
* chat history

Then generates grounded response.

---

## Backend modules

### run.py

Starts FastAPI server via Uvicorn.

### app/main.py

App entry point, CORS, routing.

### app/routes/chat.py

Handles:

* `/chat`
* history endpoints

### app/services/chat_engine.py

Core orchestration:

* routing logic
* RAG pipeline
* LLM calls

### app/schemas.py

Pydantic models for request/response validation.

### app/config.py

Environment + API configuration.

---

## Ingestion modules

### crawler.py

Crawls MPGU website and extracts text.

### pdf_loader.py

Extracts PDF text using PyMuPDF.

### clean_text.py

Normalizes extracted text.

### urls.py

Seed URLs for crawling.

---

## RAG modules

### chunker.py

Splits raw text into overlapping chunks.

### embed_store.py

Creates embeddings and stores in ChromaDB.

### retriever.py

Performs semantic search.

---

## Data directories

### data/raw/

Raw extracted text.

### data/vector_store/

ChromaDB storage.

### data/processed/

Optional intermediate outputs.

### knowledge_base.json

Fallback responses.

---

## Runtime flow

1. User sends message
2. Frontend sends request
3. FastAPI receives it
4. chat_engine processes it
5. Retriever finds context
6. Groq generates answer
7. Response returned to UI

---

## Semantic search behavior

The system understands meaning, not just keywords.

Example:

* “How to apply?”
* “Admission process”
* “Enrollment steps”

All map to similar embeddings.

---

## Models used

### Embedding model

```
all-MiniLM-L6-v2
```

### LLM

```
llama-3.1-8b-instant
```

### Vector DB

```
ChromaDB
```

### PDF parsing

```
PyMuPDF
```

---

## How to run locally

### 1. Create environment

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```env
GROQ_API_KEY=your_key
GROQ_MODEL=llama-3.1-8b-instant
```

### 4. Build knowledge base

```bash
python ingestion/pdf_loader.py
python ingestion/crawler.py
python rag/chunker.py
python rag/embed_store.py
```

### 5. Run backend

```bash
python run.py
```

### 6. Run frontend

```bash
python -m http.server 8000
```

---

## API endpoints

### GET /

Service info

### GET /health

Health check

### POST /api/v1/chat

Main chat endpoint

### GET /history/{user_id}

Fetch chat history

### DELETE /history/{user_id}

Clear history

---

## Strengths

* Full RAG pipeline
* Real-world ingestion
* Semantic search
* Modular architecture
* API-first design
* Bilingual support

---

## Limitations

* No persistent DB
* In-memory chat history
* Manual vector rebuild
* Some noisy crawl data

---

## Future improvements

* PostgreSQL + Redis integration
* JWT authentication
* Hybrid retrieval (BM25 + vector)
* Re-ranking layer
* Docker deployment
* Cloud hosting
* OCR support
* Better multilingual tuning

---

## Interview summary

> Built a FastAPI-based bilingual RAG chatbot for MPGU using website/PDF ingestion, embeddings, ChromaDB semantic retrieval, and Groq LLM for grounded responses.

---

## License

MIT or Apache 2.0 recommended.

---

## Final note

This system demonstrates a complete production-style RAG pipeline, from raw data ingestion to LLM-powered contextual answers.

```
```
