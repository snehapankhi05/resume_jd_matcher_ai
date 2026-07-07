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
      className="bg-indigo-600 hover:bg-indigo-700 text-white px-10 py-4 rounded-xl text-xl font-bold shadow-lg"
    >
      {loading ? "Analyzing..." : "🚀 Analyze Resume"}
    </button>
  );
}

export default AnalyzeButton;