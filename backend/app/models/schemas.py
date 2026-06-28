"""Schemas Pydantic para validação e serialização de dados da API."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EmotionAnalysisBase(BaseModel):
    """Campos comuns de uma análise de emoção."""

    emotion: str = Field(..., description="Emoção predominante detectada")
    confidence: float = Field(..., ge=0, le=100, description="Confiança em percentual (0-100)")
    processing_time_ms: float = Field(..., ge=0, description="Tempo de processamento em milissegundos")
    faces_detected: int = Field(default=1, ge=0, description="Quantidade de rostos detectados no frame")


class EmotionAnalysisCreate(EmotionAnalysisBase):
    """Schema usado internamente ao persistir uma nova análise."""


class EmotionAnalysisRead(EmotionAnalysisBase):
    """Schema de leitura/retorno de uma análise persistida."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime


class EmotionScores(BaseModel):
    """Distribuição de probabilidade entre as emoções suportadas."""

    angry: float = 0.0
    fear: float = 0.0
    happy: float = 0.0
    sad: float = 0.0
    surprise: float = 0.0
    neutral: float = 0.0
    disgust: float = 0.0


class BoundingBox(BaseModel):
    """Coordenadas do bounding box de um rosto detectado."""

    x: int
    y: int
    w: int
    h: int


class AnalyzeImageResponse(BaseModel):
    """Resposta do endpoint de análise de imagem."""

    emotion: str
    confidence: float
    emotion_scores: EmotionScores
    bounding_box: BoundingBox | None = None
    faces_detected: int
    processing_time_ms: float
    timestamp: datetime


class EmotionDistributionItem(BaseModel):
    """Item de distribuição de emoções para o dashboard."""

    emotion: str
    count: int
    percentage: float


class PerformanceMetrics(BaseModel):
    """Métricas agregadas de desempenho do sistema."""

    total_analyses: int
    avg_processing_time_ms: float
    approx_fps: float
    min_processing_time_ms: float
    max_processing_time_ms: float


class StatisticsResponse(BaseModel):
    """Resposta consolidada do endpoint /statistics."""

    total_analyses: int
    predominant_emotion: str | None
    emotion_distribution: list[EmotionDistributionItem]
    performance: PerformanceMetrics


class HistoryResponse(BaseModel):
    """Resposta paginada do endpoint /history."""

    total: int
    page: int
    page_size: int
    items: list[EmotionAnalysisRead]


class HealthResponse(BaseModel):
    """Resposta do endpoint /health."""

    status: str
    service: str
    deepface_ready: bool
