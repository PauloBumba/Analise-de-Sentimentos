"""Configuração de testes (pytest). Garante banco de testes isolado."""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_emotions.db")
