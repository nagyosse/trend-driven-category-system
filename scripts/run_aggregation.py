from __future__ import annotations

from pathlib import Path
import sys

# hogy a script közvetlen futtatásnál is lássa az app csomagot
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from app.services.aggregation_service import AggregationService


def main() -> None:
    source_csv = BASE_DIR / "data" / "raw" / "trends_long.csv"
    output_dir = BASE_DIR / "data" / "processed"

    service = AggregationService(
        source_csv=source_csv,
        output_dir=output_dir,
    )

    weekly_df, out_path = service.run()

    print("\n=== Aggregáció kész ===")
    print(f"Forrás: {source_csv}")
    print(f"Kimenet: {out_path}")
    print(f"Sorok száma: {len(weekly_df)}")

    print("\n=== Első 20 sor ===")
    print(weekly_df.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
