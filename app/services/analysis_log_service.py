from __future__ import annotations

from datetime import datetime
from time import perf_counter
from sqlalchemy.orm import Session

from app.schemas.analyze import AnalyzeRequest, AnalyzeRankingItem
from app.db.models.analysis_log import (
    AnalysisRun,
    AnalysisInputCategory,
    AnalysisRankingResult,
    AnalysisAIOutput,
    AnalysisSwarmRecommendation,
)


class AnalysisLogService:
    """
    Az /analyze futások naplózása adatbázisba.

    Mentett adatok:
    - futás metaadatai
    - input kategóriák és kulcsszavak
    - ranking eredmények
    - AI összefoglaló
    - Docker Swarm ajánlás
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.started_perf = perf_counter()

    def start_run(self, request: AnalyzeRequest) -> AnalysisRun:
        run = AnalysisRun(
            project_name=request.project_name,
            ai_enabled=request.ai_enabled,
            run_trends_fetch=request.run_trends_fetch,
            status="started",
            created_at=datetime.utcnow(),
        )

        self.db.add(run)
        self.db.flush()

        for category in request.categories:
            input_category = AnalysisInputCategory(
                analysis_run_id=run.id,
                category_id=category.category_id,
                category_name=category.category_name,
                keywords_json=category.keywords,
            )
            self.db.add(input_category)

        self.db.commit()
        self.db.refresh(run)

        return run

    def save_success(
        self,
        run: AnalysisRun,
        ranking: list[AnalyzeRankingItem],
        ai_summary: str | None,
    ) -> None:
        for item in ranking:
            result = AnalysisRankingResult(
                analysis_run_id=run.id,
                final_rank=item.final_rank,
                category_id=item.category_id,
                category_name=item.category_name,
                avg_53w=item.avg_53w,
                avg_last_8w=item.avg_last_8w,
                active_weeks=item.active_weeks,
                peak_value=item.peak_value,
                total_rank_score=item.total_rank_score,
            )
            self.db.add(result)

        if ai_summary:
            ai_output = AnalysisAIOutput(
                analysis_run_id=run.id,
                ai_summary=ai_summary,
            )
            self.db.add(ai_output)

        if ranking:
            top = ranking[0]

            swarm_config = {
                "action": "scale_up",
                "category_id": top.category_id,
                "category_name": top.category_name,
                "target_service": f"webshop_{top.category_id}",
                "suggested_replicas": 3,
                "priority": "high",
                "metrics": {
                    "avg_53w": top.avg_53w,
                    "avg_last_8w": top.avg_last_8w,
                    "active_weeks": top.active_weeks,
                    "peak_value": top.peak_value,
                    "total_rank_score": top.total_rank_score,
                },
                "reason": (
                    f"A(z) {top.category_name} kategória az aktuális trendrangsor "
                    "első helyén szerepel, ezért ennek a Docker Swarm szolgáltatásnak "
                    "az erősítése javasolt."
                ),
            }

            swarm = AnalysisSwarmRecommendation(
                analysis_run_id=run.id,
                action="scale_up",
                category_id=top.category_id,
                category_name=top.category_name,
                target_service=f"webshop_{top.category_id}",
                suggested_replicas=3,
                priority="high",
                reason=swarm_config["reason"],
                config_json=swarm_config,
            )
            self.db.add(swarm)

        run.status = "success"
        run.finished_at = datetime.utcnow()
        run.duration_ms = int((perf_counter() - self.started_perf) * 1000)

        self.db.commit()

    def save_error(
        self,
        run: AnalysisRun,
        error_message: str,
    ) -> None:
        run.status = "error"
        run.error_message = error_message
        run.finished_at = datetime.utcnow()
        run.duration_ms = int((perf_counter() - self.started_perf) * 1000)

        self.db.commit()
