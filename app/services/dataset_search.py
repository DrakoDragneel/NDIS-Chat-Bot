import json
import re
from typing import Any, Dict, List, Set

from app.config import DATASET_PATH


STOP_WORDS = {
    "a", "an", "the", "is", "are", "am", "i", "me", "my", "you", "your",
    "can", "could", "would", "should", "do", "does", "did", "for", "to",
    "of", "in", "on", "at", "with", "and", "or", "it", "this", "that",
    "what", "how", "why", "when", "where", "who", "if", "about", "use",
    "using", "ndis"
}


def _load_dataset() -> List[Dict[str, Any]]:
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Dataset JSON must be a list of objects.")

    return data


DATASET = _load_dataset()


def normalize(text: Any) -> str:
    if text is None:
        return ""

    text = str(text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def tokenize(text: Any) -> List[str]:
    normalized = normalize(text)
    words = normalized.split()

    return [
        word for word in words
        if word not in STOP_WORDS and len(word) > 2
    ]


def get_keywords(item: Dict[str, Any]) -> List[str]:
    keywords = item.get("keywords", []) or []

    if isinstance(keywords, str):
        return [keywords]

    if isinstance(keywords, list):
        return [str(keyword) for keyword in keywords]

    return []


def calculate_score(
    item: Dict[str, Any],
    query: str,
    query_terms: List[str],
    query_term_set: Set[str],
) -> int:
    category = item.get("category", "")
    subcategory = item.get("subcategory", "")
    question = item.get("question", "")
    answer = item.get("answer", "")
    keywords = get_keywords(item)

    question_norm = normalize(question)
    answer_norm = normalize(answer)
    category_norm = normalize(category)
    subcategory_norm = normalize(subcategory)
    keyword_norm = normalize(" ".join(keywords))

    combined_norm = normalize(
        " ".join([
            str(category),
            str(subcategory),
            str(question),
            str(answer),
            " ".join(keywords),
        ])
    )

    item_terms = set(tokenize(combined_norm))

    score = 0

    # Exact or near-exact question match
    if query and query == question_norm:
        score += 100

    if query and query in question_norm:
        score += 60

    # Important: question match is stronger than answer/body match
    for term in query_terms:
        if term in question_norm:
            score += 12

        if term in keyword_norm:
            score += 10

        if term in subcategory_norm:
            score += 8

        if term in category_norm:
            score += 5

        if term in answer_norm:
            score += 2

    # Overlap ratio bonus
    overlap = query_term_set.intersection(item_terms)

    if query_term_set:
        overlap_ratio = len(overlap) / len(query_term_set)
        score += int(overlap_ratio * 30)

    # Strong phrase intent matching
    phrase_boosts = [
        ("rent", ["rent", "housing", "accommodation", "sda", "sil"]),
        ("groceries", ["food", "groceries", "meal", "meals"]),
        ("food", ["food", "groceries", "meal", "meals"]),
        ("gym", ["gym", "exercise", "therapy"]),
        ("travel", ["travel", "transport", "holidays", "holiday"]),
        ("therapy", ["therapy", "ot", "speech", "physio", "physiotherapy"]),
        ("provider", ["provider", "registered", "unregistered"]),
        ("plan manager", ["plan manager", "plan management", "invoice", "payment"]),
        ("support coordinator", ["support coordinator", "support coordination"]),
        ("review", ["review", "reassessment", "change in circumstances"]),
        ("complaint", ["complaint", "commission", "unsafe", "provider"]),
    ]

    for trigger, related_terms in phrase_boosts:
        if trigger in query:
            if any(term in combined_norm for term in related_terms):
                score += 20
            else:
                score -= 10

    # Penalize broad "Can I use NDIS for..." matches that only match generic words
    generic_questions = [
        "can i use ndis for",
        "does ndis cover",
        "can i pay",
    ]

    if any(generic in query for generic in generic_questions):
        important_query_terms = query_term_set.difference({
            "cover", "pay", "fund", "funding"
        })

        if important_query_terms:
            important_overlap = important_query_terms.intersection(item_terms)

            if not important_overlap:
                score -= 30

    return score


def search_dataset(user_question: str, limit: int = 6) -> List[Dict[str, Any]]:
    query = normalize(user_question)
    query_terms = tokenize(query)
    query_term_set = set(query_terms)

    scored_items = []

    for item in DATASET:
        score = calculate_score(
            item=item,
            query=query,
            query_terms=query_terms,
            query_term_set=query_term_set,
        )

        if score > 0:
            item_copy = dict(item)
            item_copy["_score"] = score
            scored_items.append(item_copy)

    scored_items.sort(key=lambda x: x["_score"], reverse=True)

    return scored_items[:limit]