import React, { useState, useEffect } from "react";
import { Globe, RefreshCw, ExternalLink } from "lucide-react";
import { useDispatch, useSelector } from "react-redux";
import api from "../../api";
import { setPreviewUrl } from "../../store/slices/projectSlice";
import { API_ENDPOINTS } from "../../constants";

const Preview = () => {
  const projectStage = useSelector((state) => state.project.stage);
  const previewUrl = useSelector((state) => state.project.previewUrl);
  const dispatch = useDispatch();
  const currentChatId = useSelector((state) => state.chat.currentChatId);

  useEffect(() => {
    let interval = null;
    console.log(projectStage);

    if (projectStage === "Deploy" || projectStage === "Complete") {
      const fetchPreviewUrl = async () => {
        try {
          const response = await api.get(API_ENDPOINTS.PREVIEW_URL(currentChatId));
          const deployedUrl = response.data.deployed_url;
          if (deployedUrl) {
            dispatch(setPreviewUrl(deployedUrl));
            clearInterval(interval);
          }
        } catch (error) {
          console.error("Error fetching deployed URL:", error);
        }
      };

      interval = setInterval(fetchPreviewUrl, 5000);

      return () => clearInterval(interval);
    }
  }, [projectStage, currentChatId, dispatch]);

  const handleRefresh = () => {
    const iframe = document.getElementById("preview-iframe");
    if (iframe && previewUrl) {
      iframe.src = previewUrl;
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center p-2">
        <Globe className="mr-2" />
        <div className="flex-grow border rounded px-2 py-1 mr-2">
          {previewUrl || "Waiting for deployment..."}
        </div>
        <button
          onClick={handleRefresh}
          disabled={!previewUrl}
          className="bg-gray-200 p-2 rounded disabled:opacity-50"
        >
          <RefreshCw size={16} />
        </button>
        {previewUrl && (
          <a
            href={previewUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-2 p-2 hover:bg-gray-200 rounded"
          >
            <ExternalLink size={16} />
          </a>
        )}
      </div>

      <div className="flex-grow overflow-hidden">
        {previewUrl ? (
          <iframe
            id="preview-iframe"
            src={previewUrl}
            className="w-full h-full border-none"
            title="Website Preview"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-500">
            Preview will be available after deployment.
          </div>
        )}
      </div>
    </div>
  );
};

export default Preview;
