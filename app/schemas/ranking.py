from pydantic import BaseModel
from typing import List


class CategoryRankingItem(BaseModel):
    final_rank: int
    category_id: str
    category_name: str
    avg_53w: float
    avg_last_8w: float
    active_weeks: int
    peak_value: float
    total_rank_score: float


class RankingResponse(BaseModel):
    items: List[CategoryRankingItem]
