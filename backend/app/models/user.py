from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.progress import UserProgress, LearningSession
    from app.models.achievement import Achievement


class CEFRLevel(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class LearningMode(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    MIXED = "mixed"


class InterfaceLanguage(str, Enum):
    EN = "en"
    DE = "de"
    HI = "hi"


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(512))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Learning profile
    cefr_level: Mapped[CEFRLevel] = mapped_column(
        SAEnum(CEFRLevel), default=CEFRLevel.A1, nullable=False
    )
    native_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    interface_language: Mapped[InterfaceLanguage] = mapped_column(
        SAEnum(InterfaceLanguage), default=InterfaceLanguage.EN, nullable=False
    )
    preferred_mode: Mapped[LearningMode] = mapped_column(
        SAEnum(LearningMode), default=LearningMode.MIXED, nullable=False
    )

    # Gamification
    xp_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_activity_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    total_lessons: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Learning memory (JSON)
    weak_areas: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    learning_style: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    vocabulary_known: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    grammar_mistakes: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    progress: Mapped[list[UserProgress]] = relationship(
        "UserProgress", back_populates="user", cascade="all, delete-orphan"
    )
    sessions: Mapped[list[LearningSession]] = relationship(
        "LearningSession", back_populates="user", cascade="all, delete-orphan"
    )
    achievements: Mapped[list[Achievement]] = relationship(
        "Achievement", back_populates="user", cascade="all, delete-orphan"
    )


class UserMemory(UUIDMixin, TimestampMixin, Base):
    """Long-term episodic memory entries for the AI tutor."""

    __tablename__ = "user_memories"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_id: Mapped[str | None] = mapped_column(String(100))
    extra_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    importance_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
