from dotenv import load_dotenv
import os
load_dotenv()
class Config:
    # LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str= "openai/gpt-oss-120b"
    LLM_TEMPERATURE: float = 0.0

    # Embeddings
    EMBEDDING_MODEL: str ="all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Qdrant
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "joblens_lite")

    # Chunking
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100

    # Retrieval
    RETRIEVAL_TOP_K: int = 5
    RERANK_TOP_K: int = 3
    MIN_SIMILARITY: float = 0.3

    #LangSmith
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "joblens")
    LANGCHAIN_ENDPOINT: str = os.getenv("LANGCHAIN_ENDPOINT", 
                                         "https://api.smith.langchain.com")

    @classmethod
    def validate(cls):
        missing=[]
        if not cls.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
        if not cls.QDRANT_API_KEY:
            missing.append("QDRANT_API_KEY")
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
        
config = Config()