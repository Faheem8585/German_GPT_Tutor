"""Game engine — generates and validates all learning games."""

from __future__ import annotations

import json
import random
import re
import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

from app.models.user import CEFRLevel
from app.prompts.library import get_game_prompt
from app.services.llm_service import LLMMessage, llm_service

logger = structlog.get_logger(__name__)


class GameType(str, Enum):
    WORD_MATCH = "word_match"
    SENTENCE_BUILDER = "sentence_builder"
    LISTENING_QUIZ = "listening_quiz"
    VOCABULARY_BATTLE = "vocabulary_battle"
    FILL_IN_BLANK = "fill_in_blank"
    PRONUNCIATION_CHALLENGE = "pronunciation_challenge"
    TIMED_TRANSLATION = "timed_translation"
    SURVIVAL_MODE = "survival_mode"


@dataclass
class GameSession:
    game_id: str
    game_type: GameType
    cefr_level: str
    questions: list[dict]
    time_limit_seconds: int
    xp_per_correct: int
    created_at: float = field(default_factory=time.time)


@dataclass
class GameResult:
    game_id: str
    user_id: str
    score: int
    correct_answers: int
    total_questions: int
    time_taken_seconds: float
    xp_earned: int
    accuracy_percent: float
    mistakes: list[dict]
    level_up: bool = False


# XP table per game type
_XP_TABLE = {
    GameType.WORD_MATCH: 5,
    GameType.SENTENCE_BUILDER: 10,
    GameType.LISTENING_QUIZ: 15,
    GameType.VOCABULARY_BATTLE: 8,
    GameType.FILL_IN_BLANK: 12,
    GameType.PRONUNCIATION_CHALLENGE: 20,
    GameType.TIMED_TRANSLATION: 10,
    GameType.SURVIVAL_MODE: 25,
}

# Achievement thresholds
ACHIEVEMENTS = {
    "first_game": {"name": "Anfänger", "description": "Complete your first game", "xp": 50},
    "streak_7": {"name": "Wochenheld", "description": "7-day learning streak", "xp": 100},
    "streak_30": {"name": "Monatschampion", "description": "30-day streak", "xp": 500},
    "xp_1000": {"name": "Lernprofi", "description": "Earn 1000 XP", "xp": 100},
    "xp_10000": {"name": "Sprachmeister", "description": "Earn 10,000 XP", "xp": 1000},
    "perfect_game": {"name": "Perfektionist", "description": "100% accuracy in a game", "xp": 200},
    "b1_unlocked": {"name": "B1 Erreicht!", "description": "Reach B1 level", "xp": 300},
    "b2_unlocked": {"name": "B2 Erreicht!", "description": "Reach B2 level", "xp": 500},
    "vocabulary_500": {"name": "Wortschatz-Profi", "description": "Learn 500 vocabulary words", "xp": 200},
    "survival_10": {"name": "Überlebenskünstler", "description": "Survive 10 rounds in survival mode", "xp": 150},
}


class GameService:
    """Generates AI-powered language games with gamification mechanics."""

    async def create_game(
        self,
        game_type: GameType,
        cefr_level: CEFRLevel,
        topic: str | None = None,
    ) -> GameSession:
        """Generate a new game using LLM."""
        prompt = get_game_prompt(game_type.value, cefr_level, topic)

        response = await llm_service.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            temperature=0.8,
            max_tokens=2000,
        )

        questions = self._parse_game_response(game_type, response.content)
        game_id = f"{game_type.value}_{int(time.time())}_{random.randint(1000, 9999)}"

        time_limits = {
            GameType.TIMED_TRANSLATION: 60,
            GameType.VOCABULARY_BATTLE: 90,
            GameType.SURVIVAL_MODE: 120,
            GameType.WORD_MATCH: 180,
            GameType.SENTENCE_BUILDER: 300,
            GameType.LISTENING_QUIZ: 240,
            GameType.FILL_IN_BLANK: 240,
            GameType.PRONUNCIATION_CHALLENGE: 300,
        }

        return GameSession(
            game_id=game_id,
            game_type=game_type,
            cefr_level=cefr_level.value,
            questions=questions,
            time_limit_seconds=time_limits.get(game_type, 180),
            xp_per_correct=_XP_TABLE.get(game_type, 10),
        )

    def _parse_game_response(self, game_type: GameType, content: str) -> list[dict]:
        """Extract structured questions from LLM response."""
        try:
            # Try direct JSON parse
            data = json.loads(content)
        except json.JSONDecodeError:
            # Extract JSON block from markdown
            match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", content)
            if match:
                try:
                    data = json.loads(match.group(1))
                except json.JSONDecodeError:
                    data = {}
            else:
                match = re.search(r"\{[\s\S]+\}", content)
                data = json.loads(match.group(0)) if match else {}

        # Extract questions from response
        if game_type == GameType.WORD_MATCH:
            return data.get("pairs", [])
        elif game_type == GameType.SENTENCE_BUILDER:
            return data.get("exercises", [])
        elif game_type in (GameType.LISTENING_QUIZ, GameType.FILL_IN_BLANK):
            return data.get("exercises", data.get("questions", []))
        elif game_type == GameType.VOCABULARY_BATTLE:
            return data.get("words", [])
        else:
            return data.get("questions", data.get("exercises", data.get("pairs", [])))

    def score_answer(
        self,
        game_type: GameType,
        question: dict,
        user_answer: str | int | list,
    ) -> tuple[bool, str]:
        """Validate user answer and return (is_correct, explanation)."""
        if game_type == GameType.WORD_MATCH:
            correct = question.get("english", "").lower()
            is_correct = str(user_answer).lower().strip() == correct
            return is_correct, question.get("example", "")

        elif game_type == GameType.VOCABULARY_BATTLE:
            correct_idx = question.get("correct", 0)
            is_correct = int(user_answer) == correct_idx
            options = question.get("options", [])
            explanation = f"Correct: {options[correct_idx]}" if options else ""
            return is_correct, explanation

        elif game_type == GameType.FILL_IN_BLANK:
            correct = str(question.get("answer", "")).lower().strip()
            is_correct = str(user_answer).lower().strip() == correct
            return is_correct, question.get("hint", "")

        elif game_type == GameType.SENTENCE_BUILDER:
            correct_sentence = question.get("correct", "").lower().strip()
            user_sentence = str(user_answer).lower().strip()
            is_correct = correct_sentence == user_sentence
            return is_correct, question.get("translation", "")

        return False, ""

    def calculate_result(
        self,
        game_id: str,
        user_id: str,
        game_type: GameType,
        answers: list[dict],
        questions: list[dict],
        time_taken: float,
    ) -> GameResult:
        """Calculate final game result with XP and achievements."""
        correct = 0
        mistakes = []
        xp_per = _XP_TABLE.get(game_type, 10)

        for i, (q, a) in enumerate(zip(questions, answers)):
            is_correct, explanation = self.score_answer(game_type, q, a.get("answer"))
            if is_correct:
                correct += 1
            else:
                mistakes.append({
                    "question_index": i,
                    "expected": q.get("answer", q.get("correct", "")),
                    "given": a.get("answer"),
                    "hint": explanation,
                })

        total = len(questions)
        accuracy = (correct / total * 100) if total > 0 else 0

        # XP calculation with bonuses
        base_xp = correct * xp_per
        speed_bonus = max(0, int(10 - time_taken / 30)) * 2  # Fast answer bonus
        perfect_bonus = 50 if accuracy == 100 else 0
        total_xp = base_xp + speed_bonus + perfect_bonus

        return GameResult(
            game_id=game_id,
            user_id=user_id,
            score=int(accuracy),
            correct_answers=correct,
            total_questions=total,
            time_taken_seconds=time_taken,
            xp_earned=total_xp,
            accuracy_percent=accuracy,
            mistakes=mistakes,
        )

    async def get_daily_missions(self, cefr_level: CEFRLevel, user_id: str) -> list[dict]:
        """Generate personalized daily missions."""
        from app.agents.motivation_agent import MotivationAgent
        agent = MotivationAgent()
        challenge_text = await agent.generate_daily_challenge(cefr_level.value)

        return [
            {
                "id": f"dm_vocab_{int(time.time())}",
                "title": "Wortschatz des Tages",
                "description": "Learn 5 new vocabulary words",
                "game_type": GameType.VOCABULARY_BATTLE.value,
                "xp_reward": 50,
                "required_score": 60,
                "completed": False,
            },
            {
                "id": f"dm_grammar_{int(time.time())}",
                "title": "Grammatik-Übung",
                "description": "Complete a grammar exercise",
                "game_type": GameType.FILL_IN_BLANK.value,
                "xp_reward": 75,
                "required_score": 70,
                "completed": False,
            },
            {
                "id": f"dm_challenge_{int(time.time())}",
                "title": "AI-Tagesaufgabe",
                "description": challenge_text[:100] + "...",
                "game_type": GameType.SENTENCE_BUILDER.value,
                "xp_reward": 100,
                "required_score": 80,
                "completed": False,
            },
        ]

    def check_achievements(
        self,
        user_xp: int,
        streak_days: int,
        games_played: int,
        cefr_level: str,
        last_accuracy: float,
    ) -> list[dict]:
        """Check which achievements have been newly unlocked."""
        unlocked = []

        if games_played == 1:
            unlocked.append(ACHIEVEMENTS["first_game"])
        if streak_days >= 7:
            unlocked.append(ACHIEVEMENTS["streak_7"])
        if streak_days >= 30:
            unlocked.append(ACHIEVEMENTS["streak_30"])
        if user_xp >= 1000:
            unlocked.append(ACHIEVEMENTS["xp_1000"])
        if user_xp >= 10000:
            unlocked.append(ACHIEVEMENTS["xp_10000"])
        if last_accuracy == 100:
            unlocked.append(ACHIEVEMENTS["perfect_game"])
        if cefr_level == "B1":
            unlocked.append(ACHIEVEMENTS["b1_unlocked"])
        if cefr_level == "B2":
            unlocked.append(ACHIEVEMENTS["b2_unlocked"])

        return unlocked


game_service = GameService()
