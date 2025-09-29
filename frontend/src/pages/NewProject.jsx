import { useState } from "react";
import { Sparkles, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { API_ENDPOINTS } from "../constants";
import { setCurrentChatId } from "../store/slices/chatSlice";
import api from "../api";

const NewProject = () => {
  const [idea, setIdea] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const dispatch = useDispatch();

  const navigate = useNavigate();

  const handleStart = async () => {
    if (!idea.trim()) return;

    setIsLoading(true);
    try {
      createNewProject();
    } catch (error) {
      console.error("Failed to start project:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const createNewProject = async () => {
    try {
      const response = await api.post(API_ENDPOINTS.CHATS, {
        title: idea,
      });

      const chatId = response.data.id;
      localStorage.setItem("currentChatId", chatId);
      dispatch(setCurrentChatId(chatId));

      // Initialize with user request
      //   setMessages([{ text: idea, isUser: true }]);

      navigate("/", {
        state: { initialMessage: "I want to create " + idea },
      });
    } catch (err) {
      console.error("Error creating new project:", err);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleStart();
    }
  };

  return (
    <div className="flex flex-col justify-center items-center h-[calc(100vh-58px)] bg-gradient-to-b from-white to-gray-50 p-6">
      <div className="max-w-lg w-full bg-white rounded-xl shadow-lg p-8 transition-all duration-300 hover:shadow-xl">
        <div className="flex items-center gap-2 mb-6">
          <Sparkles className="text-indigo-500" size={24} />
          <h1 className="text-3xl font-bold text-gray-800">What are we building today?</h1>
        </div>

        <p className="text-gray-600 mb-6">
          Describe your project idea and we&apos;ll help you bring it to life.
        </p>

        <div className="space-y-6">
          <div className="relative">
            <input
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all duration-200"
              placeholder="e.g., A social media app for book lovers"
              autoFocus
            />
          </div>

          <button
            onClick={handleStart}
            disabled={!idea.trim() || isLoading}
            className={`w-full flex items-center justify-center gap-2 py-3 px-6 rounded-lg font-medium transition-all duration-200 ${
              idea.trim() && !isLoading
                ? "bg-indigo-600 hover:bg-indigo-700 text-white"
                : "bg-gray-200 text-gray-500 cursor-not-allowed"
            }`}
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg
                  className="animate-spin h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Processing...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                Start Building
                <ArrowRight size={18} />
              </span>
            )}
          </button>
        </div>

        <div className="mt-6 pt-6 border-t border-gray-100">
          <p className="text-sm text-gray-500">Need inspiration? Try one of these:</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {["A fitness tracking app", "An e-commerce store", "A note taking app"].map(
              (suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setIdea(suggestion)}
                  className="text-sm px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
                >
                  {suggestion}
                </button>
              ),
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewProject;
