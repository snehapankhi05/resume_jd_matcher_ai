from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Resume JD Matcher API",
    version="1.0.0",
    description="Backend API for Resume-JD Matching using Hybrid RAG"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React (Vite) frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {
        "status": "success",
        "message": "Backend is running successfully 🚀"
    }