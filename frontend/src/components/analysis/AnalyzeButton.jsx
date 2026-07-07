import { useState } from "react";
import { analyzeResume } from "../../services/analysisService";

function AnalyzeButton({ sessionId, setResults }) {

  const [loading, setLoading] = useState(false);

  async function handleAnalyze() {

    if (!sessionId) {
      alert("Upload Resume first");
      return;
    }

    try {

      setLoading(true);

      const data = await analyzeResume(sessionId);

      setResults(data);

    } catch (error) {

      alert(error.response?.data?.detail || "Analysis Failed");

    } finally {

      setLoading(false);

    }

  }

  return (
    <button
  onClick={handleAnalyze}
  disabled={loading}
  className="px-10 py-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold text-lg shadow-lg hover:scale-105 transition-all duration-300 disabled:opacity-50"
>
  {loading ? "Analyzing..." : "🚀 Analyze Resume"}
</button>
  );
}

export default AnalyzeButton;