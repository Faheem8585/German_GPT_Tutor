"""Grammar analysis agent with structured output."""

from __future__ import annotations

import json
import re

import structlog

from app.models.user import CEFRLevel
from app.prompts.library import GRAMMAR_CHECKER_PROMPT
from app.services.llm_service import LLMMessage, llm_service

logger = structlog.get_logger(__name__)

_ANALYSIS_PROMPT = """Analyze the following German text for grammar errors.

Text: "{text}"
Student Level: {level}

Return ONLY valid JSON in this exact format:
{{
  "errors": [
    {{
      "incorrect": "the wrong form",
      "correct": "the right form",
      "rule": "brief rule name",
      "explanation": "why it's wrong",
      "severity": "minor|major"
    }}
  ],
  "overall_grade": "A|B|C|D|F",
  "positive_feedback": "what they did well",
  "style_suggestions": ["suggestion1", "suggestion2"]
}}

If there are no errors, return an empty "errors" array."""


class GrammarAgent:
    """Structured German grammar checker returning JSON analysis."""

    async def analyze(
        self,
        text: str,
        cefr_level: CEFRLevel,
    ) -> list[dict]:
        if not text or len(text.strip()) < 3:
            return []

        prompt = _ANALYSIS_PROMPT.format(text=text, level=cefr_level.value)

        try:
            response = await llm_service.complete(
                messages=[LLMMessage(role="user", content=prompt)],
                system_prompt=GRAMMAR_CHECKER_PROMPT,
                temperature=0.1,
                max_tokens=1024,
            )
            result = self._parse_json_response(response.content)
            return result.get("errors", [])
        except Exception as e:
            logger.warning("grammar_analysis_failed", error=str(e))
            return []

    def _parse_json_response(self, content: str) -> dict:
        # Try direct parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Extract JSON from markdown code block
        match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", content)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Last resort: find first { } block
        match = re.search(r"\{[\s\S]+\}", content)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return {"errors": [], "overall_grade": "N/A"}
