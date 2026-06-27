const ORDER = ["happy", "neutral", "sad", "angry", "fear", "surprise", "disgust"];

const COLORS = {
  happy: "#ffc107",
  neutral: "#6c757d",
  sad: "#0d6efd",
  angry: "#dc3545",
  fear: "#6f42c1",
  surprise: "#fd7e14",
  disgust: "#198754",
};

/**
 * Renderiza barras horizontais com o score de cada emoção retornado pelo DeepFace.
 */
export default function EmotionScoresBars({ scores }) {
  if (!scores) return null;

  return (
    <div className="app-card p-3 mt-3">
      <h6 className="mb-3">Distribuição da última análise</h6>
      {ORDER.map((key) => {
        const value = scores[key] ?? 0;
        return (
          <div key={key} className="mb-2">
            <div className="d-flex justify-content-between small">
              <span className="text-capitalize">{key}</span>
              <span>{value.toFixed(1)}%</span>
            </div>
            <div className="progress" style={{ height: "8px" }}>
              <div
                className="progress-bar"
                style={{ width: `${value}%`, backgroundColor: COLORS[key] }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
