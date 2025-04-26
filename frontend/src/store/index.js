import { configureStore } from "@reduxjs/toolkit";
import projectReducer from "./slices/projectSlice";
import chatReducer from "./slices/chatSlice";

export const store = configureStore({
  reducer: {
    project: projectReducer,
    chat: chatReducer,
  },
});
