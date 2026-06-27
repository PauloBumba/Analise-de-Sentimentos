"""Ponto de entrada da aplicação FastAPI."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.config import get_settings
from app.database.session import init_db
from app.services.emotion_service import emotion_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa o banco de dados e pré-carrega os modelos de IA na subida da aplicação."""
    logger.info("Inicializando banco de dados...")
    init_db()
    logger.info("Realizando warmup do DeepFace (pode levar alguns segundos)...")
    emotion_service.warmup()
    logger.info("Aplicação pronta.")
    yield
    logger.info("Encerrando aplicação.")


app = FastAPI(
    title=settings.app_name,
    description=(
        "API de Visão Computacional para detecção facial (OpenCV) e "
        "reconhecimento de emoções (DeepFace) em tempo real."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["Sistema"])
def root() -> dict[str, str]:
    """Endpoint raiz com informações básicas da API."""
    return {
        "service": settings.app_name,
        "docs": "/docs",
        "api_prefix": settings.api_v1_prefix,
    }
