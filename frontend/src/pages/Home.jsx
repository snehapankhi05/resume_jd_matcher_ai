import Navbar from "../../../frontend/src/components/Navbar";
import UploadSection from "../../../frontend/src/components/UploadSection";
import ProgressTracker from "../../../frontend/src/components/ProgressTracker";
import AnalyzeButton from "../../../frontend/src/components/AnalyzeButton";
import ResultsDashboard from "../../../frontend/src/components/ResultsDashboard";

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