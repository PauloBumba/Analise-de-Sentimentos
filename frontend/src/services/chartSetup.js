import {
  ArcElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from "chart.js";

ChartJS.register(ArcElement, CategoryScale, LinearScale, LineElement, PointElement, Legend, Tooltip);

export default ChartJS;
