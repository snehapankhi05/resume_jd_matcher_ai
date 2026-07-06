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

    result = analyze_documents(request.session_id)

    return result