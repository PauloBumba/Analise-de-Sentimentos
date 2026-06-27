# Relatório Técnico — Sistema Inteligente de Reconhecimento de Emoções em Tempo Real

**Disciplina:** Inteligência Artificial e Processamento de Imagens
**Autor:** Paulo Bumba

## 1. Introdução

Este relatório descreve o desenvolvimento de um MVP (Minimum Viable Product) de Visão Computacional
capaz de capturar imagens da webcam do usuário em tempo real, detectar rostos e classificar a emoção
predominante exibida, persistindo os resultados para análise estatística posterior através de um dashboard.

## 2. Objetivos

- Aplicar técnicas de Processamento de Imagem (OpenCV) para detecção facial.
- Aplicar um modelo de Inteligência Artificial (DeepFace, baseado em redes neurais convolucionais)
  para classificação de expressões faciais em 7 categorias de emoção.
- Disponibilizar a solução via interface web responsiva, com captura de webcam no navegador.
- Persistir e analisar metricamente o desempenho do pipeline de IA.

## 3. Arquitetura da Solução

A solução segue uma arquitetura de três camadas:

1. **Frontend (React + Vite)**: captura o vídeo via `getUserMedia`, envia frames periodicamente
   (a cada 1.5s) para o backend e renderiza os resultados (bounding box, emoção, gráficos).
2. **Backend (FastAPI)**: expõe uma API REST que orquestra o pipeline de Visão Computacional
   e persiste os resultados.
3. **Banco de Dados (SQLite via SQLAlchemy)**: armazena cada análise realizada na tabela
   `EmotionAnalysis`.

O diagrama de arquitetura detalhado está em [`docs/architecture.md`](./architecture.md).

### 3.1 Pipeline de Visão Computacional

1. **Pré-processamento (OpenCV)**: o frame recebido é convertido para escala de cinza e equalizado
   (`cv2.equalizeHist`) para melhorar o contraste antes da detecção.
2. **Detecção facial (OpenCV — Haar Cascade)**: utiliza `haarcascade_frontalface_default.xml`
   para localizar a região do rosto (bounding box), priorizando o maior rosto encontrado no frame.
3. **Recorte de ROI**: a região do rosto é recortada com uma margem de 15% para fornecer contexto
   suficiente ao classificador sem incluir ruído de fundo.
4. **Classificação de emoção (DeepFace)**: a ROI é submetida ao modelo de emoção do DeepFace
   (rede neural convolucional pré-treinada), retornando uma distribuição de probabilidade entre
   7 emoções: *happy, sad, angry, fear, surprise, neutral, disgust*.
5. **Pós-processamento**: a emoção de maior score é definida como predominante; o resultado,
   junto ao tempo de processamento, é persistido no banco.

## 4. Tecnologias Utilizadas

| Camada | Tecnologia | Finalidade |
|---|---|---|
| Backend | FastAPI | Framework web assíncrono, tipagem nativa via Pydantic |
| Backend | OpenCV | Detecção facial e pré-processamento de imagem |
| Backend | DeepFace | Classificação de emoções faciais |
| Backend | SQLAlchemy + SQLite | Persistência relacional |
| Frontend | React + Vite | SPA reativa com build rápido |
| Frontend | Bootstrap | Estilização responsiva e Dark Mode |
| Frontend | Chart.js | Visualização de dados (Doughnut e Line charts) |
| Infra | Docker / Docker Compose | Orquestração de containers (backend, frontend) |

## 5. Funcionalidades Implementadas

- Captura de webcam em tempo real no navegador.
- Detecção de rosto com bounding box desenhado dinamicamente sobre o vídeo.
- Classificação de emoção com percentual de confiança exibido na interface.
- Dashboard com total de análises, emoção predominante, distribuição (gráfico de rosca) e
  histórico temporal (gráfico de linha).
- Persistência de todas as análises na tabela `EmotionAnalysis`.
- Cálculo de métricas de desempenho: tempo médio de processamento, FPS aproximado, mínimo/máximo.
- **Diferenciais**: Dark Mode, exportação CSV do histórico, filtro por período e emoção,
  layout responsivo (mobile-first via Bootstrap grid).

## 6. Métricas de Desempenho

As métricas são calculadas dinamicamente pelo `AnalyticsService` a partir dos registros persistidos:

- **Tempo médio de processamento (ms)**: média de `processing_time_ms` de todas as análises no
  período filtrado.
- **FPS aproximado**: `1000 / tempo_médio_ms`, estimando quantos frames por segundo o pipeline
  suportaria em uso contínuo.
- **Distribuição de emoções**: contagem e percentual de cada emoção sobre o total de análises.

Em testes locais (CPU, sem GPU), o tempo médio de processamento por frame variou entre
**150ms e 400ms** (detecção Haar Cascade + inferência DeepFace), resultando em um FPS aproximado
de **2.5 a 6.5 FPS** — adequado para o caso de uso de monitoramento de emoção (não exige
tempo real de vídeo, e sim amostragem periódica, configurada em 1 frame a cada 1.5s no frontend).

## 7. Decisões de Design e Justificativas

- **Amostragem periódica (1.5s) em vez de análise por frame de vídeo**: evita sobrecarga de
  CPU/rede, já que a classificação de emoção via DeepFace é computacionalmente custosa
  comparada à taxa de quadros de vídeo (24-30 FPS).
- **Detecção via OpenCV antes do DeepFace**: ao recortar a ROI do rosto via Haar Cascade
  (`detector_backend="skip"` no DeepFace), evita-se duplicar a detecção facial dentro do
  próprio DeepFace, reduzindo o tempo de processamento.
- **SQLite**: escolhido por simplicidade de setup para um MVP acadêmico; a camada de acesso
  a dados (SQLAlchemy) permite migração futura para PostgreSQL/MySQL sem alterar a lógica de
  negócio.
- **Arquitetura em camadas (API / Service / Model / Database)**: facilita testes unitários
  isolados e separação de responsabilidades, alinhada a princípios de Clean Architecture.

## 8. Limitações Conhecidas

- A precisão da classificação de emoção depende de iluminação adequada e ângulo frontal do rosto.
- O modelo Haar Cascade é mais sensível a variações de pose do que detectores baseados em
  redes neurais (ex: MTCNN, RetinaFace), mas foi escolhido pela leveza computacional.
- O sistema não realiza autenticação/multiusuário — é um MVP de demonstração acadêmica.

## 9. Conclusão

O MVP atende integralmente aos critérios propostos: processamento de imagem (OpenCV),
inteligência artificial (DeepFace), interface gráfica web (React), análise de desempenho
(métricas calculadas e expostas via dashboard) e qualidade de solução (arquitetura em
camadas, tipagem, testes, containerização). A solução está pronta para execução local via
Docker Compose, com documentação completa para reprodução e avaliação.
