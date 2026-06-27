"""Modelo ORM para a tabela EmotionAnalysis."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class EmotionAnalysis(Base):
    """Representa o resultado de uma análise de emoção facial."""

    __tablename__ = "emotion_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    emotion: Mapped[str] = mapped_column(String(20), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    processing_time_ms: Mapped[float] = mapped_column(Float)
    faces_detected: Mapped[int] = mapped_column(Integer, default=1)

    def __repr__(self) -> str:
        return f"<EmotionAnalysis id={self.id} emotion={self.emotion} confidence={self.confidence:.2f}>"
