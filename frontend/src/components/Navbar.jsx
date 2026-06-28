import { Link, useLocation } from "react-router-dom";
import { useTheme } from "../services/ThemeContext.jsx";

export default function Navbar() {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  const linkClass = (path) =>
    `nav-link ${location.pathname === path ? "fw-bold text-primary" : ""}`;

  return (
    <nav className="navbar navbar-app navbar-expand-lg px-3 py-2 mb-4">
      <div className="container-fluid">
        <span className="navbar-brand fw-bold">🎭 Emotion Vision</span>
        <div className="d-flex gap-3 align-items-center">
          <Link to="/" className={linkClass("/")}>
            Análise em Tempo Real
          </Link>
          <Link to="/dashboard" className={linkClass("/dashboard")}>
            Dashboard
          </Link>
          <button
            className="btn btn-sm btn-outline-secondary"
            onClick={toggleTheme}
            title="Alternar tema"
          >
            {theme === "light" ? "🌙 Dark" : "☀️ Light"}
          </button>
        </div>
      </div>
    </nav>
  );
}
