"""SQLite-backed chat history per session (browser-generated session_id)."""

from __future__ import annotations

import json
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from app.models.schemas import CaseCategory, OrchestrateResponse

_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "chat.sqlite"
_SESSION_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{8,128}$")


def is_valid_session_id(raw: str | None) -> bool:
    return bool(raw and _SESSION_ID_RE.fullmatch(raw.strip()))


def normalize_session_id(raw: str | None) -> str:
    if raw is None:
        return str(uuid.uuid4())
    s = raw.strip()
    if _SESSION_ID_RE.fullmatch(s):
        return s
    return str(uuid.uuid4())


@contextmanager
def _connect() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                extra_json TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_chat_session_id ON chat_messages(session_id, id)"
        )
        yield conn
        conn.commit()
    finally:
        conn.close()


_VALID_STICKY: frozenset[str] = frozenset(
    {
        "employment_wages",
        "property_tenancy",
        "womens_protection",
        "consumer_fraud",
        "police_fir",
    }
)


def get_last_assistant_category(session_id: str) -> CaseCategory | None:
    """Category from the most recent assistant turn (for short follow-ups that lack keywords)."""
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT extra_json FROM chat_messages
            WHERE session_id = ? AND role = 'assistant' AND extra_json IS NOT NULL AND extra_json != ''
            ORDER BY id DESC
            LIMIT 1
            """,
            (session_id,),
        ).fetchone()
    if not row or not row["extra_json"]:
        return None
    try:
        meta = json.loads(row["extra_json"])
        if isinstance(meta, dict):
            c = meta.get("category")
            if isinstance(c, str) and c in _VALID_STICKY:
                return c  # type: ignore[return-value]
    except json.JSONDecodeError:
        pass
    return None


def get_first_user_message(session_id: str, *, max_chars: int = 900) -> str | None:
    """First user turn in the session — keeps the original problem visible for follow-ups."""
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT content FROM chat_messages
            WHERE session_id = ? AND role = 'user'
            ORDER BY id ASC
            LIMIT 1
            """,
            (session_id,),
        ).fetchone()
    if not row:
        return None
    t = (row["content"] or "").strip()
    if not t:
        return None
    return t if len(t) <= max_chars else t[: max_chars - 1] + "…"


def get_last_assistant_content(session_id: str, *, max_chars: int = 900) -> str | None:
    """Most recent assistant reply — anchor the next turn as a continuation."""
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT content FROM chat_messages
            WHERE session_id = ? AND role = 'assistant'
            ORDER BY id DESC
            LIMIT 1
            """,
            (session_id,),
        ).fetchone()
    if not row:
        return None
    t = (row["content"] or "").strip()
    if not t:
        return None
    return t if len(t) <= max_chars else t[: max_chars - 1] + "…"


def format_thread_anchor_for_llm(session_id: str) -> str:
    """Short, repeated summary for small LLMs that drift across turns."""
    first = get_first_user_message(session_id)
    last_a = get_last_assistant_content(session_id)
    if not first and not last_a:
        return ""
    lines = [
        "THREAD ANCHOR — same conversation; continue this topic unless the user clearly starts a new legal problem.",
    ]
    if first:
        lines.append(f"User originally said: {first}")
    if last_a:
        lines.append(f"Your last reply (user is following up): {last_a}")
    return "\n".join(lines)


def get_recent_messages(
    session_id: str,
    *,
    max_messages: int = 8,
    max_chars_per_msg: int = 900,
) -> list[dict[str, str]]:
    """Recent chat as structured user/assistant turns for the LLM `history` channel.

    Small models follow real chat turns far better than a flattened transcript embedded in a prompt.
    We keep the last `max_messages` (oldest first) and trim each to keep the context window small.
    """
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT role, content FROM chat_messages
            WHERE session_id = ? AND role IN ('user', 'assistant')
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, max_messages),
        ).fetchall()
    rows = list(reversed(rows))
    out: list[dict[str, str]] = []
    for r in rows:
        text = (r["content"] or "").strip()
        if not text:
            continue
        if len(text) > max_chars_per_msg:
            text = text[: max_chars_per_msg - 1] + "…"
        out.append({"role": r["role"], "content": text})
    return out


def get_transcript_for_llm(session_id: str, *, max_messages: int = 20, max_chars: int = 6500) -> str:
    """Recent turns as plain text for the composer prompt (oldest first within the window)."""
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT role, content FROM chat_messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, max_messages),
        ).fetchall()
    rows = list(reversed(rows))
    lines: list[str] = []
    for r in rows:
        role = r["role"]
        label = "User" if role == "user" else "Assistant"
        text = (r["content"] or "").strip()
        if len(text) > 1200:
            text = text[:1197] + "…"
        lines.append(f"{label}: {text}")
    out = "\n".join(lines)
    if len(out) <= max_chars:
        return out
    if len(lines) <= 10:
        return out[-max_chars:]
    head_n = 4
    tail_n = 10
    head = "\n".join(lines[:head_n])
    tail = "\n".join(lines[-tail_n:])
    omitted = max(0, len(lines) - head_n - tail_n)
    merged = f"{head}\n\n[ ... {omitted} older turns omitted for length ... ]\n\n{tail}"
    if len(merged) <= max_chars:
        return merged
    return merged[-max_chars:]


def record_exchange(session_id: str, user_text: str, response: OrchestrateResponse) -> None:
    now = datetime.now(timezone.utc).isoformat()
    extra = {
        "category": response.category,
        "needs_clarification": response.needs_clarification,
        "crisis_detected": response.crisis_detected,
    }
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO chat_messages (session_id, role, content, extra_json, created_at)
            VALUES (?, 'user', ?, NULL, ?)
            """,
            (session_id, user_text.strip(), now),
        )
        conn.execute(
            """
            INSERT INTO chat_messages (session_id, role, content, extra_json, created_at)
            VALUES (?, 'assistant', ?, ?, ?)
            """,
            (
                session_id,
                response.rights_summary.strip(),
                json.dumps(extra),
                now,
            ),
        )


def list_messages(session_id: str, *, limit: int = 200) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT role, content, extra_json, created_at
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY id ASC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
    out: list[dict] = []
    for r in rows:
        item: dict = {
            "role": r["role"],
            "content": r["content"],
            "created_at": r["created_at"],
        }
        if r["extra_json"]:
            try:
                meta = json.loads(r["extra_json"])
                if isinstance(meta, dict) and "category" in meta:
                    item["category"] = meta["category"]
            except json.JSONDecodeError:
                pass
        out.append(item)
    return out
