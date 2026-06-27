export default function StatsCards({ statistics }) {
  if (!statistics) return null;
  const { total_analyses, predominant_emotion, performance } = statistics;

  const cards = [
    { label: "Total de Análises", value: total_analyses },
    { label: "Emoção Predominante", value: predominant_emotion ?? "—" },
    { label: "Tempo Médio (ms)", value: performance.avg_processing_time_ms.toFixed(1) },
    { label: "FPS Aproximado", value: performance.approx_fps.toFixed(1) },
  ];

  return (
    <div className="row g-3 mb-4">
      {cards.map((card) => (
        <div className="col-6 col-lg-3" key={card.label}>
          <div className="app-card p-3 text-center h-100">
            <div className="metric-value text-capitalize">{card.value}</div>
            <div className="text-muted-app small">{card.label}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
