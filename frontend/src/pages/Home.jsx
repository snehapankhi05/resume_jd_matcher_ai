import { useState } from "react";
import Navbar from "../components/layout/Navbar";
import ProgressTracker from "../components/upload/ProgressTracker";
import UploadSection from "../components/upload/UploadSection";
import Footer from "../components/layout/Footer";

function Home() {

  const [sessionId, setSessionId] = useState(null);
  const [results, setResults] = useState(null);

  function handleReset() {
    setSessionId(null);
    setResults(null);
  }

  return (
    <div className="min-h-screen bg-slate-100">

      <Navbar />

      <div className="max-w-7xl mx-auto p-8">

        <ProgressTracker />

        <UploadSection
          sessionId={sessionId}
          setSessionId={setSessionId}
          results={results}
          setResults={setResults}
          onReset={handleReset}
        />

      </div>

      <Footer />

    </div>
  );
}

export default Home;