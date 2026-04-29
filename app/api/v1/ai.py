from pathlib import Path
from fastapi import APIRouter, HTTPException

from app.core.settings import settings
from app.schemas.ai import AIExplainRankingRequest, AIExplainRankingResponse
from app.services.ai_explanation_service import AIExplanationService

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]
RANKING_CSV = BASE_DIR / "data" / "processed" / "category_ranking.csv"


@router.post("/ai/explain-ranking", response_model=AIExplainRankingResponse, tags=["ai"])
def explain_ranking(request: AIExplainRankingRequest) -> AIExplainRankingResponse:
    try:
        service = AIExplanationService(ranking_csv=RANKING_CSV)
        summary = service.explain(top_n=request.top_n)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AIExplainRankingResponse(
        ai_enabled=settings.ai_enabled,
        summary=summary,
    )
