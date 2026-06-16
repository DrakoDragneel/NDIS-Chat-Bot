import json
import numpy as np
from typing import Any, Dict, List

from app.config import DATASET_PATH


def _load_dataset() -> List[Dict[str, Any]]:
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Dataset JSON must be a list of objects.")

    return data


def _build_entry_text(item: Dict[str, Any]) -> str:
    """
    Combine the most meaningful fields into a single string for embedding.
    Keywords and subcategory are included so the model captures topic signals.
    """
    keywords = item.get("keywords", []) or []
    if isinstance(keywords, list):
        keywords_str = " ".join(str(k) for k in keywords)
    else:
        keywords_str = str(keywords)

    parts = [
        item.get("category", ""),
        item.get("subcategory", ""),
        item.get("question", ""),
        item.get("answer", ""),
        keywords_str,
    ]
    return " ".join(p for p in parts if p).strip()


def _cosine_similarity(vec_a: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between a single query vector and every row
    in a pre-normalised embedding matrix.  Both sides are L2-normalised so
    the dot product equals cosine similarity directly.
    """
    norm_a = np.linalg.norm(vec_a)
    if norm_a == 0:
        return np.zeros(matrix.shape[0])
    vec_a_norm = vec_a / norm_a

    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1e-10, norms)
    matrix_norm = matrix / norms

    return matrix_norm.dot(vec_a_norm)


# ---------------------------------------------------------------------------
# Module-level initialisation — runs once on startup
# ---------------------------------------------------------------------------

print("[dataset_search] Loading dataset...")
DATASET: List[Dict[str, Any]] = _load_dataset()
print(f"[dataset_search] {len(DATASET)} entries loaded.")

print("[dataset_search] Loading sentence-transformer model...")
try:
    from sentence_transformers import SentenceTransformer  # type: ignore
    _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    print("[dataset_search] Model loaded.")

    _ENTRY_TEXTS = [_build_entry_text(item) for item in DATASET]

    print("[dataset_search] Embedding dataset entries...")
    _EMBEDDINGS: np.ndarray = _MODEL.encode(
        _ENTRY_TEXTS,
        convert_to_numpy=True,
        show_progress_bar=False,
        batch_size=64,
    )
    print(f"[dataset_search] Embeddings ready — shape {_EMBEDDINGS.shape}.")
    _VECTOR_SEARCH_AVAILABLE = True

except ImportError:
    print(
        "[dataset_search] WARNING: sentence-transformers not installed. "
        "Falling back to keyword search. "
        "Run: pip install sentence-transformers"
    )
    _MODEL = None
    _EMBEDDINGS = None
    _VECTOR_SEARCH_AVAILABLE = False


# ---------------------------------------------------------------------------
# Keyword fallback (kept as a safety net)
# ---------------------------------------------------------------------------

import re
from typing import Set

_STOP_WORDS: Set[str] = {
    "a", "an", "the", "is", "are", "am", "i", "me", "my", "you", "your",
    "can", "could", "would", "should", "do", "does", "did", "for", "to",
    "of", "in", "on", "at", "with", "and", "or", "it", "this", "that",
    "what", "how", "why", "when", "where", "who", "if", "about", "use",
    "using", "ndis",
}


def _normalize(text: Any) -> str:
    text = str(text or "").lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _tokenize(text: Any) -> List[str]:
    return [w for w in _normalize(text).split() if w not in _STOP_WORDS and len(w) > 2]


def _keyword_score(item: Dict[str, Any], query_terms: List[str]) -> int:
    combined = _normalize(
        " ".join([
            item.get("category", ""),
            item.get("subcategory", ""),
            item.get("question", ""),
            item.get("answer", ""),
            " ".join(item.get("keywords", []) or []),
        ])
    )
    return sum(12 if t in _normalize(item.get("question", "")) else 2
               for t in query_terms if t in combined)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def search_dataset(user_question: str, limit: int = 6) -> List[Dict[str, Any]]:
    """
    Return the *limit* most relevant dataset entries for *user_question*.

    Uses semantic (vector) search when sentence-transformers is available,
    otherwise falls back to keyword matching.
    """
    if _VECTOR_SEARCH_AVAILABLE and _MODEL is not None and _EMBEDDINGS is not None:
        query_vec: np.ndarray = _MODEL.encode(
            user_question,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        scores = _cosine_similarity(query_vec, _EMBEDDINGS)

        # Attach scores and filter out very weak matches (similarity < 0.25)
        results = []
        for idx, score in enumerate(scores):
            if score >= 0.25:
                item_copy = dict(DATASET[idx])
                item_copy["_score"] = round(float(score), 4)
                results.append(item_copy)

        results.sort(key=lambda x: x["_score"], reverse=True)
        return results[:limit]

    # --- keyword fallback ---
    query_terms = _tokenize(user_question)
    results = []
    for item in DATASET:
        s = _keyword_score(item, query_terms)
        if s > 0:
            item_copy = dict(item)
            item_copy["_score"] = s
            results.append(item_copy)
    results.sort(key=lambda x: x["_score"], reverse=True)
    return results[:limit]
