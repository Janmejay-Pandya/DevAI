import React, { useState, useEffect } from "react";
import { HexColorPicker } from "react-colorful";
import { useNavigate } from "react-router-dom";
import chroma from "chroma-js";
import axios from "axios";

const ThemePicker = () => {
  const [primaryColor, setPrimaryColor] = useState("#aabbcc");
  const [suggestedColors, setSuggestedColors] = useState([]);
  const [websiteTitle, setWebsiteTitle] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    document.documentElement.style.setProperty("--primary-color", primaryColor);
    localStorage.setItem("theme-color", primaryColor);
  }, [primaryColor]);

  const generateShades = (color) => {
    return chroma
      .scale([chroma(color).darken(2), color, chroma(color).brighten(2)])
      .mode("lab")
      .colors(7);
  };

  const handleSuggestColors = async () => {
    try {
      const response = await axios.post("/api/suggest_colors/", {
        title: websiteTitle,
      });
      setSuggestedColors(response.data.suggestedColors);
    } catch (error) {
      console.error("Error suggesting colors:", error);
    }
  };

  const handleNext = () => {
    localStorage.setItem("selected-colors", JSON.stringify([primaryColor]));
    localStorage.setItem("website-title", websiteTitle);
    navigate("/previewpage");
  };

  return (
    <div className="flex h-screen">
      {/* Left Panel */}
      <div className="flex-1 flex flex-col justify-center items-center p-8 bg-gradient-to-br from-white to-[var(--primary-color)] transition-all">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Pick a Theme</h1>

        <div className="flex flex-wrap justify-center gap-2 mb-6">
          {generateShades(primaryColor).map((shade, i) => (
            <div
              key={i}
              onClick={() => setPrimaryColor(shade)}
              className="w-12 h-12 rounded-full border-2 cursor-pointer"
              style={{ backgroundColor: shade }}
            />
          ))}
        </div>

        <HexColorPicker color={primaryColor} onChange={setPrimaryColor} />

        <p className="mt-4 text-gray-700">
          Current Color: <span className="font-mono">{primaryColor}</span>
        </p>
      </div>

      {/* Right Panel */}
      <div className="w-[350px] p-6 bg-white shadow-xl border-l flex flex-col">
        <h2 className="text-xl font-semibold mb-4">Website Title</h2>

        <input
          type="text"
          placeholder="Enter your website title"
          value={websiteTitle}
          onChange={(e) => setWebsiteTitle(e.target.value)}
          className="border p-2 mb-4 rounded w-full"
        />

        <button
          className="w-full py-2 mb-6 bg-gray-800 text-white rounded-md transition hover:brightness-110"
          onClick={handleSuggestColors}
        >
          Suggest Colors
        </button>

        <div className="flex flex-wrap gap-2 mb-6">
          {suggestedColors.map((color, index) => (
            <div
              key={index}
              onClick={() => setPrimaryColor(color)}
              className="w-10 h-10 rounded-full cursor-pointer border"
              style={{ backgroundColor: color }}
            />
          ))}
        </div>

        {/* Next Button */}
        <button
          className="w-full py-2 mt-auto bg-[var(--primary-color)] text-white rounded-md transition hover:brightness-110"
          onClick={handleNext}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default ThemePicker;
