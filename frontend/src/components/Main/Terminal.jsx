import React, { useState, useEffect, useRef } from "react";
import { Terminal as TerminalIcon } from "lucide-react";

const Terminal = () => {
  const [logs, setLogs] = useState([]);
  const terminalRef = useRef(null);

  useEffect(() => {
    const simulateLogs = [
      { type: "info", message: "Initializing application..." },
      { type: "success", message: "Database connection established" },
      { type: "warning", message: "Potential performance bottleneck detected" },
      { type: "error", message: "Failed to load configuration file" },
      { type: "info", message: "Starting background services..." },
      { type: "success", message: "All services initialized successfully" },
    ];

    simulateLogs.forEach((log, index) => {
      setTimeout(() => {
        setLogs((prevLogs) => [...prevLogs, log]);
      }, (index + 1) * 1000);
    });
  }, []);

  const getLogColor = (type) => {
    switch (type) {
      case "error":
        return "text-red-500";
      case "warning":
        return "text-yellow-500";
      case "success":
        return "text-green-500";
      default:
        return "text-white";
    }
  };

  return (
    <div className="overflow-auto h-full">
      <div className="bg-black h-full shadow-lg p-4">
        <div className="flex items-center mb-2">
          <TerminalIcon className="mr-2 text-green-500" />
          <h2 className="text-white font-mono">Server Logs</h2>
        </div>
        <div
          ref={terminalRef}
          className="bg-gray-900 p-3 rounded font-mono text-sm h-[calc(100%-40px)] overflow-y-auto"
        >
          {logs.map((log, index) => (
            <div key={index} className={`${getLogColor(log.type)} mb-1`}>
              <span className="mr-2 text-gray-500">[{new Date().toLocaleTimeString()}]</span>
              {log.message}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Terminal;
