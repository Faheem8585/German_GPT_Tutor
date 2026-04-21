"""Motivation coach agent — keeps learners engaged and prevents dropout."""

from __future__ import annotations

import structlog

from app.prompts.library import MOTIVATION_COACH_PROMPT
from app.services.llm_service import LLMMessage, LLMResponse, llm_service

logger = structlog.get_logger(__name__)


class MotivationAgent:
    async def encourage(
        self,
        user_id: str,
        messages: list[dict],
        streak_days: int = 0,
        xp_points: int = 0,
        recent_mistakes: list[str] | None = None,
    ) -> LLMResponse:
        context = f"""
Student Stats:
- Current streak: {streak_days} days
- Total XP: {xp_points}
- Recent challenges: {', '.join(recent_mistakes) if recent_mistakes else 'None identified'}
"""
        recent_msgs = messages[-4:] if len(messages) > 4 else messages
        llm_messages = [
            LLMMessage(
                role=m["role"] if isinstance(m, dict) else {"human": "user", "ai": "assistant"}.get(m.type, m.type),
                content=m["content"] if isinstance(m, dict) else m.content,
            )
            for m in recent_msgs
        ]
        llm_messages.insert(0, LLMMessage(role="user", content=context))

        return await llm_service.complete(
            messages=llm_messages,
            system_prompt=MOTIVATION_COACH_PROMPT,
            temperature=0.85,
            max_tokens=512,
        )

    async def generate_daily_challenge(self, cefr_level: str) -> str:
        response = await llm_service.complete(
            messages=[
                LLMMessage(
                    role="user",
                    content=f"Generate an exciting daily German challenge for CEFR level {cefr_level}. Make it fun, achievable in 10 minutes, and rewarding. Include an XP reward suggestion.",
                )
            ],
            system_prompt=MOTIVATION_COACH_PROMPT,
            temperature=0.9,
            max_tokens=300,
        )
        return response.content
