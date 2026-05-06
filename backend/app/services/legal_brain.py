from app.models.schemas import CaseCategory, LegalSource, SupportedLanguage
from app.services.llm import call_llm_json

_CLASSIFIER_ALLOWED = {
    "employment_wages",
    "property_tenancy",
    "womens_protection",
    "consumer_fraud",
    "police_fir",
    "general",
    "out_of_scope",  # legacy model output; normalized to general
}

CLASSIFIER_SYSTEM = (
    "You classify Indian legal user queries into exactly one category. "
    "Return strict JSON only: {\"category\":\"...\"}. "
    "Allowed categories: employment_wages, property_tenancy, womens_protection, "
    "consumer_fraud, police_fir, general. "
    "Use general when the message is not about Indian legal help (weather, sports, coding, chit-chat) "
    "or when no pilot category clearly fits. "
    "If a conversation excerpt is included (oldest first), the line you must classify is usually a **short follow-up**. "
    "Infer the ongoing legal topic from the excerpt plus that line; **keep the same category** unless the user clearly "
    "switches to a different problem (e.g. was about an online refund, now only unpaid salary at a job). "
    "Wages, salary, employer, unpaid dues, PF, termination -> employment_wages. "
    "Rent, landlord, tenant, eviction, deposit, possession -> property_tenancy. "
    "Dowry, domestic violence, harassment of women, POSH -> womens_protection. "
    "Online purchase, refund denied, defective product, seller fraud -> consumer_fraud. "
    "FIR, police refusal, theft complaint, station -> police_fir."
)

NYAAY_PERSONA = (
    "You are **Nyaay Sathi**: a warm, patient legal-information companion for people in India—like a careful "
    "advisor at a legal help desk, not a formal chatbot. You speak in plain language, acknowledge feelings "
    "when someone is stressed, and ask clarifying questions when details are missing (dates, district, "
    "what exactly happened, any papers). You are not a lawyer: you do not predict outcomes or give binding "
    "advice; you explain typical processes, forums, and documents, and you encourage DLSA or qualified counsel "
    "when facts are serious or unclear.\n\n"
    "When the user asks who you are or how you can help (e.g. “how can you help”, “what do you do”), answer "
    "clearly in their language: you help with everyday Indian legal topics—**wages and employment**, "
    "**rent and tenancy**, **women’s safety and protection laws**, **consumer fraud and refunds**, "
    "**police complaints and FIR**—and you can suggest sensible next steps, places to approach (e.g. DLSA, "
    "labour office, consumer commission), papers to gather, and rough complaint outlines. Then invite them "
    "to describe their situation.\n\n"
    "Example tone (adapt fully to the user’s language; do not sound like a brochure):\n"
    "User: How can you help me?\n"
    "Assistant: I’m Nyaay Sathi—I help you make sense of common legal situations in India without the jargon. "
    "If you’re dealing with unpaid wages, a landlord dispute, something serious at home, a bad online purchase, "
    "or trouble getting an FIR filed, I can outline what people usually do next, where to go, and what to "
    "collect first. I won’t tell you who wins in court, but I can make the path less confusing. What’s going on for you?\n"
    "User: I don’t know where to start.\n"
    "Assistant: That’s okay. In your own words, what happened—roughly when, and which district or city are you in? "
    "Even a short story is enough for me to suggest a first step.\n\n"
)

UNIFIED_COMPOSER_RULES = (
    "Use the retrieved sources when they help; if they are only loosely related or empty, say so naturally "
    "and still respond like a human (e.g. small talk or weather: brief, kind reply, then offer legal help). "
    "Do not refuse with rigid 'pilot scope' or 'out of scope' boilerplate. "
    "If important facts are missing, set needs_clarification true and add 1–3 short, specific questions—like "
    "an advisor would—not an interrogation. "
    "Some sources are **illustrative_case** rows: anonymized patterns tied to a **district**, with **outcome** "
    "(won / lost / settled / partial), **forum_visited**, and **documents_used**. **Do not quote, paraphrase, or "
    "list these snippets verbatim.** Instead, when the user's district matches, summarise them as a single human "
    "sentence in your own words—e.g. \"in our anonymized notes from {district}, one person who kept their "
    "appointment letter and salary slips and went to the labour office got things moving, while another with only "
    "verbal promises and a long delay didn't get far\". Use at most one favourable and one unfavourable example. "
    "Make clear in passing that these are anonymized patterns, **not** court judgments or guarantees, and every "
    "case turns on its own facts. Never invent case names, citation numbers, or outcomes not in the sources. "
    "If the chat excerpt shows the user is continuing the same problem (e.g. already discussing a defective online order), "
    "keep that topic and category—do not jump to unrelated areas like wages or PF. "
    "Write rights_summary as if speaking to one person across a desk: a short paragraph (3–5 sentences) of warm, "
    "spoken-style prose. No bullet characters. No numbered lists. No section labels like [employment_wages]. No "
    "headings like 'Where to go'. Don't restate retrieved snippets word-for-word. Don't enumerate every act—mention "
    "at most one statute by name when it genuinely helps, in passing. End with a gentle next-step question or offer. "
    "Return strict JSON with keys: "
    "rights_summary (string), suggested_forum (array of strings), required_documents (array of strings), "
    "limitation_hint (string), complaint_template (string), "
    "needs_clarification (boolean), clarifying_questions (array of strings), "
    "category (string, one of employment_wages, property_tenancy, womens_protection, consumer_fraud, "
    "police_fir, general — optional hint; omit or use general if unsure)."
)


def _format_source_for_prompt(s: LegalSource) -> str:
    base = f"[{s.corpus_category or '?'}] {s.title} | {s.section} | {s.snippet}"
    if s.entry_type != "illustrative_case":
        return base
    bits: list[str] = [base, "type=illustrative_case (anonymized pattern, not a court judgment)"]
    if s.district:
        bits.append(f"district={s.district}")
    if s.state:
        bits.append(f"state={s.state}")
    if s.outcome:
        bits.append(f"outcome={s.outcome}")
    if s.forum_visited:
        bits.append(f"forum_visited={s.forum_visited}")
    if s.documents_used:
        bits.append("documents_used=" + "; ".join(s.documents_used))
    return " | ".join(bits)

UNIFIED_COMPOSER_SYSTEM = NYAAY_PERSONA + UNIFIED_COMPOSER_RULES

_OUTPUT_LANG_NAMES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi in Devanagari",
    "mr": "Marathi in Devanagari",
    "ta": "Tamil",
    "bn": "Bengali",
}

META_INTRO_SYSTEM = (
    NYAAY_PERSONA
    + "This turn is ONLY a greeting or meta-question (who are you, how can you help, hello). "
    "Reply in 3–6 short sentences as natural speech. **First** say clearly that you are an **AI assistant** "
    "(not a human lawyer), **then** introduce the name Nyaay Sathi and what you help with in India. "
    "Do NOT cite specific Acts, BNSS, Code on Wages, or any retrieved legal database snippets. "
    "No bullet characters or numbered lists. End by inviting the user to describe their situation. "
    "Set category to general. needs_clarification false unless they already described a concrete legal problem. "
    "Return strict JSON: rights_summary, suggested_forum (e.g. DLSA, NyayaBandhu), "
    "required_documents (empty array), limitation_hint (one line: urgency / real lawyer / DLSA), "
    "complaint_template (one line inviting their story), needs_clarification (boolean), clarifying_questions (array), "
    "category (general)."
)


def llm_classify_case(
    user_text: str,
    *,
    chat_context: str | None = None,
    chat_history: list[dict[str, str]] | None = None,
) -> CaseCategory | None:
    excerpt = ""
    if not chat_history and chat_context and chat_context.strip():
        ctx = chat_context.strip()
        if len(ctx) > 2800:
            ctx = ctx[-2800:]
        excerpt = (
            "Conversation excerpt (oldest first; the message after the separator is the **latest** line to classify):\n"
            f"{ctx}\n\n---\n\n"
        )
    data = call_llm_json(
        system_prompt=CLASSIFIER_SYSTEM,
        user_prompt=f"{excerpt}Latest user message to classify:\n{user_text}",
        max_tokens=80,
        temperature=0.0,
        history=chat_history,
    )
    if not data:
        return None
    category = data.get("category")
    if category == "out_of_scope":
        category = "general"
    if category in _CLASSIFIER_ALLOWED and category != "out_of_scope":
        return category  # type: ignore[return-value]
    return None


def llm_compose_meta_intro(
    *,
    user_text: str,
    language: SupportedLanguage,
    district: str | None,
    state: str | None,
    chat_context: str | None = None,
) -> dict | None:
    transcript = ""
    if chat_context and chat_context.strip():
        transcript = f"Earlier conversation:\n{chat_context.strip()}\n\n---\n\n"
    lang_label = _OUTPUT_LANG_NAMES.get(language, language)
    raw = call_llm_json(
        system_prompt=META_INTRO_SYSTEM,
        user_prompt=(
            f"{transcript}"
            f"REQUIRED OUTPUT LANGUAGE: {language} ({lang_label}). "
            "Write every JSON field only in this language—no English if language is hi, mr, ta, or bn.\n\n"
            f"Interface language code: {language}\n"
            f"District (if known): {district or 'unknown'}\n"
            f"State (if known): {state or 'unknown'}\n"
            f"User message:\n{user_text}\n"
        ),
        max_tokens=450,
        temperature=0.3,
    )
    if not raw:
        return None
    cleaned: dict = {}
    model_used = raw.get("_model")
    if isinstance(raw.get("rights_summary"), str):
        cleaned["rights_summary"] = raw["rights_summary"]
    if isinstance(raw.get("limitation_hint"), str):
        cleaned["limitation_hint"] = raw["limitation_hint"]
    if isinstance(raw.get("complaint_template"), str):
        cleaned["complaint_template"] = raw["complaint_template"]
    if isinstance(raw.get("suggested_forum"), list):
        cleaned["suggested_forum"] = [str(x) for x in raw["suggested_forum"] if isinstance(x, str)]
    if isinstance(raw.get("required_documents"), list):
        cleaned["required_documents"] = [str(x) for x in raw["required_documents"] if isinstance(x, str)]
    if isinstance(raw.get("needs_clarification"), bool):
        cleaned["needs_clarification"] = raw["needs_clarification"]
    if isinstance(raw.get("clarifying_questions"), list):
        cleaned["clarifying_questions"] = [
            str(x) for x in raw["clarifying_questions"] if isinstance(x, str)
        ]
    cleaned["category"] = "general"
    if model_used:
        cleaned["_model"] = str(model_used)
    return cleaned


def llm_compose_unified(
    *,
    user_text: str,
    language: SupportedLanguage,
    district: str | None,
    state: str | None,
    sources: list[LegalSource],
    category_hint: CaseCategory,
    clarification_suggestions: list[str] | None = None,
    chat_context: str | None = None,
    conversation_anchor: str | None = None,
    chat_history: list[dict[str, str]] | None = None,
) -> dict | None:
    src_blob = "\n".join(f"- {_format_source_for_prompt(s)}" for s in sources) or "(no retrieved snippets)"
    extra = ""
    if clarification_suggestions:
        extra = (
            "\nOptional follow-up questions suggested by the system "
            "(rephrase in the user's language if you set needs_clarification): "
            + "; ".join(clarification_suggestions)
        )
    lang_label = _OUTPUT_LANG_NAMES.get(language, language)
    has_thread = bool(
        chat_history
        or (conversation_anchor and conversation_anchor.strip())
        or (chat_context and chat_context.strip())
    )
    compose_temp = 0.18 if has_thread else 0.25

    # When real history is available, pass it as actual chat turns (best for small models).
    # Only fall back to embedding the transcript when there is no structured history.
    history_for_llm: list[dict[str, str]] | None = None
    transcript = ""
    if chat_history:
        history_for_llm = chat_history
        if conversation_anchor and conversation_anchor.strip():
            transcript = conversation_anchor.strip() + "\n\n---\n\n"
    else:
        preamble = ""
        if conversation_anchor and conversation_anchor.strip():
            preamble = conversation_anchor.strip() + "\n\n---\n\n"
        if chat_context and chat_context.strip():
            transcript = (
                f"{preamble}"
                "Earlier in this conversation (excerpt; oldest first):\n"
                f"{chat_context.strip()}\n\n---\n\n"
            )
        elif preamble:
            transcript = preamble

    followup_hint = (
        "This is a follow-up in the same conversation above. Continue the SAME legal topic and category as the "
        "prior turns; do NOT switch to an unrelated area (e.g. wages → consumer or vice versa) unless the user "
        "clearly raises a new problem.\n\n"
        if has_thread
        else ""
    )

    raw = call_llm_json(
        system_prompt=UNIFIED_COMPOSER_SYSTEM,
        user_prompt=(
            f"{transcript}"
            f"{followup_hint}"
            f"REQUIRED OUTPUT LANGUAGE: {language} ({lang_label}). "
            "You MUST write every user-visible field in the JSON (rights_summary, suggested_forum, "
            "required_documents, limitation_hint, complaint_template, clarifying_questions) ONLY in this "
            "language—do not use English when the required language is hi, mr, ta, or bn. "
            "Stay in the required language for the whole reply, including follow-up turns.\n\n"
            f"Interface language code: {language}\n"
            f"District: {district or 'unknown'}\n"
            f"State: {state or 'unknown'}\n"
            f"Classifier hint category: {category_hint}\n"
            f"Current user message:\n{user_text}\n"
            f"Retrieved sources:\n{src_blob}\n"
            f"{extra}\n"
            f"Again: entire JSON values in {_OUTPUT_LANG_NAMES.get(language, language)} only."
        ),
        max_tokens=900,
        temperature=compose_temp,
        history=history_for_llm,
    )
    if not raw:
        return None
    cleaned: dict = {}
    model_used = raw.get("_model")

    if isinstance(raw.get("rights_summary"), str):
        cleaned["rights_summary"] = raw["rights_summary"]
    if isinstance(raw.get("limitation_hint"), str):
        cleaned["limitation_hint"] = raw["limitation_hint"]
    if isinstance(raw.get("complaint_template"), str):
        cleaned["complaint_template"] = raw["complaint_template"]
    if isinstance(raw.get("suggested_forum"), list):
        cleaned["suggested_forum"] = [str(x) for x in raw["suggested_forum"] if isinstance(x, str)]
    if isinstance(raw.get("required_documents"), list):
        cleaned["required_documents"] = [str(x) for x in raw["required_documents"] if isinstance(x, str)]
    if isinstance(raw.get("needs_clarification"), bool):
        cleaned["needs_clarification"] = raw["needs_clarification"]
    if isinstance(raw.get("clarifying_questions"), list):
        cleaned["clarifying_questions"] = [
            str(x) for x in raw["clarifying_questions"] if isinstance(x, str)
        ]
    cat = raw.get("category")
    if isinstance(cat, str):
        if cat == "out_of_scope":
            cleaned["category"] = "general"
        elif cat in _CLASSIFIER_ALLOWED - {"out_of_scope"}:
            cleaned["category"] = cat
    if model_used:
        cleaned["_model"] = str(model_used)
    return cleaned
