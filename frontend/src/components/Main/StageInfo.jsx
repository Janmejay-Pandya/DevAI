import { useSelector } from "react-redux";
import {
  LightBulbIcon,
  FlagIcon,
  PaintBrushIcon,
  CpuChipIcon,
  CodeBracketIcon,
  BeakerIcon,
  RocketLaunchIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/solid"; // Heroicons package

const stages = [
  { name: "Init", icon: FlagIcon },
  { name: "Ideation", icon: LightBulbIcon },
  { name: "Design", icon: PaintBrushIcon },
  { name: "Tech Stack", icon: CpuChipIcon },
  { name: "Development", icon: CodeBracketIcon },
  { name: "Testing", icon: BeakerIcon },
  { name: "Deployment", icon: RocketLaunchIcon },
  { name: "Complete", icon: CheckCircleIcon },
];

const ProjectStageStrip = () => {
  const currentStage = useSelector((state) => state.project.stage);
  const currentIndex = stages.findIndex((s) => s.name === currentStage);

  return (
    <div className="flex items-center justify-center space-x-4 overflow-x-auto py-2 px-2">
      {stages.map((stage, index) => {
        const Icon = stage.icon;
        const isActive = index === currentIndex;
        const isCompleted = index < currentIndex;

        return (
          <div key={stage.name} className="flex items-center relative group">
            {/* Stage Icon */}
            <div
              className={`p-2 rounded-full transition-colors duration-300
                ${isActive ? "bg-blue-600 text-white" : isCompleted ? "bg-blue-400 text-white" : "bg-gray-200 text-gray-600"}
              `}
            >
              <Icon className="w-6 h-6" />
            </div>

            {/* Tooltip */}
            <span className="absolute bottom-full mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded px-2 py-1 whitespace-nowrap">
              {stage.name}
            </span>

            {/* Connector Line */}
            {index !== stages.length - 1 && (
              <div
                className={`h-1 flex-1 mx-1 rounded-full transition-colors duration-300
                  ${index < currentIndex ? "bg-blue-400" : "bg-gray-300"}
                `}
              />
            )}
          </div>
        );
      })}
    </div>
  );
};

export default ProjectStageStrip;
