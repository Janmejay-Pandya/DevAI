import React, { useState } from "react";
import { Globe, RefreshCw, ExternalLink } from "lucide-react";

const Preview = () => {
  const [previewUrl, setPreviewtUrl] = useState("https://www.wikipedia.com");

  const handleRefresh = () => {
    const iframe = document.getElementById("preview-iframe");
    if (iframe) {
      iframe.src = previewUrl;
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center p-2">
        <Globe className="mr-2" />
        <div className="flex-grow border rounded px-2 py-1 mr-2">{previewUrl}</div>
        <button onClick={handleRefresh} className="bg-gray-200 p-2 rounded">
          <RefreshCw size={16} />
        </button>
        <a
          href={previewUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="ml-2 p-2 hover:bg-gray-200 rounded"
        >
          <ExternalLink size={16} />
        </a>
      </div>
      <div className="flex-grow overflow-hidden">
        <iframe
          id="preview-iframe"
          src={previewUrl}
          className="w-full h-full border-none"
          title="Website Preview"
        />
      </div>
    </div>
  );
};

export default Preview;
