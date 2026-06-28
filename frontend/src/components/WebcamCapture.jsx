import { useCallback, useEffect, useRef, useState } from "react";
import { analyzeImage } from "../services/api.js";

/**
 * Componente responsável por capturar o vídeo da webcam, desenhar o bounding box
 * do rosto detectado e disparar periodicamente a análise de emoção no backend.
 * @param {object} props
 * @param {(result: object) => void} props.onResult - Callback chamado a cada resultado de análise.
 * @param {number} props.intervalMs - Intervalo entre capturas, em milissegundos.
 */
export default function WebcamCapture({ onResult, intervalMs = 1500 }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const captureCanvasRef = useRef(document.createElement("canvas"));
  const intervalRef = useRef(null);

  const [streamError, setStreamError] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [fps, setFps] = useState(0);
  const lastFrameTimeRef = useRef(performance.now());

  const drawBoundingBox = useCallback((bbox) => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (bbox) {
      ctx.strokeStyle = "#5b6cff";
      ctx.lineWidth = 3;
      ctx.strokeRect(bbox.x, bbox.y, bbox.w, bbox.h);
    }
  }, []);

  const captureAndAnalyze = useCallback(async () => {
    const video = videoRef.current;
    if (!video || video.readyState !== 4) return;

    const canvas = captureCanvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      async (blob) => {
        if (!blob) return;
        setIsAnalyzing(true);
        try {
          const result = await analyzeImage(blob);
          drawBoundingBox(result.bounding_box);

          const now = performance.now();
          const delta = now - lastFrameTimeRef.current;
          lastFrameTimeRef.current = now;
          setFps(delta > 0 ? Math.round(1000 / delta) : 0);

          onResult?.(result);
        } catch (err) {
          console.error("Erro ao analisar frame:", err);
        } finally {
          setIsAnalyzing(false);
        }
      },
      "image/jpeg",
      0.85
    );
  }, [drawBoundingBox, onResult]);

  useEffect(() => {
    let activeStream;

    async function startWebcam() {
      try {
        activeStream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480, facingMode: "user" },
          audio: false,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = activeStream;
        }
      } catch (err) {
        setStreamError(
          "Não foi possível acessar a webcam. Verifique as permissões do navegador."
        );
        console.error(err);
      }
    }

    startWebcam();

    return () => {
      activeStream?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  useEffect(() => {
    intervalRef.current = setInterval(captureAndAnalyze, intervalMs);
    return () => clearInterval(intervalRef.current);
  }, [captureAndAnalyze, intervalMs]);

  return (
    <div>
      {streamError && <div className="alert alert-danger">{streamError}</div>}
      <div className="webcam-wrapper">
        <video ref={videoRef} className="webcam-video" autoPlay playsInline muted />
        <canvas ref={canvasRef} className="webcam-canvas" />
      </div>
      <div className="d-flex justify-content-between mt-2 text-muted-app small">
        <span>{isAnalyzing ? "Analisando frame..." : "Aguardando próximo frame"}</span>
        <span>~{fps} FPS (captura)</span>
      </div>
    </div>
  );
}
