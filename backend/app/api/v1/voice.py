"""Voice API — STT, TTS, pronunciation scoring."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from app.core.exceptions import VoiceProcessingError
from app.models.user import CEFRLevel
from app.services.voice_service import voice_service

router = APIRouter(prefix="/voice", tags=["Voice"])


class PronunciationRequest(BaseModel):
    reference_text: str
    spoken_text: str
    native_language: str = "en"
    cefr_level: CEFRLevel = CEFRLevel.B1


class TTSRequest(BaseModel):
    text: str
    voice: str = "nova"  # openai voices: alloy, echo, fable, onyx, nova, shimmer
    speed: float = 0.9


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form(default="de"),
    session_context: str = Form(default=""),
):
    """Transcribe audio to text using Whisper."""
    if not audio.content_type or not any(
        ct in audio.content_type for ct in ["audio", "video", "octet-stream"]
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {audio.content_type}. Expected audio file.",
        )

    try:
        audio_bytes = await audio.read()
        result = await voice_service.transcribe(
            audio_bytes=audio_bytes,
            language=language,
            prompt=session_context or None,
        )
        return {
            "text": result.text,
            "language": result.language,
            "confidence": result.confidence,
            "duration_seconds": result.duration_seconds,
            "latency_ms": result.latency_ms,
        }
    except VoiceProcessingError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """Convert German text to speech."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if len(request.text) > 4096:
        raise HTTPException(status_code=400, detail="Text too long (max 4096 chars)")

    try:
        audio_bytes = await voice_service.synthesize(
            text=request.text,
            voice=request.voice,
            speed=request.speed,
        )
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "X-Text-Length": str(len(request.text)),
            },
        )
    except VoiceProcessingError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/pronunciation/score")
async def score_pronunciation(request: PronunciationRequest):
    """Score pronunciation accuracy."""
    score = await voice_service.score_pronunciation(
        reference_text=request.reference_text,
        spoken_text=request.spoken_text,
        native_language=request.native_language,
        cefr_level=request.cefr_level.value,
    )
    return {
        "overall_score": score.overall_score,
        "fluency_score": score.fluency_score,
        "accuracy_score": score.accuracy_score,
        "feedback": score.feedback,
        "problem_sounds": score.problem_sounds,
        "xp_earned": max(0, int(score.overall_score / 2)),  # Max 50 XP for pronunciation
    }


@router.post("/voice-tutor")
async def voice_tutor_session(
    audio: UploadFile = File(...),
    cefr_level: str = Form(default="A1"),
    session_id: str = Form(default=""),
    language: str = Form(default="de"),
):
    """Full voice tutor loop: STT → AI response → TTS."""
    # Step 1: Transcribe
    audio_bytes = await audio.read()
    try:
        transcription = await voice_service.transcribe(
            audio_bytes=audio_bytes, language=language
        )
    except VoiceProcessingError as e:
        raise HTTPException(status_code=422, detail=f"Transcription failed: {e}")

    user_text = transcription.text
    if not user_text.strip():
        raise HTTPException(status_code=422, detail="Could not transcribe audio. Please speak clearly.")

    # Step 2: Get AI tutor response
    from app.agents.orchestrator import orchestrator
    from app.models.user import CEFRLevel as Level, InterfaceLanguage

    try:
        level = Level(cefr_level.upper())
    except ValueError:
        level = Level.A1

    result = await orchestrator.run(
        user_message=user_text,
        user_id="voice_demo_user",
        cefr_level=level,
        interface_language=InterfaceLanguage.EN,
    )

    # Step 3: Synthesize response
    try:
        audio_response = await voice_service.synthesize(
            text=result["response"],
            voice="nova",
            speed=0.85,
        )
    except VoiceProcessingError:
        audio_response = b""

    # Return as multipart with JSON metadata + audio
    import base64

    return {
        "transcription": user_text,
        "response_text": result["response"],
        "grammar_errors": result.get("grammar_errors", []),
        "xp_earned": result.get("xp_earned", 0),
        "audio_base64": base64.b64encode(audio_response).decode() if audio_response else None,
    }
