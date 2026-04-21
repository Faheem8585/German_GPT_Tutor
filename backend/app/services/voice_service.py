"""Voice AI service — STT (Whisper) + TTS (OpenAI/ElevenLabs) + pronunciation scoring."""

from __future__ import annotations

import io
import time
from dataclasses import dataclass

import structlog
from openai import AsyncOpenAI

from app.config import settings
from app.core.exceptions import VoiceProcessingError

logger = structlog.get_logger(__name__)


@dataclass
class TranscriptionResult:
    text: str
    language: str
    confidence: float
    duration_seconds: float
    latency_ms: float


@dataclass
class PronunciationScore:
    overall_score: float  # 0-100
    fluency_score: float
    accuracy_score: float
    feedback: str
    problem_sounds: list[str]


class VoiceService:
    """Multi-provider voice AI — STT + TTS + pronunciation analysis."""

    def __init__(self) -> None:
        self._openai: AsyncOpenAI | None = None

    @property
    def openai(self) -> AsyncOpenAI:
        if self._openai is None:
            self._openai = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._openai

    async def transcribe(
        self,
        audio_bytes: bytes,
        language: str = "de",
        prompt: str | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio using OpenAI Whisper."""
        if len(audio_bytes) > settings.max_audio_size_mb * 1024 * 1024:
            raise VoiceProcessingError(
                f"Audio file exceeds {settings.max_audio_size_mb}MB limit"
            )

        t0 = time.monotonic()
        try:
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.webm"

            kwargs = {
                "model": settings.openai_whisper_model,
                "file": audio_file,
                "language": language,
                "response_format": "verbose_json",
            }
            if prompt:
                kwargs["prompt"] = prompt

            response = await self.openai.audio.transcriptions.create(**kwargs)
            latency = (time.monotonic() - t0) * 1000

            return TranscriptionResult(
                text=response.text,
                language=response.language or language,
                confidence=0.95,  # Whisper doesn't return confidence scores
                duration_seconds=getattr(response, "duration", 0.0),
                latency_ms=latency,
            )
        except Exception as e:
            raise VoiceProcessingError(f"Transcription failed: {e}") from e

    async def synthesize(
        self,
        text: str,
        voice: str = "nova",
        speed: float = 0.9,
        format: str = "mp3",
    ) -> bytes:
        """Convert text to speech using OpenAI TTS."""
        if not text.strip():
            raise VoiceProcessingError("Empty text for synthesis")

        try:
            response = await self.openai.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=text,
                speed=speed,
                response_format=format,
            )
            return response.content
        except Exception as e:
            raise VoiceProcessingError(f"TTS synthesis failed: {e}") from e

    async def score_pronunciation(
        self,
        reference_text: str,
        spoken_text: str,
        native_language: str = "en",
        cefr_level: str = "B1",
    ) -> PronunciationScore:
        """
        Score pronunciation by comparing what was said vs. what should have been said.
        Uses LLM to identify phonetic issues based on transcription comparison.
        """
        from app.services.llm_service import LLMMessage, llm_service

        prompt = f"""Analyze German pronunciation quality.

Reference text (what should be said): "{reference_text}"
Spoken text (what was transcribed): "{spoken_text}"
Native language of speaker: {native_language}
CEFR Level: {cefr_level}

Evaluate:
1. Accuracy (0-100): How close is the spoken to the reference?
2. Common German pronunciation issues for {native_language} speakers
3. Specific sounds that need work

Respond in JSON:
{{
  "overall_score": 85,
  "fluency_score": 80,
  "accuracy_score": 90,
  "feedback": "brief encouraging feedback",
  "problem_sounds": ["ü", "ch"]
}}"""

        try:
            response = await llm_service.complete(
                messages=[LLMMessage(role="user", content=prompt)],
                temperature=0.1,
                max_tokens=300,
            )

            import json, re
            content = response.content
            match = re.search(r"\{[\s\S]+\}", content)
            if match:
                data = json.loads(match.group(0))
                return PronunciationScore(
                    overall_score=data.get("overall_score", 70),
                    fluency_score=data.get("fluency_score", 70),
                    accuracy_score=data.get("accuracy_score", 70),
                    feedback=data.get("feedback", "Keep practicing!"),
                    problem_sounds=data.get("problem_sounds", []),
                )
        except Exception as e:
            logger.warning("pronunciation_scoring_failed", error=str(e))

        return PronunciationScore(
            overall_score=70.0,
            fluency_score=70.0,
            accuracy_score=70.0,
            feedback="Good effort! Keep practicing your German pronunciation.",
            problem_sounds=[],
        )

    async def generate_pronunciation_guide(self, word: str) -> str:
        """Generate a detailed pronunciation guide for a German word."""
        from app.services.llm_service import LLMMessage, llm_service
        from app.prompts.library import PRONUNCIATION_COACH_PROMPT

        response = await llm_service.complete(
            messages=[
                LLMMessage(
                    role="user",
                    content=f"Explain how to pronounce the German word/phrase: '{word}'. Include IPA, mouth position, and a memory trick.",
                )
            ],
            system_prompt=PRONUNCIATION_COACH_PROMPT,
            temperature=0.5,
            max_tokens=400,
        )
        return response.content


voice_service = VoiceService()
