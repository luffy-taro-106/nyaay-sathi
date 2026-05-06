import os
from pathlib import Path

from fastapi import FastAPI, HTTPException

# Load backend/.env so OPENAI_API_KEY / LLM_PROVIDER work when not using run_product.sh.
_backend_dir = Path(__file__).resolve().parents[1]
try:
    from dotenv import load_dotenv

    load_dotenv(_backend_dir / ".env", override=False)
except ImportError:
    pass
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.models.schemas import TTSRequest, VoiceTokenRequest
from app.routes.orchestrator import router as orchestrator_router
from app.services.llm import cheap_model_name, llm_provider

app = FastAPI(
    title="Nyaay Sathi API",
    version="0.1.0",
    description="Voice-first legal navigator orchestrator API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orchestrator_router, prefix="/v1", tags=["orchestrator"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/config")
def config() -> dict[str, str]:
    return {
        "llm_provider": llm_provider(),
        "llm_model": cheap_model_name(),
    }


@app.get("/v1/voice-config")
def voice_config() -> dict[str, object]:
    livekit_url = os.getenv("LIVEKIT_URL", "")
    has_credentials = bool(
        livekit_url
        and os.getenv("LIVEKIT_API_KEY")
        and os.getenv("LIVEKIT_API_SECRET")
    )
    return {
        "livekit_url": livekit_url,
        "configured": has_credentials,
        "agent_command": "python voice/livekit_agent.py dev",
    }


@app.post("/v1/voice-token")
async def voice_token(payload: VoiceTokenRequest) -> dict[str, str]:
    livekit_url = os.getenv("LIVEKIT_URL", "")
    api_key = os.getenv("LIVEKIT_API_KEY", "")
    api_secret = os.getenv("LIVEKIT_API_SECRET", "")
    if not (livekit_url and api_key and api_secret):
        raise HTTPException(status_code=400, detail="LiveKit is not configured on server")

    try:
        from livekit import api  # lazy import to avoid hard failure if dependency missing
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="livekit dependency missing on backend. Install livekit-api.",
        ) from exc

    token = (
        api.AccessToken(api_key, api_secret)
        .with_identity(payload.identity)
        .with_name(payload.name or payload.identity)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=payload.room,
                can_publish=True,
                can_subscribe=True,
            )
        )
        .to_jwt()
    )
    return {
        "token": token,
        "livekit_url": livekit_url,
        "room": payload.room,
        "identity": payload.identity,
    }


@app.post("/v1/tts")
async def tts(payload: TTSRequest) -> Response:
    try:
        import edge_tts
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="edge-tts dependency missing on backend. Install backend dependencies.",
        ) from exc

    voice_by_lang = {
        "en": "en-IN-NeerjaNeural",
        "hi": "hi-IN-SwaraNeural",
        "mr": "mr-IN-AarohiNeural",
        "ta": "ta-IN-PallaviNeural",
        "bn": "bn-IN-TanishaaNeural",
    }
    voice = voice_by_lang.get(payload.language, "en-IN-NeerjaNeural")
    # Azure/edge-tts: +40% ≈ 1.4× default speaking rate (see prosody rate docs).
    communicate = edge_tts.Communicate(payload.text, voice=voice, rate="+40%")
    audio_chunks: list[bytes] = []
    try:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"TTS synthesis failed: {exc}") from exc

    if not audio_chunks:
        raise HTTPException(status_code=502, detail="TTS synthesis returned empty audio")

    return Response(content=b"".join(audio_chunks), media_type="audio/mpeg")
