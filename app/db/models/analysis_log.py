from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    project_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    run_trends_fetch: Mapped[bool] = mapped_column(Boolean, default=False)

    status: Mapped[str] = mapped_column(String(50), default="started")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    input_categories = relationship(
        "AnalysisInputCategory",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )

    ranking_results = relationship(
        "AnalysisRankingResult",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )

    ai_outputs = relationship(
        "AnalysisAIOutput",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )

    swarm_recommendations = relationship(
        "AnalysisSwarmRecommendation",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )


class AnalysisInputCategory(Base):
    __tablename__ = "analysis_input_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    analysis_run_id: Mapped[int] = mapped_column(
        ForeignKey("analysis_runs.id"),
        nullable=False,
    )

    category_id: Mapped[str] = mapped_column(String(100), nullable=False)
    category_name: Mapped[str] = mapped_column(String(200), nullable=False)
    keywords_json: Mapped[list[str]] = mapped_column(JSON, nullable=False)

    analysis_run = relationship(
        "AnalysisRun",
        back_populates="input_categories",
    )


class AnalysisRankingResult(Base):
    __tablename__ = "analysis_ranking_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    analysis_run_id: Mapped[int] = mapped_column(
        ForeignKey("analysis_runs.id"),
        nullable=False,
    )

    final_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[str] = mapped_column(String(100), nullable=False)
    category_name: Mapped[str] = mapped_column(String(200), nullable=False)

    avg_53w: Mapped[float] = mapped_column(Float, nullable=False)
    avg_last_8w: Mapped[float] = mapped_column(Float, nullable=False)
    active_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    peak_value: Mapped[float] = mapped_column(Float, nullable=False)
    total_rank_score: Mapped[float] = mapped_column(Float, nullable=False)

    analysis_run = relationship(
        "AnalysisRun",
        back_populates="ranking_results",
    )


class AnalysisAIOutput(Base):
    __tablename__ = "analysis_ai_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    analysis_run_id: Mapped[int] = mapped_column(
        ForeignKey("analysis_runs.id"),
        nullable=False,
    )

    ai_summary: Mapped[str] = mapped_column(Text, nullable=False)

    analysis_run = relationship(
        "AnalysisRun",
        back_populates="ai_outputs",
    )


class AnalysisSwarmRecommendation(Base):
    __tablename__ = "analysis_swarm_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    analysis_run_id: Mapped[int] = mapped_column(
        ForeignKey("analysis_runs.id"),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(String(50), nullable=False)
    category_id: Mapped[str] = mapped_column(String(100), nullable=False)
    category_name: Mapped[str] = mapped_column(String(200), nullable=False)
    target_service: Mapped[str] = mapped_column(String(200), nullable=False)
    suggested_replicas: Mapped[int] = mapped_column(Integer, default=3)
    priority: Mapped[str] = mapped_column(String(50), default="high")
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    config_json: Mapped[dict] = mapped_column(JSON, nullable=False)

    analysis_run = relationship(
        "AnalysisRun",
        back_populates="swarm_recommendations",
    )
