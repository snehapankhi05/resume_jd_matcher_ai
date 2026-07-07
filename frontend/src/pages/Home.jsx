import Navbar from "../../../frontend/src/components/Navbar";
import UploadSection from "../components/upload/UploadSection";
import ProgressTracker from "../../../frontend/src/components/ProgressTracker";
import AnalyzeButton from "../components/analysis/AnalyzeButton";
import ResultsDashboard from "../components/analysis/ResultsDashboard";

function Home() {
    return (
        <>
            <Navbar />

            <ProgressTracker />

            <UploadSection />

            <AnalyzeButton />

            <ResultsDashboard />
        </>
    );
}

export default Home;