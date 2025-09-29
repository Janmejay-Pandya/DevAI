import { useState } from "react";
import PropTypes from "prop-types";

const ColorPickerInput = ({ onColorSelect, disabled }) => {
  const [selectedPalette, setSelectedPalette] = useState({
    name: "Ocean Blue",
    colors: ["#1e40af", "#3b82f6", "#93c5fd"],
  });

  // Popular color palettes
  const popularPalettes = [
    {
      name: "Ocean Blue",
      colors: ["#1e40af", "#3b82f6", "#93c5fd"],
    },
    {
      name: "Sunset Orange",
      colors: ["#ea580c", "#f97316", "#fed7aa"],
    },
    {
      name: "Forest Green",
      colors: ["#166534", "#22c55e", "#bbf7d0"],
    },
    {
      name: "Royal Purple",
      colors: ["#6b21a8", "#a855f7", "#ddd6fe"],
    },
    {
      name: "Rose Pink",
      colors: ["#be185d", "#ec4899", "#fce7f3"],
    },
    {
      name: "Golden Yellow",
      colors: ["#ca8a04", "#eab308", "#fef3c7"],
    },
    {
      name: "Crimson Red",
      colors: ["#b91c1c", "#ef4444", "#fecaca"],
    },
    {
      name: "Teal Mint",
      colors: ["#0f766e", "#14b8a6", "#ccfbf1"],
    },
    {
      name: "Slate Gray",
      colors: ["#374151", "#6b7280", "#e5e7eb"],
    },
    {
      name: "Emerald",
      colors: ["#047857", "#10b981", "#d1fae5"],
    },
    {
      name: "Indigo",
      colors: ["#4338ca", "#6366f1", "#e0e7ff"],
    },
    {
      name: "Amber",
      colors: ["#d97706", "#f59e0b", "#fef3c7"],
    },
  ];

  // Generate color shades for custom color picker
  const generateShades = (color) => {
    const hexToRgb = (hex) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result
        ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16),
          }
        : null;
    };

    const rgbToHex = (r, g, b) => {
      return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    };

    const lighten = (color, amount) => {
      const rgb = hexToRgb(color);
      if (!rgb) return color;
      return rgbToHex(
        Math.min(255, Math.floor(rgb.r + (255 - rgb.r) * amount)),
        Math.min(255, Math.floor(rgb.g + (255 - rgb.g) * amount)),
        Math.min(255, Math.floor(rgb.b + (255 - rgb.b) * amount)),
      );
    };

    const darken = (color, amount) => {
      const rgb = hexToRgb(color);
      if (!rgb) return color;
      return rgbToHex(
        Math.max(0, Math.floor(rgb.r * (1 - amount))),
        Math.max(0, Math.floor(rgb.g * (1 - amount))),
        Math.max(0, Math.floor(rgb.b * (1 - amount))),
      );
    };

    return [darken(color, 0.3), color, lighten(color, 0.4)];
  };

  const handleCustomColorChange = (colorIndex, newColor) => {
    const newColors = [...selectedPalette.colors];
    newColors[colorIndex] = newColor;

    setSelectedPalette({
      name: "Custom Palette",
      colors: newColors,
    });
  };

  const handlePaletteSelect = (palette) => {
    setSelectedPalette(palette);
  };

  const handlePaletteSubmit = () => {
    if (disabled) return;

    const paletteData = {
      name: selectedPalette.name,
      colors: selectedPalette.colors.map((color) => {
        const hex = color.replace("#", "");
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);

        return {
          hex: color,
          rgb: { r, g, b },
        };
      }),
    };

    const paletteText = `Selected palette: ${selectedPalette.name} - Colors: ${selectedPalette.colors.join(", ")}`;
    onColorSelect({
      text: paletteText,
      palette: paletteData,
    });
  };

  return (
    <div className="border-t border-gray-200 bg-white">
      {/* Header */}
      <div className="flex justify-center py-3 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <span className="text-lg">🎨</span>
          <h3 className="text-lg font-semibold text-gray-800">Choose Color Palette</h3>
        </div>
      </div>

      <div className="flex h-[550px]">
        {/* Left Panel - Custom Palette Creator */}
        <div className="flex-1 flex flex-col justify-center items-center p-6 bg-gradient-to-br from-white to-gray-50">
          <h3 className="text-lg font-semibold text-gray-800 mb-6">Custom Palette</h3>

          {/* Current Palette Preview */}
          <div className="mb-6">
            <div className="flex gap-2 mb-2">
              {selectedPalette.colors.map((color, index) => (
                <div
                  key={index}
                  className="w-16 h-16 rounded-lg border-2 border-gray-300 shadow-sm"
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
            <p className="text-sm text-gray-600 text-center font-medium">{selectedPalette.name}</p>
          </div>

          {/* Color Editors */}
          <div className="space-y-4 w-full max-w-sm">
            {["Primary", "Secondary", "Accent"].map((label, index) => (
              <div key={index} className="flex items-center gap-4">
                <label className="text-sm font-medium text-gray-700 w-20">{label}:</label>
                <input
                  type="color"
                  value={selectedPalette.colors[index]}
                  onChange={(e) => handleCustomColorChange(index, e.target.value)}
                  className="w-12 h-12 rounded-lg border-2 border-gray-300 cursor-pointer"
                />
                <span className="text-xs font-mono text-gray-600">
                  {selectedPalette.colors[index].toUpperCase()}
                </span>
              </div>
            ))}
          </div>

          {/* Generated Shades Preview */}
          <div className="mt-6">
            <p className="text-sm text-gray-600 mb-2 text-center">Color Harmony</p>
            <div className="flex gap-1">
              {generateShades(selectedPalette.colors[0]).map((shade, i) => (
                <div
                  key={i}
                  onClick={() => handleCustomColorChange(0, shade)}
                  className="w-8 h-8 rounded border cursor-pointer hover:scale-110 transition-transform"
                  style={{ backgroundColor: shade }}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Right Panel - Popular Palettes */}
        <div className="w-80 p-6 bg-white shadow-xl border-l flex flex-col">
          <h4 className="text-lg font-semibold mb-4 text-gray-800">Popular Palettes</h4>

          {/* Palette Grid */}
          <div className="flex-1 overflow-y-auto space-y-3 mb-6">
            {popularPalettes.map((palette, index) => (
              <div
                key={index}
                onClick={() => handlePaletteSelect(palette)}
                className={`p-3 rounded-lg border-2 cursor-pointer transition-all  ${
                  selectedPalette.name === palette.name
                    ? "border-gray-800 bg-gray-50 shadow-md"
                    : "border-gray-200 hover:border-gray-400"
                }`}
              >
                <div className="flex gap-2 mb-2">
                  {palette.colors.map((color, colorIndex) => (
                    <div
                      key={colorIndex}
                      className="w-8 h-8 rounded border"
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
                <p className="text-sm font-medium text-gray-800">{palette.name}</p>
                <p className="text-xs text-gray-500">{palette.colors.join(" • ")}</p>
              </div>
            ))}
          </div>

          {/* Palette Info */}
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600">
              <div className="font-medium mb-1">Selected: {selectedPalette.name}</div>
              <div className="space-y-1">
                {selectedPalette.colors.map((color, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded border" style={{ backgroundColor: color }} />
                    <span className="font-mono text-xs">{color.toUpperCase()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <button
            onClick={handlePaletteSubmit}
            disabled={disabled}
            className="w-full py-3 bg-gray-800 text-white rounded-lg hover:brightness-110 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all font-medium"
            style={{
              background: `linear-gradient(135deg, ${selectedPalette.colors[0]}, ${selectedPalette.colors[1]}, ${selectedPalette.colors[2]})`,
            }}
          >
            Select This Palette
          </button>
        </div>
      </div>
    </div>
  );
};

ColorPickerInput.propTypes = {
  onColorSelect: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};

export default ColorPickerInput;
