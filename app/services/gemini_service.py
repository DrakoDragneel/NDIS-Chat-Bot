import requests
from typing import Any, Dict, List
from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.prompts.system_prompt import SYSTEM_PROMPT

class GeminiError(Exception):
    pass

def build_context(context_items: List[Dict[str, Any]]) -> str:
    blocks = []
    for index, item in enumerate(context_items, start=1):
        keywords = item.get("keywords", []) or []
        keywords_text = ", ".join(str(k) for k in keywords) if isinstance(keywords, list) else str(keywords)
        blocks.append(f"""
SOURCE {index}
Category: {item.get("category", "")}
Subcategory: {item.get("subcategory", "")}
Question: {item.get("question", "")}
Answer: {item.get("answer", "")}
Keywords: {keywords_text}
Source document: {item.get("source", "")}
""".strip())
    return "\\n\\n".join(blocks)

def generate_gemini_answer(user_question: str, context_items: List[Dict[str, Any]]) -> str:
    if not GEMINI_API_KEY:
        raise GeminiError("GEMINI_API_KEY is missing. Add it to your .env file.")

    prompt = f"""
{SYSTEM_PROMPT}

User question:
{user_question}

Use only this NDIS dataset context:
{build_context(context_items)}
""".strip()

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "topP": 0.9, "maxOutputTokens": 700}
    }

    response = requests.post(url, json=payload, timeout=45)
    if response.status_code >= 400:
        raise GeminiError(f"Gemini API error {response.status_code}: {response.text}")

    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise GeminiError(f"Unexpected Gemini response format: {data}") from exc
