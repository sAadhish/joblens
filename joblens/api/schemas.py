from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message :str =  Field(...,min_length=1, max_length=1000)
    session_id:str = Field(...,min_length=1,max_length=100)

    class Config:
        json_schema_extra={
            "example":{
                "message":"What does Sarvam AI do",
                "session_id":"user_123"
            }
        }

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    question_type: str
    iterations_used: int
    session_id: str


class IndexJDRequest(BaseModel):
    """Request to index a job description."""
    company: str = Field(..., min_length=1, max_length=100)
    jd_text: str = Field(..., min_length=10, max_length=10000)


class IndexResponse(BaseModel):
    """Response after indexing."""
    success: bool
    source_label: str
    chunks_indexed: int
    message: str


class CompaniesResponse(BaseModel):
    """List of indexed companies."""
    companies: list[str]
    total: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    qdrant_connected: bool
    total_vectors: int