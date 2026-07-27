from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from config import Config

class EmbeddingService:

    @classmethod
    @lru_cache(maxsize=1)
    def get_embedding_model(cls):
        return HuggingFaceEmbeddings(model_name =Config.EMBEDDING_MODEL)