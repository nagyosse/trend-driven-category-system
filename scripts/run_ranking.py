from __future__ import annotations

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from app.services.ranking_service import RankingService


def main() -> None:
    source_csv = BASE_DIR / "data" / "processed" / "category_weekly_index.csv"
    output_dir = BASE_DIR / "data" / "processed"

    service = RankingService(
        source_csv=source_csv,
        output_dir=output_dir,
    )

    ranking_df, summary_path, result_path = service.run()

    print("\n=== Rangsorolás kész ===")
    print(f"Forrás: {source_csv}")
    print(f"Összesítő: {summary_path}")
    print(f"Rangsor: {result_path}")
    print(f"Sorok száma: {len(ranking_df)}")

    print("\n=== Végső rangsor ===")
    print(
        ranking_df[
            [
                "final_rank",
                "category_id",
                "avg_53w",
                "avg_last_8w",
                "active_weeks",
                "peak_value",
                "total_rank_score",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
