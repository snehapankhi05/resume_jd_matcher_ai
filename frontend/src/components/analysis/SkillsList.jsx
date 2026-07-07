import { FaCheckCircle, FaTimesCircle } from "react-icons/fa";

function SkillsList({ title, skills, color }) {
  const isGreen = color === "green";

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-bold mb-5">{title}</h2>

      <div className="flex flex-wrap gap-3">
        {skills.map((skill) => (
          <span
            key={skill}
            className={`flex items-center gap-2 px-4 py-2 rounded-full font-medium ${
              isGreen
                ? "bg-green-100 text-green-700"
                : "bg-red-100 text-red-700"
            }`}
          >
            {isGreen ? <FaCheckCircle /> : <FaTimesCircle />}
            {skill}
          </span>
        ))}
      </div>
    </div>
  );
}

export default SkillsList;