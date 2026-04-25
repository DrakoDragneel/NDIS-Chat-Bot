# NDIS Chatbot Backend — Python FastAPI + Gemini

## Requirements

Install before running:

1. Python 3.10 or newer
2. A Gemini API key from Google AI Studio

## Setup

```bash
cd ndis-chatbot-backend-python
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

Create `.env` file:

```env
GEMINI_API_KEY=your_new_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
PORT=5000
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
```

Open:

```txt
http://localhost:5000
```

API docs/testing page:

```txt
http://localhost:5000/docs
```

## Test with PowerShell

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/chat" -Method POST -ContentType "application/json" -Body '{"message":"Can I use NDIS for rent?"}'
```

## Production notes

- Change CORS from `*` to your WordPress domain.
- Keep `.env` private.
- Add rate limiting before public launch.
- Upgrade keyword search to vector search later.
