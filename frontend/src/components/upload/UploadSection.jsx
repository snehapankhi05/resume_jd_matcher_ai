import { useState } from "react";

import ResumeUpload from "./ResumeUpload";
import JDUpload from "./JDUpload";

import AnalyzeButton from "../analysis/AnalyzeButton";
import ResultsDashboard from "../analysis/ResultsDashboard";

function UploadSection() {
  const [sessionId, setSessionId] = useState("");
  const [results, setResults] = useState(null);

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

      <div className="mt-8 text-center">

        <AnalyzeButton
          sessionId={sessionId}
          setResults={setResults}
        />

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