import { useState } from "react";

function ResumeUpload({ onUploadSuccess }) {
    const [file, setFile] = useState(null);

    function handleFileChange(event) {
        setFile(event.target.files[0]);
    }

    return (
        <div>
            <h3>Upload Resume</h3>

            <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
            />

            {file && (
                <p>{file.name}</p>
            )}

            <button>
                Upload Resume
            </button>
        </div>
    );
}

export default ResumeUpload;