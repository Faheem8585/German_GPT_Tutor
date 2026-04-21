"""Tutor API — text and streaming conversation endpoints."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agents.orchestrator import orchestrator
from app.core.security import detect_prompt_injection, sanitize_user_input
from app.memory.user_memory import UserMemoryService
from app.models.user import CEFRLevel, InterfaceLanguage
from app.services.llm_service import LLMMessage

router = APIRouter(prefix="/tutor", tags=["Tutor"])


class ChatMessage(BaseModel):
    role: str
    content: str


class TutorRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096)
    session_id: str | None = None
    cefr_level: CEFRLevel = CEFRLevel.A1
    interface_language: InterfaceLanguage = InterfaceLanguage.EN
    mode: str = "text"  # text | voice


class TutorResponse(BaseModel):
    response: str
    session_id: str
    grammar_errors: list[dict]
    xp_earned: int
    intent: str
    metadata: dict


class ConversationRequest(BaseModel):
    scenario: str  # job_interview | apartment_rental | doctor_visit | etc.
    cefr_level: CEFRLevel = CEFRLevel.B1
    interface_language: InterfaceLanguage = InterfaceLanguage.EN


@router.post("/chat", response_model=TutorResponse)
async def chat(
    request: TutorRequest,
    # current_user: Annotated[dict, Depends(get_current_user)],  # Enable with auth
    background_tasks: BackgroundTasks,
    memory: UserMemoryService = Depends(UserMemoryService),
):
    """Send a message to the German tutor and get a response."""
    user_id = "demo_user"  # Replace with current_user["id"] when auth enabled
    session_id = request.session_id or str(uuid.uuid4())

    # Sanitize input
    clean_message = sanitize_user_input(request.message)

    # Load conversation history
    history = await memory.get_session_history(user_id, session_id)

    # Run through multi-agent orchestrator
    result = await orchestrator.run(
        user_message=clean_message,
        user_id=user_id,
        cefr_level=request.cefr_level,
        interface_language=request.interface_language,
        conversation_history=history,
    )

    # Persist messages in background
    background_tasks.add_task(
        memory.append_message, user_id, session_id, "user", clean_message
    )
    background_tasks.add_task(
        memory.append_message, user_id, session_id, "assistant", result["response"]
    )
    background_tasks.add_task(memory.add_xp, user_id, result["xp_earned"])
    background_tasks.add_task(memory.update_streak, user_id)

    return TutorResponse(
        response=result["response"],
        session_id=session_id,
        grammar_errors=result.get("grammar_errors", []),
        xp_earned=result.get("xp_earned", 0),
        intent=result.get("intent", "tutor"),
        metadata=result.get("metadata", {}),
    )


@router.post("/chat/stream")
async def chat_stream(
    request: TutorRequest,
    memory: UserMemoryService = Depends(UserMemoryService),
):
    """Stream tutor response token-by-token via Server-Sent Events."""
    user_id = "demo_user"
    session_id = request.session_id or str(uuid.uuid4())
    clean_message = sanitize_user_input(request.message)
    history = await memory.get_session_history(user_id, session_id)

    # Add user message to history for context
    history.append({"role": "user", "content": clean_message})

    from app.agents.tutor_agent import TutorAgent
    tutor = TutorAgent()

    async def event_generator():
        try:
            async for chunk in tutor.stream_response(
                messages=history,
                cefr_level=request.cefr_level,
                interface_language=request.interface_language,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/conversation/start")
async def start_conversation(
    request: ConversationRequest,
    memory: UserMemoryService = Depends(UserMemoryService),
):
    """Start a structured conversation scenario (job interview, doctor visit, etc.)."""
    from app.prompts.library import CONVERSATION_SCENARIOS
    from app.services.llm_service import llm_service, LLMMessage
    from app.prompts.library import build_tutor_system_prompt

    scenario_prompt = CONVERSATION_SCENARIOS.get(request.scenario)
    if not scenario_prompt:
        raise HTTPException(status_code=404, detail=f"Scenario '{request.scenario}' not found")

    session_id = str(uuid.uuid4())
    system = build_tutor_system_prompt(request.cefr_level, request.interface_language)
    system += f"\n\n## Current Scenario\n{scenario_prompt}"

    # Generate opening message for the scenario
    response = await llm_service.complete(
        messages=[
            LLMMessage(
                role="user",
                content="Please start this conversation scenario. Set the scene and say your opening line.",
            )
        ],
        system_prompt=system,
        temperature=0.8,
    )

    return {
        "session_id": session_id,
        "scenario": request.scenario,
        "opening_message": response.content,
        "system_prompt_used": system[:200] + "...",
    }


@router.get("/scenarios")
async def list_scenarios():
    """List all available conversation scenarios."""
    from app.prompts.library import CONVERSATION_SCENARIOS
    return {
        "scenarios": [
            {
                "id": key,
                "name": key.replace("_", " ").title(),
                "description": value[:100] + "...",
            }
            for key, value in CONVERSATION_SCENARIOS.items()
        ]
    }


@router.post("/grammar/check")
async def grammar_check(
    text: str,
    cefr_level: CEFRLevel = CEFRLevel.B1,
):
    """Standalone grammar checking endpoint."""
    from app.agents.grammar_agent import GrammarAgent
    agent = GrammarAgent()
    errors = await agent.analyze(text=text, cefr_level=cefr_level)
    return {
        "text": text,
        "errors": errors,
        "error_count": len(errors),
        "grade": "A" if not errors else ("B" if len(errors) < 2 else "C"),
    }


@router.post("/pronunciation/guide")
async def pronunciation_guide(word: str):
    """Get pronunciation guide for a German word."""
    from app.services.voice_service import voice_service
    guide = await voice_service.generate_pronunciation_guide(word)
    return {"word": word, "guide": guide}


@router.get("/level/estimate")
async def estimate_level(sample: str):
    """Auto-detect CEFR level from a German writing sample."""
    from app.agents.planner_agent import PlannerAgent
    planner = PlannerAgent()
    level = await planner.estimate_level([sample])
    return {"estimated_level": level.value, "sample": sample}
