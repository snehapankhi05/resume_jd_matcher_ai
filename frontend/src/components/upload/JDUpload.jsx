import { useState } from "react";
import { uploadJD } from "../../services/uploadService";

function JDUpload({ sessionId }) {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);

  function handleFileChange(e) {
    setFile(e.target.files[0]);
  }

  async function handleUpload() {

    if (!sessionId) {
      alert("Upload Resume first");
      return;
    }

    if (!file) {
      alert("Select a JD");
      return;
    }

    try {

      setLoading(true);

      await uploadJD(
        file,
        sessionId,
        setProgress
      );

      alert("JD Uploaded Successfully");

    } catch (error) {

      alert(error.response?.data?.detail || "Upload Failed");

    } finally {

      setLoading(false);

    }
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">

      <h2 className="text-2xl font-bold mb-5">
        💼 Upload Job Description
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
        className="mt-5 w-full bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg font-semibold"
      >
        {loading ? "Uploading..." : "Upload JD"}
      </button>

    </div>
  );
}

export default JDUpload;