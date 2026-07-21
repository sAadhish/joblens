from pydantic import BaseModel, Field
from typing import Optional


class DocumentChunk(BaseModel):
    """A single chunk of text with its metadata."""
    text: str
    source_label: str
    chunk_index: int
    char_count: int
    strategy: str = "recursive"


class RetrievedChunk(BaseModel):
    """A chunk returned from vector search, with its relevance score."""
    text: str
    source_label: str
    score: float
    chunk_index: int


class RAGResponse(BaseModel):
    """The final response from a RAG query."""
    question: str
    answer: str
    sources: list[str]
    chunks_used: int
    retrieval_scores: list[float] = Field(default_factory=list)


class IndexingResult(BaseModel):
    """Result of indexing a document."""
    source_label: str
    chunks_indexed: int
    success: bool
    error: Optional[str] = None