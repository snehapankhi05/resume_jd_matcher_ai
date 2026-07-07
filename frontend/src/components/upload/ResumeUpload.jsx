import { useState } from "react";
import { uploadResume } from "../../services/uploadService";

function ResumeUpload({ onResumeUploaded }) {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);

  function handleFileChange(e) {
    setFile(e.target.files[0]);
  }

  async function handleUpload() {
    if (!file) {
      alert("Select a resume first");
      return;
    }

    try {
      setLoading(true);

      const response = await uploadResume(file, setProgress);

      onResumeUploaded(response.session_id);

      alert("Resume uploaded successfully");
    } catch (error) {
      alert(error.response?.data?.detail || "Upload Failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">

      <h2 className="text-2xl font-bold mb-5">
        📄 Upload Resume
      </h2>

      <input
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
        className="w-full border rounded-lg p-3"
      />

      {file && (
        <p className="mt-4 text-gray-700">
          {file.name}
        </p>
      )}

      <progress
        value={progress}
        max="100"
        className="w-full mt-4"
      />

      <button
        onClick={handleUpload}
        disabled={loading}
        className="mt-5 w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold"
      >
        {loading ? "Uploading..." : "Upload Resume"}
      </button>

    </div>
  );
}

export default ResumeUpload;