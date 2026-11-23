import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.app.core.config import settings
from backend.app.rag.pipeline import process_document
from backend.app.rag.vectordb import session_has_documents
from backend.app.utils.document_validator import (
    DocumentValidationError,
    FileTooLargeError,
    validate_session_id,
)
from backend.app.utils.uploads import (
    safe_display_name,
    save_pdf_upload,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

UPLOAD_PATH = Path(settings.UPLOAD_FOLDER)
JD_PATH = UPLOAD_PATH / "jds"

JD_PATH.mkdir(parents=True, exist_ok=True)


@router.post("/jd")
def upload_jd(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):

    try:
        session_id = validate_session_id(session_id)
    except DocumentValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # A JD only makes sense for a session that already has a resume.
    if not session_has_documents("resume_collection", session_id):
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please upload the resume first."
        )

    # The client's file name is never used in the path (path traversal).
    destination = JD_PATH / f"{session_id}.pdf"

    collection_name = "jd_collection"

    try:
        save_pdf_upload(file, destination, settings.MAX_FILE_SIZE_MB)

        result = process_document(
            file_path=str(destination),
            collection_name=collection_name,
            session_id=session_id
        )

    except FileTooLargeError as e:

        raise HTTPException(
            status_code=413,
            detail=str(e)
        )

    except DocumentValidationError as e:

        destination.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:

        logger.exception("JD processing failed")

        destination.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Could not process the job description. Please try again."
        )

    return {
        "success": True,
        "message": "JD uploaded successfully.",
        "collection_name": collection_name,
        "filename": safe_display_name(file.filename),
        "pages_processed": result["pages"],
        "chunks_created": result["chunks"]
    }
