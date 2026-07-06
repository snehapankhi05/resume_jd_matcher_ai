import { useState } from "react";
import { analyzeResume } from "../services/analysisService";

function AnalyzeButton({ sessionId, setResults }) {

    const [loading, setLoading] = useState(false);

    async function handleAnalyze() {

        if (!sessionId) {
            alert("Upload Resume first.");
            return;
        }

        try {

            setLoading(true);

            const data = await analyzeResume(sessionId);

            setResults(data);

        }

        catch (error) {

            console.error(error);

            alert(
                error.response?.data?.detail ||
                "Analysis failed."
            );

        }

        finally {

            setLoading(false);

        }

    }

    return (

        <button
            onClick={handleAnalyze}
            disabled={loading}
        >

            {
                loading
                    ? "Analyzing..."
                    : "Analyze Resume"
            }

        </button>

    );

}

export default AnalyzeButton;