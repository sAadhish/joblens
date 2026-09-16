from config import Config
from langchain_groq import ChatGroq

class LLMService:
    _model=None

    @classmethod
    def get_model(cls):
        if cls._model is None: 
            cls._model = ChatGroq(
            api_key=Config.GROQ_API_KEY,
            model=Config.LLM_MODEL,
            temperature=Config.LLM_TEMPERATURE
         )

        return cls._model