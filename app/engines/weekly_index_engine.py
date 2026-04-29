from __future__ import annotations

from dataclasses import dataclass
import pandas as pd


REQUIRED_COLUMNS = {"date", "keyword", "category_id", "value"}


@dataclass
class WeeklyIndexEngine:
    """
    A kategória-szintű heti indexek előállításáért felelős motor.

    Bemenet:
        trends_long.csv jellegű long/tidy adatok

    Kimenet:
        kategória-szintű heti indexek DataFrame formában
    """

    def validate_input(self, df: pd.DataFrame) -> None:
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"Hiányzó oszlop(ok): {sorted(missing)}")

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Alap normalizálás:
        - szükséges oszlopok ellenőrzése
        - dátum konvertálása
        - value numerikussá alakítása
        - hiányzó sorok kiszűrése
        """
        self.validate_input(df)

        out = df.copy()

        out["date"] = pd.to_datetime(out["date"], errors="coerce")
        out["value"] = pd.to_numeric(out["value"], errors="coerce")

        out = out.dropna(subset=["date", "keyword", "category_id", "value"])
        out["keyword"] = out["keyword"].astype(str).str.strip()
        out["category_id"] = out["category_id"].astype(str).str.strip()

        out = out.sort_values(["category_id", "keyword", "date"]).reset_index(drop=True)
        return out

    def compute_category_weekly_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Kategória-szintű heti index számítás.

        Logika:
        - azonos héten belül, azonos kategóriához tartozó kulcsszavak értékeinek átlaga
        - ez adja a kategória heti indexét
        """
        normalized = self.normalize(df)

        weekly = (
            normalized.groupby(["date", "category_id"], as_index=False)
            .agg(
                weekly_index=("value", "mean"),
                keyword_count=("keyword", "nunique"),
                row_count=("value", "size"),
            )
            .sort_values(["date", "category_id"])
            .reset_index(drop=True)
        )

        weekly["weekly_index"] = weekly["weekly_index"].round(4)
        return weekly
