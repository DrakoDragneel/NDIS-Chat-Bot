def get_suggestions(message: str, context_items: list) -> list:
    msg = message.lower()

    if "fund" in msg or "budget" in msg or "pay" in msg:
        return [
            "What is NDIS funding?",
            "How does NDIS funding work?",
            "What can NDIS funding be used for?"
        ]

    if "eligib" in msg or "qualify" in msg or "apply" in msg:
        return [
            "Who is eligible for NDIS?",
            "What evidence do I need for NDIS?",
            "How do I apply for NDIS?"
        ]

    if "provider" in msg:
        return [
            "What is an NDIS provider?",
            "Can I change providers?",
            "What is a service agreement?"
        ]

    if "plan" in msg or "review" in msg:
        return [
            "What is an NDIS plan?",
            "How do I request a plan review?",
            "Can NDIS reduce my funding?"
        ]

    if "sil" in msg or "sda" in msg or "housing" in msg:
        return [
            "What is the difference between SIL and SDA?",
            "Can I get both SIL and SDA?",
            "Does NDIS pay rent?"
        ]

    return [
        "What is NDIS?",
        "How does NDIS funding work?",
        "What services does NDIS cover?"
    ]


def should_show_contact(message: str, answer: str) -> bool:
    combined = f"{message} {answer}".lower()

    contact_triggers = [
        "contact",
        "team",
        "speak",
        "call",
        "help me",
        "not enough information",
        "provider",
        "complaint",
        "unsafe",
        "urgent",
        "apply",
        "review"
    ]

    return any(trigger in combined for trigger in contact_triggers)