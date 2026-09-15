# RAG API

A minimal Retrieval-Augmented Generation service built with FastAPI. It indexes PDFs
into a local Chroma vector store and answers questions about them using Google Gemini.

Answers are grounded in the indexed documents only — if the retrieved context doesn't
contain the answer, the model is instructed to say it doesn't know.

## How it works

```
PDFs in documents/  ──►  split into chunks  ──►  Gemini embeddings  ──►  Chroma (chroma_db/)
                                                                              │
question ──►  retrieve top 3 chunks  ──►  prompt + context  ──►  Gemini  ──►  answer
```

## Requirements

- Python 3.10+ (3.9 works, but the Google client libraries emit end-of-life warnings)
- A Google Gemini API key — https://aistudio.google.com/apikey

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key_here
```

## Running

```bash
uvicorn app.main:app --reload
```

The API is served at http://127.0.0.1:8000, with interactive docs at
http://127.0.0.1:8000/docs.

## Usage

**1. Add documents.** Drop one or more PDFs into `documents/`.

**2. Index them.**

```bash
curl -X POST http://127.0.0.1:8000/api/ingest
# {"chunks_indexed": 42}
```

**3. Ask questions.**

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
# {"answer": "..."}
```

## Endpoints

| Method | Path          | Description                                              |
| ------ | ------------- | -------------------------------------------------------- |
| GET    | `/`           | Service banner                                            |
| GET    | `/health`     | Health check                                              |
| POST   | `/api/ingest` | Index every PDF in `documents/`; returns the chunk count  |
| POST   | `/api/chat`   | Answer `{"question": "..."}` from the indexed documents   |

## Project layout

```
app/
  main.py                  FastAPI app, routing, Gemini error handlers
  api/routes/chat.py       /ingest and /chat endpoints
  models/schema.py         Request models
  services/ingestion.py    PDF loading, chunking, embeddings, Chroma writes
  services/rag.py          Retrieval + prompt + Gemini call
documents/                 Source PDFs (gitignored)
chroma_db/                 Persisted vector store (gitignored)
```

## Configuration

| What        | Where                                          | Default                     |
| ----------- | ---------------------------------------------- | --------------------------- |
| Chat model  | [`app/services/rag.py`](app/services/rag.py)   | `gemini-3.6-flash`          |
| Embeddings  | [`app/services/ingestion.py`](app/services/ingestion.py) | `models/gemini-embedding-001` |
| Chunk size  | `app/services/ingestion.py`                    | 1000 chars, 200 overlap     |
| Retrieved chunks | `app/services/rag.py`                     | top 3                       |

Changing the embeddings model invalidates the existing index — delete `chroma_db/` and
re-run `/api/ingest` afterwards.

## Error handling

Gemini failures are mapped to HTTP responses in
[`app/main.py`](app/main.py) rather than surfacing as 500s:

| Condition                   | Status |
| --------------------------- | ------ |
| Quota / rate limit          | 429    |
| Bad or rejected credentials | 500    |
| Timeout, service down       | 504    |
| Any other upstream error    | 502    |

## Notes

- `/api/ingest` rebuilds from whatever is in `documents/` and appends to the existing
  store; it does not deduplicate or clear prior chunks. Delete `chroma_db/` for a clean
  rebuild.
- Both endpoints are synchronous and run in FastAPI's threadpool.
