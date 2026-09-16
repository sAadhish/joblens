from fastapi import APIRouter, UploadFile, File, HTTPException
from api.schemas import IndexJDRequest, IndexResponse
from joblens_langchain.services.career_service import CareerService
import tempfile
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

_service = None
def get_service():
    global _service
    if _service is None:
        _service = CareerService()
    return _service


@router.post("/index/jd", response_model=IndexResponse)
async def index_jd(request: IndexJDRequest):
    """Index a job description from text."""
    try:
        service = get_service()
        result = service.index_jd(request.jd_text, request.company)
        return IndexResponse(
            success=result.success,
            source_label=result.source_label,
            chunks_indexed=result.chunks_indexed,
            message="JD indexed successfully" if result.success else result.error
        )
    except Exception as e:
        logger.error(f"Index JD failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/resume", response_model=IndexResponse)
async def index_resume(file: UploadFile = File(...)):
    """Index a resume PDF by uploading the file."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        service = get_service()

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = service.index_resume(tmp_path)
        os.remove(tmp_path)

        return IndexResponse(
            success=result.success,
            source_label=result.source_label,
            chunks_indexed=result.chunks_indexed,
            message="Resume indexed successfully" if result.success else result.error
        )
    except Exception as e:
        logger.error(f"Index resume failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))