from fastapi.testclient import TestClient

from app.main import app
from app.routes import orchestrator as orchestrator_module

client = TestClient(app)


def _disable_semantic_crisis(monkeypatch):
    monkeypatch.setattr(orchestrator_module, "detect_crisis_semantic", lambda _msg: False)


def test_crisis_short_circuit(monkeypatch):
    _disable_semantic_crisis(monkeypatch)
    res = client.post(
        "/v1/orchestrate",
        json={"message": "I am facing violence and need urgent help", "language": "en", "district": "Pune"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["crisis_detected"] is True
    assert body["category"] == "general"
    assert len(body["helplines"]) > 0
    assert body["needs_clarification"] is False
    assert len(body.get("session_id", "")) >= 8


def test_fallback_when_llm_unavailable(monkeypatch):
    _disable_semantic_crisis(monkeypatch)
    monkeypatch.setattr(orchestrator_module, "llm_classify_case", lambda _msg, **kwargs: "employment_wages")
    monkeypatch.setattr(orchestrator_module, "build_clarifying_questions", lambda **_kwargs: [])
    monkeypatch.setattr(orchestrator_module, "llm_compose_unified", lambda **_kwargs: None)
    res = client.post(
        "/v1/orchestrate",
        json={
            "message": "Wage issue with unknown terms no match",
            "language": "en",
            "district": "Pune",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["category"] == "employment_wages"
    # New behavior: short / vague messages get a friendly clarification path, not a RAG dump.
    assert body["needs_clarification"] is True
    assert "could not find enough verified legal sources" not in body["rights_summary"].lower()


def test_clarifier_via_unified_llm(monkeypatch):
    _disable_semantic_crisis(monkeypatch)
    monkeypatch.setattr(orchestrator_module, "llm_classify_case", lambda _msg, **kwargs: "employment_wages")
    monkeypatch.setattr(
        orchestrator_module,
        "llm_compose_unified",
        lambda **_kwargs: {
            "rights_summary": "Need a bit more detail.",
            "suggested_forum": ["Labour Commissioner office"],
            "required_documents": ["ID proof"],
            "limitation_hint": "Act soon.",
            "complaint_template": "TBD",
            "needs_clarification": True,
            "clarifying_questions": ["When were wages last paid?"],
            "_model": "mock",
        },
    )
    res = client.post(
        "/v1/orchestrate",
        json={
            "message": "salary issue",
            "language": "en",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["needs_clarification"] is True
    assert len(body["clarifying_questions"]) > 0


def test_general_nonlegal_natural_reply(monkeypatch):
    _disable_semantic_crisis(monkeypatch)
    monkeypatch.setattr(orchestrator_module, "llm_classify_case", lambda _msg, **kwargs: "general")
    monkeypatch.setattr(
        orchestrator_module,
        "llm_compose_unified",
        lambda **_kwargs: {
            "rights_summary": "I do not have live weather data—try a weather app. I can help with Indian legal questions.",
            "suggested_forum": [],
            "required_documents": [],
            "limitation_hint": "N/A",
            "complaint_template": "",
            "category": "general",
            "_model": "mock",
        },
    )
    res = client.post(
        "/v1/orchestrate",
        json={
            "message": "What is the weather in Mumbai today?",
            "language": "en",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["category"] == "general"
    assert "pilot" not in body["rights_summary"].lower()


def test_legacy_out_of_scope_label_normalized_and_rules_win(monkeypatch):
    """Tiny local models may still emit the old label; rule keywords must still win."""
    _disable_semantic_crisis(monkeypatch)
    monkeypatch.setattr(orchestrator_module, "llm_classify_case", lambda _msg, **kwargs: "out_of_scope")
    monkeypatch.setattr(orchestrator_module, "build_clarifying_questions", lambda **_kwargs: [])
    monkeypatch.setattr(orchestrator_module, "llm_compose_unified", lambda **_kwargs: None)
    res = client.post(
        "/v1/orchestrate",
        json={
            "message": "My employer has not paid me for three months",
            "language": "en",
            "district": "Pune",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["category"] == "employment_wages"
    assert len(body["sources"]) > 0


def test_employment_success_without_llm(monkeypatch):
    _disable_semantic_crisis(monkeypatch)
    monkeypatch.setattr(orchestrator_module, "llm_classify_case", lambda _msg, **kwargs: None)
    monkeypatch.setattr(orchestrator_module, "build_clarifying_questions", lambda **_kwargs: [])
    monkeypatch.setattr(orchestrator_module, "llm_compose_unified", lambda **_kwargs: None)
    res = client.post(
        "/v1/orchestrate",
        json={
            "message": "My employer has not paid minimum wage for 3 months and amount is 30000",
            "language": "en",
            "district": "Pune",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["category"] == "employment_wages"
    assert body["model_used"] is None


def test_employment_success_with_llm_payload(monkeypatch):
    _disable_semantic_crisis(monkeypatch)
    monkeypatch.setattr(orchestrator_module, "llm_classify_case", lambda _msg, **kwargs: "employment_wages")
    monkeypatch.setattr(orchestrator_module, "build_clarifying_questions", lambda **_kwargs: [])
    monkeypatch.setattr(
        orchestrator_module,
        "llm_compose_unified",
        lambda **_kwargs: {
            "rights_summary": "Custom LLM rights summary.",
            "suggested_forum": ["Labour Commissioner office"],
            "required_documents": ["Contract copy"],
            "limitation_hint": "Act immediately.",
            "complaint_template": "Custom template",
            "_model": "mock-llm",
        },
    )
    res = client.post(
        "/v1/orchestrate",
        json={
            "message": "My employer has not paid wage for months 1 to 3 amount 30000",
            "language": "en",
            "district": "Pune",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["category"] == "employment_wages"
    assert body["model_used"] == "mock-llm"
    assert body["rights_summary"] == "Custom LLM rights summary."


def test_indic_fallback_classification(monkeypatch):
    _disable_semantic_crisis(monkeypatch)
    monkeypatch.setattr(orchestrator_module, "llm_classify_case", lambda _msg, **kwargs: None)
    monkeypatch.setattr(orchestrator_module, "llm_compose_unified", lambda **_kwargs: None)
    monkeypatch.setattr(orchestrator_module, "build_clarifying_questions", lambda **_kwargs: [])
    res = client.post(
        "/v1/orchestrate",
        json={
            "message": "मेरा वेतन नहीं मिला है",
            "language": "hi",
            "district": "Pune",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["category"] == "employment_wages"


def test_complaint_pdf_endpoint(monkeypatch):
    _disable_semantic_crisis(monkeypatch)
    monkeypatch.setattr(orchestrator_module, "llm_classify_case", lambda _msg, **kwargs: None)
    monkeypatch.setattr(orchestrator_module, "llm_compose_unified", lambda **_kwargs: None)
    monkeypatch.setattr(orchestrator_module, "build_clarifying_questions", lambda **_kwargs: [])
    res = client.post(
        "/v1/complaint-pdf",
        json={
            "message": "My employer has not paid wage for 3 months amount 30000",
            "language": "en",
            "district": "Pune",
        },
    )
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/pdf")
    assert res.content.startswith(b"%PDF")


def test_chat_history_roundtrip(monkeypatch):
    _disable_semantic_crisis(monkeypatch)
    monkeypatch.setattr(orchestrator_module, "llm_classify_case", lambda _msg, **kwargs: "general")
    monkeypatch.setattr(orchestrator_module, "llm_compose_unified", lambda **_kwargs: None)
    r1 = client.post(
        "/v1/orchestrate",
        json={"message": "Landlord gave notice in Pune", "language": "en", "district": "Pune"},
    )
    sid = r1.json()["session_id"]
    assert len(sid) >= 8
    r2 = client.post(
        "/v1/orchestrate",
        json={
            "message": "Follow up: he changed the locks",
            "language": "en",
            "district": "Pune",
            "session_id": sid,
        },
    )
    assert r2.json()["session_id"] == sid
    hist = client.get(f"/v1/chat/{sid}/history")
    assert hist.status_code == 200
    msgs = hist.json()
    assert len(msgs) == 4
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"


def test_chat_history_invalid_session():
    bad = client.get("/v1/chat/not!!!valid/history")
    assert bad.status_code == 400


def test_meta_question_skips_rag_corpus(monkeypatch):
    """'How can you help' should introduce the AI assistant, not dump acts from RAG."""
    _disable_semantic_crisis(monkeypatch)
    monkeypatch.setattr(orchestrator_module, "llm_compose_meta_intro", lambda **_kwargs: None)
    monkeypatch.setattr(orchestrator_module, "retrieve_context_all", lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("RAG should not run for meta")))
    res = client.post(
        "/v1/orchestrate",
        json={"message": "hey how can you help me", "language": "en", "district": "Pune"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["category"] == "general"
    assert body["sources"] == []
    assert "code on wages" not in body["rights_summary"].lower()
    assert "ai assistant" in body["rights_summary"].lower()
    assert "nyaay" in body["rights_summary"].lower()


def test_vague_topic_intro_asks_clarifying_questions(monkeypatch):
    """'I have an issue with my land' → acknowledge the area + ask follow-ups, no RAG dump."""
    _disable_semantic_crisis(monkeypatch)
    monkeypatch.setattr(orchestrator_module, "llm_classify_case", lambda _msg, **kwargs: None)
    monkeypatch.setattr(orchestrator_module, "llm_compose_unified", lambda **_kwargs: None)
    monkeypatch.setattr(
        orchestrator_module,
        "retrieve_context_all",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("RAG should not run for vague intros")),
    )
    res = client.post(
        "/v1/orchestrate",
        json={
            "message": "can you help me with a issue regarding my land",
            "language": "en",
            "district": "Pune",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["category"] == "property_tenancy"
    assert body["needs_clarification"] is True
    assert len(body["clarifying_questions"]) >= 2
    assert body["sources"] == []
    assert "code on wages" not in body["rights_summary"].lower()


def test_substantive_help_question_still_uses_normal_path(monkeypatch):
    """Do not treat wage-recovery questions as meta."""
    _disable_semantic_crisis(monkeypatch)
    monkeypatch.setattr(orchestrator_module, "llm_classify_case", lambda _msg, **kwargs: None)
    monkeypatch.setattr(orchestrator_module, "llm_compose_unified", lambda **_kwargs: None)
    monkeypatch.setattr(orchestrator_module, "build_clarifying_questions", lambda **_kwargs: [])
    res = client.post(
        "/v1/orchestrate",
        json={
            "message": "can you help me recover unpaid wages from my company in Pune",
            "language": "en",
            "district": "Pune",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["category"] == "employment_wages"
    assert len(body["sources"]) > 0


def test_complaint_pdf_skips_chat_persistence(monkeypatch):
    _disable_semantic_crisis(monkeypatch)
    monkeypatch.setattr(orchestrator_module, "llm_classify_case", lambda _msg, **kwargs: None)
    monkeypatch.setattr(orchestrator_module, "llm_compose_unified", lambda **_kwargs: None)
    monkeypatch.setattr(orchestrator_module, "build_clarifying_questions", lambda **_kwargs: [])
    r1 = client.post(
        "/v1/orchestrate",
        json={"message": "My employer has not paid wage for 3 months", "language": "en", "district": "Pune"},
    )
    sid = r1.json()["session_id"]
    assert len(client.get(f"/v1/chat/{sid}/history").json()) == 2
    pdf = client.post(
        "/v1/complaint-pdf",
        json={
            "message": "My employer has not paid wage for 3 months",
            "language": "en",
            "district": "Pune",
            "session_id": sid,
        },
    )
    assert pdf.status_code == 200
    assert len(client.get(f"/v1/chat/{sid}/history").json()) == 2


def test_hindi_invoice_followup_classifies_consumer_not_wages():
    """'Payment receipt' must not trigger employment keywords."""
    from app.services.classifier import classify_case

    msg = (
        "मेरे पास इनवॉइस ऑर्डर रिसीवड और पेमेंट रिसिप्ट है "
        "लेकिन मेरे पास कोई वीडियो और स्क्रीनशॉट नहीं है"
    )
    assert classify_case(msg) == "consumer_fraud"


def test_consumer_thread_short_followup_stays_consumer(monkeypatch):
    _disable_semantic_crisis(monkeypatch)
    monkeypatch.setattr(
        orchestrator_module,
        "llm_classify_case",
        lambda _msg, **kwargs: "employment_wages",
    )
    monkeypatch.setattr(orchestrator_module, "llm_compose_unified", lambda **_kwargs: None)
    r1 = client.post(
        "/v1/orchestrate",
        json={
            "message": "I ordered a phone online, it is defective and seller refuses refund",
            "language": "hi",
            "district": "Pune",
        },
    )
    assert r1.status_code == 200
    assert r1.json()["category"] == "consumer_fraud"
    sid = r1.json()["session_id"]
    r2 = client.post(
        "/v1/orchestrate",
        json={
            "message": "mere paas invoice order received aur payment receipt hai lekin video nahi",
            "language": "hi",
            "district": "Pune",
            "session_id": sid,
        },
    )
    assert r2.status_code == 200
    assert r2.json()["category"] == "consumer_fraud"


def test_rag_injects_pune_won_and_lost_illustrative_patterns():
    from app.services.rag import retrieve_context_all

    src = retrieve_context_all(
        "employer has not paid my salary and wages for months in Pune",
        limit=8,
        district="Pune",
        category_hint="employment_wages",
    )
    pune_ill = [
        s
        for s in src
        if s.entry_type == "illustrative_case" and (s.district or "").strip().casefold() == "pune".casefold()
    ]
    outcomes = {s.outcome for s in pune_ill}
    assert "won" in outcomes
    assert "lost" in outcomes
