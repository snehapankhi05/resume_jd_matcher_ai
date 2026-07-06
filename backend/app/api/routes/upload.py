from pathlib import Path
import shutil
import uuid
from backend.app.rag.pipeline import process_document
from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.app.core.config import settings

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_PATH = Path(settings.UPLOAD_FOLDER)
RESUME_PATH = UPLOAD_PATH / "resumes"

RESUME_PATH.mkdir(parents=True, exist_ok=True)


@router.post("/resume")
async def upload_resume(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    session_id = str(uuid.uuid4())

    filename = f"{session_id}_{file.filename}"

    destination = RESUME_PATH / filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    collection_name = f"{session_id}_resume"

    process_document(
        file_path=str(destination),
        collection_name=collection_name
    )

    return {
        "message": "Resume uploaded successfully.",
        "session_id": session_id,
        "collection_name": collection_name,
        "filename": filename
    }