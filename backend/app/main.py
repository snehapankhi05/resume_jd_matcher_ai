import logging
import threading

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.app.core.config import PROJECT_ROOT, settings
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

DIST = PROJECT_ROOT / "frontend" / "dist"


def _warm_embedding_model() -> None:
    """Load MiniLM after the port is open, so the first upload is not the one that pays for it."""
    try:
        from backend.app.rag.embeddings import get_embedding_model
        get_embedding_model()
    except Exception:
        logging.getLogger(__name__).exception("Embedding model failed to load")


@app.on_event("startup")
def warm_model():
    threading.Thread(target=_warm_embedding_model, daemon=True).start()


@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy"
    }


def _frontend_file(full_path: str):
    if not DIST.exists():
        raise HTTPException(status_code=404, detail="Frontend build not found.")

    if full_path:
        candidate = (DIST / full_path).resolve()
        try:
            candidate.relative_to(DIST.resolve())
        except ValueError:
            raise HTTPException(status_code=404, detail="Not found.")
        if candidate.is_file():
            return FileResponse(candidate)

    index = DIST / "index.html"
    if index.is_file():
        return FileResponse(index)
    raise HTTPException(status_code=404, detail="Frontend build not found.")


@app.get("/")
def frontend_index():
    return _frontend_file("")


@app.get("/{full_path:path}")
def frontend(full_path: str):
    return _frontend_file(full_path)
