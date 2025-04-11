import { useState, useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import axios from "axios";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentChatId, setCurrentChatId] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const initializeChat = async () => {
      try {
        const savedChatId = localStorage.getItem("currentChatId");

        if (savedChatId) {
          setCurrentChatId(savedChatId);
          const response = await axios.get(`/api/chats/${savedChatId}/messages/`);
          setMessages(
            response.data.map((msg) => ({
              text: msg.content,
              isUser: msg.sender === "user",
            })),
          );
        } else {
          // creating a new chat here
          const response = await axios.post("/api/chats/", {
            title: `Chat ${new Date().toLocaleString()}`,
          });
          setCurrentChatId(response.data.id);
          localStorage.setItem("currentChatId", response.data.id);

          setMessages([{ text: "Hello! How can I assist you today?", isUser: false }]);
        }
      } catch (error) {
        console.error("Error initializing chat:", error);
        //in case API call fails
        setMessages([{ text: "Hello! How can I assist you today?", isUser: false }]);
      }
    };

    initializeChat();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (text) => {
    setMessages((prev) => [...prev, { text, isUser: true }]);
    setIsLoading(true);

    try {
      await axios.post(`/api/chats/${currentChatId}/messages/`, {
        content: text,
        sender: "user",
      });

      setMessages((prev) => [...prev, { text: "Thinking...", isUser: false, isLoading: true }]);

      const response = await axios.post("/api/assistant/respond/", {
        chat_id: currentChatId,
        message: text,
      });

      setMessages((prev) => {
        const filtered = prev.filter((msg) => !msg.isLoading);
        return [...filtered, { text: response.data.response, isUser: false }];
      });
    } catch (error) {
      console.error("Error sending message:", error);
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

  return (
    <div className="flex flex-col h-full bg-gray-100 mx-auto">
      <div className="p-2 bg-white border-b border-gray-300 font-medium text-center">
        Chat {currentChatId ? `#${currentChatId}` : ""}
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, index) => (
          <ChatMessage key={index} text={msg.text} isUser={msg.isUser} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
};

export default Chat;
