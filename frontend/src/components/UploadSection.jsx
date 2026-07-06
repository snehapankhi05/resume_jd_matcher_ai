import { useState } from "react";

import ResumeUpload from "./ResumeUpload";
import JDUpload from "./JDUpload";

function UploadSection() {

    const [sessionId, setSessionId] = useState("");

    return (

        <div>

            <ResumeUpload
                onResumeUploaded={setSessionId}
            />

            <hr />

            <JDUpload
                sessionId={sessionId}
            />

        </div>

    );
}

export default UploadSection;