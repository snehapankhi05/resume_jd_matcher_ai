import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.app.core.config import settings
from backend.app.rag.pipeline import process_document
from backend.app.utils.document_validator import (
    DocumentValidationError,
    FileTooLargeError,
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

RESUME_PATH = UPLOAD_PATH / "resumes"

RESUME_PATH.mkdir(parents=True, exist_ok=True)


# Plain "def" (not "async def"): saving, PDF parsing and embedding are
# blocking work, and FastAPI runs "def" endpoints in a worker thread so
# they do not freeze the event loop for other requests.
@router.post("/resume")
def upload_resume(
    file: UploadFile = File(...)
):

    # Generate Session ID
    session_id = str(uuid.uuid4())

    # The client's file name is never used in the path (path traversal).
    destination = RESUME_PATH / f"{session_id}.pdf"

    collection_name = "resume_collection"

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

        logger.exception("Resume processing failed")

        destination.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Could not process the resume. Please try again."
        )

    return {
        "success": True,
        "message": "Resume uploaded and processed successfully.",
        "session_id": session_id,
        "collection_name": collection_name,
        "filename": safe_display_name(file.filename),
        "pages_processed": result["pages"],
        "chunks_created": result["chunks"]
    }
