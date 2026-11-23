import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",

    // Analysis runs embeddings + an LLM call, so allow a generous timeout.
    timeout: 120000,
});

export default api;
