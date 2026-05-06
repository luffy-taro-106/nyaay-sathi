import json
import os
from urllib import request

from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai, silero


ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://127.0.0.1:8000/v1/orchestrate")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
DEFAULT_DISTRICT = os.getenv("DEFAULT_DISTRICT", "Pune")


def call_orchestrator(message: str, language: str, district: str) -> dict:
    payload = {
        "message": message,
        "language": language,
        "district": district,
    }
    req = request.Request(
        ORCHESTRATOR_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


class NyaaySathiAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are Nyaay Sathi voice assistant. Speak clearly in short steps. "
                "Never claim legal advice or case outcome prediction."
            )
        )

    async def on_user_turn_completed(self, session: AgentSession, message: str) -> None:
        try:
            result = call_orchestrator(message, DEFAULT_LANGUAGE, DEFAULT_DISTRICT)
            spoken = result.get("rights_summary", "I could not process that. Please try again.")
            if result.get("needs_clarification"):
                questions = result.get("clarifying_questions", [])
                if questions:
                    spoken += " " + " ".join(questions[:2])
            if result.get("crisis_detected"):
                helplines = result.get("helplines", [])
                if helplines:
                    spoken += " Emergency contacts: " + ", ".join(helplines)
        except Exception:
            spoken = "I could not reach legal backend right now. Please retry."
        await session.say(spoken)


async def entrypoint(ctx: JobContext) -> None:
    await ctx.connect()
    session = AgentSession(
        stt=openai.STT(model="gpt-4o-mini-transcribe"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(model="gpt-4o-mini-tts"),
        vad=silero.VAD.load(),
    )
    await session.start(agent=NyaaySathiAgent(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
