import { getExportCsvUrl } from "../services/api.js";

export default function HistoryTable({ items, filters, onFilterChange }) {
  const handleChange = (field) => (e) => {
    onFilterChange({ ...filters, [field]: e.target.value || undefined });
  };

  return (
    <div className="app-card p-3 mt-4">
      <div className="d-flex flex-wrap gap-2 align-items-end justify-content-between mb-3">
        <h6 className="mb-0">Histórico de Análises</h6>
        <div className="d-flex flex-wrap gap-2">
          <input
            type="datetime-local"
            className="form-control form-control-sm"
            onChange={handleChange("start")}
            title="Data/hora inicial"
          />
          <input
            type="datetime-local"
            className="form-control form-control-sm"
            onChange={handleChange("end")}
            title="Data/hora final"
          />
          <select
            className="form-select form-select-sm"
            onChange={handleChange("emotion")}
            defaultValue=""
          >
            <option value="">Todas as emoções</option>
            {["happy", "sad", "angry", "fear", "surprise", "neutral", "disgust"].map((e) => (
              <option key={e} value={e}>
                {e}
              </option>
            ))}
          </select>
          <a
            className="btn btn-sm btn-outline-primary"
            href={getExportCsvUrl(filters)}
            download
          >
            ⬇ Exportar CSV
          </a>
        </div>
      </div>

      <div className="table-responsive" style={{ maxHeight: "320px", overflowY: "auto" }}>
        <table className="table table-sm align-middle mb-0">
          <thead>
            <tr>
              <th>#</th>
              <th>Data/Hora</th>
              <th>Emoção</th>
              <th>Confiança</th>
              <th>Tempo (ms)</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{new Date(item.timestamp).toLocaleString()}</td>
                <td className="text-capitalize">{item.emotion}</td>
                <td>{item.confidence.toFixed(1)}%</td>
                <td>{item.processing_time_ms.toFixed(0)}</td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={5} className="text-center text-muted-app">
                  Nenhum registro encontrado.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
