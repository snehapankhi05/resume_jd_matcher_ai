import { useState } from "react";

import ResumeUpload from "./ResumeUpload";
import JDUpload from "./JDUpload";
import AnalyzeButton from "./AnalyzeButton";
import ResultsDashboard from "./ResultsDashboard";

function UploadSection() {

    const [sessionId, setSessionId] = useState("");
    const [results, setResults] = useState(null);

    return (
        <div>

            <ResumeUpload
                onResumeUploaded={setSessionId}
            />

            <hr />

            <JDUpload
                sessionId={sessionId}
            />

            <hr />

            <AnalyzeButton
                sessionId={sessionId}
                setResults={setResults}
            />

            <hr />

            <ResultsDashboard
                results={results}
            />

        </div>
    );
}

export default UploadSection;