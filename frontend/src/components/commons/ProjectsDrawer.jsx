import React from "react";
import { X, Columns2 } from "lucide-react";
import { Link } from "react-router-dom";
import PropTypes from "prop-types";

const ProjectsDrawer = ({ isOpen, onClose, isDarkMode }) => {
  // Hardcoded list of projects
  const projects = [
    { id: 1, title: "E-commerce Dashboard", lastAccessed: "2 hours ago" },
    { id: 2, title: "Social Media App", lastAccessed: "Yesterday" },
    { id: 3, title: "Task Management Tool", lastAccessed: "3 days ago" },
    { id: 4, title: "Recipe Collection App", lastAccessed: "1 week ago" },
    { id: 5, title: "Personal Portfolio Website", lastAccessed: "2 weeks ago" },
    { id: 6, title: "Fitness Tracker", lastAccessed: "1 month ago" },
  ];

  // Sort projects by recently accessed
  const sortedProjects = [...projects].sort((a, b) => {
    // Simple sort based on "ago" time periods
    const getTimeValue = (time) => {
      if (time.includes("hour")) return 1;
      if (time.includes("Yesterday")) return 2;
      if (time.includes("day")) return 3;
      if (time.includes("week")) return 4;
      return 5;
    };
    return getTimeValue(a.lastAccessed) - getTimeValue(b.lastAccessed);
  });

  return (
    <>
      {/* Overlay */}
      <div
        className={`fixed inset-0 z-40 bg-black bg-opacity-50 transition-opacity duration-300 ${
          isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        }`}
        onClick={onClose}
      />

      {/* Drawer */}
      <div
        className={`fixed z-50 top-0 left-0 h-full w-72 shadow-xl transform transition-transform duration-300 ease-in-out ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        } ${isDarkMode ? "bg-gray-800 text-white" : "bg-white text-gray-800"}`}
      >
        <div className="py-3 px-4">
          <div className="flex items-center mb-4">
            <button
              onClick={onClose}
              className={`px-3 py-1 rounded text-sm font-medium border ${
                isDarkMode
                  ? "border-gray-500 text-gray-300 hover:bg-gray-700"
                  : "border-gray-300 text-gray-600 hover:bg-gray-100"
              }`}
            >
              <Columns2 />
            </button>
            <h2 className="ml-4 text-lg font-medium">My Projects</h2>
          </div>

          {/* Projects List */}
          <div className="space-y-1 mt-2">
            {sortedProjects.map((project) => (
              <Link
                key={project.id}
                to={`/project/${project.id}`}
                className={`block px-3 py-2 rounded-lg ${
                  isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-100"
                }`}
              >
                {project.title}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </>
  );
};

ProjectsDrawer.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  isDarkMode: PropTypes.bool.isRequired,
};

export default ProjectsDrawer;
