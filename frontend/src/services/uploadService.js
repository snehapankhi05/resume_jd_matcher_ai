import api from "../api/api";

export async function uploadResume(file, onUploadProgress) {

    const formData = new FormData();

    formData.append("file", file);

    const response = await api.post(
        "/upload/resume",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data"
            },

            onUploadProgress: (progressEvent) => {

                const percent = Math.round(
                    (progressEvent.loaded * 100) /
                    progressEvent.total
                );

                onUploadProgress(percent);
            }
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
            headers: {
                "Content-Type": "multipart/form-data"
            },

            onUploadProgress: (progressEvent) => {

                const percent = Math.round(
                    (progressEvent.loaded * 100) /
                    progressEvent.total
                );

                onUploadProgress(percent);
            }
        }
    );

    return response.data;
}