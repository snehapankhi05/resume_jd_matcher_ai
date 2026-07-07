import Navbar from "../components/layout/Navbar";
import UploadSection from "../components/upload/UploadSection";
import ProgressTracker from "../components/upload/ProgressTracker";
import Footer from "../components/layout/Footer";

function Home() {
  return (
    <div className="min-h-screen bg-slate-100">

      <Navbar />

      <div className="max-w-7xl mx-auto p-8">

        <ProgressTracker />

        <UploadSection />

      </div>

      <Footer />

    </div>
  );
}

export default Home;