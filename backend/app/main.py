from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes.upload import router as upload_router
from backend.app.api.routes.analysis import router as analysis_router
from backend.app.api.routes.jd import router as jd_router

app = FastAPI()
app.include_router(analysis_router)
app.include_router(jd_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)


@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy"
    }