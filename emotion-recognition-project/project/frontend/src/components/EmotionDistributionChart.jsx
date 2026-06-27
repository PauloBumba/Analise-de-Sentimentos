import { Doughnut } from "react-chartjs-2";
import "../services/chartSetup.js";

const COLORS = {
  happy: "#ffc107",
  neutral: "#6c757d",
  sad: "#0d6efd",
  angry: "#dc3545",
  fear: "#6f42c1",
  surprise: "#fd7e14",
  disgust: "#198754",
};

export default function EmotionDistributionChart({ distribution }) {
  if (!distribution || distribution.length === 0) {
    return <div className="app-card p-4 text-center text-muted-app">Sem dados ainda.</div>;
  }

  const data = {
    labels: distribution.map((d) => d.emotion),
    datasets: [
      {
        data: distribution.map((d) => d.count),
        backgroundColor: distribution.map((d) => COLORS[d.emotion] || "#999"),
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="app-card p-3">
      <h6 className="mb-3">Distribuição de Emoções</h6>
      <Doughnut data={data} options={{ plugins: { legend: { position: "bottom" } } }} />
    </div>
  );
}
