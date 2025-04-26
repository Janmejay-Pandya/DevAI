import { useState, useEffect, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import api from "../../api";
import { API_ENDPOINTS } from "../../constants";
import { setStage } from "../../store/slices/projectSlice";
import { setCurrentChatId } from "../../store/slices/chatSlice";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const currentChatId = useSelector((state) => state.chat.currentChatId);
  const dispatch = useDispatch();

  useEffect(() => {
    const initializeChat = async () => {
      try {
        const savedChatId = localStorage.getItem("currentChatId");

        if (savedChatId) {
          dispatch(setCurrentChatId(savedChatId));
          try {
            const response = await api.get(API_ENDPOINTS.MESSAGES(savedChatId));
            setMessages(
              response.data.map((msg) => ({
                text: msg.content,
                isUser: msg.sender !== "assistant",
              })),
            );
          } catch (err) {
            // If we can't load messages for the saved chat, create a new one
            console.warn("Couldn't load saved chat, creating a new one");
            createNewChat();
          }
        } else {
          // No saved chat, create a new one
          createNewChat();
        }
      } catch (error) {
        console.error("Error initializing chat:", error);
        setError("Could not connect to chat service");
        // Fallback welcome message
        setMessages([{ text: "Hello! How can I assist you today?", isUser: false }]);
      }
    };

    const createNewChat = async () => {
      try {
        const response = await api.post(API_ENDPOINTS.CHATS, {
          title: `Chat ${new Date().toLocaleString()}`,
        });

        dispatch(setCurrentChatId(response.data.id));
        localStorage.setItem("currentChatId", response.data.id);

        // Initialize with welcome message
        setMessages([{ text: "Hello! How can I assist you today?", isUser: false }]);

        // Save welcome message to database
        await api.post(API_ENDPOINTS.MESSAGES(response.data.id), {
          content: "Hello! How can I assist you today?",
          sender: "assistant",
        });
      } catch (err) {
        console.error("Error creating new chat:", err);
        setError("Could not create a new chat");
      }
    };

    initializeChat();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (text) => {
    if (!text.trim()) return;

    // Update UI immediately
    setMessages((prev) => [...prev, { text, isUser: true }]);
    // Clear choices if user manually types
    setMessages((prev) =>
      prev.map((msg) => ({
        ...msg,
        isSeekingApproval: false,
      })),
    );
    setIsLoading(true);

    try {
      // Save user message to database
      await api.post(API_ENDPOINTS.MESSAGES(currentChatId), {
        content: text,
        sender: "user",
      });

      // Show thinking indicator
      setMessages((prev) => [...prev, { text: "Thinking...", isUser: false, isLoading: true }]);

      // Get assistant response
      const response = await api.post(API_ENDPOINTS.ASSISTANT_RESPOND, {
        chat_id: currentChatId,
        message: text,
      });

      // Update messages with assistant response
      setMessages((prev) => {
        const filtered = prev.filter((msg) => !msg.isLoading);
        return [
          ...filtered,
          {
            text: response.data.response,
            isUser: false,
            isSeekingApproval: response.data.is_seeking_approval,
          },
        ];
      });

      // No need to save assistant response as the backend should already do this
    } catch (error) {
      console.error("Error sending message:", error);
      setError("Failed to send message");

      // Show error message
      setMessages((prev) => {
        const filtered = prev.filter((msg) => !msg.isLoading);
        return [
          ...filtered,
          { text: "Sorry, I couldn't process your message. Please try again.", isUser: false },
        ];
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleChoice = async (choiceText) => {
    if (!choiceText.trim()) return;

    // Remove all pending choices immediately
    setMessages((prev) =>
      prev.map((msg) => ({
        ...msg,
        isSeekingApproval: false,
      })),
    );

    setMessages((prev) => [...prev, { text: choiceText, isUser: true }]);
    setIsLoading(true);

    try {
      // Save choice message to database
      await api.post(API_ENDPOINTS.MESSAGES(currentChatId), {
        content: choiceText,
        sender: "user",
      });

      // Show thinking...
      setMessages((prev) => [...prev, { text: "Thinking...", isUser: false, isLoading: true }]);

      // Get assistant's new response
      const response = await api.post(API_ENDPOINTS.ASSISTANT_RESPOND, {
        chat_id: currentChatId,
        message: choiceText,
        is_choice: true,
      });

      if (response.data.project_stage) {
        dispatch(setStage(response.data.project_stage));
      }

      setMessages((prev) => {
        const filtered = prev.filter((msg) => !msg.isLoading);
        return [
          ...filtered,
          {
            text: response.data.response,
            isUser: false,
            isSeekingApproval: response.data.is_seeking_approval,
          },
        ];
      });
    } catch (error) {
      console.error("Error sending choice:", error);
      setError("Failed to process choice");

      setMessages((prev) => {
        const filtered = prev.filter((msg) => !msg.isLoading);
        return [
          ...filtered,
          { text: "Sorry, I couldn't process your choice. Please try again.", isUser: false },
        ];
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-100 mx-auto">
      <div className="flex justify-center items-center p-2 bg-white border-b border-gray-300">
        <div className="font-medium">Project {currentChatId ? `#${currentChatId}` : ""}</div>
      </div>

      {error && (
        <div className="bg-red-100 p-2 text-red-700 text-sm">
          {error}
          <button className="ml-2 text-red-500" onClick={() => setError(null)}>
            ✕
          </button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, index) => (
          <ChatMessage
            key={index}
            text={msg.text}
            isUser={msg.isUser}
            isLoading={msg.isLoading}
            is_choice={msg.isSeekingApproval}
            onChoiceSelect={handleChoice}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
};

export default Chat;
