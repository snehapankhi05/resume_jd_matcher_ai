import { useState } from "react";

function JDUpload() {
    const [file, setFile] = useState(null);

    function handleFileChange(event) {
        setFile(event.target.files[0]);
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

            <button>
                Upload JD
            </button>
        </div>
    );
}

export default JDUpload;