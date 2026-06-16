# NDIS Chatbot Backend — Python FastAPI + Gemini + Semantic Search

## What changed in v2.0

- **Vector / semantic search** replaces the old keyword scorer.
  The bot now understands meaning, so "Do I qualify?" and "Am I eligible?"
  both find the right entries even if the wording differs from the dataset.
- **Conversation history** — the `/api/chat` endpoint now accepts an optional
  `history` array so follow-up questions ("what about for transport?") work
  correctly.
- **Bug fix** — context blocks sent to Gemini were joined with a literal
  `\n` string instead of a real newline. Fixed in `gemini_service.py`.
- **Smarter suggestions** — follow-up suggestions are now drawn from the
  same category as the search result instead of being fully hardcoded.

---

## Requirements

1. Python 3.10 or newer
2. A Gemini API key from [Google AI Studio](https://aistudio.google.com/)

---

## Setup

```bash
cd NDIS-Chat-Bot
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Install packages:

```bash
pip install -r requirements.txt
```

> **Note:** `sentence-transformers` will download the `all-MiniLM-L6-v2`
> model (~80 MB) on first startup. This happens once and is cached locally.

Create `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
PORT=5000
```

---

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
```

Open:

```
http://localhost:5000
```

API docs / testing page:

```
http://localhost:5000/docs
```

---

## API

### `POST /api/chat`

**Request body:**

```json
{
  "message": "How do I apply for NDIS?",
  "history": [
    { "role": "user", "content": "What is NDIS?" },
    { "role": "assistant", "content": "The NDIS is ..." }
  ]
}
```

`history` is optional. Pass the last few turns so the bot handles
follow-up questions correctly.

**Response:**

```json
{
  "answer": "...",
  "suggestions": ["...", "...", "..."],
  "show_contact": false,
  "sources": [
    {
      "category": "Application Process",
      "subcategory": "How to Apply",
      "question": "How do I apply for NDIS?",
      "source": "...",
      "score": 0.87
    }
  ]
}
```

---

## Test with PowerShell

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:5000/api/chat" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"message":"Can I use NDIS for rent?"}'
```

---

## Production checklist

- Change `allow_origins=["*"]` in `main.py` to your WordPress domain.
- Keep `.env` private and never commit it.
- Add rate limiting before public launch.
- The semantic model runs in-process — for high traffic consider moving
  embeddings to a dedicated vector store (ChromaDB, Qdrant, Pinecone).
