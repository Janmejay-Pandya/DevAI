import { Route, Routes, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import Navbar from "../components/commons/Navbar";
import Main from "../pages/Main";
import Login from "../components/Login/Login";
import { ACCESS_TOKEN } from "../constants";
import PropTypes from "prop-types";

const ProtectedRoute = ({ children }) => {
  const isAuthenticated = !!localStorage.getItem(ACCESS_TOKEN);
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  return children;
};

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

const AppRoutes = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is authenticated on mount and token changes
    const checkAuth = () => {
      const token = localStorage.getItem(ACCESS_TOKEN);
      setIsAuthenticated(!!token);
    };

    checkAuth();

    // Listen for storage events (like token being added or removed)
    window.addEventListener("storage", checkAuth);
    return () => window.removeEventListener("storage", checkAuth);
  }, []);

  return (
    <>
      <Navbar isAuthenticated={isAuthenticated} />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Main />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
};

export default AppRoutes;
