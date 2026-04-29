from pathlib import Path
import json
import pandas as pd
from fastapi import APIRouter, HTTPException

from app.schemas.ranking import RankingResponse, CategoryRankingItem

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]
RANKING_CSV = BASE_DIR / "data" / "processed" / "category_ranking.csv"
CATEGORIES_JSON = BASE_DIR / "config" / "categories.json"


def load_categories() -> dict:
    if not CATEGORIES_JSON.exists():
        return {}

    with CATEGORIES_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/ranking", response_model=RankingResponse, tags=["ranking"])
def get_ranking() -> RankingResponse:
    if not RANKING_CSV.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Hiányzik a rangsor fájl: {RANKING_CSV}"
        )

    df = pd.read_csv(RANKING_CSV)
    categories = load_categories()

    required_columns = [
        "final_rank",
        "category_id",
        "avg_53w",
        "avg_last_8w",
        "active_weeks",
        "peak_value",
        "total_rank_score",
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Hiányzó oszlop(ok) a rangsor fájlban: {missing}"
        )

    items = [
        CategoryRankingItem(
            final_rank=int(row["final_rank"]),
            category_id=str(row["category_id"]),
            category_name=categories.get(str(row["category_id"]), str(row["category_id"])),
            avg_53w=float(row["avg_53w"]),
            avg_last_8w=float(row["avg_last_8w"]),
            active_weeks=int(row["active_weeks"]),
            peak_value=float(row["peak_value"]),
            total_rank_score=float(row["total_rank_score"]),
        )
        for _, row in df.iterrows()
    ]

    return RankingResponse(items=items)
