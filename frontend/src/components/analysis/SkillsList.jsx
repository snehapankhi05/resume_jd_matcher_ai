import { FaCheckCircle, FaTimesCircle } from "react-icons/fa";

function SkillsList({ title, skills, color }) {
  const isGreen = color === "green";

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 min-h-[270px]">

      <h2 className="text-xl font-bold mb-5">
        {title}
      </h2>

      {skills.length === 0 ? (

        <div className="h-[180px] flex flex-col justify-center items-center text-center">

          <div className="text-6xl mb-4">
            🎉
          </div>

          <p className="text-xl font-semibold text-green-600">
            No Missing Skills
          </p>

          <p className="text-gray-500 mt-2">
            Excellent! Your resume matches all required skills.
          </p>

        </div>

      ) : (

        <div className="flex flex-wrap gap-3">

          {skills.map((skill) => (

            <span
              key={skill}
              className={`flex items-center gap-2 px-4 py-2 rounded-full font-medium transition hover:scale-105 ${
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

      )}

    </div>
  );
}

export default SkillsList;