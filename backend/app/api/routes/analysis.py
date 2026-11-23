import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.services.analysis_service import analyze_documents
from backend.app.services.context_service import MissingDocumentError
from backend.app.services.llm_service import LLMAnalysisError
from backend.app.utils.document_validator import (
    DocumentValidationError,
    validate_session_id,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


class AnalysisRequest(BaseModel):
    session_id: str


# Plain "def": the analysis does blocking work (embeddings, LLM call) and
# FastAPI runs it in a worker thread instead of blocking the event loop.
@router.post("/")
def analyze(request: AnalysisRequest):

    try:
        session_id = validate_session_id(request.session_id)

        return analyze_documents(session_id)

    except DocumentValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except MissingDocumentError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except LLMAnalysisError:
        raise HTTPException(
            status_code=502,
            detail="The AI analysis service failed. Please try again."
        )

    except Exception:
        logger.exception("Analysis failed")

        raise HTTPException(
            status_code=500,
            detail="Analysis failed. Please try again."
        )
