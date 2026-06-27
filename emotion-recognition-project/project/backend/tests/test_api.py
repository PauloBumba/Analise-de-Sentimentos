"""Testes básicos da API (smoke tests). Execução: pytest -q"""
import io

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    """Cliente de testes com o ciclo de vida (lifespan) da app ativo, garantindo
    que as tabelas do banco sejam criadas antes dos testes rodarem."""
    with TestClient(app) as test_client:
        yield test_client


def _fake_jpeg_bytes() -> bytes:
    """Gera bytes de uma imagem JPEG sintética (sem rosto) para testes."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    ok, buf = cv2.imencode(".jpg", img)
    assert ok
    return buf.tobytes()


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_root(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200


def test_analyze_image_no_face(client: TestClient) -> None:
    """Imagem sem rosto deve retornar faces_detected == 0, sem erro."""
    files = {"file": ("frame.jpg", io.BytesIO(_fake_jpeg_bytes()), "image/jpeg")}
    response = client.post("/api/v1/analyze-image", files=files)
    assert response.status_code == 200
    body = response.json()
    assert body["faces_detected"] == 0


def test_analyze_image_invalid_type(client: TestClient) -> None:
    files = {"file": ("frame.txt", io.BytesIO(b"not an image"), "text/plain")}
    response = client.post("/api/v1/analyze-image", files=files)
    assert response.status_code == 415


def test_statistics_empty_ok(client: TestClient) -> None:
    response = client.get("/api/v1/statistics")
    assert response.status_code == 200
    assert "total_analyses" in response.json()


def test_history_ok(client: TestClient) -> None:
    response = client.get("/api/v1/history")
    assert response.status_code == 200
    assert "items" in response.json()
