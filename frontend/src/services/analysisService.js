import api from "../api/api";

export async function analyzeResume(sessionId) {

    const response = await api.post("/analysis/", {
        session_id: sessionId,
    });

    return response.data;
}