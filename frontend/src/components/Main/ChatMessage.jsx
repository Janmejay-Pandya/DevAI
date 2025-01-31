import { motion } from "framer-motion";
import { User, Bot } from "lucide-react";

import PropTypes from "prop-types";

const ChatMessage = ({ text, isUser }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className={`flex ${isUser ? "justify-end" : "justify-start"} mb-2`}
  >
    <div
      className={`flex items-center gap-2 p-3 rounded-2xl shadow-md max-w-xs sm:max-w-sm md:max-w-md lg:max-w-lg
      ${isUser ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-900"}`}
    >
      {isUser ? <User size={18} /> : <Bot size={18} />}
      <span>{text}</span>
    </div>
  </motion.div>
);

ChatMessage.propTypes = {
  text: PropTypes.string.isRequired,
  isUser: PropTypes.bool.isRequired,
};

export default ChatMessage;
