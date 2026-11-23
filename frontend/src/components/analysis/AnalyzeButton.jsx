import { useState } from "react";
import { analyzeResume } from "../../services/analysisService";
import { getErrorMessage } from "../../utils/errors";

function AnalyzeButton({ sessionId, ready, setResults }) {

  const [loading, setLoading] = useState(false);

  async function handleAnalyze() {

    if (!sessionId) {
      alert("Upload Resume first");
      return;
    }

    if (!ready) {
      alert("Upload the Job Description first");
      return;
    }

    try {

      setLoading(true);

      const data = await analyzeResume(sessionId);

      setResults(data);

    } catch (error) {

      alert(getErrorMessage(error, "Analysis Failed"));

    } finally {

      setLoading(false);

    }

  }

  return (
    <button
      onClick={handleAnalyze}
      disabled={loading || !ready}
      className="px-10 py-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold text-lg shadow-lg hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:hover:scale-100"
    >
      {loading ? "Analyzing..." : "🚀 Analyze Resume"}
    </button>
  );
}

export default AnalyzeButton;
