from __future__ import annotations

from dataclasses import dataclass
import pandas as pd


REQUIRED_COLUMNS = {"date", "category_id", "weekly_index"}


@dataclass
class RankingEngine:
    """
    Kategória-szintű összesítő és végső rangsor előállítása.
    """

    def validate_input(self, df: pd.DataFrame) -> None:
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"Hiányzó oszlop(ok): {sorted(missing)}")

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        self.validate_input(df)

        out = df.copy()
        out["date"] = pd.to_datetime(out["date"], errors="coerce")
        out["weekly_index"] = pd.to_numeric(out["weekly_index"], errors="coerce")
        out = out.dropna(subset=["date", "category_id", "weekly_index"])
        out["category_id"] = out["category_id"].astype(str).str.strip()
        out = out.sort_values(["category_id", "date"]).reset_index(drop=True)
        return out

    def build_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        normalized = self.normalize(df)

        rows = []

        for category_id, group in normalized.groupby("category_id"):
            group = group.sort_values("date").reset_index(drop=True)

            avg_53w = group["weekly_index"].mean()
            avg_last_8w = group["weekly_index"].tail(8).mean()
            active_weeks = int((group["weekly_index"] > 0).sum())
            peak_value = group["weekly_index"].max()

            rows.append(
                {
                    "category_id": category_id,
                    "avg_53w": round(avg_53w, 4),
                    "avg_last_8w": round(avg_last_8w, 4),
                    "active_weeks": active_weeks,
                    "peak_value": round(peak_value, 4),
                }
            )

        summary_df = pd.DataFrame(rows)

        # Részrangsorok: minél nagyobb az érték, annál jobb
        summary_df["rank_avg_53w"] = summary_df["avg_53w"].rank(method="min", ascending=False)
        summary_df["rank_avg_last_8w"] = summary_df["avg_last_8w"].rank(method="min", ascending=False)
        summary_df["rank_active_weeks"] = summary_df["active_weeks"].rank(method="min", ascending=False)
        summary_df["rank_peak_value"] = summary_df["peak_value"].rank(method="min", ascending=False)

        # Összesített rangpont (minél kisebb, annál jobb)
        summary_df["total_rank_score"] = (
            summary_df["rank_avg_53w"]
            + summary_df["rank_avg_last_8w"]
            + summary_df["rank_active_weeks"]
            + summary_df["rank_peak_value"]
        )

        # Tie-break:
        # 1. total_rank_score (kisebb jobb)
        # 2. avg_last_8w (nagyobb jobb)
        # 3. peak_value (nagyobb jobb)
        summary_df = summary_df.sort_values(
            by=["total_rank_score", "avg_last_8w", "peak_value"],
            ascending=[True, False, False],
        ).reset_index(drop=True)

        summary_df["final_rank"] = range(1, len(summary_df) + 1)

        return summary_df
