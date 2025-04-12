export const ACCESS_TOKEN = "access";
export const REFRESH_TOKEN = "refresh";

export const API_ENDPOINTS = {
  CHATS: "/api/chat/chats/",
  MESSAGES: (chatId) => `/api/chat/chats/${chatId}/messages/`,
  ASSISTANT_RESPOND: "/api/chat/assistant/respond/",
  LOGIN: "/api/token/",
  REGISTER: "/api/user/register/",
  REFRESH: "/api/token/refresh/",
  USER: "/api/auth/user/",
};
