from pathlib import Path
import shutil

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.app.core.config import settings
from backend.app.rag.pipeline import process_document
from backend.app.utils.document_validator import DocumentValidationError

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

UPLOAD_PATH = Path(settings.UPLOAD_FOLDER)
JD_PATH = UPLOAD_PATH / "jds"

JD_PATH.mkdir(parents=True, exist_ok=True)


@router.post("/jd")
async def upload_jd(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    filename = f"{session_id}_{file.filename}"

    destination = JD_PATH / filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    collection_name = f"{session_id}_jd"

    try:

        result = process_document(
            file_path=str(destination),
            collection_name=collection_name
        )

    except DocumentValidationError as e:

        if destination.exists():
            destination.unlink()

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "success": True,
        "message": "JD uploaded successfully.",
        "collection_name": collection_name,
        "pages_processed": result["pages"],
        "chunks_created": result["chunks"]
    }