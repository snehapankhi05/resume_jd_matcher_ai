from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.app.core.config import settings
from backend.app.rag.pipeline import process_document
from backend.app.utils.document_validator import DocumentValidationError

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

UPLOAD_PATH = Path(settings.UPLOAD_FOLDER)

RESUME_PATH = UPLOAD_PATH / "resumes"

RESUME_PATH.mkdir(parents=True, exist_ok=True)


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...)
):

    # Validate MIME Type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Generate Session ID
    session_id = str(uuid.uuid4())

    # Unique Filename
    filename = f"{session_id}_{file.filename}"

    destination = RESUME_PATH / filename

    # Save File
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    collection_name = "resume_collection"

    try:
        result = process_document(
            file_path=str(destination),
            collection_name=collection_name,
            session_id=session_id
)

    except DocumentValidationError as e:

        if destination.exists():
            destination.unlink()

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        if destination.exists():
            destination.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error : {str(e)}"
        )

    return {
        "success": True,
        "message": "Resume uploaded and processed successfully.",
        "session_id": session_id,
        "collection_name": collection_name,
        "filename": filename,
        "pages_processed": result["pages"],
        "chunks_created": result["chunks"]
    }