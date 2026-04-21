"""Core tutor agent — the primary conversational German teacher."""

from __future__ import annotations

import structlog

from app.models.user import CEFRLevel, InterfaceLanguage
from app.prompts.library import (
    FEW_SHOT_GRAMMAR_CORRECTIONS,
    build_tutor_system_prompt,
)
from app.services.llm_service import LLMMessage, LLMResponse, llm_service

logger = structlog.get_logger(__name__)

_LC_ROLE_MAP = {"human": "user", "ai": "assistant", "system": "system"}


def _msg_role(m) -> str:
    return m["role"] if isinstance(m, dict) else _LC_ROLE_MAP.get(m.type, m.type)


def _msg_content(m) -> str:
    return m["content"] if isinstance(m, dict) else m.content


_FEW_SHOT_PREFIX = "\n".join(
    f"Human: {ex['user']}\nAssistant: {ex['assistant']}"
    for ex in FEW_SHOT_GRAMMAR_CORRECTIONS
)


class TutorAgent:
    """Conversational German tutor with level-adaptive responses."""

    async def respond(
        self,
        messages: list[dict],
        cefr_level: CEFRLevel,
        interface_language: InterfaceLanguage = InterfaceLanguage.EN,
        rag_context: str = "",
        weak_areas: list[str] | None = None,
        lesson_focus: str | None = None,
    ) -> LLMResponse:
        system_prompt = build_tutor_system_prompt(
            cefr_level=cefr_level,
            interface_lang=interface_language,
            weak_areas=weak_areas,
            lesson_focus=lesson_focus,
        )

        if rag_context:
            system_prompt += f"\n\n## Relevant Knowledge Base Context\n{rag_context}\n\nUse this context to provide accurate, sourced information when relevant."

        if len(messages) < 4:
            system_prompt += f"\n\n## Example Interactions\n{_FEW_SHOT_PREFIX}"

        llm_messages = [
            LLMMessage(role=_msg_role(m), content=_msg_content(m))
            for m in messages
            if _msg_role(m) in ("user", "assistant")
        ]

        response = await llm_service.complete(
            messages=llm_messages,
            system_prompt=system_prompt,
            temperature=0.75,
        )
        logger.info(
            "tutor_response",
            cefr_level=cefr_level.value,
            tokens=response.total_tokens(),
            latency_ms=round(response.latency_ms),
        )
        return response

    async def stream_response(
        self,
        messages: list[dict],
        cefr_level: CEFRLevel,
        interface_language: InterfaceLanguage = InterfaceLanguage.EN,
        rag_context: str = "",
    ):
        """Async generator for streaming tutor responses."""
        system_prompt = build_tutor_system_prompt(
            cefr_level=cefr_level,
            interface_lang=interface_language,
        )
        if rag_context:
            system_prompt += f"\n\n## Knowledge Base Context\n{rag_context}"

        llm_messages = [
            LLMMessage(role=_msg_role(m), content=_msg_content(m))
            for m in messages
            if _msg_role(m) in ("user", "assistant")
        ]
        async for chunk in llm_service.stream(
            messages=llm_messages,
            system_prompt=system_prompt,
            temperature=0.75,
        ):
            yield chunk
