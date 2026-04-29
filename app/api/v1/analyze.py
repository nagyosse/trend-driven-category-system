from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.services.analyze_pipeline_service import AnalyzePipelineService
from app.services.analysis_log_service import AnalysisLogService

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]


@router.post("/analyze", response_model=AnalyzeResponse, tags=["analyze"])
def analyze(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
) -> AnalyzeResponse:
    log_service = AnalysisLogService(db=db)
    run = log_service.start_run(request)

    try:
        service = AnalyzePipelineService(base_dir=BASE_DIR)
        ranking, ai_summary = service.run(request)

        log_service.save_success(
            run=run,
            ranking=ranking,
            ai_summary=ai_summary,
        )

        return AnalyzeResponse(
            status="ok",
            message="Az elemzés sikeresen lefutott.",
            project_name=request.project_name,
            category_count=len(request.categories),
            ai_enabled=request.ai_enabled,
            ranking=ranking,
            ai_summary=ai_summary,
        )

    except Exception as exc:
        log_service.save_error(
            run=run,
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc
