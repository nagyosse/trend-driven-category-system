from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd

from app.schemas.analyze import AnalyzeRequest, AnalyzeRankingItem
from app.services.config_service import ConfigService
from app.services.aggregation_service import AggregationService
from app.services.ranking_service import RankingService
from app.services.ai_explanation_service import AIExplanationService


class AnalyzePipelineService:
    """
    Teljes IPO pipeline:

    Input →
    konfiguráció →
    adatgyűjtés →
    aggregáció →
    rangsor →
    opcionális AI →
    Output
    """

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.config_dir = base_dir / "config"

        self.raw_csv = base_dir / "data" / "raw" / "trends_long.csv"
        self.processed_dir = base_dir / "data" / "processed"
        self.ranking_csv = self.processed_dir / "category_ranking.csv"

    def run_trends_fetcher(self) -> None:
        """
        Google Trends adatlekérő script futtatása.

        Csak akkor fut, ha a request.run_trends_fetch = True.
        """
        script_path = self.base_dir / "scripts" / "trends_analyzer_long.py"

        if not script_path.exists():
            raise FileNotFoundError(f"Hiányzik a Trends script: {script_path}")

        subprocess.run(
            ["python", str(script_path)],
            cwd=str(self.base_dir),
            check=True,
        )

    def add_category_names(
        self,
        df: pd.DataFrame,
        request: AnalyzeRequest,
    ) -> pd.DataFrame:
        """
        A category_id mellé hozzáadja az ügyfél által megadott kategórianevet.
        """
        mapping = {
            category.category_id: category.category_name
            for category in request.categories
        }

        df = df.copy()
        df["category_name"] = df["category_id"].map(mapping)
        df["category_name"] = df["category_name"].fillna(df["category_id"])

        return df

    def filter_requested_categories(
        self,
        df: pd.DataFrame,
        request: AnalyzeRequest,
    ) -> pd.DataFrame:
        """
        Csak azokat a kategóriákat tartja meg,
        amelyeket az aktuális /analyze kérésben a felhasználó megadott.
        """
        requested_ids = {
            category.category_id
            for category in request.categories
        }

        return df[df["category_id"].isin(requested_ids)].copy()

    def rerank_filtered_result(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        A szűrt eredmény újrasorszámozása.

        Erre azért van szükség, mert a globális rangsorban például egy kategória
        lehetett 2. helyezett, de ha az ügyfél csak két kategóriát vizsgál,
        akkor a szűrt listában a legjobb kategóriának 1. helyezést kell kapnia.
        """
        df = df.copy()

        if df.empty:
            return df

        df = df.sort_values(
            by=["final_rank", "total_rank_score", "avg_last_8w", "peak_value"],
            ascending=[True, True, False, False],
        ).reset_index(drop=True)

        df["final_rank"] = range(1, len(df) + 1)

        return df

    def build_ranking_items(
        self,
        df: pd.DataFrame,
    ) -> list[AnalyzeRankingItem]:
        """
        DataFrame átalakítása API válaszmodellé.
        """
        items: list[AnalyzeRankingItem] = []

        for _, row in df.sort_values("final_rank").iterrows():
            items.append(
                AnalyzeRankingItem(
                    final_rank=int(row["final_rank"]),
                    category_id=str(row["category_id"]),
                    category_name=str(row["category_name"]),
                    avg_53w=float(row["avg_53w"]),
                    avg_last_8w=float(row["avg_last_8w"]),
                    active_weeks=int(row["active_weeks"]),
                    peak_value=float(row["peak_value"]),
                    total_rank_score=float(row["total_rank_score"]),
                )
            )

        return items

    def run(
        self,
        request: AnalyzeRequest,
    ) -> tuple[list[AnalyzeRankingItem], str | None]:
        """
        Teljes elemzési folyamat futtatása.
        """

        # 1. Input → config mentés
        ConfigService(self.config_dir).save_input_config(request)

        # 2. Google Trends lekérés opcionálisan
        if request.run_trends_fetch:
            self.run_trends_fetcher()

        # 3. Aggregáció
        aggregation_service = AggregationService(
            source_csv=self.raw_csv,
            output_dir=self.processed_dir,
        )
        aggregation_service.run()

        # 4. Rangsorolás
        ranking_service = RankingService(
            source_csv=self.processed_dir / "category_weekly_index.csv",
            output_dir=self.processed_dir,
        )
        ranking_df, _, _ = ranking_service.run()

        # 5. Csak az aktuális kérésben szereplő kategóriák megtartása
        ranking_df = self.filter_requested_categories(ranking_df, request)

        # 6. Szűrt lista újrasorszámozása
        ranking_df = self.rerank_filtered_result(ranking_df)

        # 7. Kategórianevek hozzáadása
        ranking_df = self.add_category_names(ranking_df, request)

        # 8. Mentés
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        ranking_df.to_csv(self.ranking_csv, index=False, encoding="utf-8-sig")

        # 9. AI opcionálisan
        ai_summary = None
        if request.ai_enabled:
            ai_service = AIExplanationService(self.ranking_csv)
            ai_summary = ai_service.explain(top_n=3)

        # 10. Output
        return self.build_ranking_items(ranking_df), ai_summary
