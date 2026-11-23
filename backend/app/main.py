import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.tracing import setup_tracing

# Must run before any traced code is called (LangSmith caches env lookups).
setup_tracing()

from backend.app.api.routes.upload import router as upload_router
from backend.app.api.routes.analysis import router as analysis_router
from backend.app.api.routes.jd import router as jd_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

app = FastAPI(title="Resume JD Matcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    # No cookies/credentials are used, so they are not enabled.
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(jd_router)
app.include_router(analysis_router)


@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy"
    }
