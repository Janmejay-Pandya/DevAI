import {
  Sparkles,
  Code,
  Zap,
  MessageSquare,
  Pencil,
  TestTube,
  Rocket,
  Layers,
  Palette,
  ArrowRight,
} from "lucide-react";
import PropTypes from "prop-types";

const FeatureCard = ({ icon: Icon, title, description, gradient }) => (
  <div className="group relative bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100">
    <div className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${gradient} mb-4`}>
      <Icon className="text-white" size={24} />
    </div>
    <h3 className="text-xl font-semibold text-gray-800 mb-2">{title}</h3>
    <p className="text-gray-600 leading-relaxed">{description}</p>
  </div>
);

const LandingSection = () => {
  const features = [
    {
      icon: Sparkles,
      title: "Ideation to Reality",
      description:
        "Transform your ideas into concrete project plans with intelligent suggestions and architectural guidance.",
      gradient: "from-purple-500 to-indigo-600",
    },
    {
      icon: Palette,
      title: "Design First",
      description:
        "Create wireframes and mockups collaboratively, ensuring your vision is clear before writing a single line of code.",
      gradient: "from-pink-500 to-rose-600",
    },
    {
      icon: Pencil,
      title: "Sketch to Code",
      description:
        "Draw your interface and watch it transform into production-ready code instantly. Your sketches become reality.",
      gradient: "from-orange-500 to-amber-600",
    },
    {
      icon: Code,
      title: "Smart Code Generation",
      description:
        "Write less, build more. Get clean, maintainable code that follows best practices and your project's conventions.",
      gradient: "from-blue-500 to-cyan-600",
    },
    {
      icon: MessageSquare,
      title: "Conversational Development",
      description:
        "No complex commands or interfaces. Just talk naturally about what you want to build and iterate in real-time.",
      gradient: "from-green-500 to-emerald-600",
    },
    {
      icon: TestTube,
      title: "Automated Testing",
      description:
        "Generate comprehensive test cases and catch bugs before they reach production. Quality built in from the start.",
      gradient: "from-teal-500 to-cyan-600",
    },
    {
      icon: Layers,
      title: "End-to-End Support",
      description:
        "From database schema to API endpoints to frontend components—we've got every layer of your stack covered.",
      gradient: "from-indigo-500 to-purple-600",
    },
    {
      icon: Rocket,
      title: "Deploy with Confidence",
      description:
        "Get deployment-ready code with configurations, CI/CD pipelines, and infrastructure recommendations included.",
      gradient: "from-red-500 to-pink-600",
    },
    {
      icon: Zap,
      title: "Interactive & Live",
      description:
        "See changes instantly. Preview components, test APIs, and validate logic without leaving the conversation.",
      gradient: "from-yellow-500 to-orange-600",
    },
  ];

  return (
    <div className="bg-gradient-to-b from-gray-50 to-white py-16 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Your Complete Development Copilot
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            From the first spark of an idea to production deployment, we&apos;re with you every step
            of the way. Build better software faster with an AI partner that truly understands your
            entire development lifecycle.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {features.map((feature, index) => (
            <FeatureCard key={index} {...feature} />
          ))}
        </div>

        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-12 text-center text-white shadow-2xl">
          <h3 className="text-3xl font-bold mb-4">Ready to revolutionize your workflow?</h3>
          <p className="text-lg mb-8 text-indigo-100">
            Join developers who are building faster, smarter, and more collaboratively than ever
            before.
          </p>
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            className="inline-flex items-center gap-2 bg-white text-indigo-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-indigo-50 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            Start Your Project Now
            <ArrowRight size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

FeatureCard.propTypes = {
  icon: PropTypes.elementType.isRequired,
  title: PropTypes.string.isRequired,
  description: PropTypes.string,
  gradient: PropTypes.string,
};

FeatureCard.defaultProps = {
  description: "",
  gradient: "from-gray-100 to-gray-200",
};

export default LandingSection;
