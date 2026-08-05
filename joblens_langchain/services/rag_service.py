from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from vectorstore.qdrant_service import QdrantService
from services.llm_service import LLMService
from prompts.rag_prompt import RAGPrompt
from models.schemas import (RetrievedChunk,RAGResponse)
from config import Config
from logger import logger

class RAGService:

    def __init__(self,vector: QdrantService):
        self.vector = QdrantService()
        self.llm=LLMService.get_model()
        self.prompt = RAGPrompt.get_prompt()
        self.output_parser = StrOutputParser()

        logger.info("RAG Service initialized")


    def _build_context(self, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "No relevant documents found."
        context = []
        for i, chunk in enumerate(chunks, 1):
            context.append(f"[Source {i}: {chunk.source_label}]\n{chunk.text}")
        return "\n\n".join(context)

    def query(
        self,
        question: str,
        source_label: str = None,
        top_k: int = Config.RERANK_TOP_K
    ) -> RAGResponse:
        chunks = self.vector.retrieve(
            question=question,
            source_label=source_label,
            top_k=top_k
        )

        if not chunks:
            return RAGResponse(
                question=question,
                answer="I don't have enough information to answer that.",
                sources=[],
                chunks_used=0
            )

        context = self._build_context(chunks)

        #LCEL
        chain=(
            {"context":lambda _: context, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | self.output_parser
        )

        answer=chain.invoke(question)
        sources = list({c.source_label for c in chunks})
        scores = [c.score for c in chunks]

        logger.info(f"RAG query answered using {len(chunks)} chunks from {sources}")

        return RAGResponse(
            question=question,
            answer=answer,
            sources=sources,
            chunks_used=len(chunks),
            retrieval_scores=scores
        ) 