import React, { useState, useEffect } from "react";
import { Moon, Sun, User, LogOut, Settings } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../../constants";

const Navbar = () => {
  const navigate = useNavigate();

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle("dark");
  };

  const handleLogout = () => {
    // Clear tokens from localStorage
    localStorage.removeItem(ACCESS_TOKEN);
    localStorage.removeItem(REFRESH_TOKEN);

    // Update UI state
    setIsLoggedIn(false);
    setShowDropdown(false);

    // Redirect to login page
    navigate("/login");
  };

  return (
    <nav
      className={`w-full py-2 px-4 flex border-b-2 justify-between items-center ${
        isDarkMode ? "bg-gray-800 text-white" : "bg-white text-black"
      }`}
    >
      <div className="flex items-center">
        <Link to="/" className="text-2xl font-bold">
          dev.ai
        </Link>

        {/* Navigation links */}
        <div className="hidden sm:flex sm:ml-6 sm:space-x-8">
          <Link
            to="/"
            className={`border-transparent ${
              isDarkMode ? "text-gray-300 hover:text-white" : "text-gray-500 hover:text-gray-700"
            } hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
          >
            Home
          </Link>
          {isLoggedIn && (
            <Link
              to="/chat"
              className={`border-transparent ${
                isDarkMode ? "text-gray-300 hover:text-white" : "text-gray-500 hover:text-gray-700"
              } hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
            >
              Chat
            </Link>
          )}
        </div>
      </div>

      <div className="relative">
        {isLoggedIn ? (
          <div className="relative">
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className={`p-2 rounded-full ${
                isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-200"
              } cursor-pointer`}
            >
              <User />
            </button>
            {showDropdown && (
              <div
                className={`absolute right-0 mt-2 w-48 rounded-lg shadow-lg ${
                  isDarkMode ? "bg-gray-700" : "bg-white"
                } z-10`}
              >
                <ul className="py-1">
                  <li
                    className={`px-4 py-2 ${
                      isDarkMode ? "hover:bg-gray-600" : "hover:bg-gray-100"
                    } flex items-center cursor-pointer`}
                  >
                    <Settings className="mr-2" size={16} /> Profile
                  </li>
                  <li
                    className={`px-4 py-2 ${
                      isDarkMode ? "hover:bg-gray-600" : "hover:bg-gray-100"
                    } flex items-center cursor-pointer`}
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
                    className={`px-4 py-2 ${
                      isDarkMode ? "hover:bg-gray-600" : "hover:bg-gray-100"
                    } flex items-center cursor-pointer`}
                    onClick={handleLogout}
                  >
                    <LogOut className="mr-2" size={16} /> Logout
                  </li>
                </ul>
              </div>
            )}
          </div>
        ) : (
          <Link
            to="/login"
            className={`px-4 py-2 rounded ${
              isDarkMode
                ? "bg-blue-600 text-white hover:bg-blue-700"
                : "bg-blue-500 text-white hover:bg-blue-600"
            }`}
          >
            Login
          </Link>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
