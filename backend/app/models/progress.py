from __future__ import annotations

import uuid
from enum import Enum

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class LessonType(str, Enum):
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"
    PRONUNCIATION = "pronunciation"
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"
    CONVERSATION = "conversation"
    EXAM_PREP = "exam_prep"
    BUSINESS = "business"
    DAILY_LIFE = "daily_life"


class SessionType(str, Enum):
    TUTOR_CHAT = "tutor_chat"
    VOICE_SESSION = "voice_session"
    GAME = "game"
    LESSON = "lesson"
    EXAM = "exam"


class UserProgress(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "user_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lesson_type: Mapped[LessonType] = mapped_column(SAEnum(LessonType), nullable=False)
    cefr_level: Mapped[str] = mapped_column(String(2), nullable=False)

    # Scores 0-100
    accuracy_score: Mapped[float] = mapped_column(Float, default=0.0)
    fluency_score: Mapped[float] = mapped_column(Float, default=0.0)
    vocabulary_score: Mapped[float] = mapped_column(Float, default=0.0)
    grammar_score: Mapped[float] = mapped_column(Float, default=0.0)

    lessons_completed: Mapped[int] = mapped_column(Integer, default=0)
    exercises_completed: Mapped[int] = mapped_column(Integer, default=0)
    time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0)

    topic_mastery: Mapped[dict] = mapped_column(JSONB, default=dict)

    user: Mapped["User"] = relationship("User", back_populates="progress")  # noqa: F821


class LearningSession(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "learning_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    session_type: Mapped[SessionType] = mapped_column(SAEnum(SessionType), nullable=False)
    cefr_level: Mapped[str] = mapped_column(String(2), nullable=False)

    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    messages_count: Mapped[int] = mapped_column(Integer, default=0)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)

    llm_provider: Mapped[str | None] = mapped_column(String(50))
    llm_model: Mapped[str | None] = mapped_column(String(100))
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)

    # Mistakes captured during session
    mistakes: Mapped[list] = mapped_column(JSONB, default=list)
    feedback: Mapped[str | None] = mapped_column(Text)
    session_summary: Mapped[dict] = mapped_column(JSONB, default=dict)

    user: Mapped["User"] = relationship("User", back_populates="sessions")  # noqa: F821


class Achievement(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "achievements"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    achievement_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    badge_icon: Mapped[str | None] = mapped_column(String(100))
    xp_reward: Mapped[int] = mapped_column(Integer, default=0)
    extra_data: Mapped[dict] = mapped_column(JSONB, default=dict)

    user: Mapped["User"] = relationship("User", back_populates="achievements")  # noqa: F821
