# ===================================
# MEMORY RAG SERVICE
# Stateful RAG — remembers conversation history
# ===================================

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.memory import ConversationBufferMemory
from vectorstore.qdrant_service import QdrantService
from services.llm_service import LLMService
from models.schemas import RAGResponse
from callbacks.logging_callback import JobLensCallbackHandler
from config import Config
from logger import logger


class MemoryRAGService:
    """
    RAG with conversation memory.

    Key difference from RAGService:
    Every query includes the full conversation history.
    The LLM can refer to "that role" or "the previous answer"
    and understand what it means.

    Why a separate class and not just updating RAGService?
    Stateless and stateful are fundamentally different contracts.
    A stateless service can be called from anywhere safely.
    A stateful service must be managed — you need to know when
    to reset memory (new user session) and when to keep it (same session).
    Mixing them in one class creates confusion about which mode you're in.
    """

    def __init__(self, vector_service: QdrantService):
        self.vector = vector_service
        self.llm = LLMService.get_model()
        self.output_parser = StrOutputParser()

        # Memory stores the conversation history
        # ConversationBufferMemory keeps ALL messages — good for short conversations
        # For long conversations, you'd use ConversationSummaryMemory instead
        # which summarizes older messages to save context window space
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )

        # Prompt includes chat_history placeholder
        # MessagesPlaceholder injects the full conversation history here
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a career advisor for tech professionals in India.
Answer using ONLY the provided documents.
If the answer is not in the documents, say "I don't have enough information to answer that."
Do not use general knowledge. Cite your sources like [Source: Company JD].

DOCUMENTS:
{context}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])

        logger.info("MemoryRAGService initialized")

    def chat(
        self,
        question: str,
        source_label: str = None,
        top_k: int = Config.RERANK_TOP_K
    ) -> RAGResponse:
        """
        Stateful query — includes conversation history in every call.
        """
        callback = JobLensCallbackHandler()

        # Retrieve relevant chunks
        chunks = self.vector.retrieve(
            question=question,
            source_label=source_label,
            top_k=top_k
        )

        if not chunks:
            response_text = "I don't have enough information to answer that."
            self.memory.chat_memory.add_user_message(question)
            self.memory.chat_memory.add_ai_message(response_text)
            return RAGResponse(
                question=question,
                answer=response_text,
                sources=[],
                chunks_used=0
            )

        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Source {i}: {chunk.source_label}]\n{chunk.text}")
        context = "\n\n".join(context_parts)

        # Load conversation history from memory
        history = self.memory.load_memory_variables({})
        chat_history = history.get("chat_history", [])

        # Build and run the chain with callbacks
        chain = (
            self.prompt
            | self.llm
            | self.output_parser
        )

        answer = chain.invoke(
            {
                "context": context,
                "question": question,
                "chat_history": chat_history
            },
            config={"callbacks": [callback]}
        )

        # Save this exchange to memory
        self.memory.chat_memory.add_user_message(question)
        self.memory.chat_memory.add_ai_message(answer)

        sources = list({c.source_label for c in chunks})

        logger.info(f"Memory RAG answered | History length: {len(chat_history)} messages")

        return RAGResponse(
            question=question,
            answer=answer,
            sources=sources,
            chunks_used=len(chunks)
        )

    def reset_memory(self):
        """Clears conversation history — call this when a new session starts."""
        self.memory.clear()
        logger.info("Conversation memory cleared")

    def get_history(self) -> list:
        """Returns the full conversation history."""
        return self.memory.chat_memory.messages