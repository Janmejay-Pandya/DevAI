import React, { useState, useEffect, useRef } from "react";
import { Terminal as TerminalIcon } from "lucide-react";

const Terminal = () => {
  const [logs, setLogs] = useState([]);
  const terminalRef = useRef(null);
  const websocketRef = useRef(null);

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL.replace(/^http/, "ws");
    const socket = new WebSocket(`${apiUrl}/ws/terminal/`);
    websocketRef.current = socket;

    socket.onopen = () => {
      console.log("Connected to terminal websocket");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const { time, type, category, message } = data;
      console.log("recieved");

      setLogs((prevLogs) => [...prevLogs, { time, type, category, message }]);
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    socket.onclose = (event) => {
      console.log("WebSocket closed:", event.reason);
    };

    return () => {
      socket.close();
    };
  }, []);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  const getLogColor = (type) => {
    switch (type) {
      case "error":
        return "text-red-500";
      case "warning":
        return "text-yellow-500";
      case "success":
        return "text-green-500";
      case "progress":
        return "text-blue-400";
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
              <span className="mr-2 text-gray-500">[{log.time}]</span>
              {log.category}: {log.message}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Terminal;
