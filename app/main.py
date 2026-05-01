from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.dataset_search import search_dataset
from app.services.gemini_service import generate_gemini_answer, GeminiError
from app.services.suggestion_service import get_suggestions, should_show_contact


app = FastAPI(
    title="NDIS Chatbot Backend",
    description="Gemini-only RAG backend for NDIS chatbot.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your WordPress domain before production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


NDIS_KEYWORDS = [
    "ndis",
    "national disability insurance scheme",
    "disability",
    "participant",
    "plan",
    "plans",
    "funding",
    "budget",
    "support",
    "supports",
    "provider",
    "providers",
    "sil",
    "sda",
    "supported independent living",
    "specialist disability accommodation",
    "plan manager",
    "plan management",
    "support coordinator",
    "support coordination",
    "ndia",
    "ndis commission",
    "quality and safeguards",
    "eligibility",
    "eligible",
    "qualify",
    "access request",
    "application",
    "apply",
    "review",
    "reassessment",
    "therapy",
    "assistive technology",
    "home modification",
    "transport",
    "community participation",
    "personal care",
    "behaviour support",
    "service agreement",
    "invoice",
    "claim",
    "pricing",
    "price limit",
    "registered provider",
    "unregistered provider",
    "carer",
    "advocacy",
    "respite",
    "short term accommodation",
    "sta",
    "rent",
    "housing",
    "groceries",
    "food",
    "gym",
    "travel",
    "complaint",
    "unsafe",
    "support worker",
]


def is_ndis_related(message: str) -> bool:
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in NDIS_KEYWORDS)


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

    # Backend-level scope protection
    if not is_ndis_related(message):
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
        answer = generate_gemini_answer(message, context_items)
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