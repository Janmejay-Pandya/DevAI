import { useState } from "react";
import ChatMesssage from "./ChatMessage";
import ChatInput from "./ChatInput";

const Chat = () => {
  const [messages, setMessages] = useState([
    { text: "Hello! How can I assist you today?", isUser: false },
  ]);

  const handleSend = (text) => {
    setMessages([...messages, { text, isUser: true }]);
    setTimeout(() => {
      setMessages((prev) => [...prev, { text: "Thinking...", isUser: false }]);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-full bg-gray-100 mx-auto">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, index) => (
          <ChatMesssage key={index} text={msg.text} isUser={msg.isUser} />
        ))}
      </div>
      <ChatInput onSend={handleSend} />
    </div>
  );
};

export default Chat;
