from typing import Annotated , TypedDict ,Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

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


class ConversationState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]
    chat_history: list                    
    question: str
    source_label: Optional[str]
    retrieved_chunks: Annotated[list, lambda x, y: y]  # replace, not accumulate
    chunk_sources: Annotated[list, lambda x, y: y]
    sources: Annotated[list, lambda x, y: y]
    chunks_used: int
    answer: str
    error: Optional[str]


class AgentState(TypedDict):
    #converstion memory
    messages: Annotated[list[BaseMessage],add_messages]
    chat_history:list

    # Current turn inputs
    question: str
    source_label: Optional[str]

    # Classification result
    question_type: str          # "jd", "resume", "comparison", "general"
    classified_company: str     # extracted company name if question is about a JD

     # Retrieval results
    retrieved_chunks: Annotated[list, lambda x, y: y]
    chunk_sources: Annotated[list, lambda x, y: y]
    sources: Annotated[list, lambda x, y: y]
    chunks_used: int

    # Generation results
    answer: str
    answer_quality: str

    # Self-correction
    original_question: str
    reformulated_question: str
    iteration_count: int
    max_iterations: int

    error: Optional[str]




