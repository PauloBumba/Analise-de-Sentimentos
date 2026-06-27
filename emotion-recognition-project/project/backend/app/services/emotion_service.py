"""Serviço de processamento de imagem (OpenCV) e reconhecimento de emoções (DeepFace)."""
from __future__ import annotations

import base64
import logging
import time
from dataclasses import dataclass, field

import cv2
import numpy as np
from deepface import DeepFace

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Cascata Haar do OpenCV usada para a detecção rápida de rostos e desenho do bounding box.
_FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

SUPPORTED_EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]


@dataclass
class FaceDetectionResult:
    """Resultado da etapa de detecção facial via OpenCV."""

    faces_detected: int
    bounding_box: tuple[int, int, int, int] | None  # x, y, w, h
    gray_frame: np.ndarray = field(repr=False)


@dataclass
class EmotionResult:
    """Resultado consolidado da análise de emoção."""

    dominant_emotion: str
    confidence: float
    emotion_scores: dict[str, float]
    bounding_box: tuple[int, int, int, int] | None
    faces_detected: int
    processing_time_ms: float


class EmotionRecognitionService:
    """Encapsula o pipeline de Visão Computacional: OpenCV (detecção) + DeepFace (classificação)."""

    def decode_image(self, image_bytes: bytes) -> np.ndarray:
        """Decodifica bytes de imagem (JPEG/PNG) para uma matriz BGR do OpenCV."""
        np_array = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Não foi possível decodificar a imagem enviada.")
        return frame

    def decode_base64_image(self, base64_str: str) -> np.ndarray:
        """Decodifica uma imagem em base64 (com ou sem prefixo data:image/...)."""
        if "," in base64_str:
            base64_str = base64_str.split(",", 1)[1]
        image_bytes = base64.b64decode(base64_str)
        return self.decode_image(image_bytes)

    def detect_faces(self, frame: np.ndarray) -> FaceDetectionResult:
        """Detecta rostos utilizando o classificador Haar Cascade do OpenCV.

        Faz uma primeira tentativa com parâmetros conservadores (menos falsos positivos)
        e, caso nenhum rosto seja encontrado, tenta novamente com parâmetros mais
        permissivos (útil para rostos de perfil leve, distância maior ou iluminação
        mais fraca), antes de desistir.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)  # melhora contraste para detecção mais estável

        faces = _FACE_CASCADE.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
        )

        if len(faces) == 0:
            # Segunda tentativa: parâmetros mais permissivos (rosto menor/mais distante,
            # ou levemente de perfil).
            faces = _FACE_CASCADE.detectMultiScale(
                gray, scaleFactor=1.05, minNeighbors=3, minSize=(40, 40)
            )

        bounding_box: tuple[int, int, int, int] | None = None
        if len(faces) > 0:
            # Seleciona o maior rosto detectado (mais próximo da câmera)
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            bounding_box = (int(x), int(y), int(w), int(h))

        return FaceDetectionResult(
            faces_detected=len(faces), bounding_box=bounding_box, gray_frame=gray
        )

    def _detect_faces_deepface(self, frame: np.ndarray) -> FaceDetectionResult:
        """Detecção facial usando o detector embutido do DeepFace (mais preciso, porém
        mais lento que o Haar Cascade). Usado quando `face_detection_mode='accurate'`.
        """
        try:
            faces_data = DeepFace.extract_faces(
                img_path=frame,
                detector_backend=settings.deepface_detector_backend,
                enforce_detection=False,
                align=False,
            )
        except Exception:  # noqa: BLE001
            logger.exception("Falha no detector DeepFace; sem rosto detectado.")
            faces_data = []

        valid_faces = [
            f for f in faces_data if f.get("confidence", 0) and f["facial_area"]["w"] > 0
        ]

        if not valid_faces:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return FaceDetectionResult(faces_detected=0, bounding_box=None, gray_frame=gray)

        best = max(valid_faces, key=lambda f: f["facial_area"]["w"] * f["facial_area"]["h"])
        area = best["facial_area"]
        bounding_box = (int(area["x"]), int(area["y"]), int(area["w"]), int(area["h"]))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        return FaceDetectionResult(
            faces_detected=len(valid_faces), bounding_box=bounding_box, gray_frame=gray
        )

    def analyze_emotion(self, frame: np.ndarray) -> EmotionResult:
        """Executa o pipeline completo: detecção facial + classificação (DeepFace).

        O backend de detecção é configurável via `DEEPFACE_DETECTOR_BACKEND`/
        `FACE_DETECTION_MODE`: 'fast' usa Haar Cascade (OpenCV, baixa latência);
        'accurate' usa o detector nativo do DeepFace (ex.: retinaface/mtcnn),
        mais robusto a poses e iluminação, porém mais lento.
        """
        start = time.perf_counter()

        if settings.face_detection_mode == "accurate":
            detection = self._detect_faces_deepface(frame)
        else:
            detection = self.detect_faces(frame)

        if detection.faces_detected == 0:
            processing_time_ms = (time.perf_counter() - start) * 1000
            return EmotionResult(
                dominant_emotion="neutral",
                confidence=0.0,
                emotion_scores={e: 0.0 for e in SUPPORTED_EMOTIONS},
                bounding_box=None,
                faces_detected=0,
                processing_time_ms=processing_time_ms,
            )

        # Recorta a região do rosto para acelerar e estabilizar a classificação do DeepFace
        x, y, w, h = detection.bounding_box
        margin = int(0.15 * w)
        x0, y0 = max(0, x - margin), max(0, y - margin)
        x1, y1 = min(frame.shape[1], x + w + margin), min(frame.shape[0], y + h + margin)
        face_roi = frame[y0:y1, x0:x1]

        try:
            analysis = DeepFace.analyze(
                img_path=face_roi,
                actions=["emotion"],
                detector_backend="skip",  # já temos o rosto recortado pelo OpenCV
                enforce_detection=False,
                silent=True,
            )
            result = analysis[0] if isinstance(analysis, list) else analysis
            emotion_scores: dict[str, float] = {
                k.lower(): float(v) for k, v in result["emotion"].items()
            }
            dominant_emotion = str(result["dominant_emotion"]).lower()
            confidence = float(emotion_scores.get(dominant_emotion, 0.0))
        except Exception:  # noqa: BLE001 - fallback robusto para falhas do modelo
            logger.exception("Falha ao executar DeepFace.analyze; aplicando fallback neutro.")
            emotion_scores = {e: 0.0 for e in SUPPORTED_EMOTIONS}
            emotion_scores["neutral"] = 100.0
            dominant_emotion = "neutral"
            confidence = 100.0

        processing_time_ms = (time.perf_counter() - start) * 1000

        return EmotionResult(
            dominant_emotion=dominant_emotion,
            confidence=round(confidence, 2),
            emotion_scores={k: round(v, 2) for k, v in emotion_scores.items()},
            bounding_box=detection.bounding_box,
            faces_detected=detection.faces_detected,
            processing_time_ms=round(processing_time_ms, 2),
        )

    def warmup(self) -> bool:
        """Pré-carrega os modelos do DeepFace para evitar latência na primeira requisição real."""
        try:
            dummy = np.zeros((100, 100, 3), dtype=np.uint8)
            DeepFace.analyze(
                img_path=dummy,
                actions=["emotion"],
                detector_backend="skip",
                enforce_detection=False,
                silent=True,
            )
            return True
        except Exception:  # noqa: BLE001
            logger.exception("Falha no warmup do DeepFace.")
            return False


emotion_service = EmotionRecognitionService()
