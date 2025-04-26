import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  stage: "ideation",
  previewUrl: null,
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
  },
});

export const { setStage, setPreviewUrl } = projectSlice.actions;
export default projectSlice.reducer;
