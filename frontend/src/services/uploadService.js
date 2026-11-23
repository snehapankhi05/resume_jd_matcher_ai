import api from "../api/api";

// Axios sets the multipart Content-Type (including the required boundary)
// automatically for FormData. Setting it by hand removes the boundary.

function reportProgress(progressEvent, onUploadProgress) {

    // `total` is undefined when the browser cannot compute it.
    if (!onUploadProgress || !progressEvent.total) {
        return;
    }

    onUploadProgress(
        Math.round((progressEvent.loaded * 100) / progressEvent.total)
    );
}

export async function uploadResume(file, onUploadProgress) {

    const formData = new FormData();

    formData.append("file", file);

    const response = await api.post(
        "/upload/resume",
        formData,
        {
            onUploadProgress: (progressEvent) =>
                reportProgress(progressEvent, onUploadProgress),
        }
    );

    return response.data;
}


export async function uploadJD(
    file,
    sessionId,
    onUploadProgress
) {

    const formData = new FormData();

    formData.append("file", file);
    formData.append("session_id", sessionId);

    const response = await api.post(
        "/upload/jd",
        formData,
        {
            onUploadProgress: (progressEvent) =>
                reportProgress(progressEvent, onUploadProgress),
        }
    );

    return response.data;
}
