import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  currentChatId: null,
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    setCurrentChatId: (state, action) => {
      state.currentChatId = action.payload;
    },
  },
});

export const { setCurrentChatId } = chatSlice.actions;
export default chatSlice.reducer;
