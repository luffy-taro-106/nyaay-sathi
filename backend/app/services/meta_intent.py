"""Detect greetings, meta-questions, and vague topic intros so we respond like an advisor, not a RAG dump."""

import re
from app.models.schemas import CaseCategory


_TOPIC_INTRO_PATTERNS = [
    r"\b(help|assist|guide|advice)\b.*\b(with|on|regarding|about|for)\b",
    r"\bissue\b.*\b(with|on|regarding|about)\b",
    r"\bproblem\b.*\b(with|on|regarding|about)\b",
    r"\bquery\b.*\b(about|on|regarding)\b",
    r"\bquestion\b.*\b(about|on|regarding)\b",
    r"\b(i need|i want|i'd like|i would like)\b.*\b(help|assistance|advice|guidance)\b",
]
_INTRO_WORD_THRESHOLD = 12  # short messages are usually just a topic, not facts


def is_meta_help_request(user_text: str) -> bool:
    """
    True when the user is asking who we are / how we help, not describing a legal fact pattern.

    Avoid matching substantive questions like "can you help me get my wages back".
    """
    t = user_text.strip().lower()
    if len(t) > 220:
        return False

    if any(
        p in t
        for p in (
            "how can you help",
            "how could you help",
            "how may you help",
            "what can you do",
            "what do you do",
            "who are you",
            "tell me about yourself",
            "introduce yourself",
            "what is nyaay",
            "what's nyaay",
            "what are you",
            "are you a bot",
            "are you an ai",
            "you a chatbot",
        )
    ):
        return True

    # Short standalone greetings
    if re.match(
        r"^(hi|hello|hey|namaste|namaskar|good morning|good evening)\b[!.,?…\s]*$",
        t,
    ):
        return True

    if t in ("help", "help me", "i need help", "can you help me", "can you help me?"):
        return True

    return False


def is_vague_topic_intro(user_text: str) -> bool:
    """
    True when the message names a topic but doesn't describe what happened — the assistant
    should acknowledge the topic and ask clarifying questions instead of pulling reference
    snippets.

    Examples that match: "I have an issue regarding my land", "help me with my rent",
    "can you help me with a problem about wages".
    Examples that DON'T match (have facts): "my employer hasn't paid me for 3 months",
    "landlord changed locks last week and kept my deposit".
    """
    t = user_text.strip().lower()
    if not t:
        return False

    has_concrete_facts = (
        any(ch.isdigit() for ch in t)
        or any(
            kw in t
            for kw in (
                " ago",
                "last week",
                "last month",
                "yesterday",
                "today",
                "since",
                "from ",
                "until ",
                "on the",
                "did not",
                "didn't",
                "has not",
                "hasn't",
                "refused",
                "kicked",
                "evict",
                "fired",
                "beat",
                "harass",
                "stole",
                "scammed",
                "broke",
            )
        )
    )

    word_count = len(t.split())
    if word_count <= _INTRO_WORD_THRESHOLD and not has_concrete_facts:
        return True

    if not has_concrete_facts:
        for pat in _TOPIC_INTRO_PATTERNS:
            if re.search(pat, t):
                return True
    return False


def topic_hint_category(user_text: str) -> CaseCategory:
    """Coarse single-word topic detection for vague intros — only triggers on obvious keywords."""
    t = user_text.lower()
    if any(k in t for k in ("wage", "salary", "employer", "boss", "company", "job", "fired", "pf")):
        return "employment_wages"
    if any(
        k in t
        for k in (
            "rent",
            "tenant",
            "landlord",
            "evict",
            "lease",
            "house",
            "flat",
            "apartment",
            "land",
            "plot",
            "property",
            "society",
            "builder",
            "makaan",
            "kiraya",
            "ghar",
            "जमीन",
            "ज़मीन",
            "किराया",
            "घर",
            "மனை",
            "நிலம்",
            "জমি",
            "বাড়ি",
        )
    ):
        return "property_tenancy"
    if any(k in t for k in ("dowry", "domestic violence", "harass", "abuse", "posh", "mahila", "दहेज", "घरेलू")):
        return "womens_protection"
    if any(k in t for k in ("refund", "fraud", "scam", "consumer", "online", "delivery", "warranty", "seller")):
        return "consumer_fraud"
    if any(k in t for k in ("fir", "police", "magistrate", "thana", "एफआईआर", "पुलिस")):
        return "police_fir"
    return "general"
