import { useCallback, useEffect, useState } from "react";
import StatsCards from "../components/StatsCards.jsx";
import EmotionDistributionChart from "../components/EmotionDistributionChart.jsx";
import HistoryLineChart from "../components/HistoryLineChart.jsx";
import HistoryTable from "../components/HistoryTable.jsx";
import { fetchHistory, fetchStatistics } from "../services/api.js";

const POLL_INTERVAL_MS = 5000;

export default function Dashboard() {
  const [statistics, setStatistics] = useState(null);
  const [history, setHistory] = useState({ items: [], total: 0 });
  const [filters, setFilters] = useState({});

  const loadData = useCallback(async () => {
    try {
      const [statsData, historyData] = await Promise.all([
        fetchStatistics(filters),
        fetchHistory({ page: 1, page_size: 50, ...filters }),
      ]);
      setStatistics(statsData);
      setHistory(historyData);
    } catch (err) {
      console.error("Erro ao carregar dados do dashboard:", err);
    }
  }, [filters]);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [loadData]);

  return (
    <div className="container">
      <h2 className="mb-4">Dashboard de Desempenho</h2>

      <StatsCards statistics={statistics} />

      <div className="row g-4">
        <div className="col-lg-5">
          <EmotionDistributionChart distribution={statistics?.emotion_distribution} />
        </div>
        <div className="col-lg-7">
          <HistoryLineChart items={history.items} />
        </div>
      </div>

      <HistoryTable items={history.items} filters={filters} onFilterChange={setFilters} />
    </div>
  );
}
