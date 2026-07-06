import Navbar from "../components/Navbar";
import UploadSection from "../components/UploadSection";
import ProgressTracker from "../components/ProgressTracker";
import AnalyzeButton from "../components/AnalyzeButton";
import ResultsDashboard from "../components/ResultsDashboard";

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