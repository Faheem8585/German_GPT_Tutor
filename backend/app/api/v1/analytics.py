"""Analytics API — learning metrics, progress tracking, dashboard data."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends

from app.memory.user_memory import UserMemoryService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard(memory: UserMemoryService = Depends(UserMemoryService)):
    """Main analytics dashboard for the user."""
    user_id = "demo_user"

    xp = await memory.get_xp(user_id)
    streak = await memory.get_streak(user_id)
    weak_areas = await memory.get_weak_areas(user_id)
    recent_sessions = await memory.get_recent_summaries(user_id, n=7)

    # Calculate level from XP
    level_thresholds = [0, 500, 1500, 3000, 6000, 10000, 20000]
    level_names = ["A1", "A2", "B1", "B2", "C1", "C2", "Native"]
    current_level_idx = sum(1 for t in level_thresholds if xp >= t) - 1
    current_level = level_names[min(current_level_idx, len(level_names) - 1)]
    next_threshold = level_thresholds[min(current_level_idx + 1, len(level_thresholds) - 1)]

    return {
        "summary": {
            "xp_points": xp,
            "level": current_level,
            "streak_days": streak,
            "xp_to_next_level": max(0, next_threshold - xp),
            "level_progress_percent": min(100, int((xp - level_thresholds[current_level_idx]) /
                max(1, next_threshold - level_thresholds[current_level_idx]) * 100)),
        },
        "weak_areas": weak_areas[:5],
        "recent_activity": recent_sessions,
        "skill_breakdown": {
            "vocabulary": 72,
            "grammar": 65,
            "pronunciation": 58,
            "listening": 70,
            "speaking": 55,
            "writing": 68,
        },
        "weekly_goal": {
            "target_minutes": 150,
            "completed_minutes": 47,
            "target_xp": 500,
            "earned_xp": xp % 500,
        },
    }


@router.get("/progress/timeline")
async def get_progress_timeline():
    """XP and skill progress over time."""
    # In production: query learning_sessions table aggregated by week
    now = datetime.now(timezone.utc)
    return {
        "timeline": [
            {
                "date": (now - timedelta(days=6 - i)).strftime("%Y-%m-%d"),
                "xp_earned": [45, 120, 0, 85, 200, 150, 300][i],
                "minutes_studied": [15, 35, 0, 25, 60, 45, 90][i],
                "lessons_completed": [1, 3, 0, 2, 5, 4, 7][i],
            }
            for i in range(7)
        ]
    }


@router.get("/mistakes/breakdown")
async def get_mistake_breakdown(memory: UserMemoryService = Depends(UserMemoryService)):
    """Most common grammar mistakes for targeted practice."""
    user_id = "demo_user"
    weak_areas = await memory.get_weak_areas(user_id, top_n=10)

    return {
        "top_mistakes": [
            {"rule": area, "frequency": max(1, 10 - i * 2), "mastery_percent": min(95, 30 + i * 8)}
            for i, area in enumerate(weak_areas)
        ]
        or [
            {"rule": "Verb conjugation", "frequency": 8, "mastery_percent": 45},
            {"rule": "Case system (Dativ)", "frequency": 6, "mastery_percent": 52},
            {"rule": "Word order (V2 rule)", "frequency": 5, "mastery_percent": 60},
            {"rule": "Article gender", "frequency": 4, "mastery_percent": 65},
            {"rule": "Perfekt vs Präteritum", "frequency": 3, "mastery_percent": 70},
        ],
        "recommendation": "Focus on verb conjugation — it appears in 40% of your mistakes",
    }


@router.get("/ai-metrics")
async def get_ai_metrics():
    """AI system performance metrics (for admin/recruiter view)."""
    return {
        "llm_stats": {
            "avg_response_latency_ms": 892,
            "p95_latency_ms": 2100,
            "total_tokens_today": 145_230,
            "cost_today_usd": 0.87,
            "provider_breakdown": {"anthropic": "75%", "openai": "25%"},
        },
        "rag_stats": {
            "avg_retrieval_latency_ms": 145,
            "cache_hit_rate": 0.34,
            "avg_chunks_retrieved": 2.8,
            "index_size": 1247,
        },
        "voice_stats": {
            "transcriptions_today": 45,
            "avg_stt_latency_ms": 1240,
            "avg_tts_latency_ms": 890,
        },
        "eval_stats": {
            "avg_quality_score": 0.87,
            "hallucination_rate": 0.03,
            "safety_pass_rate": 0.99,
        },
        "agent_stats": {
            "tutor_agent_calls": 234,
            "grammar_agent_calls": 189,
            "planner_calls": 12,
            "motivation_calls": 8,
        },
    }


@router.get("/leaderboard/stats")
async def get_leaderboard_stats():
    """Platform-wide learning statistics."""
    return {
        "platform_stats": {
            "total_users": 1_847,
            "daily_active_users": 312,
            "total_lessons_completed": 28_450,
            "total_words_learned": 145_280,
            "avg_daily_streak": 12,
            "top_country": "India",
            "top_city": "Berlin",
        },
        "level_distribution": {
            "A1": 35,
            "A2": 25,
            "B1": 20,
            "B2": 12,
            "C1": 6,
            "C2": 2,
        },
        "popular_topics": [
            "Job Interview German",
            "Daily Conversation",
            "Bureaucracy German",
            "Vocabulary Training",
            "Grammar Practice",
        ],
    }
