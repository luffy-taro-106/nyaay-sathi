import json
import os
from typing import Any
from urllib import error, request


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_CHAT_API_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_OLLAMA_MODEL = "qwen2.5:1.5b"
DEFAULT_ANTHROPIC_MODEL = "claude-3-5-haiku-latest"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
OPENAI_CHAT_COMPLETIONS_PATH = "/v1/chat/completions"
SUPPORTED_PROVIDERS = {"ollama", "anthropic", "openai"}


def llm_enabled() -> bool:
    provider = llm_provider()
    if provider == "anthropic":
        return bool(os.getenv("ANTHROPIC_API_KEY"))
    if provider == "openai":
        return bool(os.getenv("OPENAI_API_KEY"))
    return True


def cheap_model_name() -> str:
    p = llm_provider()
    if p == "anthropic":
        return os.getenv("ANTHROPIC_CHEAP_MODEL", DEFAULT_ANTHROPIC_MODEL)
    if p == "openai":
        return os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    return os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)


def llm_provider() -> str:
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    if provider not in SUPPORTED_PROVIDERS:
        return "ollama"
    return provider


def call_anthropic_json(
    *,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 500,
    temperature: float = 0.1,
    model: str | None = None,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any] | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    messages: list[dict[str, str]] = []
    if history:
        for m in history:
            role = m.get("role")
            content = (m.get("content") or "").strip()
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_prompt})

    payload = {
        "model": model or cheap_model_name(),
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
        "messages": messages,
    }

    req = request.Request(
        ANTHROPIC_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError):
        return None

    content = body.get("content", [])
    if not content:
        return None
    text_blocks = [blk.get("text", "") for blk in content if blk.get("type") == "text"]
    merged = "".join(text_blocks).strip()
    if not merged:
        return None
    try:
        parsed = json.loads(merged)
    except json.JSONDecodeError:
        return None
    parsed["_model"] = payload["model"]
    return parsed


def _openai_chat_url() -> str:
    base = (os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    return f"{base}{OPENAI_CHAT_COMPLETIONS_PATH}"


def call_openai_json(
    *,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 500,
    temperature: float = 0.1,
    model: str | None = None,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any] | None:
    """OpenAI Chat Completions with native multi-turn history (strong context handling)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    chosen_model = model or cheap_model_name()
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    if history:
        for m in history:
            role = m.get("role")
            content = (m.get("content") or "").strip()
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_prompt})

    try:
        timeout_s = int(os.getenv("OPENAI_TIMEOUT", "90"))
    except ValueError:
        timeout_s = 90

    payload: dict[str, Any] = {
        "model": chosen_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }

    req = request.Request(
        _openai_chat_url(),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout_s) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError):
        return None

    choices = body.get("choices") or []
    if not choices:
        return None
    msg = (choices[0].get("message") or {}) if isinstance(choices[0], dict) else {}
    raw = (msg.get("content") or "").strip()
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    parsed["_model"] = chosen_model
    return parsed


def call_ollama_json(
    *,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 500,
    temperature: float = 0.1,
    model: str | None = None,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any] | None:
    """Use Ollama /api/chat so prior turns are real chat messages, not flattened into one prompt.

    Small models (qwen2.5:1.5b) drift badly when context is jammed into the user prompt — they
    treat earlier text as part of the instructions and answer from scratch. /api/chat keeps each
    turn structured, and bumping num_ctx ensures history is not silently truncated.
    """
    chat_url = os.getenv("OLLAMA_CHAT_API_URL", OLLAMA_CHAT_API_URL)
    chosen_model = model or cheap_model_name()
    try:
        num_ctx = int(os.getenv("OLLAMA_NUM_CTX", "8192"))
    except ValueError:
        num_ctx = 8192

    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    if history:
        for m in history:
            role = m.get("role")
            content = (m.get("content") or "").strip()
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_prompt})

    payload = {
        "model": chosen_model,
        "messages": messages,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
            "num_ctx": num_ctx,
        },
    }

    req = request.Request(
        chat_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError):
        return None

    msg = body.get("message") or {}
    raw = (msg.get("content") or "").strip()
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    parsed["_model"] = chosen_model
    return parsed


def call_llm_json(
    *,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 500,
    temperature: float = 0.1,
    model: str | None = None,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any] | None:
    provider = llm_provider()
    if provider == "openai":
        return call_openai_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            model=model,
            history=history,
        )
    if provider == "anthropic":
        return call_anthropic_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            model=model,
            history=history,
        )
    return call_ollama_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        model=model,
        history=history,
    )
