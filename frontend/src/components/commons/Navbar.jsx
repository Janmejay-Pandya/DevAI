import React, { useState } from "react";
import { Moon, Sun, User, LogOut, Settings } from "lucide-react";

const Navbar = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle("dark");
  };

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setShowDropdown(false);
  };

  return (
    <nav
      className={`w-full py-2 px-4 flex border-b-2 justify-between items-center ${
        isDarkMode ? "bg-gray-800 text-white" : "bg-white text-black"
      }`}
    >
      <div className="text-2xl font-bold">dev.ai</div>
      <div className="relative">
        {isLoggedIn ? (
          <div className="relative">
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className="p-2 rounded-full hover:bg-gray-200 cursor-pointer"
            >
              <User />
            </button>
            {showDropdown && (
              <div
                className={`absolute right-0 mt-2 w-48 rounded-lg shadow-lg ${
                  isDarkMode ? "bg-gray-700" : "bg-white"
                }`}
              >
                <ul className="py-1">
                  <li
                    className={`px-4 py-2 hover:bg-gray-100 flex items-center cursor-pointer`}
                    onClick={() => {
                      /* Navigate to profile */
                    }}
                  >
                    <Settings className="mr-2" size={16} /> Profile
                  </li>
                  <li
                    className={`px-4 py-2 hover:bg-gray-100 flex items-center cursor-pointer`}
                    onClick={toggleDarkMode}
                  >
                    {isDarkMode ? (
                      <Sun className="mr-2" size={16} />
                    ) : (
                      <Moon className="mr-2" size={16} />
                    )}
                    {isDarkMode ? "Light Mode" : "Dark Mode"}
                  </li>
                  <li
                    className={`px-4 py-2 hover:bg-gray-100 flex items-center cursor-pointer`}
                    onClick={handleLogout}
                  >
                    <LogOut className="mr-2" size={16} /> Logout
                  </li>
                </ul>
              </div>
            )}
          </div>
        ) : (
          <button
            onClick={handleLogin}
            className={`px-4 py-2 rounded ${
              isDarkMode
                ? "bg-blue-600 text-white hover:bg-blue-700"
                : "bg-blue-500 text-white hover:bg-blue-600"
            }`}
          >
            Login
          </button>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
