import axios from "axios";

// Dev calls the local API. A production build uses the same host as the page,
// so one free Render service can serve both the site and the API.
const baseURL =
    import.meta.env.VITE_API_URL ||
    (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");

const api = axios.create({
    baseURL,

    // Analysis runs embeddings + an LLM call, so allow a generous timeout.
    timeout: 120000,
});

export default api;
