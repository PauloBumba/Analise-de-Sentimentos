# Diagrama de Arquitetura — Sistema de Reconhecimento de Emoções

## Visão Geral dos Componentes

```mermaid
flowchart TD
    subgraph Client["Navegador do Usuário"]
        Webcam["Webcam (getUserMedia)"]
        ReactApp["React + Vite + Bootstrap + Chart.js"]
    end

    subgraph Backend["Backend - FastAPI (Python 3.12)"]
        API["Camada API (routes.py)"]
        CV["Serviço OpenCV (detecção facial)"]
        DF["Serviço DeepFace (classificação de emoção)"]
        Analytics["Serviço de Analytics/Estatísticas"]
        ORM["SQLAlchemy ORM"]
    end

    DB[("SQLite - emotions.db")]

    Webcam --> ReactApp
    ReactApp -- "POST /api/v1/analyze-image (frame JPEG)" --> API
    API --> CV
    CV -- "ROI do rosto" --> DF
    DF -- "emoção + confiança" --> API
    API --> Analytics
    Analytics --> ORM
    ORM --> DB
    API -- "JSON: emoção, confiança, bbox, métricas" --> ReactApp
    ReactApp -- "GET /api/v1/statistics, /history" --> API
```

## Fluxo de Análise (sequência)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant W as Webcam (Browser)
    participant F as Frontend (React)
    participant B as Backend (FastAPI)
    participant O as OpenCV
    participant D as DeepFace
    participant S as SQLite

    U->>W: Permite acesso à câmera
    loop A cada 1.5s
        F->>F: Captura frame do <video> em <canvas>
        F->>B: POST /analyze-image (multipart/form-data)
        B->>O: Detecta rosto (Haar Cascade)
        O-->>B: bounding box + ROI
        B->>D: Classifica emoção (ROI)
        D-->>B: emoção dominante + scores
        B->>S: Persiste EmotionAnalysis
        B-->>F: JSON (emoção, confiança, bbox, tempo_ms)
        F->>F: Desenha bounding box no canvas
        F->>U: Exibe emoção + confiança
    end
```

## Modelo de Dados

```mermaid
erDiagram
    EMOTION_ANALYSIS {
        int id PK
        datetime timestamp
        string emotion
        float confidence
        float processing_time_ms
        int faces_detected
    }
```

## Camadas (Clean Architecture simplificada)

- **API Layer** (`app/api`): contratos HTTP, validação de entrada/saída (Pydantic).
- **Service Layer** (`app/services`): regras de negócio — `emotion_service` (CV/IA) e `analytics_service` (estatísticas).
- **Model/Domain Layer** (`app/models`): entidades ORM e schemas Pydantic.
- **Database Layer** (`app/database`): configuração de engine/sessão SQLAlchemy.

Essa separação permite testar a lógica de IA isoladamente da camada HTTP e trocar o banco de dados (SQLite → PostgreSQL, por exemplo) sem impactar as camadas superiores.
