from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from typing import List


class CategoryInput(BaseModel):
    category_id: str = Field(..., min_length=1, max_length=100)
    category_name: str = Field(..., min_length=1, max_length=200)
    keywords: List[str] = Field(..., min_length=1, max_length=4)

    @field_validator("category_id", "category_name")
    @classmethod
    def not_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("A mező nem lehet üres.")
        return value

    @field_validator("keywords")
    @classmethod
    def validate_keywords(cls, value: List[str]) -> List[str]:
        cleaned = [item.strip() for item in value if item and item.strip()]
        if not cleaned:
            raise ValueError("Legalább egy kulcsszót meg kell adni.")
        if len(cleaned) > 4:
            raise ValueError("Maximum 4 kulcsszó adható meg kategóriánként.")
        return cleaned


class AnalyzeRequest(BaseModel):
    project_name: str | None = Field(default=None, max_length=200)
    categories: List[CategoryInput] = Field(..., min_length=1, max_length=8)
    ai_enabled: bool = False

    # fejlesztéshez false lehet, hogy a meglévő trends_long.csv-ből dolgozzon
    run_trends_fetch: bool = False


class AnalyzeRankingItem(BaseModel):
    final_rank: int
    category_id: str
    category_name: str
    avg_53w: float
    avg_last_8w: float
    active_weeks: int
    peak_value: float
    total_rank_score: float


class AnalyzeResponse(BaseModel):
    status: str
    message: str
    project_name: str | None
    category_count: int
    ai_enabled: bool
    ranking: List[AnalyzeRankingItem]
    ai_summary: str | None = None
