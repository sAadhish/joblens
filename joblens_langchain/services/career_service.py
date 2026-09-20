# ===================================
# CAREER SERVICE
# JobLens-specific business logic
# Coordinates IngestionService + VectorService + RAGService
# ===================================

from services.injection import IngestionService
from vectorstore.qdrant_service import QdrantService
from services.rag_service import RAGService
from models.schemas import RAGResponse, IndexingResult
from config import Config
import logging
logger = logging.getLogger(__name__)
import tempfile
import os

logger = logging.getLogger(__name__)


class CareerService:
 
    def __init__(self):
        self.ingestion = IngestionService()
        self.vector = QdrantService()
        self.rag = RAGService(self.vector)
        logger.info("CareerService initialized")

    def index_jd(self, jd_text: str, company: str) -> IndexingResult:
        """Index a job description from raw text."""
        source_label = f"{company} JD"
        chunks = self.ingestion.ingest_text(jd_text, source_label)
        return self.vector.index_chunks(chunks)

    def index_resume(self, file_path: str) -> IndexingResult:
        """Index a resume from a PDF file."""
        chunks = self.ingestion.ingest(file_path, "My Resume")
        return self.vector.index_chunks(chunks)

    def ask_about_company(self, company: str, question: str) -> RAGResponse:
        """Ask a question grounded in a specific company's JD."""
        return self.rag.query(
            question=question,
            source_label=f"{company} JD"
        )

    def ask_about_resume(self, question: str) -> RAGResponse:
        """Ask a question grounded in the indexed resume."""
        return self.rag.query(
            question=question,
            source_label="My Resume"
        )

    def general_query(self, question: str) -> RAGResponse:
        """Ask across all indexed documents."""
        return self.rag.query(question=question)

    def collection_stats(self) -> dict:
        """Returns current state of the vector store."""
        return {
            "total_vectors": self.vector.collection_count(),
            "collection": Config.QDRANT_COLLECTION
        }