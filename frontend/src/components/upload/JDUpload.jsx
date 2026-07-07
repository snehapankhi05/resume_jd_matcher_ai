import { useState } from "react";
import { uploadJD } from "../../services/uploadService";

function JDUpload({ sessionId }) {

    const [file, setFile] = useState(null);
    const [progress, setProgress] = useState(0);
    const [loading, setLoading] = useState(false);

    function handleFileChange(event) {
        setFile(event.target.files[0]);
    }

    async function handleUpload() {

        if (!sessionId) {
            alert("Please upload Resume first.");
            return;
        }

        if (!file) {
            alert("Please select a JD PDF.");
            return;
        }

        try {

            setLoading(true);

            await uploadJD(
                file,
                sessionId,
                setProgress
            );

            alert("Job Description uploaded successfully!");

        } catch (error) {

            console.error(error);

            alert(
                error.response?.data?.detail ||
                "JD upload failed."
            );

        } finally {

            setLoading(false);

        }
    }

    return (

        <div>

            <h3>Upload Job Description</h3>

            <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
            />

            {file && (
                <p>{file.name}</p>
            )}

            <progress
                value={progress}
                max="100"
            />

            <br /><br />

            <button
                onClick={handleUpload}
                disabled={loading}
            >
                {loading ? "Uploading..." : "Upload JD"}
            </button>

        </div>

    );
}

export default JDUpload;