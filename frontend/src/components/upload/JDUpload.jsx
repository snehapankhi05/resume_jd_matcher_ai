import { useState } from "react";
import { uploadJD } from "../../services/uploadService";

function JDUpload({ sessionId }) {

  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  function handleFileChange(e) {
    setFile(e.target.files[0]);
    setStatus(null);
  }

  async function handleUpload() {

    if (!sessionId) {
      setStatus({
        type: "error",
        message: "Please upload the resume first."
      });
      return;
    }

    if (!file) {
      setStatus({
        type: "error",
        message: "Please select a Job Description."
      });
      return;
    }

    try {

      setLoading(true);

      await uploadJD(
        file,
        sessionId,
        setProgress
      );

      setStatus({
        type: "success",
        message: "JD uploaded successfully!"
      });

    } catch (error) {

      setStatus({
        type: "error",
        message:
          error.response?.data?.detail ||
          "Upload failed."
      });

    } finally {

      setLoading(false);

    }

  }

  return (

    <div className="bg-white rounded-xl shadow-lg p-6">

      <h2 className="text-2xl font-bold mb-5">
        💼 Upload Job Description
      </h2>

      <label className="block">

  <input
    type="file"
    accept=".pdf"
    onChange={handleFileChange}
    className="hidden"
  />

  <div className="border-2 border-dashed border-green-300 rounded-xl p-8 text-center cursor-pointer hover:border-green-600 hover:bg-green-50 transition">

    <p className="text-4xl">💼</p>

    <p className="mt-3 font-semibold text-gray-700">
      Click to choose a Job Description
    </p>

    <p className="text-sm text-gray-500 mt-1">
      PDF files only
    </p>

  </div>

</label>

      {file && (
  <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-3">

    <p className="font-semibold text-green-700">
      ✅ {file.name}
    </p>

  </div>
)}

      <progress
        value={progress}
        max="100"
        className="w-full mt-4"
      />

      {status && (
        <div
          className={`mt-4 rounded-lg p-3 font-medium ${
            status.type === "success"
              ? "bg-green-100 text-green-700"
              : "bg-red-100 text-red-700"
          }`}
        >
          {status.message}
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={loading}
        className="mt-5 w-full bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg font-semibold disabled:opacity-50"
      >
        {loading ? "Uploading..." : "Upload JD"}
      </button>

    </div>

  );

}

export default JDUpload;