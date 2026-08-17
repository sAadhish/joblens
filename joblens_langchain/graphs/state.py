from typing import TypedDict,Optional

class RAGState(TypedDict):
    question: str
    source_label: Optional[str]
    retrieved_chunks: list
    retrieval_scores: list
    answer: str
    sources: list
    chunks_used: int
    error: Optional[str]
    original_question: str    
    reformulated_question: str  
    answer_quality: str    
    iteration_count: int   
    max_iterations: int  


