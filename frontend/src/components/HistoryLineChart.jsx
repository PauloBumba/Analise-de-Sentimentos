import { Line } from "react-chartjs-2";
import "../services/chartSetup.js";

const EMOTION_NUMERIC = {
  angry: 0,
  disgust: 1,
  fear: 2,
  sad: 3,
  neutral: 4,
  surprise: 5,
  happy: 6,
};

/**
 * Exibe o histórico temporal das análises, mapeando emoções para um eixo numérico
 * para visualizar a tendência ao longo do tempo.
 */
export default function HistoryLineChart({ items }) {
  if (!items || items.length === 0) {
    return <div className="app-card p-4 text-center text-muted-app">Sem histórico ainda.</div>;
  }

  const ordered = [...items].reverse();

  const data = {
    labels: ordered.map((item) => new Date(item.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: "Emoção (escala)",
        data: ordered.map((item) => EMOTION_NUMERIC[item.emotion] ?? 4),
        borderColor: "#5b6cff",
        backgroundColor: "rgba(91,108,255,0.15)",
        tension: 0.3,
        fill: true,
      },
    ],
  };

  const options = {
    scales: {
      y: {
        ticks: {
          callback: (value) =>
            Object.keys(EMOTION_NUMERIC).find((k) => EMOTION_NUMERIC[k] === value) ?? "",
        },
        min: 0,
        max: 6,
      },
    },
    plugins: { legend: { display: false } },
  };

  return (
    <div className="app-card p-3">
      <h6 className="mb-3">Histórico Temporal</h6>
      <Line data={data} options={options} />
    </div>
  );
}
