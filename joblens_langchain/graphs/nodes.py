import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs.state import RAGState
from vectorstore.qdrant_service import QdrantService
from services.llm_service import LLMService
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import Config
from logger import logger

_vector_service = None
_llm = None
_prompt = None
_parser = None


def _get_services():

    global _vector_service, _llm, _prompt, _parser

    if _vector_service is None:
        _vector_service = QdrantService()

    if _llm is None:
        _llm = LLMService.get_model()

    if _prompt is None:
        _prompt = ChatPromptTemplate.from_template("""
You are a career advisor for tech professionals in India.
Answer the user's question using ONLY the information in the documents provided.

Rules:
1. If documents fully answer the question, give a clear direct answer.
2. If partially answered, answer what you can and state what's missing.
3. If not in documents at all, say: "I don't have enough information to answer that."
4. Never use general knowledge. Only use what's provided.
5. Cite sources like [Source: Company JD].

DOCUMENTS:
{context}

QUESTION:
{question}
""")

    if _parser is None:
        _parser = StrOutputParser()

    return _vector_service, _llm, _prompt, _parser


# Node 1
def retrieve_node(state : RAGState) -> dict:

    _vector_service,_,_,_=_get_services()
    question = state["question"]
    source_label = state.get("source_label")

    logger.info(f"[retrieve_node] question='{question[:50]}' source='{source_label}'")
    chunks= _vector_service.retrieve(
        question=question,
        source_label=source_label,
        top_k=Config.RETRIEVAL_TOP_K
    )

    logger.info(f"[retrieve_node] found {len(chunks)} chunks")


    return {
        "retrieved_chunks": [c.text for c in chunks],
        "retrieval_scores": [c.score for c in chunks],
        "sources": list({c.source_label for c in chunks}),
        "chunk_sources": [c.source_label for c in chunks],
        "chunks_used": len(chunks),
    }

#node 2
def generate_node(state: RAGState) ->dict:
    _,_llm,_prompt,_parser = _get_services()

    chunks=state["retrieved_chunks"]
    questions=state["question"]

    logger.info(f"[generate_node] generating from {len(chunks)} chunks")

    if not chunks:
        logger.warning(f"No chunks have been retrieved")

        return{
         "answer" : "i dont have information o answer that",
         "error" :None
        }

    context_parts = []
    chunk_sources = state.get("chunk_score",[])
    for i,chunk in enumerate(chunks,1):
        source = chunk_sources[i-1] if i<=len(chunk_sources) else "unknown"
        context_parts.append(f"[Source {i} : {source}]\n{chunk}")
    context ="\n\n".join(context_parts) 

    chain=_prompt | _llm | _parser

    try:
        answer=chain.invoke({
            "context" :context,
            "question" : questions
        })
        logger.info(f"[generate_node] answer generated ({len(answer)} chars)")
        return {"answer" : answer, "error":None}

    except Exception as e:
        logger.error(f"[generate_node] LLM call failed: {e}")
        return {
            "answer": "I encountered an error generating an answer.",
            "error": str(e)
        }

#node 3

def evaluate_node(state: RAGState) -> dict:
  
    answer = state.get("answer", "")
    chunks_used = state.get("chunks_used", 0)
    iteration = state.get("iteration_count", 0)

    # Failure conditions
    refusal_phrases = [
        "i don't have enough information",
        "not mentioned",
        "cannot find",
        "no information found",
        "no relevant"
    ]

    is_refusal = any(phrase in answer.lower() for phrase in refusal_phrases)
    is_too_short = len(answer.strip()) < 50
    no_chunks = chunks_used == 0

    if (is_refusal or is_too_short or no_chunks) and iteration < state.get("max_iterations", 3):
        quality = "bad"
        reason = "refusal" if is_refusal else "too_short" if is_too_short else "no_chunks"
        logger.info(f"[evaluate_node] quality=BAD reason={reason} iteration={iteration}")
    else:
        quality = "good"
        logger.info(f"[evaluate_node] quality=GOOD iteration={iteration}")

    return {
        "answer_quality": quality,
        "iteration_count": iteration + 1
    }


def reformulate_node(state: RAGState) -> dict:
    _,_llm,_,_parser =_get_services()
    original = state.get("original_question", state["question"])
    iteration = state.get("iteration_count", 1)

    reformulate_prompt = ChatPromptTemplate.from_template("""
You are helping improve a search query for a job search system.
The original query didn't retrieve good results.

Original question: {question}
Attempt number: {iteration}

Rewrite this as a keyword-dense search query that will find
relevant job description or resume content.
Focus on specific skills, technologies, and role terms.
Return ONLY the rewritten query, nothing else.
""")
    
    chain= reformulate_prompt | _llm | _parser

    try:
        new_query = chain.invoke({
            "question": original,
            "iteration": iteration
        }).strip()

        logger.info(f"[reformulate_node] '{original[:40]}' → '{new_query[:40]}'")
        return {"reformulated_question": new_query, "question": new_query}

    except Exception as e:
        logger.error(f"[reformulate_node] failed: {e}")
        return {"reformulated_question": original}
