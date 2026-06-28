import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

/**
 * Envia um frame (Blob) capturado da webcam para análise de emoção no backend.
 * @param {Blob} imageBlob - Frame JPEG capturado do canvas.
 * @returns {Promise<object>} Resultado da análise (emoção, confiança, bbox, métricas).
 */
export async function analyzeImage(imageBlob) {
  const formData = new FormData();
  formData.append("file", imageBlob, "frame.jpg");
  const { data } = await api.post("/analyze-image", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

/**
 * Busca estatísticas agregadas para o dashboard.
 * @param {{start?: string, end?: string}} filters
 */
export async function fetchStatistics(filters = {}) {
  const { data } = await api.get("/statistics", { params: filters });
  return data;
}

/**
 * Busca histórico paginado de análises.
 * @param {{page?: number, page_size?: number, start?: string, end?: string, emotion?: string}} params
 */
export async function fetchHistory(params = {}) {
  const { data } = await api.get("/history", { params });
  return data;
}

/**
 * Retorna a URL de exportação CSV (usada diretamente em um link de download).
 * @param {{start?: string, end?: string, emotion?: string}} filters
 */
export function getExportCsvUrl(filters = {}) {
  const params = new URLSearchParams(filters).toString();
  return `${API_BASE_URL}/history/export${params ? `?${params}` : ""}`;
}

export async function checkHealth() {
  const { data } = await api.get("/health");
  return data;
}
