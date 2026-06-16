from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Suggestions
# ---------------------------------------------------------------------------

# Map category names to a curated set of follow-up questions.
# Pulled from real questions already in the dataset so suggestions
# always reflect actual content the bot can answer.
_CATEGORY_SUGGESTIONS: Dict[str, List[str]] = {
    "Plans & Funding": [
        "What can NDIS funding be used for?",
        "What happens if my NDIS budget runs out?",
        "What is the difference between core and capacity building funding?",
    ],
    "Eligibility": [
        "Who is eligible for NDIS?",
        "What evidence do I need to apply for NDIS?",
        "Can I apply for NDIS if my condition is not permanent?",
    ],
    "Providers": [
        "What is the difference between registered and unregistered providers?",
        "Can I change my NDIS provider?",
        "What is a service agreement?",
    ],
    "Plan Management": [
        "What is self-managed NDIS?",
        "What does a plan manager do?",
        "Can I switch between plan management types?",
    ],
    "Plan Review & Changes": [
        "How do I request an NDIS plan review?",
        "What happens if my NDIS funding is reduced?",
        "Can I request an early plan review?",
    ],
    "Services": [
        "What therapies does NDIS fund?",
        "What is the difference between SIL and SDA?",
        "Does NDIS cover assistive technology?",
    ],
    "Application Process": [
        "How do I apply for NDIS?",
        "What documents do I need for my NDIS application?",
        "How long does the NDIS application process take?",
    ],
    "Rules, Compliance & Safety": [
        "How do I make a complaint about an NDIS provider?",
        "What are my rights as an NDIS participant?",
        "What is the NDIS Quality and Safeguards Commission?",
    ],
    "Pricing & Payments": [
        "How does NDIS pay providers?",
        "What is the NDIS price guide?",
        "What should I do if a provider overcharges me?",
    ],
    "Participant Support": [
        "What does a support coordinator do?",
        "Can my family member be my support worker?",
        "How can I get advocacy support through NDIS?",
    ],
    "Real User Questions": [
        "Can I use NDIS for gym membership?",
        "Does NDIS cover rent or housing?",
        "Can I use NDIS for travel?",
    ],
    "Edge Cases": [
        "What happens to my NDIS plan if I go to hospital?",
        "Can I use NDIS if I move interstate?",
        "Does NDIS support people who are employed?",
    ],
    "NDIS Basics": [
        "What is NDIS?",
        "What is the difference between NDIA and NDIS?",
        "What does 'reasonable and necessary' mean?",
    ],
}

_DEFAULT_SUGGESTIONS: List[str] = [
    "What is NDIS?",
    "How does NDIS funding work?",
    "What services does NDIS cover?",
]


def get_suggestions(
    message: str,
    context_items: List[Dict[str, Any]],
) -> List[str]:
    """
    Return 3 follow-up suggestions based on the categories found in the
    search results.  Falls back to defaults when no results are available.
    """
    if not context_items:
        return _DEFAULT_SUGGESTIONS

    # Count category hits across returned results (highest-scored items first)
    category_counts: Dict[str, int] = {}
    for item in context_items:
        cat = item.get("category", "")
        if cat:
            category_counts[cat] = category_counts.get(cat, 0) + 1

    # Pick the most represented category
    if category_counts:
        top_category = max(category_counts, key=lambda c: category_counts[c])
        suggestions = _CATEGORY_SUGGESTIONS.get(top_category)
        if suggestions:
            # Avoid suggesting the exact question the user just asked
            msg_lower = message.lower().strip()
            filtered = [s for s in suggestions if s.lower().strip() != msg_lower]
            return (filtered + _DEFAULT_SUGGESTIONS)[:3]

    return _DEFAULT_SUGGESTIONS


# ---------------------------------------------------------------------------
# Contact banner
# ---------------------------------------------------------------------------

_CONTACT_TRIGGERS = {
    "contact", "team", "speak", "call", "help me",
    "not enough information", "complaint", "unsafe", "urgent",
    "apply", "review",
}

# Exclude "provider" as a blanket trigger — it fires too often and is not
# always a signal that the user needs human help.
def should_show_contact(message: str, answer: str) -> bool:
    combined = f"{message} {answer}".lower()
    return any(trigger in combined for trigger in _CONTACT_TRIGGERS)
