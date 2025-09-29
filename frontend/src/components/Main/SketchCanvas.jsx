import { useRef, useEffect, useState } from "react";
import PropTypes from "prop-types";

export default function SketchCanvas({ open, onClose }) {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [ctx, setCtx] = useState(null);
  const [previewHtml, setPreviewHtml] = useState("");
  const [activeTab, setActiveTab] = useState("draw");

  // Initialize and keep canvas sized to its parent (modal content)
  useEffect(() => {
    if (!open) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const parent = canvas.parentElement;

    const initializeContext = () => {
      const context = canvas.getContext("2d");
      context.lineCap = "round";
      context.lineWidth = 2;
      context.strokeStyle = "#000000";
      setCtx(context);
    };

    const setSize = () => {
      if (!parent) return;
      canvas.width = parent.clientWidth;
      canvas.height = parent.clientHeight;
    };

    setSize();
    initializeContext();

    const ro = new ResizeObserver(() => {
      setSize();
    });
    ro.observe(parent);

    const handleKeyDown = (e) => {
      if (e.key === "Escape" && onClose) onClose();
    };
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      ro.disconnect();
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [open, onClose]);

  const startDrawing = (e) => {
    if (!ctx) return;
    ctx.beginPath();
    ctx.moveTo(e.nativeEvent.offsetX, e.nativeEvent.offsetY);
    setIsDrawing(true);
  };

  const handleSubmit = async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const offscreenCanvas = document.createElement("canvas");
    offscreenCanvas.width = canvas.width;
    offscreenCanvas.height = canvas.height;

    const offscreenCtx = offscreenCanvas.getContext("2d");
    offscreenCtx.fillStyle = "#ffffff";
    offscreenCtx.fillRect(0, 0, canvas.width, canvas.height);
    offscreenCtx.drawImage(canvas, 0, 0);

    const imageData = offscreenCanvas.toDataURL("image/png");

    try {
      const res = await fetch("http://localhost:8000/api/upload-sketch/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ image: imageData }),
      });

      const data = await res.json();
      console.log("LLM Response:", data);
      if (data && typeof data.llm_output === "string" && data.llm_output.trim().length > 0) {
        setPreviewHtml(data.llm_output);
        setActiveTab("preview");
      }
    } catch (err) {
      console.error("Error uploading image:", err);
    }
  };

  const draw = (e) => {
    if (!isDrawing || !ctx) return;
    ctx.lineTo(e.nativeEvent.offsetX, e.nativeEvent.offsetY);
    ctx.stroke();
  };

  const stopDrawing = () => {
    if (!ctx) return;
    ctx.closePath();
    setIsDrawing(false);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!ctx || !canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-5xl h-[80vh] bg-white rounded-lg shadow-xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="absolute top-3 left-3 flex gap-2 z-10">
          <button
            className={`px-3 py-1.5 rounded shadow border ${activeTab === "draw" ? "bg-gray-800 text-white" : "bg-white"}`}
            onClick={() => setActiveTab("draw")}
          >
            Draw
          </button>
          <button
            className={`px-3 py-1.5 rounded shadow border ${activeTab === "preview" ? "bg-gray-800 text-white" : "bg-white"}`}
            onClick={() => setActiveTab("preview")}
            disabled={!previewHtml}
          >
            Preview
          </button>
        </div>
        <div className="absolute top-3 right-3 flex gap-2 z-10">
          <button onClick={clearCanvas} className="bg-white border px-3 py-1.5 rounded shadow">
            Clear
          </button>
          <button
            onClick={handleSubmit}
            className="bg-blue-600 text-white px-3 py-1.5 rounded shadow"
          >
            Convert
          </button>
          <button onClick={onClose} className="bg-gray-200 px-3 py-1.5 rounded shadow">
            Close
          </button>
        </div>
        {activeTab === "draw" && (
          <div className="absolute inset-0">
            <canvas
              ref={canvasRef}
              className="w-full h-full cursor-crosshair"
              onMouseDown={startDrawing}
              onMouseMove={draw}
              onMouseUp={stopDrawing}
              onMouseLeave={stopDrawing}
            />
          </div>
        )}
        {activeTab === "preview" && (
          <div className="absolute inset-0 bg-white">
            <iframe
              title="Sketch Preview"
              className="w-full h-full"
              sandbox="allow-scripts allow-forms allow-popups allow-same-origin"
              srcDoc={previewHtml}
            />
          </div>
        )}
      </div>
    </div>
  );
}

SketchCanvas.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};
