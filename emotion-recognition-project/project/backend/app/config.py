"""Configurações centrais da aplicação."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação, lidas de variáveis de ambiente."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Emotion Recognition API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:////app/data/emotions.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost"]
    deepface_detector_backend: str = "retinaface"
    face_detection_mode: str = "fast"  # 'fast' (Haar/OpenCV) ou 'accurate' (detector DeepFace)
    max_image_size_mb: int = 5


@lru_cache
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()
