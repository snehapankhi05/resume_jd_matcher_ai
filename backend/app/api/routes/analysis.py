from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.services.analysis_service import analyze_documents

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


class AnalysisRequest(BaseModel):
    session_id: str


@router.post("/")
async def analyze(request: AnalysisRequest):

    try:
        result = analyze_documents(request.session_id)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )