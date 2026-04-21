"""Unit tests for the game service."""

from __future__ import annotations

import pytest

from app.models.user import CEFRLevel
from app.services.game_service import GameService, GameType


class TestGameService:
    def setup_method(self):
        self.service = GameService()

    def test_score_word_match_correct(self):
        question = {"german": "Hund", "english": "dog", "example": "Der Hund läuft."}
        is_correct, _ = self.service.score_answer(GameType.WORD_MATCH, question, "dog")
        assert is_correct is True

    def test_score_word_match_case_insensitive(self):
        question = {"german": "Hund", "english": "dog"}
        is_correct, _ = self.service.score_answer(GameType.WORD_MATCH, question, "DOG")
        assert is_correct is True

    def test_score_word_match_wrong(self):
        question = {"german": "Hund", "english": "dog"}
        is_correct, _ = self.service.score_answer(GameType.WORD_MATCH, question, "cat")
        assert is_correct is False

    def test_score_vocab_battle_correct(self):
        question = {"german": "Haus", "options": ["table", "house", "dog", "car"], "correct": 1}
        is_correct, _ = self.service.score_answer(GameType.VOCABULARY_BATTLE, question, 1)
        assert is_correct is True

    def test_score_vocab_battle_wrong(self):
        question = {"german": "Haus", "options": ["table", "house", "dog", "car"], "correct": 1}
        is_correct, _ = self.service.score_answer(GameType.VOCABULARY_BATTLE, question, 0)
        assert is_correct is False

    def test_score_fill_blank_correct(self):
        question = {"sentence": "Ich ___ müde.", "answer": "bin", "hint": "sein verb"}
        is_correct, _ = self.service.score_answer(GameType.FILL_IN_BLANK, question, "bin")
        assert is_correct is True

    def test_calculate_result_all_correct(self):
        questions = [{"german": "Hund", "english": "dog"}] * 5
        answers = [{"answer": "dog"}] * 5
        result = self.service.calculate_result(
            game_id="test_game",
            user_id="test_user",
            game_type=GameType.WORD_MATCH,
            answers=answers,
            questions=questions,
            time_taken=30.0,
        )
        assert result.correct_answers == 5
        assert result.accuracy_percent == 100.0
        assert result.xp_earned > 0

    def test_calculate_result_perfect_bonus(self):
        questions = [{"german": "Hund", "english": "dog"}] * 5
        answers = [{"answer": "dog"}] * 5
        result = self.service.calculate_result(
            game_id="test_game",
            user_id="test_user",
            game_type=GameType.WORD_MATCH,
            answers=answers,
            questions=questions,
            time_taken=30.0,
        )
        # Perfect game should include 50 XP bonus
        base_xp = 5 * 5  # 5 questions * 5 XP each
        assert result.xp_earned >= base_xp + 50

    def test_calculate_result_records_mistakes(self):
        questions = [
            {"german": "Hund", "english": "dog"},
            {"german": "Katze", "english": "cat"},
        ]
        answers = [
            {"answer": "dog"},
            {"answer": "bird"},  # Wrong
        ]
        result = self.service.calculate_result(
            game_id="test",
            user_id="user",
            game_type=GameType.WORD_MATCH,
            answers=answers,
            questions=questions,
            time_taken=20.0,
        )
        assert result.correct_answers == 1
        assert len(result.mistakes) == 1
        assert result.mistakes[0]["given"] == "bird"

    def test_check_achievements_first_game(self):
        achievements = self.service.check_achievements(
            user_xp=10, streak_days=1, games_played=1,
            cefr_level="A1", last_accuracy=80.0
        )
        achievement_ids = [a["name"] for a in achievements]
        assert "Anfänger" in achievement_ids

    def test_check_achievements_perfect_game(self):
        achievements = self.service.check_achievements(
            user_xp=500, streak_days=5, games_played=10,
            cefr_level="A2", last_accuracy=100.0
        )
        achievement_ids = [a["name"] for a in achievements]
        assert "Perfektionist" in achievement_ids

    def test_parse_game_response_handles_malformed_json(self):
        result = self.service._parse_game_response(
            GameType.WORD_MATCH,
            "Here are the word pairs: some text without JSON"
        )
        assert result == []
