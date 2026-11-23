import { useState } from "react";
import Navbar from "../components/layout/Navbar";
import ProgressTracker from "../components/upload/ProgressTracker";
import UploadSection from "../components/upload/UploadSection";
import Footer from "../components/layout/Footer";

function Home() {

  const [sessionId, setSessionId] = useState("");
  const [jdUploaded, setJdUploaded] = useState(false);
  const [results, setResults] = useState(null);

  // Changing this key remounts the upload section, which clears the
  // selected files without reloading the whole page.
  const [resetKey, setResetKey] = useState(0);

  function handleResumeUploaded(newSessionId) {
    // A new resume means a new session: the JD and old results no longer apply.
    setSessionId(newSessionId);
    setJdUploaded(false);
    setResults(null);
  }

  function handleReset() {
    setSessionId("");
    setJdUploaded(false);
    setResults(null);
    setResetKey((key) => key + 1);
  }

  return (
    <div className="min-h-screen bg-slate-100">

      <Navbar />

      <div className="max-w-7xl mx-auto p-8">

        <ProgressTracker
          resumeDone={Boolean(sessionId)}
          jdDone={jdUploaded}
          analysisDone={Boolean(results)}
        />

        <UploadSection
          key={resetKey}
          sessionId={sessionId}
          jdUploaded={jdUploaded}
          results={results}
          onResumeUploaded={handleResumeUploaded}
          onJDUploaded={() => setJdUploaded(true)}
          setResults={setResults}
          onReset={handleReset}
        />

      </div>

      <Footer />

    </div>
  );
}

export default Home;
