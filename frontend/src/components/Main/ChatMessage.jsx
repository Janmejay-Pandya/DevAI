import { motion } from "framer-motion";
import { User, Bot } from "lucide-react";
import PropTypes from "prop-types";

const ChatMessage = ({ text, isUser, isLoading = false }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className={`flex ${isUser ? "justify-end" : "justify-start"} mb-2`}
  >
    <div
      className={`flex items-start gap-2 p-3 rounded-lg shadow-sm max-w-xs sm:max-w-sm md:max-w-md lg:max-w-lg
      ${isUser ? "bg-blue-500 text-white" : "bg-white text-gray-800 border border-gray-200"}`}
    >
      <div className={`rounded-full p-1 ${isUser ? "bg-blue-600" : "bg-gray-100"}`}>
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>

      {isLoading ? (
        <div className="flex space-x-2 items-center">
          <div
            className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
            style={{ animationDelay: "0ms" }}
          ></div>
          <div
            className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
            style={{ animationDelay: "300ms" }}
          ></div>
          <div
            className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
            style={{ animationDelay: "600ms" }}
          ></div>
        </div>
      ) : (
        <span className="whitespace-pre-wrap break-words">{text}</span>
      )}
    </div>
  </motion.div>
);

ChatMessage.propTypes = {
  text: PropTypes.string.isRequired,
  isUser: PropTypes.bool.isRequired,
  isLoading: PropTypes.bool,
};

export default ChatMessage;
