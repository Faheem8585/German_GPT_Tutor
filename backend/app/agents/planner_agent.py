"""Adaptive curriculum planner agent."""

from __future__ import annotations

import structlog

from app.models.user import CEFRLevel
from app.prompts.library import PLANNER_AGENT_PROMPT
from app.services.llm_service import LLMMessage, LLMResponse, llm_service

logger = structlog.get_logger(__name__)

_LEVEL_HOURS = {
    CEFRLevel.A1: (0, 80),
    CEFRLevel.A2: (80, 200),
    CEFRLevel.B1: (200, 400),
    CEFRLevel.B2: (400, 600),
    CEFRLevel.C1: (600, 900),
    CEFRLevel.C2: (900, 1200),
}

_NEXT_LEVEL = {
    CEFRLevel.A1: CEFRLevel.A2,
    CEFRLevel.A2: CEFRLevel.B1,
    CEFRLevel.B1: CEFRLevel.B2,
    CEFRLevel.B2: CEFRLevel.C1,
    CEFRLevel.C1: CEFRLevel.C2,
    CEFRLevel.C2: None,
}


class PlannerAgent:
    """Creates personalized German learning roadmaps."""

    async def create_plan(
        self,
        user_id: str,
        cefr_level: CEFRLevel,
        messages: list[dict],
        hours_per_week: int = 5,
        goals: list[str] | None = None,
    ) -> LLMResponse:
        next_level = _NEXT_LEVEL.get(cefr_level)
        _, hours_needed = _LEVEL_HOURS.get(cefr_level, (0, 100))
        weeks_estimated = max(1, hours_needed // hours_per_week)

        context = f"""
Student Profile:
- Current Level: {cefr_level.value}
- Next Target Level: {next_level.value if next_level else "Mastery"}
- Estimated hours to next level: {hours_needed}
- Study hours per week: {hours_per_week}
- Estimated weeks: {weeks_estimated}
- Goals: {', '.join(goals) if goals else 'General fluency'}
"""

        return await llm_service.complete(
            messages=[
                LLMMessage(role="user", content=f"{context}\n\nPlease create my personalized German learning plan.")
            ],
            system_prompt=PLANNER_AGENT_PROMPT,
            temperature=0.6,
        )

    async def estimate_level(self, sample_texts: list[str]) -> CEFRLevel:
        """Auto-detect CEFR level from writing samples."""
        combined = "\n".join(f"- {t}" for t in sample_texts[:5])
        prompt = f"""Analyze these German writing samples and classify the CEFR level (A1/A2/B1/B2/C1/C2).

Samples:
{combined}

Respond with ONLY the CEFR level code (e.g., "B1") followed by a one-sentence justification."""

        response = await llm_service.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            temperature=0.1,
            max_tokens=100,
        )
        content = response.content.strip().upper()
        for level in CEFRLevel:
            if level.value in content[:3]:
                return level
        return CEFRLevel.A1
