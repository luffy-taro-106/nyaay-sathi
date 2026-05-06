from typing import Literal

from pydantic import BaseModel, Field


SupportedLanguage = Literal["en", "hi", "mr", "ta", "bn"]
CaseCategory = Literal[
    "employment_wages",
    "property_tenancy",
    "womens_protection",
    "consumer_fraud",
    "police_fir",
    "general",
]


class OrchestrateRequest(BaseModel):
    message: str = Field(min_length=2, max_length=2000)
    language: SupportedLanguage = "en"
    district: str | None = None
    state: str | None = None
    session_id: str | None = Field(
        default=None,
        max_length=128,
        description="Client-owned conversation id (UUID recommended). Omit to start a new thread.",
    )


class VoiceTokenRequest(BaseModel):
    room: str = Field(min_length=2, max_length=128)
    identity: str = Field(min_length=2, max_length=128)
    name: str | None = Field(default=None, max_length=128)


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    language: SupportedLanguage = "en"


LegalEntryType = Literal["statute", "illustrative_case"]
IllustrativeOutcome = Literal["won", "lost", "settled", "partial"]


class LegalSource(BaseModel):
    """Statute rows document law; illustrative_case rows are anonymized district-level patterns for advisor-style examples."""

    title: str
    section: str
    snippet: str
    corpus_category: str | None = None
    entry_type: LegalEntryType = "statute"
    district: str | None = None
    state: str | None = None
    outcome: IllustrativeOutcome | None = None
    forum_visited: str | None = None
    documents_used: list[str] | None = None


class OrchestrateResponse(BaseModel):
    disclaimer: str
    category: CaseCategory
    crisis_detected: bool
    rights_summary: str
    suggested_forum: list[str]
    required_documents: list[str]
    limitation_hint: str
    free_legal_aid: list[str]
    complaint_template: str
    helplines: list[str]
    sources: list[LegalSource]
    model_used: str | None = None
    needs_clarification: bool = False
    clarifying_questions: list[str] = []
    session_id: str = Field(
        default="",
        description="Echo this on the next request to continue the conversation.",
    )


class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    created_at: str
    category: str | None = None
