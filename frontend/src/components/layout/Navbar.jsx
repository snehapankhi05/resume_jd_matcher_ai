import { FaRobot } from "react-icons/fa";
function Navbar() {
  return (
    <nav className="bg-gradient-to-r from-blue-600 to-indigo-600 shadow-lg">

      <div className="max-w-7xl mx-auto px-8 py-5">

       <h1 className="text-3xl font-bold flex items-center gap-3 text-white">
  <FaRobot />
  Resume ↔ JD Matcher AI
</h1>

        <p className="text-blue-100 mt-2">
          AI Powered ATS Resume Screening & Skill Matching
        </p>

      </div>

    </nav>
  );
}

export default Navbar;