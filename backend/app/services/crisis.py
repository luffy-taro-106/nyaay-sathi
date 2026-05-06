from app.services.llm import call_llm_json

CRISIS_TERMS = {
    "kill",
    "suicide",
    "beating",
    "assault",
    "rape",
    "violence",
    "threat to life",
    "danger",
    "urgent help",
    "bachao",
    "madad",
    "hinsa",
    "maar",
    "zindagi khatra",
    "आत्महत्या",
    "मारपीट",
    "हिंसा",
    "बचाओ",
    "जीवन को खतरा",
    "आत्महत्या कर",
    "मारहाण",
    "हल्ला",
    "जीवाला धोका",
    "உதவி",
    "வன்முறை",
    "தற்கொலை",
    "বাঁচান",
    "সহায়তা",
    "হিংসা",
    "আত্মহত্যা",
}


def detect_crisis(user_text: str) -> bool:
    text = user_text.lower()
    return any(term in text for term in CRISIS_TERMS)


SEMANTIC_GATE_KEYWORDS = {
    "help",
    "save",
    "scared",
    "afraid",
    "hurt",
    "harm",
    "die",
    "death",
    "blood",
    "dead",
    "abuse",
    "force",
    "forced",
    "hit",
    "hitting",
    "attack",
    "attacked",
    "weapon",
    "knife",
    "gun",
    "kidnap",
    "stalk",
    "stalking",
    "molest",
    "harass",
    "threat",
    "threaten",
    "scream",
    "alone",
    "trapped",
    "बचाओ",
    "मदद",
    "मारना",
    "धमकी",
    "खतरा",
    "जान",
    "मरना",
    "चोट",
    "हमला",
    "धमकाया",
    "वाचवा",
    "मदत",
    "धोका",
    "हल्ला",
    "जीव",
    "காப்பாற்று",
    "உதவி",
    "ஆபத்து",
    "உயிர்",
    "தாக்கு",
    "বাঁচাও",
    "সাহায্য",
    "বিপদ",
    "প্রাণ",
    "আক্রমণ",
}


def _should_run_semantic(user_text: str) -> bool:
    """Lightweight prefilter: only call LLM when message length and keywords suggest possible risk."""
    if len(user_text) < 12:
        return False
    text = user_text.lower()
    return any(term in text for term in SEMANTIC_GATE_KEYWORDS)


def detect_crisis_semantic(user_text: str) -> bool:
    if not _should_run_semantic(user_text):
        return False
    data = call_llm_json(
        system_prompt=(
            "Classify if the message indicates immediate safety risk "
            "(violence, self-harm, threat to life, sexual assault, urgent danger). "
            "Return strict JSON only: {\"is_crisis\": true|false}."
        ),
        user_prompt=user_text,
        max_tokens=20,
        temperature=0.0,
    )
    if not data:
        return False
    return bool(data.get("is_crisis") is True)


def crisis_helplines() -> list[str]:
    return [
        "112 (Emergency Response Support System)",
        "181 (Women Helpline)",
        "1098 (Childline)",
    ]
