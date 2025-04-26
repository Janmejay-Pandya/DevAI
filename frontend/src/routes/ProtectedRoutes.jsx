import { Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { ACCESS_TOKEN } from "../constants";
import PropTypes from "prop-types";

const ProtectedRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);

  useEffect(() => {
    // Function to check authentication status
    const checkAuth = () => {
      const token = localStorage.getItem(ACCESS_TOKEN);
      setIsAuthenticated(!!token);
    };

    checkAuth();

    // Listen for storage events (like token being added or removed)
    window.addEventListener("storage", checkAuth);

    return () => {
      window.removeEventListener("storage", checkAuth);
    };
  }, []);

  if (isAuthenticated === null) {
    return null;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return children;
};

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

export default ProtectedRoute;
