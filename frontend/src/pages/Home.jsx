import Navbar from "../components/layout/Navbar";
import UploadSection from "../components/upload/UploadSection";

function Home() {
  return (
    <div className="min-h-screen bg-slate-100">
      <Navbar />

      <div className="max-w-7xl mx-auto p-8">
        <UploadSection />
      </div>
    </div>
  );
}

export default Home;