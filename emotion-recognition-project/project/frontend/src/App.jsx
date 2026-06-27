import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Home from "./pages/Home.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import { ThemeProvider } from "./services/ThemeContext.jsx";

export default function App() {
  return (
    <ThemeProvider>
      <Navbar />
      <main className="pb-5">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </main>
    </ThemeProvider>
  );
}
