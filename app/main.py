from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from app.services.dataset_search import search_dataset
from app.services.gemini_service import generate_gemini_answer, GeminiError
from app.services.suggestion_service import get_suggestions, should_show_contact


app = FastAPI(
    title="NDIS Chatbot Backend",
    description="Gemini RAG backend with semantic search for NDIS chatbot.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your WordPress domain before production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str          # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []  # conversation history for multi-turn


# ---------------------------------------------------------------------------
# NDIS scope guard
# ---------------------------------------------------------------------------

NDIS_KEYWORDS = [
    "ndis", "national disability insurance scheme", "disability", "participant",
    "plan", "plans", "funding", "budget", "support", "supports", "provider",
    "providers", "sil", "sda", "supported independent living",
    "specialist disability accommodation", "plan manager", "plan management",
    "support coordinator", "support coordination", "ndia", "ndis commission",
    "quality and safeguards", "eligibility", "eligible", "qualify",
    "access request", "application", "apply", "review", "reassessment",
    "therapy", "assistive technology", "home modification", "transport",
    "community participation", "personal care", "behaviour support",
    "service agreement", "invoice", "claim", "pricing", "price limit",
    "registered provider", "unregistered provider", "carer", "advocacy",
    "respite", "short term accommodation", "sta", "rent", "housing",
    "groceries", "food", "gym", "travel", "complaint", "unsafe",
    "support worker",
]


def is_ndis_related(message: str) -> bool:
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in NDIS_KEYWORDS)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def health_check():
    return {
        "status": "running",
        "message": "NDIS chatbot FastAPI backend is running.",
        "docs": "/docs",
        "chat_endpoint": "/api/chat",
    }


@app.post("/api/chat")
def chat(request: ChatRequest):
    message = (request.message or "").strip()

    if not message:
        raise HTTPException(status_code=400, detail="Message is required.")

    # Build conversation context string from history (most recent 6 turns)
    history_context = ""
    if request.history:
        recent = request.history[-6:]
        history_context = "\n".join(
            f"{msg.role.capitalize()}: {msg.content}" for msg in recent
        )

    # Scope guard — check against full message + last user turn for follow-ups
    full_check = message
    if request.history:
        last_user = next(
            (m.content for m in reversed(request.history) if m.role == "user"),
            "",
        )
        full_check = f"{last_user} {message}"

    if not is_ndis_related(full_check):
        return {
            "answer": (
                "I'm here to help with NDIS-related questions only. "
                "Please ask about NDIS eligibility, services, funding, providers, plans, "
                "plan management, reviews, or support."
            ),
            "suggestions": [
                "What is NDIS?",
                "How does NDIS funding work?",
                "What services does NDIS cover?",
            ],
            "show_contact": False,
            "sources": [],
        }

    context_items = search_dataset(message, limit=6)

    if not context_items:
        return {
            "answer": (
                "I do not have enough information in my NDIS dataset to answer that clearly. "
                "For official guidance, please contact the NDIA for plan, funding, access, "
                "or payment questions, or the NDIS Quality and Safeguards Commission for "
                "provider safety, complaints, or incident concerns."
            ),
            "suggestions": [
                "What is NDIS?",
                "How does NDIS funding work?",
                "How do I apply for NDIS?",
            ],
            "show_contact": True,
            "sources": [],
        }

    try:
        # Pass conversation history into the answer generator
        answer = generate_gemini_answer(message, context_items, history_context)
    except GeminiError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while generating the response.",
        ) from exc

    sources = [
        {
            "category": item.get("category", ""),
            "subcategory": item.get("subcategory", ""),
            "question": item.get("question", ""),
            "source": item.get("source") or item.get("source_document", ""),
            "score": item.get("_score", 0),
        }
        for item in context_items
    ]

    suggestions = get_suggestions(message, context_items)
    show_contact = should_show_contact(message, answer)

    return {
        "answer": answer,
        "suggestions": suggestions,
        "show_contact": show_contact,
        "sources": sources,
    }
