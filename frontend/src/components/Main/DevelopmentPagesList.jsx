import React from "react";
import { motion } from "framer-motion";
import { Bot, Pencil, PlusCircle, Trash2 } from "lucide-react";
import PropTypes from "prop-types";
import { useDispatch, useSelector } from "react-redux";
import { setPages } from "../../store/slices/projectSlice";
import api from "../../api";

const DevelopmentPagesList = ({ pages, onAddDesign, onEditDetails }) => {
  const dispatch = useDispatch();
  const currentChatId = useSelector((state) => state.chat.currentChatId);

  const handleDelete = async (pageName) => {
    const confirm = window.confirm(`Delete page "${pageName}"? This cannot be undone.`);
    if (!confirm) return;

    try {
      const updatedPages = pages.filter((p) => p.name !== pageName);

      // persist to backend
      if (currentChatId) {
        await api.put(`/api/project/update-development-pages/${currentChatId}/`, updatedPages);
      }

      // update local store
      dispatch(setPages(updatedPages));
    } catch (err) {
      console.error("Failed to delete page:", err);
      // optionally notify user
      alert("Failed to delete page. See console for details.");
    }
  };
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex justify-start mb-2"
    >
      <div className="flex items-start gap-2 p-3 rounded-lg shadow-sm w-full max-w-lg bg-white text-gray-800 border border-gray-200">
        {/* Bot Icon */}
        <div className="rounded-full p-1 bg-gray-100">
          <Bot size={16} />
        </div>

        {/* Pages List */}
        <div className="flex flex-col gap-2 w-full">
          <div className="font-medium text-gray-900">Pages to be built:</div>

          <ul className="flex flex-col gap-2">
            {pages.map((page, index) => (
              <li
                key={index}
                className="flex justify-between gap-2 items-center bg-gray-50 px-3 py-2 rounded-md border border-gray-200"
              >
                <div>
                  <div className="font-medium text-gray-800">{page.name}</div>
                  {page.description && (
                    <div className="text-sm text-gray-600">{page.description}</div>
                  )}
                </div>

                <div className="flex gap-1 shrink-0">
                  <button
                    disabled={!!page.design}
                    onClick={() => !page.design && onAddDesign(page.name)}
                    className={`flex items-center gap-1 text-xs px-2 py-2 rounded-md ${
                      page.design
                        ? "bg-gray-200 text-gray-500 cursor-not-allowed"
                        : "bg-green-100 hover:bg-green-200 text-green-800"
                    }`}
                  >
                    {page.design ? (
                      <>Uploaded</>
                    ) : (
                      <>
                        <PlusCircle size={14} /> Add UI
                      </>
                    )}
                  </button>

                  <button
                    onClick={() => onEditDetails(page.name)}
                    className="flex items-center gap-1 text-xs px-2 py-1 rounded-md bg-blue-100 hover:bg-blue-200 text-blue-800"
                  >
                    <Pencil size={14} /> Edit
                  </button>
                  <button
                    onClick={() => handleDelete(page.name)}
                    className="flex items-center gap-1 text-xs px-2 py-1 rounded-md bg-red-100 hover:bg-red-200 text-red-800"
                  >
                    <Trash2 size={14} /> Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </motion.div>
  );
};

DevelopmentPagesList.propTypes = {
  pages: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      description: PropTypes.string,
    }),
  ).isRequired,
  onAddDesign: PropTypes.func.isRequired,
  onEditDetails: PropTypes.func.isRequired,
};

export default DevelopmentPagesList;
