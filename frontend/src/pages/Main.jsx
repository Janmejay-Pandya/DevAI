import { useState, useEffect } from "react";
import Chat from "../components/Main/Chat";
import Preview from "../components/Main/Preview";
import Terminal from "../components/Main/Terminal";

const Main = () => {
  const [rightView, setRightView] = useState("preview");

  useEffect(() => {
    const currentUrl = window.location.href;
    if (currentUrl.includes("/?folder=/tmp/code-environment")) {
      setRightView("code");
    }
  }, []);

  return (
    <div className="flex h-[calc(100vh-58px)]">
      <div className="w-1/2 border-r">
        <Chat />
      </div>

      <div className="w-1/2 flex flex-col">
        {/* Tabs */}
        <div className="flex border-b">
          <button
            onClick={() => setRightView("preview")}
            className={`flex-1 p-2 ${rightView === "preview" ? "bg-gray-300" : ""}`}
          >
            Preview
          </button>
          <button
            onClick={() => setRightView("terminal")}
            className={`flex-1 p-2 ${rightView === "terminal" ? "bg-gray-300" : ""}`}
          >
            Terminal
          </button>
          <button
            onClick={() => setRightView("code")}
            className={`flex-1 p-2 ${rightView === "code" ? "bg-gray-300" : ""}`}
          >
            Code Environment
          </button>
        </div>

        {/* View rendering */}
        <div className="flex-grow relative">
          <div className={`${rightView === "preview" ? "block" : "hidden"} absolute inset-0`}>
            <Preview />
          </div>
          <div className={`${rightView === "terminal" ? "block" : "hidden"} absolute inset-0`}>
            <Terminal />
          </div>
          <div className={`${rightView === "code" ? "block" : "hidden"} absolute inset-0`}>
            <iframe
              src="http://127.0.0.1:8080"
              title="Code Environment"
              sandbox="allow-scripts allow-same-origin"
              className="w-full h-full border-none"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Main;
