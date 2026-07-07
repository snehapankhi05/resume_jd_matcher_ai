import { useState } from "react";

import ResumeUpload from "./ResumeUpload";
import JDUpload from "./JDUpload";

import AnalyzeButton from "../analysis/AnalyzeButton";
import ResultsDashboard from "../analysis/ResultsDashboard";

function UploadSection() {

  const [sessionId, setSessionId] = useState("");
  const [results, setResults] = useState(null);

  function handleReset() {
    setSessionId("");
    setResults(null);

    // Reload page to clear selected files
    window.location.reload();
  }

  return (
    <>

      <div className="grid md:grid-cols-2 gap-6">

        <ResumeUpload
          onResumeUploaded={setSessionId}
        />

        <JDUpload
          sessionId={sessionId}
        />

      </div>

      <div className="flex justify-center gap-4 mt-8">

        <AnalyzeButton
          sessionId={sessionId}
          setResults={setResults}
        />

        <button
          onClick={handleReset}
          className="px-10 py-4 rounded-xl bg-red-500 hover:bg-red-600 text-white font-bold shadow-lg transition-all duration-300"
        >
          🔄 Reset
        </button>

      </div>

      <div className="mt-10">

        <ResultsDashboard
          results={results}
        />

      </div>

    </>
  );
}

export default UploadSection;