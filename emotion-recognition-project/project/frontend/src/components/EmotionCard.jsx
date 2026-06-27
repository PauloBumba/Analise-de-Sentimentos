const EMOTION_EMOJI = {
  happy: "😄",
  sad: "😢",
  angry: "😠",
  fear: "😨",
  surprise: "😲",
  neutral: "😐",
  disgust: "🤢",
};

const EMOTION_LABEL_PT = {
  happy: "Feliz",
  sad: "Triste",
  angry: "Irritado",
  fear: "Medo",
  surprise: "Surpreso",
  neutral: "Neutro",
  disgust: "Enojado",
};

/**
 * Exibe a emoção predominante atual, percentual de confiança e tempo de processamento.
 */
export default function EmotionCard({ result }) {
  if (!result) {
    return (
      <div className="app-card p-4 text-center text-muted-app">
        Aguardando primeira análise...
      </div>
    );
  }

  const { emotion, confidence, faces_detected, processing_time_ms } = result;
  const emoji = EMOTION_EMOJI[emotion] || "🤔";
  const label = EMOTION_LABEL_PT[emotion] || emotion;

  return (
    <div className="app-card p-4 text-center">
      {faces_detected === 0 ? (
        <p className="text-muted-app mb-0">Nenhum rosto detectado no momento.</p>
      ) : (
        <>
          <div className="emotion-badge mb-2">
            {emoji} {label} <span className="text-muted-app">{confidence.toFixed(0)}%</span>
          </div>
          <div className="row mt-3">
            <div className="col">
              <div className="metric-value">{processing_time_ms.toFixed(0)}ms</div>
              <div className="text-muted-app small">Tempo de processamento</div>
            </div>
            <div className="col">
              <div className="metric-value">{faces_detected}</div>
              <div className="text-muted-app small">Rosto(s) detectado(s)</div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
