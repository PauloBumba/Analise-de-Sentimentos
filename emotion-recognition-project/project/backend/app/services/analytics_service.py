"""Serviço de persistência e cálculo de estatísticas/métricas de desempenho."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.emotion_analysis import EmotionAnalysis
from app.models.schemas import (
    EmotionAnalysisCreate,
    EmotionDistributionItem,
    HistoryResponse,
    PerformanceMetrics,
    StatisticsResponse,
)


class AnalyticsService:
    """Responsável por persistir análises e calcular métricas agregadas."""

    def save_analysis(self, db: Session, data: EmotionAnalysisCreate) -> EmotionAnalysis:
        """Persiste o resultado de uma análise de emoção no banco de dados."""
        record = EmotionAnalysis(
            emotion=data.emotion,
            confidence=data.confidence,
            processing_time_ms=data.processing_time_ms,
            faces_detected=data.faces_detected,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_statistics(
        self,
        db: Session,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> StatisticsResponse:
        """Calcula estatísticas agregadas e métricas de desempenho, com filtro opcional de período."""
        query = select(EmotionAnalysis)
        if start is not None:
            query = query.where(EmotionAnalysis.timestamp >= start)
        if end is not None:
            query = query.where(EmotionAnalysis.timestamp <= end)

        records = db.execute(query).scalars().all()
        total = len(records)

        if total == 0:
            return StatisticsResponse(
                total_analyses=0,
                predominant_emotion=None,
                emotion_distribution=[],
                performance=PerformanceMetrics(
                    total_analyses=0,
                    avg_processing_time_ms=0.0,
                    approx_fps=0.0,
                    min_processing_time_ms=0.0,
                    max_processing_time_ms=0.0,
                ),
            )

        counts: dict[str, int] = {}
        for r in records:
            counts[r.emotion] = counts.get(r.emotion, 0) + 1

        distribution = [
            EmotionDistributionItem(
                emotion=emotion, count=count, percentage=round(100 * count / total, 2)
            )
            for emotion, count in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
        ]
        predominant = distribution[0].emotion if distribution else None

        times = [r.processing_time_ms for r in records]
        avg_time = sum(times) / total
        approx_fps = round(1000 / avg_time, 2) if avg_time > 0 else 0.0

        performance = PerformanceMetrics(
            total_analyses=total,
            avg_processing_time_ms=round(avg_time, 2),
            approx_fps=approx_fps,
            min_processing_time_ms=round(min(times), 2),
            max_processing_time_ms=round(max(times), 2),
        )

        return StatisticsResponse(
            total_analyses=total,
            predominant_emotion=predominant,
            emotion_distribution=distribution,
            performance=performance,
        )

    def get_history(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        start: datetime | None = None,
        end: datetime | None = None,
        emotion: str | None = None,
    ) -> HistoryResponse:
        """Retorna histórico paginado de análises, com filtros opcionais."""
        query = select(EmotionAnalysis)
        count_query = select(func.count()).select_from(EmotionAnalysis)

        if start is not None:
            query = query.where(EmotionAnalysis.timestamp >= start)
            count_query = count_query.where(EmotionAnalysis.timestamp >= start)
        if end is not None:
            query = query.where(EmotionAnalysis.timestamp <= end)
            count_query = count_query.where(EmotionAnalysis.timestamp <= end)
        if emotion is not None:
            query = query.where(EmotionAnalysis.emotion == emotion)
            count_query = count_query.where(EmotionAnalysis.emotion == emotion)

        total = db.execute(count_query).scalar_one()

        query = (
            query.order_by(EmotionAnalysis.timestamp.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = db.execute(query).scalars().all()

        return HistoryResponse(total=total, page=page, page_size=page_size, items=items)


analytics_service = AnalyticsService()
