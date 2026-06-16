import requests
from typing import Any, Dict, List, Optional

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.prompts.system_prompt import SYSTEM_PROMPT


class GeminiError(Exception):
    pass


def build_context(context_items: List[Dict[str, Any]]) -> str:
    blocks = []
    for index, item in enumerate(context_items, start=1):
        keywords = item.get("keywords", []) or []
        keywords_text = (
            ", ".join(str(k) for k in keywords)
            if isinstance(keywords, list)
            else str(keywords)
        )
        block = (
            f"SOURCE {index}\n"
            f"Category: {item.get('category', '')}\n"
            f"Subcategory: {item.get('subcategory', '')}\n"
            f"Question: {item.get('question', '')}\n"
            f"Answer: {item.get('answer', '')}\n"
            f"Keywords: {keywords_text}\n"
            f"Source document: {item.get('source', '') or item.get('source_document', '')}"
        )
        blocks.append(block)
    # FIX: was "\\n\\n" (literal backslash-n) — now a real newline separator
    return "\n\n".join(blocks)


def generate_gemini_answer(
    user_question: str,
    context_items: List[Dict[str, Any]],
    history_context: Optional[str] = "",
) -> str:
    if not GEMINI_API_KEY:
        raise GeminiError("GEMINI_API_KEY is missing. Add it to your .env file.")

    # Include conversation history so the model handles follow-up questions
    history_section = ""
    if history_context:
        history_section = f"\nConversation so far:\n{history_context}\n"

    prompt = (
        f"{SYSTEM_PROMPT}"
        f"{history_section}\n\n"
        f"User question:\n{user_question}\n\n"
        f"Use only this NDIS dataset context:\n{build_context(context_items)}"
    )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.9,
            "maxOutputTokens": 700,
        },
    }

    response = requests.post(url, json=payload, timeout=45)
    if response.status_code >= 400:
        raise GeminiError(
            f"Gemini API error {response.status_code}: {response.text}"
        )

    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise GeminiError(
            f"Unexpected Gemini response format: {data}"
        ) from exc
