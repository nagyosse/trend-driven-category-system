from __future__ import annotations

from pathlib import Path
import pandas as pd

from app.engines.ranking_engine import RankingEngine


class RankingService:
    """
    A kategória-szintű heti indexből összesítőt és rangsort készít.
    """

    def __init__(self, source_csv: Path, output_dir: Path) -> None:
        self.source_csv = source_csv
        self.output_dir = output_dir
        self.engine = RankingEngine()

    def load_weekly_index(self) -> pd.DataFrame:
        if not self.source_csv.exists():
            raise FileNotFoundError(f"Hiányzik a forrásfájl: {self.source_csv}")

        return pd.read_csv(self.source_csv)

    def build_ranking(self) -> pd.DataFrame:
        weekly_df = self.load_weekly_index()
        ranking_df = self.engine.build_summary(weekly_df)
        return ranking_df

    def save_ranking(self, ranking_df: pd.DataFrame) -> tuple[Path, Path]:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        summary_path = self.output_dir / "category_summary.csv"
        result_path = self.output_dir / "category_ranking.csv"

        ranking_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
        ranking_df.to_csv(result_path, index=False, encoding="utf-8-sig")

        return summary_path, result_path

    def run(self) -> tuple[pd.DataFrame, Path, Path]:
        ranking_df = self.build_ranking()
        summary_path, result_path = self.save_ranking(ranking_df)
        return ranking_df, summary_path, result_path
