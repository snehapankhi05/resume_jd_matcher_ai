import { FaLightbulb, FaCheckCircle, FaExclamationTriangle } from "react-icons/fa";

function SummaryCard({ title, items }) {

  let Icon = FaLightbulb;

  if (title === "Strengths") Icon = FaCheckCircle;
  if (title === "Weaknesses") Icon = FaExclamationTriangle;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">

      <h2 className="flex items-center gap-3 text-xl font-bold mb-4">
        <Icon />
        {title}
      </h2>

      <ul className="space-y-3">
        {items.map((item, index) => (
          <li key={index} className="text-gray-700">
            • {item}
          </li>
        ))}
      </ul>

    </div>
  );
}

export default SummaryCard;