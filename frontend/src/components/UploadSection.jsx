function UploadSection() {
    return (
        <div>
            <h2>Upload Files</h2>
        </div>
    );
}

export default UploadSection;import ResumeUpload from "./ResumeUpload";
import JDUpload from "./JDUpload";

function UploadSection() {
    return (
        <div>

            <ResumeUpload />

            <hr />

            <JDUpload />

        </div>
    );
}

export default UploadSection;