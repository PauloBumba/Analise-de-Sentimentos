import { useState } from "react";
import WebcamCapture from "../components/WebcamCapture.jsx";
import EmotionCard from "../components/EmotionCard.jsx";
import EmotionScoresBars from "../components/EmotionScoresBars.jsx";

export default function Home() {
  const [lastResult, setLastResult] = useState(null);
  const [intervalMs, setIntervalMs] = useState(1500);

  return (
    <div className="container">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-2">
        <h2 className="mb-0">Análise de Emoções em Tempo Real</h2>
        <div className="d-flex align-items-center gap-2">
          <label htmlFor="intervalRange" className="small text-muted-app mb-0">
            Intervalo de captura: <strong>{(intervalMs / 1000).toFixed(1)}s</strong>
          </label>
          <input
            id="intervalRange"
            type="range"
            className="form-range"
            style={{ width: "140px" }}
            min={500}
            max={4000}
            step={250}
            value={intervalMs}
            onChange={(e) => setIntervalMs(Number(e.target.value))}
          />
        </div>
      </div>
      <div className="row g-4">
        <div className="col-lg-7">
          <div className="app-card p-3">
            <WebcamCapture onResult={setLastResult} intervalMs={intervalMs} />
          </div>
        </div>
        <div className="col-lg-5">
          <EmotionCard result={lastResult} />
          <EmotionScoresBars scores={lastResult?.emotion_scores} />
        </div>
      </div>
    </div>
  );
}
