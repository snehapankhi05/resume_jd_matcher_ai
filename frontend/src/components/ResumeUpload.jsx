import { useState } from "react";
import { uploadResume } from "../services/uploadService";

function ResumeUpload({ onResumeUploaded }) {
    const [file, setFile] = useState(null);
    const [progress, setProgress] = useState(0);
    const [loading, setLoading] = useState(false);

    function handleFileChange(event) {
        setFile(event.target.files[0]);
    }

    async function handleUpload() {

        if (!file) {
            alert("Please select a Resume PDF.");
            return;
        }

        try {

            setLoading(true);

            const response = await uploadResume(
                file,
                setProgress
            );

            onResumeUploaded(response.session_id);

            alert("Resume uploaded successfully!");

        } catch (error) {

            console.error(error);

            alert(
                error.response?.data?.detail ||
                "Resume upload failed."
            );

        } finally {

            setLoading(false);

        }
    }

    return (
        <div>

            <h3>Upload Resume</h3>

            <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
            />

            {file && <p>{file.name}</p>}

            <progress
                value={progress}
                max="100"
            />

            <br /><br />

            <button
                onClick={handleUpload}
                disabled={loading}
            >
                {loading ? "Uploading..." : "Upload Resume"}
            </button>

        </div>
    );
}

export default ResumeUpload;