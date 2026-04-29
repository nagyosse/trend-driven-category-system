from __future__ import annotations

from pathlib import Path
import pandas as pd

from app.engines.weekly_index_engine import WeeklyIndexEngine


class AggregationService:
    """
    A nyers trends_long.csv beolvasása és a kategória-szintű heti index előállítása.
    """

    def __init__(self, source_csv: Path, output_dir: Path) -> None:
        self.source_csv = source_csv
        self.output_dir = output_dir
        self.engine = WeeklyIndexEngine()

    def load_raw_data(self) -> pd.DataFrame:
        if not self.source_csv.exists():
            raise FileNotFoundError(f"Hiányzik a forrásfájl: {self.source_csv}")

        return pd.read_csv(self.source_csv)

    def build_weekly_index(self) -> pd.DataFrame:
        raw_df = self.load_raw_data()
        weekly_df = self.engine.compute_category_weekly_index(raw_df)
        return weekly_df

    def save_weekly_index(self, weekly_df: pd.DataFrame) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.output_dir / "category_weekly_index.csv"
        weekly_df.to_csv(out_path, index=False, encoding="utf-8-sig")
        return out_path

    def run(self) -> tuple[pd.DataFrame, Path]:
        weekly_df = self.build_weekly_index()
        out_path = self.save_weekly_index(weekly_df)
        return weekly_df, out_path
