from pydantic import BaseModel


class AIExplainRankingRequest(BaseModel):
    top_n: int = 3


class AIExplainRankingResponse(BaseModel):
    ai_enabled: bool
    summary: str
