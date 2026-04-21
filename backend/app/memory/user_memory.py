"""Stores and retrieves per-user learning history and grammar mistakes via Redis."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import structlog
from redis.asyncio import Redis

from app.config import settings

logger = structlog.get_logger(__name__)

_MEMORY_TTL = 60 * 60 * 24 * 90  # 90 days
_SESSION_TTL = 60 * 60 * 24  # 24 hours


class UserMemoryService:

    def __init__(self) -> None:
        self._redis: Redis | None = None

    async def _get_redis(self) -> Redis:
        if self._redis is None:
            self._redis = Redis.from_url(settings.redis_url, decode_responses=True)
        return self._redis

    async def get_session_history(
        self, user_id: str, session_id: str, max_messages: int = 20
    ) -> list[dict]:
        """Retrieve recent conversation history from Redis."""
        r = await self._get_redis()
        key = f"session:{user_id}:{session_id}:messages"
        raw = await r.lrange(key, -max_messages, -1)
        return [json.loads(msg) for msg in raw]

    async def append_message(
        self, user_id: str, session_id: str, role: str, content: str
    ) -> None:
        """Append a message to session history."""
        r = await self._get_redis()
        key = f"session:{user_id}:{session_id}:messages"
        message = json.dumps({
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        await r.rpush(key, message)
        await r.expire(key, _SESSION_TTL)

    async def get_user_context(self, user_id: str) -> dict:
        """Get cached user learning context."""
        r = await self._get_redis()
        key = f"user:{user_id}:context"
        raw = await r.get(key)
        if raw:
            return json.loads(raw)
        return {}

    async def update_user_context(self, user_id: str, context: dict) -> None:
        """Update user learning context cache."""
        r = await self._get_redis()
        key = f"user:{user_id}:context"
        await r.setex(key, _MEMORY_TTL, json.dumps(context))

    async def record_mistakes(self, user_id: str, mistakes: list[dict]) -> None:
        """Track grammar and vocabulary mistakes for spaced repetition."""
        if not mistakes:
            return

        r = await self._get_redis()
        key = f"user:{user_id}:mistakes"

        existing_raw = await r.get(key)
        existing: dict = json.loads(existing_raw) if existing_raw else {}

        for mistake in mistakes:
            rule = mistake.get("rule", "unknown")
            if rule not in existing:
                existing[rule] = {"count": 0, "examples": [], "last_seen": ""}
            existing[rule]["count"] += 1
            existing[rule]["examples"].append(mistake.get("incorrect", ""))
            existing[rule]["last_seen"] = datetime.now(timezone.utc).isoformat()
            # Keep only last 5 examples
            existing[rule]["examples"] = existing[rule]["examples"][-5:]

        await r.setex(key, _MEMORY_TTL, json.dumps(existing))
        logger.debug("mistakes_recorded", user_id=user_id, count=len(mistakes))

    async def get_weak_areas(self, user_id: str, top_n: int = 5) -> list[str]:
        """Return the user's most common mistake categories."""
        r = await self._get_redis()
        key = f"user:{user_id}:mistakes"
        raw = await r.get(key)
        if not raw:
            return []

        mistakes: dict = json.loads(raw)
        sorted_rules = sorted(mistakes.items(), key=lambda x: x[1]["count"], reverse=True)
        return [rule for rule, _ in sorted_rules[:top_n]]

    async def record_vocabulary(self, user_id: str, words: list[str], known: bool) -> None:
        """Track vocabulary the user knows or struggles with."""
        r = await self._get_redis()
        prefix = "known" if known else "unknown"
        key = f"user:{user_id}:vocab:{prefix}"
        await r.sadd(key, *words)
        await r.expire(key, _MEMORY_TTL)

    async def get_xp(self, user_id: str) -> int:
        """Get user's current XP from cache."""
        r = await self._get_redis()
        val = await r.get(f"user:{user_id}:xp")
        return int(val) if val else 0

    async def add_xp(self, user_id: str, amount: int) -> int:
        """Add XP and return new total."""
        r = await self._get_redis()
        key = f"user:{user_id}:xp"
        new_total = await r.incrby(key, amount)
        await r.expire(key, _MEMORY_TTL)
        return int(new_total)

    async def get_streak(self, user_id: str) -> int:
        """Get current learning streak in days."""
        r = await self._get_redis()
        val = await r.get(f"user:{user_id}:streak")
        return int(val) if val else 0

    async def update_streak(self, user_id: str) -> int:
        """Update streak and return new count."""
        r = await self._get_redis()
        today = datetime.now(timezone.utc).date().isoformat()
        last_key = f"user:{user_id}:last_active"
        streak_key = f"user:{user_id}:streak"

        last_active = await r.get(last_key)

        if last_active == today:
            return int(await r.get(streak_key) or 0)

        if last_active:
            from datetime import date, timedelta

            last_date = date.fromisoformat(last_active)
            today_date = date.fromisoformat(today)
            if (today_date - last_date).days == 1:
                # Consecutive day — extend streak
                new_streak = await r.incr(streak_key)
            else:
                # Streak broken
                await r.set(streak_key, 1)
                new_streak = 1
        else:
            await r.set(streak_key, 1)
            new_streak = 1

        await r.set(last_key, today)
        await r.expire(streak_key, _MEMORY_TTL)
        return int(new_streak)

    async def save_learning_summary(self, user_id: str, session_id: str, summary: dict) -> None:
        """Persist session summary for analytics."""
        r = await self._get_redis()
        key = f"user:{user_id}:sessions"
        await r.lpush(key, json.dumps({"session_id": session_id, **summary}))
        await r.ltrim(key, 0, 99)  # Keep last 100 sessions
        await r.expire(key, _MEMORY_TTL)

    async def get_recent_summaries(self, user_id: str, n: int = 10) -> list[dict]:
        r = await self._get_redis()
        key = f"user:{user_id}:sessions"
        raw = await r.lrange(key, 0, n - 1)
        return [json.loads(s) for s in raw]
