# 🎭 Sistema Inteligente de Reconhecimento de Emoções em Tempo Real

MVP acadêmico de Visão Computacional que detecta rostos via webcam e classifica a emoção
predominante (Happy, Sad, Neutral, Angry, Fear, Surprise, Disgust) em tempo real, com dashboard
de estatísticas e métricas de desempenho.

> Disciplina: Inteligência Artificial e Processamento de Imagens

## Stack

- **Backend:** Python 3.12, FastAPI, OpenCV, DeepFace, SQLAlchemy, SQLite
- **Frontend:** React, Vite, Bootstrap, Chart.js
- **Infra:** Docker, Docker Compose

## Estrutura do Projeto

```
project/
├── backend/
│   ├── app/
│   │   ├── api/          # Rotas REST (FastAPI)
│   │   ├── services/     # Lógica de negócio (OpenCV/DeepFace, Analytics)
│   │   ├── models/       # Modelos ORM (SQLAlchemy) e Schemas (Pydantic)
│   │   ├── database/     # Configuração de sessão/engine
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/        # Home (captura) e Dashboard
│   │   ├── components/   # Webcam, gráficos, cards, tabela
│   │   ├── services/     # Cliente API, ThemeContext
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── docs/
│   ├── architecture.md       # Diagramas Mermaid (arquitetura, sequência, ER)
│   └── relatorio_tecnico.md  # Relatório técnico completo
└── docker-compose.yml
```

## Como Executar (Docker — recomendado)

Requisitos: Docker e Docker Compose instalados.

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend (Swagger docs): http://localhost:8000/docs

> ⚠️ A primeira subida do backend pode demorar alguns minutos: o DeepFace fará o download
> dos pesos do modelo de emoção na primeira execução (requer acesso à internet).

## Como Executar Localmente (sem Docker)

### Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Acesse http://localhost:5173.

## Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/health` | Verifica status da API |
| POST | `/api/v1/analyze-image` | Recebe frame (multipart), retorna emoção/confiança/bbox |
| GET | `/api/v1/statistics` | Estatísticas agregadas e métricas de desempenho |
| GET | `/api/v1/history` | Histórico paginado de análises (filtros: período, emoção) |
| GET | `/api/v1/history/export` | Exporta histórico filtrado em CSV |

Documentação interativa (Swagger UI) disponível em `/docs` quando o backend estiver em execução.

## Funcionalidades

- ✅ Captura de webcam em tempo real
- ✅ Detecção facial com bounding box (OpenCV)
- ✅ Classificação de emoção com % de confiança (DeepFace)
- ✅ Dashboard com total de análises, emoção predominante, distribuição e histórico temporal
- ✅ Persistência em SQLite (tabela `EmotionAnalysis`)
- ✅ Métricas de desempenho (tempo médio, FPS aproximado)
- ✅ Dark Mode
- ✅ Exportação CSV
- ✅ Filtro por período e emoção
- ✅ Layout responsivo

## Modos de Detecção Facial

O backend suporta dois modos, configuráveis via variável de ambiente `FACE_DETECTION_MODE`:

| Modo | Detector | Velocidade | Robustez |
|---|---|---|---|
| `fast` (padrão) | Haar Cascade (OpenCV) | Alta (poucos ms) | Boa para rosto frontal e bem iluminado |
| `accurate` | Detector nativo do DeepFace (`retinaface`, configurável via `DEEPFACE_DETECTOR_BACKEND`) | Mais lenta | Melhor com pose levemente lateral, óculos, iluminação fraca |

Para alternar, defina no `.env` do backend: `FACE_DETECTION_MODE=accurate`.

## Testes

```bash
cd backend
pip install pytest httpx
pytest -q
```

## Documentação Adicional

- [Diagrama de Arquitetura](./docs/architecture.md)
- [Relatório Técnico](./docs/relatorio_tecnico.md)

## Autor

Paulo Bumba — [GitHub](https://github.com/PauloBumba) · [LinkedIn](https://linkedin.com/in/paulo-mario-valente-bumba) · [Site](https://xampz.net)
