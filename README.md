# GermanGPT Tutor

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat-square&logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=flat-square&logo=typescript&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-FF6B35?style=flat-square&logo=chainlink&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-1.9-FF3366?style=flat-square&logo=qdrant&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-3.4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Gemma](https://img.shields.io/badge/Gemma-3%2012B-4285F4?style=flat-square&logo=google&logoColor=white)

![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![CEFR](https://img.shields.io/badge/CEFR-A1--C2-8B5CF6?style=flat-square)
![Games](https://img.shields.io/badge/Games-6%20Types-F59E0B?style=flat-square)
![Status](https://img.shields.io/badge/Status-Production-22C55E?style=flat-square)

---

A German language learning app I built to practice advanced LLM engineering. It has an AI tutor that adapts to your level, grammar correction on every message, voice input/output, six types of games, a structured lesson curriculum, and a progress dashboard — all running locally with Docker Compose.

---

## Features

- **AI Tutor** — chat in German or English, get corrections with explanations, earn XP
- **Voice input** — speak into the mic, speech-to-text runs in the browser (no paid API needed)
- **Text-to-speech** — tutor reads responses in German using the browser's built-in voice
- **Games** — Vocabulary Battle, Word Match, Sentence Builder, Fill in the Blank, Listening Quiz, Pronunciation Challenge
- **Lessons** — 17 lessons across 5 units (A1 to B2), each opens a pre-configured tutor session
- **Grammar correction** — every message you send is analysed and errors are shown inline
- **Analytics** — XP over time, most common mistakes, AI response metrics
- **Multi-language UI** — explanations in English, German, or Hindi

---

## Tech Stack

**Backend:** FastAPI, SQLAlchemy (async), PostgreSQL, Redis, LangGraph, LangChain, Qdrant, rank-bm25, Pydantic v2, Structlog, Prometheus

**Frontend:** Next.js 15, React 19, TypeScript, Tailwind CSS, Zustand, TanStack Query, Framer Motion, Recharts

**AI:** Google Gemma 3 12B via `google-generativeai` (free tier), hybrid RAG (BM25 + vector search + Reciprocal Rank Fusion), LangGraph multi-agent orchestration

**Infra:** Docker Compose, Nginx, Prometheus, Grafana

---

## Architecture

The backend is built around a LangGraph state graph. Every incoming message goes through the same pipeline:

```
user message
  → safety check (prompt injection detection)
  → RAG retrieval (BM25 + Qdrant vector search, merged via RRF)
  → intent router (tutor / grammar / plan / motivate)
  → agent node
  → grammar analysis
  → response synthesiser (adds corrections, calculates XP)
  → memory update (saves mistakes to Redis/Postgres)
```

The LLM service supports Gemini, Anthropic, and OpenAI behind a single interface with tenacity retries and token tracking. I'm using Gemma 3 12B because it has a generous free tier and handles German well.

RAG combines BM25 keyword matching with Qdrant semantic search. The two result lists are merged with Reciprocal Rank Fusion before being injected into the system prompt. If vector search is unavailable (e.g. embedding model quota exceeded), it falls back to BM25-only without breaking the request.

Voice input and output both use browser-native APIs (`SpeechRecognition` / `SpeechSynthesis`) — no OpenAI or ElevenLabs key needed.

---

## Running locally

You need Docker Desktop and a Google AI API key (free at [ai.google.dev](https://ai.google.dev)).

```bash
git clone https://github.com/Faheem8585/German_GPT_Tutor
cd German_GPT_Tutor

cp .env.example .env
# add your GOOGLE_API_KEY to .env

docker compose up --build
```

| Service | URL |
|---------|-----|
| App | http://localhost:3000 |
| API docs | http://localhost:8000/docs |
| Grafana | http://localhost:3001 (admin/admin) |
| Prometheus | http://localhost:9090 |

```bash
# stop without wiping data
docker compose down

# full reset
docker compose down -v
```

---

## Project structure

```
├── backend/
│   └── app/
│       ├── agents/       # LangGraph nodes (tutor, grammar, planner, motivation, orchestrator)
│       ├── api/v1/       # FastAPI routes (tutor, games, voice, analytics)
│       ├── core/         # Auth, logging, exceptions
│       ├── memory/       # Redis-backed user memory
│       ├── models/       # SQLAlchemy models
│       ├── prompts/      # System prompts and few-shot examples
│       ├── rag/          # Hybrid retrieval pipeline + knowledge base
│       └── services/     # LLM client, game logic, voice processing
├── frontend/
│   └── src/
│       ├── app/          # Next.js pages (tutor, games, lessons, dashboard, analytics)
│       ├── lib/api.ts    # Axios client
│       └── stores/       # Zustand state (XP, CEFR level, session)
├── infra/
│   ├── nginx/            # Reverse proxy config
│   └── prometheus.yml
└── docker-compose.yml    # Postgres, Redis, Qdrant, backend, frontend, Prometheus, Grafana
```

---

## Environment variables

| Variable | Notes |
|----------|-------|
| `GOOGLE_API_KEY` | Required — gives access to Gemma 3 12B on the free tier |
| `ANTHROPIC_API_KEY` | Optional — set `DEFAULT_LLM_PROVIDER=anthropic` to use Claude |
| `OPENAI_API_KEY` | Optional — only needed for server-side Whisper/TTS (app uses browser APIs otherwise) |
| `SECRET_KEY` | Any random string, used for JWT signing |
| `DEFAULT_CHAT_MODEL` | Default: `gemma-3-12b-it` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins |

Everything else (`DATABASE_URL`, `REDIS_URL`, `QDRANT_URL`) is set automatically by docker-compose.

---

## A few things I learned building this

**Gemma vs Gemini:** Gemma models don't accept a `system_instruction` parameter like Gemini models do. I worked around it by prepending the system prompt to the first user message.

**LangGraph message types:** `add_messages` converts plain dicts into `HumanMessage`/`AIMessage` objects, so any code that tries `message["role"]` crashes. I added small helpers to handle both types.

**pydantic-settings v2:** `list[str]` fields can't parse comma-separated env vars. I switched to a `str` field with an `allowed_origins_list` property.

**Qdrant healthcheck:** The Qdrant Docker image doesn't have `curl`, so the standard healthcheck fails. I used a bash TCP probe instead: `bash -c 'echo > /dev/tcp/localhost/6333'`.

**Speech recognition on stop:** With `continuous = false`, pressing stop before a natural speech pause drops the transcript. I switched to `continuous = true` with `interimResults = true`, accumulated the transcript in a ref, and send it on `onend`.
