import React from "react";
import { motion } from "framer-motion";
import { Bot, Pencil, PlusCircle } from "lucide-react";
import PropTypes from "prop-types";

const DevelopmentPagesList = ({ pages, onAddDesign, onEditDetails }) => {
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
