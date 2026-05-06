# Nyaay Sathi (MVP Scaffold)

Voice-first, multilingual legal navigator for India.

## Project overview

Nyaay Sathi is built to solve a simple but critical gap: many people face legal problems, but do not know where to start, which office to approach, what documents to collect, or how to explain their case clearly.

The idea is **not** to replace lawyers or courts. The idea is to provide a calm, multilingual, first-step legal companion that turns confusion into an actionable path:

- Explain legal issues in plain language (instead of heavy legal jargon)
- Ask smart follow-up questions to understand missing facts
- Suggest likely forums (labour office, consumer forum, DLSA, police station, etc.)
- List useful documents to prepare
- Generate a complaint draft PDF that users can take forward
- Detect crisis situations and prioritize immediate safety guidance

In short, Nyaay Sathi helps people move from **\"I don't know what to do\"** to **\"I know my next step\"**, especially for common everyday issues like wages, tenancy, consumer fraud, women's protection, and FIR-related problems.

This repository currently contains the first backend slice:

- Employment category seed data ingest pipeline
- FastAPI orchestrator endpoint with:
  - cheap-model LLM classification/composition (Ollama local model by default)
  - rule-based local fallback when LLM/key is unavailable
  - crisis detection (multilingual keywords + immediate short-circuit routing)
  - clarifying-question loop (asks for missing facts before detailed guidance)
  - legal response composition with source citations and source-gating
  - `/v1/config` endpoint for active model/provider visibility

## Quick start

1. Create and activate a virtual environment
2. Install dependencies
3. Run ingest
4. Start API

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python scripts/ingest_all_categories.py
uvicorn app.main:app --reload --port 8000
```

## Frontend demo dashboard

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:3000` for:
- Coverage map (honest live vs roadmap status)
- Backend config check (`/v1/config`)
- Orchestrator tester (`/v1/orchestrate`)

## LiveKit voice agent

```bash
cd voice
pip install -r requirements.txt
python livekit_agent.py dev
```

This voice agent sends user utterances to backend `/v1/orchestrate` and speaks back legal guidance.

## Complaint PDF generation

```bash
curl -X POST http://127.0.0.1:8000/v1/complaint-pdf \
  -H "Content-Type: application/json" \
  -o complaint.pdf \
  -d '{
    "message": "My employer has not paid wage for 3 months amount 30000",
    "language": "en",
    "district": "Pune"
  }'
```

This returns a downloadable complaint draft PDF.

Optional environment variables for cheap LLM mode (local Ollama default):

```bash
export LLM_PROVIDER="ollama"
export OLLAMA_API_URL="http://127.0.0.1:11434/api/generate"
export OLLAMA_MODEL="qwen2.5:1.5b"
```

To switch to Anthropic for deployment:

```bash
export LLM_PROVIDER="anthropic"
export ANTHROPIC_API_KEY="your_key_here"
export ANTHROPIC_CHEAP_MODEL="claude-3-5-haiku-latest"
```

## Test the API

```bash
curl -X POST http://127.0.0.1:8000/v1/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My employer is not paying minimum wages for 3 months",
    "language": "en",
    "district": "Pune"
  }'
```

## Smoke tests

```bash
source .venv/bin/activate
PYTHONPATH=backend python -m pytest backend/tests -q
```

## Product mode (end-user flow)

Run the app as a final-user experience (voice + text + PDF):

```bash
./scripts/run_product.sh
```

Then open `http://127.0.0.1:3000` and use:
- **Start Voice Call** (auto token generation, no manual token steps)
- **Get Legal Guidance** (text flow)
- **Download Complaint PDF**

To stop everything:

```bash
./scripts/stop_product.sh
```

## Docker deployment

```bash
docker compose up --build
```

Brings up backend (port 8000), frontend (port 3000), and the LiveKit voice worker. Reads LLM and LiveKit credentials from your shell env (or a `.env` next to the compose file).

## Demo script

See [`DEMO.md`](DEMO.md) for the 5-minute live demo plan with 5 ready-made prompts, expected outputs, and a crisis short-circuit demo.

## Current limits

- Voice agent requires LiveKit credentials and OpenAI key to connect.
- RAG is local JSON retrieval (Qdrant integration next).
- PDF uses Arial Unicode / DejaVuSans when available for Indic scripts; falls back to Helvetica otherwise.
