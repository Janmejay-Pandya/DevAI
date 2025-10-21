import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  stage: "Init",
  previewUrl: null,
  pages: [],
};

const projectSlice = createSlice({
  name: "project",
  initialState,
  reducers: {
    setStage: (state, action) => {
      state.stage = action.payload;
    },
    setPreviewUrl: (state, action) => {
      state.previewUrl = action.payload;
    },
    setPages: (state, action) => {
      state.pages = action.payload;
    },
  },
});

export const { setStage, setPreviewUrl, setPages } = projectSlice.actions;
export default projectSlice.reducer;
