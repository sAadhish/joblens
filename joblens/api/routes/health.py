from fastapi import APIRouter
from api.schemas import HealthResponse, CompaniesResponse
from joblens_langchain.services.career_service import CareerService
from qdrant_client import QdrantClient
from joblens_langchain.config import Config
from api.cache import response_cache
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

_service = None
def get_service():
    global _service
    if _service is None:
        _service= CareerService()
    return _service


@router.get("/health",response_model=HealthResponse)
async def health_check():
    try:
        client = QdrantClient(url=Config.QDRANT_URL, api_key=Config.QDRANT_API_KEY)
        count = client.count( collection_name=Config.QDRANT_COLLECTION).count
        cache_stats = response_cache.stats()
        logger.info(f"Cache stats: {cache_stats}")
        return HealthResponse(
            status="healthy",
            qdrant_connected=True,
            total_vectors=count
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="degraded",
            qdrant_connected=False,
            total_vectors=0
        )

    

@router.get("/companies", response_model=CompaniesResponse)
async def list_companies():
    try:
        client = QdrantClient(url=Config.QDRANT_URL, api_key=Config.QDRANT_API_KEY)
        results = client.scroll(
            collection_name=Config.QDRANT_COLLECTION,
            limit=100,
            with_payload=True
        )
        companies = set()
        for point in results[0]:
            label = point.payload.get("metadata", {}).get("source_label", "")
            if label.endswith(" JD"):
                companies.add(label.replace(" JD", ""))

        return CompaniesResponse(
            companies=sorted(companies),
            total=len(companies)
        )
    except Exception as e:
        logger.error(f"List companies failed: {e}")
        return CompaniesResponse(companies=[], total=0)
    

from joblens_langchain.prompts.registry import list_prompts

@router.get("/prompts")
async def get_prompt_versions():
    """List all prompt versions currently deployed."""
    return {"prompts": list_prompts()}