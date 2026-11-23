import ResumeUpload from "./ResumeUpload";
import JDUpload from "./JDUpload";

import AnalyzeButton from "../analysis/AnalyzeButton";
import ResultsDashboard from "../analysis/ResultsDashboard";

function UploadSection({
  sessionId,
  jdUploaded,
  results,
  onResumeUploaded,
  onJDUploaded,
  setResults,
  onReset,
}) {

  return (
    <>

      <div className="grid md:grid-cols-2 gap-6">

        <ResumeUpload
          onResumeUploaded={onResumeUploaded}
        />

        {/* key: uploading a new resume creates a new session, so the JD
            uploader starts fresh for it */}
        <JDUpload
          key={sessionId || "no-session"}
          sessionId={sessionId}
          onJDUploaded={onJDUploaded}
        />

      </div>

      <div className="flex justify-center gap-4 mt-8">

        <AnalyzeButton
          sessionId={sessionId}
          ready={Boolean(sessionId) && jdUploaded}
          setResults={setResults}
        />

        <button
          onClick={onReset}
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
