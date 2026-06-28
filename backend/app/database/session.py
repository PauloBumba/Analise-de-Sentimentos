"""Configuração de conexão e sessão do banco de dados (SQLAlchemy 2.0)."""
import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# Garante que o diretório do banco exista (para SQLite em arquivo)
db_path = settings.database_url.replace("sqlite:///", "")
if db_path and not db_path.startswith(":memory:"):
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base declarativa para os modelos ORM."""


def get_db() -> Generator[Session, None, None]:
    """Dependency do FastAPI que fornece uma sessão de banco por requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Cria as tabelas no banco de dados, caso não existam."""
    from app.models import emotion_analysis  # noqa: F401  (garante import do modelo)

    Base.metadata.create_all(bind=engine)
