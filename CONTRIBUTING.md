# Contributing

## Running locally

```bash
cp .env.example .env   # add GOOGLE_API_KEY
docker compose up --build
```

The app is at `http://localhost:3000`, API docs at `http://localhost:8000/docs`.

## Project layout

```
backend/app/agents/     LangGraph nodes
backend/app/api/v1/     FastAPI routes
backend/app/rag/        Hybrid retrieval pipeline
backend/app/prompts/    System prompts
frontend/src/app/       Next.js pages
```

## Backend changes

```bash
# shell into the running container
docker compose exec backend bash

# run tests
pytest tests/ -v

# after changing a model, create a migration
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Frontend changes

```bash
docker compose exec frontend sh
# Next.js hot-reloads automatically inside the container
```

## Switching the LLM

Set `DEFAULT_LLM_PROVIDER` and `DEFAULT_CHAT_MODEL` in `.env`:

| Provider | Value | Model example |
|----------|-------|---------------|
| Google (free) | `gemini` | `gemma-3-12b-it` |
| Anthropic | `anthropic` | `claude-sonnet-4-6` |
| OpenAI | `openai` | `gpt-4o` |

## Adding a game type

1. Add a prompt in `backend/app/prompts/library.py` → `get_game_prompt()`
2. Add the type to `GameType` enum in `backend/app/api/v1/games.py`
3. Add a component in `frontend/src/app/games/page.tsx`

## Notes

- Gemma models don't support `system_instruction` — the system prompt is prepended to the first user message instead
- Voice input/output uses browser-native APIs (no paid key needed)
- Qdrant healthcheck uses a bash TCP probe because the image doesn't have `curl`
