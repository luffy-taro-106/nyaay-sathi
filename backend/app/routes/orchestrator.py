from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    CaseCategory,
    ChatHistoryMessage,
    OrchestrateRequest,
    OrchestrateResponse,
)
from app.services.chat_store import (
    format_thread_anchor_for_llm,
    get_last_assistant_category,
    get_recent_messages,
    get_transcript_for_llm,
    is_valid_session_id,
    list_messages,
    normalize_session_id,
    record_exchange,
)
from app.services.classifier import classify_case
from app.services.clarifier import build_clarifying_questions
from app.services.composer import (
    DISCLAIMER_BY_LANG,
    TEXT_BY_LANG,
    compose_fallback_unified,
    compose_meta_intro_fallback,
    compose_topic_clarification,
)
from app.services.crisis import crisis_helplines, detect_crisis, detect_crisis_semantic
from app.services.legal_brain import llm_classify_case, llm_compose_meta_intro, llm_compose_unified
from app.services.meta_intent import is_meta_help_request, is_vague_topic_intro, topic_hint_category
from app.services.pdf import build_complaint_pdf
from app.services.rag import retrieve_context_all

router = APIRouter()

CRISIS_MESSAGE_BY_LANG = {
    "en": "Your safety is the priority. Please contact emergency support immediately, then continue legal process with assistance.",
    "hi": "Aapki suraksha sabse pehle hai. Kripya turant emergency support se sampark karein, phir kanooni process jaari rakhein.",
    "mr": "तुमची सुरक्षितता सर्वात महत्त्वाची आहे. कृपया त्वरित आपत्कालीन मदत घ्या, नंतर कायदेशीर प्रक्रिया सुरू ठेवा.",
    "ta": "உங்கள் பாதுகாப்பே முதன்மை. உடனே அவசர உதவியை தொடர்பு கொள்ளுங்கள்; அதன் பிறகு சட்ட நடைமுறையை தொடரலாம்.",
    "bn": "আপনার নিরাপত্তাই প্রথম অগ্রাধিকার। অনুগ্রহ করে দ্রুত জরুরি সহায়তার সাথে যোগাযোগ করুন, তারপর আইনি প্রক্রিয়া চালিয়ে যান।",
}

_VALID_CATEGORY: set[CaseCategory] = {
    "employment_wages",
    "property_tenancy",
    "womens_protection",
    "consumer_fraud",
    "police_fir",
    "general",
}


def _resolve_category_hint(
    llm_category: CaseCategory | None,
    rule_category: CaseCategory,
) -> CaseCategory:
    """Prefer rule when the LLM drifts to wages on e-commerce / refund stories."""
    if rule_category == "consumer_fraud" and llm_category == "employment_wages":
        return "consumer_fraud"
    if llm_category and llm_category != "general":
        return llm_category
    if rule_category != "general":
        return rule_category
    return llm_category or rule_category


def _final_category_from_llm(
    *,
    category_hint: CaseCategory,
    llm_category_raw: str | None,
) -> CaseCategory:
    """Do not let the model JSON category relabel a consumer thread as employment_wages."""
    final_category: CaseCategory = category_hint
    if not llm_category_raw or not isinstance(llm_category_raw, str):
        return final_category
    if llm_category_raw not in _VALID_CATEGORY:
        return final_category
    c: CaseCategory = llm_category_raw  # type: ignore[assignment]
    if category_hint == "consumer_fraud" and c == "employment_wages":
        return "consumer_fraud"
    return c


def _vague_intro_response(
    request: OrchestrateRequest,
    sid: str,
    prior: str,
    thread_anchor: str,
    chat_history: list[dict[str, str]] | None,
    category_hint: CaseCategory,
    persist_chat: bool,
) -> OrchestrateResponse:
    """User named a topic (e.g. 'help me with my land') but gave no facts—respond like an advisor."""
    anchor_kw = thread_anchor.strip() or None
    llm_payload = llm_compose_unified(
        user_text=request.message,
        language=request.language,
        district=request.district,
        state=request.state,
        sources=[],  # explicit: no RAG dump for vague intros
        category_hint=category_hint,
        clarification_suggestions=None,
        chat_context=prior or None,
        conversation_anchor=anchor_kw,
        chat_history=chat_history or None,
    )
    base = compose_topic_clarification(
        category=category_hint,
        language=request.language,
        district=request.district,
    )
    if not llm_payload:
        resp = base.model_copy(update={"session_id": sid})
    else:
        final_category: CaseCategory = category_hint
        c = llm_payload.get("category")
        if isinstance(c, str) and c in _VALID_CATEGORY:
            final_category = c  # type: ignore[assignment]
        clar_qs = llm_payload.get("clarifying_questions") or base.clarifying_questions
        if not isinstance(clar_qs, list):
            clar_qs = base.clarifying_questions
        resp = OrchestrateResponse(
            disclaimer=base.disclaimer,
            category=final_category,
            crisis_detected=False,
            rights_summary=llm_payload.get("rights_summary") or base.rights_summary,
            suggested_forum=llm_payload.get("suggested_forum") or base.suggested_forum,
            required_documents=llm_payload.get("required_documents") or base.required_documents,
            limitation_hint=llm_payload.get("limitation_hint") or base.limitation_hint,
            complaint_template=llm_payload.get("complaint_template") or base.complaint_template,
            free_legal_aid=base.free_legal_aid,
            helplines=[],
            sources=[],
            model_used=llm_payload.get("_model"),
            needs_clarification=True,
            clarifying_questions=[str(q) for q in clar_qs][:4],
            session_id=sid,
        )
    if persist_chat:
        record_exchange(sid, request.message, resp)
    return resp


def _meta_response(
    request: OrchestrateRequest,
    sid: str,
    prior: str,
    persist_chat: bool,
) -> OrchestrateResponse:
    """Greetings / how-can-you-help: AI assistant first, no RAG corpus."""
    llm_payload = llm_compose_meta_intro(
        user_text=request.message,
        language=request.language,
        district=request.district,
        state=request.state,
        chat_context=prior or None,
    )
    base = compose_meta_intro_fallback(
        language=request.language,
        district=request.district,
    )
    if not llm_payload:
        resp = base.model_copy(update={"session_id": sid})
    else:
        needs_clarification = bool(llm_payload.get("needs_clarification", False))
        clarifying_questions = llm_payload.get("clarifying_questions") or []
        if not isinstance(clarifying_questions, list):
            clarifying_questions = []
        resp = OrchestrateResponse(
            disclaimer=base.disclaimer,
            category="general",
            crisis_detected=False,
            rights_summary=llm_payload.get("rights_summary") or base.rights_summary,
            suggested_forum=llm_payload.get("suggested_forum") or base.suggested_forum,
            required_documents=llm_payload.get("required_documents") or base.required_documents,
            limitation_hint=llm_payload.get("limitation_hint") or base.limitation_hint,
            complaint_template=llm_payload.get("complaint_template") or base.complaint_template,
            free_legal_aid=base.free_legal_aid,
            helplines=[],
            sources=[],
            model_used=llm_payload.get("_model"),
            needs_clarification=needs_clarification,
            clarifying_questions=[str(q) for q in clarifying_questions],
            session_id=sid,
        )
    if persist_chat:
        record_exchange(sid, request.message, resp)
    return resp


def orchestrate_core(request: OrchestrateRequest, *, persist_chat: bool) -> OrchestrateResponse:
    sid = normalize_session_id(request.session_id)
    prior = get_transcript_for_llm(sid)
    thread_anchor = format_thread_anchor_for_llm(sid)
    chat_history = get_recent_messages(sid, max_messages=8)

    crisis = detect_crisis(request.message) or detect_crisis_semantic(request.message)
    if crisis:
        lang = TEXT_BY_LANG[request.language]
        resp = OrchestrateResponse(
            disclaimer=DISCLAIMER_BY_LANG[request.language],
            category="general",
            crisis_detected=True,
            rights_summary=CRISIS_MESSAGE_BY_LANG[request.language],
            suggested_forum=["Nearest police station", "District Legal Services Authority (DLSA)"],
            required_documents=[],
            limitation_hint=lang["fallback_limit"],
            free_legal_aid=[lang["dlsa"], lang["nyayabandhu"]],
            complaint_template=lang["fallback_template"],
            helplines=crisis_helplines(),
            sources=[],
            needs_clarification=False,
            clarifying_questions=[],
            session_id=sid,
        )
        if persist_chat:
            record_exchange(sid, request.message, resp)
        return resp

    if is_meta_help_request(request.message):
        return _meta_response(request, sid, prior, persist_chat)

    rule_category = classify_case(request.message)
    cls_ctx = prior.strip()[-2800:] if prior.strip() else None
    llm_category = llm_classify_case(
        request.message,
        chat_context=cls_ctx,
        chat_history=chat_history or None,
    )
    if llm_category is not None and llm_category not in _VALID_CATEGORY:
        llm_category = "general"
    # Short follow-up: "payment receipt" etc. must not re-tag an ongoing consumer chat as wages.
    sticky = get_last_assistant_category(sid)
    if (
        sticky == "consumer_fraud"
        and rule_category == "employment_wages"
        and len(request.message.strip()) < 700
    ):
        rule_category = "consumer_fraud"
    category_hint = _resolve_category_hint(llm_category, rule_category)

    # Vague topic intros ("help me with my land") shouldn't trigger a RAG dump—
    # respond like an advisor: acknowledge the area, ask short follow-ups.
    if is_vague_topic_intro(request.message):
        if category_hint == "general":
            category_hint = topic_hint_category(request.message)
        return _vague_intro_response(
            request, sid, prior, thread_anchor, chat_history, category_hint, persist_chat
        )

    clarification_suggestions = (
        build_clarifying_questions(
            message=request.message,
            language=request.language,
            district=request.district,
            state=request.state,
        )
        if category_hint == "employment_wages"
        else []
    )

    sources = retrieve_context_all(
        request.message,
        limit=8,
        district=request.district,
        category_hint=category_hint if category_hint != "general" else None,
    )
    anchor_kw = thread_anchor.strip() or None
    llm_payload = llm_compose_unified(
        user_text=request.message,
        language=request.language,
        district=request.district,
        state=request.state,
        sources=sources,
        category_hint=category_hint,
        clarification_suggestions=clarification_suggestions or None,
        chat_context=prior or None,
        conversation_anchor=anchor_kw,
        chat_history=chat_history or None,
    )

    final_category = _final_category_from_llm(
        category_hint=category_hint,
        llm_category_raw=llm_payload.get("category") if llm_payload else None,
    )

    base = compose_fallback_unified(
        category=final_category,
        language=request.language,
        district=request.district,
        sources=sources,
    )
    if not llm_payload:
        resp = base.model_copy(update={"session_id": sid})
        if persist_chat:
            record_exchange(sid, request.message, resp)
        return resp

    needs_clarification = bool(llm_payload.get("needs_clarification", False))
    clarifying_questions = llm_payload.get("clarifying_questions") or []
    if not isinstance(clarifying_questions, list):
        clarifying_questions = []

    resp = OrchestrateResponse(
        disclaimer=base.disclaimer,
        category=final_category,
        crisis_detected=False,
        rights_summary=llm_payload.get("rights_summary") or base.rights_summary,
        suggested_forum=llm_payload.get("suggested_forum") or base.suggested_forum,
        required_documents=llm_payload.get("required_documents") or base.required_documents,
        limitation_hint=llm_payload.get("limitation_hint") or base.limitation_hint,
        complaint_template=llm_payload.get("complaint_template") or base.complaint_template,
        free_legal_aid=base.free_legal_aid,
        helplines=[],
        sources=sources,
        model_used=llm_payload.get("_model"),
        needs_clarification=needs_clarification,
        clarifying_questions=[str(q) for q in clarifying_questions],
        session_id=sid,
    )
    if persist_chat:
        record_exchange(sid, request.message, resp)
    return resp


@router.post("/orchestrate", response_model=OrchestrateResponse)
def orchestrate(request: OrchestrateRequest) -> OrchestrateResponse:
    return orchestrate_core(request, persist_chat=True)


@router.get("/chat/{session_id}/history", response_model=list[ChatHistoryMessage])
def chat_history(session_id: str) -> list[ChatHistoryMessage]:
    if not is_valid_session_id(session_id):
        raise HTTPException(status_code=400, detail="Invalid session id")
    rows = list_messages(session_id.strip())
    return [ChatHistoryMessage(**row) for row in rows]


@router.post("/complaint-pdf")
def complaint_pdf(request: OrchestrateRequest) -> StreamingResponse:
    response = orchestrate_core(request, persist_chat=False)
    pdf_bytes = build_complaint_pdf(response)
    filename = f"nyaay-sathi-{response.category}.pdf"
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
