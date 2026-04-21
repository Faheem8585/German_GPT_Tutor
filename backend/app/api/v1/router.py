"""Central API v1 router."""

from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.games import router as games_router
from app.api.v1.tutor import router as tutor_router
from app.api.v1.voice import router as voice_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(tutor_router)
api_router.include_router(voice_router)
api_router.include_router(games_router)
api_router.include_router(analytics_router)
