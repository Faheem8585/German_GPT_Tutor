"""Games API — create games, submit answers, fetch leaderboard."""

from __future__ import annotations

import time

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel

from app.memory.user_memory import UserMemoryService
from app.models.user import CEFRLevel
from app.services.game_service import GameType, game_service

router = APIRouter(prefix="/games", tags=["Games"])


class CreateGameRequest(BaseModel):
    game_type: GameType
    cefr_level: CEFRLevel = CEFRLevel.A1
    topic: str | None = None


class SubmitAnswerRequest(BaseModel):
    game_id: str
    answers: list[dict]  # [{"question_index": 0, "answer": "value"}]
    questions: list[dict]
    game_type: GameType
    time_taken_seconds: float
    cefr_level: CEFRLevel = CEFRLevel.A1


@router.post("/create")
async def create_game(request: CreateGameRequest):
    """Generate a new AI-powered game."""
    session = await game_service.create_game(
        game_type=request.game_type,
        cefr_level=request.cefr_level,
        topic=request.topic,
    )
    return {
        "game_id": session.game_id,
        "game_type": session.game_type.value,
        "cefr_level": session.cefr_level,
        "questions": session.questions,
        "time_limit_seconds": session.time_limit_seconds,
        "xp_per_correct": session.xp_per_correct,
    }


@router.post("/submit")
async def submit_game_result(
    request: SubmitAnswerRequest,
    background_tasks: BackgroundTasks,
    memory: UserMemoryService = Depends(UserMemoryService),
):
    """Submit game answers and get scored results."""
    user_id = "demo_user"

    result = game_service.calculate_result(
        game_id=request.game_id,
        user_id=user_id,
        game_type=request.game_type,
        answers=request.answers,
        questions=request.questions,
        time_taken=request.time_taken_seconds,
    )

    # Persist XP
    background_tasks.add_task(memory.add_xp, user_id, result.xp_earned)
    background_tasks.add_task(memory.update_streak, user_id)

    # Check achievements
    current_xp = await memory.get_xp(user_id)
    streak = await memory.get_streak(user_id)

    new_achievements = game_service.check_achievements(
        user_xp=current_xp + result.xp_earned,
        streak_days=streak,
        games_played=1,
        cefr_level=request.cefr_level.value,
        last_accuracy=result.accuracy_percent,
    )

    return {
        "game_id": result.game_id,
        "score": result.score,
        "correct_answers": result.correct_answers,
        "total_questions": result.total_questions,
        "accuracy_percent": result.accuracy_percent,
        "xp_earned": result.xp_earned,
        "time_taken_seconds": result.time_taken_seconds,
        "mistakes": result.mistakes,
        "new_achievements": new_achievements,
        "level_up": result.level_up,
    }


@router.get("/daily-missions")
async def get_daily_missions(
    cefr_level: CEFRLevel = CEFRLevel.A1,
    memory: UserMemoryService = Depends(UserMemoryService),
):
    """Get personalized daily missions."""
    user_id = "demo_user"
    missions = await game_service.get_daily_missions(cefr_level, user_id)
    xp = await memory.get_xp(user_id)
    streak = await memory.get_streak(user_id)

    return {
        "missions": missions,
        "current_xp": xp,
        "current_streak": streak,
        "next_milestone": max(100, ((xp // 100) + 1) * 100),
    }


@router.get("/leaderboard")
async def get_leaderboard():
    """Get global XP leaderboard (demo data)."""
    # In production, this queries the PostgreSQL users table ordered by xp_points
    return {
        "leaderboard": [
            {"rank": 1, "username": "GermanMaster_Anna", "xp": 15420, "streak": 45, "level": "C1"},
            {"rank": 2, "username": "BerlinBound_Max", "xp": 12800, "streak": 38, "level": "B2"},
            {"rank": 3, "username": "Sprachprofi_Priya", "xp": 11200, "streak": 22, "level": "B2"},
            {"rank": 4, "username": "DeutschFan_Carlos", "xp": 9800, "streak": 15, "level": "B1"},
            {"rank": 5, "username": "You", "xp": 0, "streak": 0, "level": "A1"},
        ],
        "updated_at": time.time(),
    }


@router.get("/types")
async def get_game_types():
    """List all available game types with descriptions."""
    return {
        "games": [
            {
                "type": GameType.WORD_MATCH.value,
                "name": "Word Match",
                "name_de": "Wörter zuordnen",
                "description": "Match German words to their English meanings",
                "xp_per_correct": 5,
                "time_limit": 180,
                "icon": "🃏",
            },
            {
                "type": GameType.SENTENCE_BUILDER.value,
                "name": "Sentence Builder",
                "name_de": "Sätze bauen",
                "description": "Arrange scrambled words into correct German sentences",
                "xp_per_correct": 10,
                "time_limit": 300,
                "icon": "🏗️",
            },
            {
                "type": GameType.VOCABULARY_BATTLE.value,
                "name": "Vocabulary Battle",
                "name_de": "Vokabel-Kampf",
                "description": "Speed-round multiple choice vocabulary quiz",
                "xp_per_correct": 8,
                "time_limit": 90,
                "icon": "⚔️",
            },
            {
                "type": GameType.FILL_IN_BLANK.value,
                "name": "Fill in the Blank",
                "name_de": "Lückentext",
                "description": "Complete German sentences with the correct word",
                "xp_per_correct": 12,
                "time_limit": 240,
                "icon": "✍️",
            },
            {
                "type": GameType.LISTENING_QUIZ.value,
                "name": "Listening Quiz",
                "name_de": "Hörübung",
                "description": "Listen to German and answer comprehension questions",
                "xp_per_correct": 15,
                "time_limit": 240,
                "icon": "🎧",
            },
            {
                "type": GameType.PRONUNCIATION_CHALLENGE.value,
                "name": "Pronunciation Challenge",
                "name_de": "Aussprache-Challenge",
                "description": "Speak German words and get AI pronunciation feedback",
                "xp_per_correct": 20,
                "time_limit": 300,
                "icon": "🎤",
            },
            {
                "type": GameType.SURVIVAL_MODE.value,
                "name": "Survival Mode",
                "name_de": "Überlebensmodus",
                "description": "Keep answering correctly — one wrong answer ends the game!",
                "xp_per_correct": 25,
                "time_limit": 120,
                "icon": "💀",
            },
        ]
    }
