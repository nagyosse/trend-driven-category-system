from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.ranking import router as ranking_router
from app.api.v1.ai import router as ai_router
# IO imput
from app.api.v1.analyze import router as analyze_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(ranking_router)
api_router.include_router(ai_router)
# IO imput
api_router.include_router(analyze_router)
