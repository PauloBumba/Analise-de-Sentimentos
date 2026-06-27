"""Definição das rotas REST da API de reconhecimento de emoções."""
from __future__ import annotations

import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.schemas import (
    AnalyzeImageResponse,
    BoundingBox,
    EmotionAnalysisCreate,
    EmotionScores,
    HealthResponse,
    HistoryResponse,
    StatisticsResponse,
)
from app.services.analytics_service import analytics_service
from app.services.emotion_service import emotion_service

router = APIRouter()

MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB


@router.get("/health", response_model=HealthResponse, tags=["Sistema"])
def health_check() -> HealthResponse:
    """Verifica se a API e o pipeline de IA estão operacionais."""
    return HealthResponse(status="ok", service="emotion-recognition-api", deepface_ready=True)


@router.post("/analyze-image", response_model=AnalyzeImageResponse, tags=["Análise"])
async def analyze_image(
    file: UploadFile = File(..., description="Frame capturado da webcam (JPEG/PNG)"),
    db: Session = Depends(get_db),
) -> AnalyzeImageResponse:
    """Recebe um frame de imagem, detecta o rosto e classifica a emoção predominante."""
    if file.content_type not in {"image/jpeg", "image/png", "image/jpg", "image/webp"}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato de imagem não suportado. Envie JPEG, PNG ou WEBP.",
        )

    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Imagem excede o tamanho máximo permitido (5MB).",
        )

    try:
        frame = emotion_service.decode_image(image_bytes)
        result = emotion_service.analyze_emotion(frame)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    # Persiste somente quando ao menos um rosto foi detectado
    if result.faces_detected > 0:
        analytics_service.save_analysis(
            db,
            EmotionAnalysisCreate(
                emotion=result.dominant_emotion,
                confidence=result.confidence,
                processing_time_ms=result.processing_time_ms,
                faces_detected=result.faces_detected,
            ),
        )

    bbox = None
    if result.bounding_box is not None:
        x, y, w, h = result.bounding_box
        bbox = BoundingBox(x=x, y=y, w=w, h=h)

    return AnalyzeImageResponse(
        emotion=result.dominant_emotion,
        confidence=result.confidence,
        emotion_scores=EmotionScores(**result.emotion_scores),
        bounding_box=bbox,
        faces_detected=result.faces_detected,
        processing_time_ms=result.processing_time_ms,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/statistics", response_model=StatisticsResponse, tags=["Dashboard"])
def get_statistics(
    start: datetime | None = Query(default=None, description="Filtro: data/hora inicial (ISO 8601)"),
    end: datetime | None = Query(default=None, description="Filtro: data/hora final (ISO 8601)"),
    db: Session = Depends(get_db),
) -> StatisticsResponse:
    """Retorna estatísticas agregadas: total de análises, distribuição e desempenho."""
    return analytics_service.get_statistics(db, start=start, end=end)


@router.get("/history", response_model=HistoryResponse, tags=["Dashboard"])
def get_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    emotion: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> HistoryResponse:
    """Retorna o histórico paginado de análises, com filtros opcionais por período e emoção."""
    return analytics_service.get_history(
        db, page=page, page_size=page_size, start=start, end=end, emotion=emotion
    )


@router.get("/history/export", tags=["Dashboard"])
def export_history_csv(
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    emotion: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Exporta o histórico de análises filtrado em formato CSV."""
    history = analytics_service.get_history(
        db, page=1, page_size=100000, start=start, end=end, emotion=emotion
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "timestamp", "emotion", "confidence", "processing_time_ms", "faces_detected"])
    for item in history.items:
        writer.writerow(
            [item.id, item.timestamp.isoformat(), item.emotion, item.confidence,
             item.processing_time_ms, item.faces_detected]
        )
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=emotion_history.csv"},
    )
