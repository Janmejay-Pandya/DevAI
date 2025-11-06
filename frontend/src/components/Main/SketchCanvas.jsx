import { useRef, useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { setPages } from "../../store/slices/projectSlice";
import api from "../../api";
import PropTypes from "prop-types";

export default function SketchCanvas({ open, onClose, fileName }) {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [ctx, setCtx] = useState(null);
  const currentChatId = useSelector((state) => state.chat.currentChatId);
  const pages = useSelector((state) => state.project.pages);
  const dispatch = useDispatch();

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
      const uploadRes = await api.post("/api/upload-sketch/", {
        image: imageData,
        chat_id: currentChatId,
        file_name: fileName,
      });

      const designPath = uploadRes.data.filepath;
      console.log("Response:", designPath);

      // Create updated pages array
      const updatedPages = pages.map((page) =>
        page.name === fileName ? { ...page, design: designPath } : page,
      );

      await api.put(`/api/project/update-development-pages/${currentChatId}/`, updatedPages);

      dispatch(setPages(updatedPages));
      onClose();
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
          <div className="px-3 py-1.5 rounded shadow border bg-gray-800 text-white">Draw Here</div>
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
      </div>
    </div>
  );
}

SketchCanvas.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  fileName: PropTypes.string.isRequired,
};
