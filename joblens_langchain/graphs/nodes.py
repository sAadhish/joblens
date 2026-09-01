import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_core.messages import HumanMessage,AIMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
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



#############################################################
##################  Full Career Agentic System  ###########################
#############################################################


# -------------------------------------------------------
# AGENT NODE 1 — Load History
# -------------------------------------------------------

def agent_load_history(state) -> dict:
    messages = state.get("messages", [])
    logger.info(f"[agent_load_history] {len(messages)} messages in history")
    return {"chat_history": messages}


# -------------------------------------------------------
# AGENT NODE 2 — Classify
# -------------------------------------------------------

def classify_node(state) -> dict:
    _, llm, _, parser = _get_services()

    question = state["question"]
    logger.info(f"[classify_node] classifying: '{question[:50]}'")

    classify_prompt = ChatPromptTemplate.from_template("""
Classify this career-related question into exactly one category.

Question: {question}

Categories:
- jd: question is about a specific company's job requirements, role, or JD
- resume: question is about the candidate's own background, skills, or experience
- comparison: question compares multiple companies or roles against each other
- general: anything else

If category is "jd", also extract the company name.

Reply in this EXACT format (nothing else):
CATEGORY: <category>
COMPANY: <company name or "none">
""")

    chain = classify_prompt | llm | parser

    try:
        result = chain.invoke({"question": question})
        lines = result.strip().split("\n")

        category = "general"
        company = "none"

        for line in lines:
            if line.startswith("CATEGORY:"):
                category = line.split(":", 1)[1].strip().lower()
            elif line.startswith("COMPANY:"):
                company = line.split(":", 1)[1].strip()

        logger.info(f"[classify_node] type={category} company={company}")
        return {
            "question_type": category,
            "classified_company": company,
            "original_question": question,
            "reformulated_question": question
        }

    except Exception as e:
        logger.error(f"[classify_node] failed: {e}")
        return {
            "question_type": "general",
            "classified_company": "none",
            "original_question": question,
            "reformulated_question": question
        }


# -------------------------------------------------------
# AGENT NODE 3 — JD Retrieve
# -------------------------------------------------------

def jd_retrieve_node(state) -> dict:
    vector_service, _, _, _ = _get_services()

    question = state.get("reformulated_question", state["question"])
    company = state.get("classified_company", "")

    # Build source label from classified company
    source_label = f"{company} JD" if company and company != "none" else None

    logger.info(f"[jd_retrieve] company='{company}' source='{source_label}'")

    chunks = vector_service.retrieve(
        question=question,
        source_label=source_label,
        top_k=Config.RETRIEVAL_TOP_K
    )

    return {
        "retrieved_chunks": [c.text for c in chunks],
        "chunk_sources": [c.source_label for c in chunks],
        "sources": list({c.source_label for c in chunks}),
        "chunks_used": len(chunks)
    }


# -------------------------------------------------------
# AGENT NODE 4 — Resume Retrieve
# -------------------------------------------------------

def resume_retrieve_node(state) -> dict:
    vector_service, _, _, _ = _get_services()

    question = state.get("reformulated_question", state["question"])
    logger.info(f"[resume_retrieve] question='{question[:50]}'")

    chunks = vector_service.retrieve(
        question=question,
        source_label="My Resume",
        top_k=Config.RETRIEVAL_TOP_K
    )

    return {
        "retrieved_chunks": [c.text for c in chunks],
        "chunk_sources": [c.source_label for c in chunks],
        "sources": list({c.source_label for c in chunks}),
        "chunks_used": len(chunks)
    }


# -------------------------------------------------------
# AGENT NODE 5 — General Retrieve
# -------------------------------------------------------

def general_retrieve_node(state) -> dict:
    vector_service, _, _, _ = _get_services()

    question = state.get("reformulated_question", state["question"])
    logger.info(f"[general_retrieve] question='{question[:50]}'")

    chunks = vector_service.retrieve(
        question=question,
        source_label=None,    # no filter — search everything
        top_k=Config.RETRIEVAL_TOP_K
    )

    return {
        "retrieved_chunks": [c.text for c in chunks],
        "chunk_sources": [c.source_label for c in chunks],
        "sources": list({c.source_label for c in chunks}),
        "chunks_used": len(chunks)
    }


# -------------------------------------------------------
# AGENT NODE 6 — Agent Generate
# -------------------------------------------------------

def agent_generate_node(state) -> dict:
    _, llm, _, parser = _get_services()

    chunks = state["retrieved_chunks"]
    question = state["question"]
    chat_history = state.get("chat_history", [])

    context_parts = []
    chunk_sources = state.get("chunk_sources", [])
    for i, chunk in enumerate(chunks, 1):
        source = chunk_sources[i-1] if i <= len(chunk_sources) else "unknown"
        context_parts.append(f"[Source {i}: {source}]\n{chunk}")

    context = "\n\n".join(context_parts) if context_parts else "No relevant documents found."

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a career advisor for tech professionals in India.
Answer using ONLY the provided documents.
If the answer is not in the documents, say "I don't have enough information to answer that."
Cite sources like [Source 1: Company JD].

DOCUMENTS:
{context}"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])

    chain = prompt | llm | StrOutputParser()
    recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history

    try:
        answer = chain.invoke({
            "context": context,
            "chat_history": recent_history,
            "question": question
        })
        logger.info(f"[agent_generate] {len(answer)} chars | history: {len(chat_history)}")
    except Exception as e:
        logger.error(f"[agent_generate] failed: {e}")
        answer = "I encountered an error. Please try again."

    new_messages = [
        HumanMessage(content=question),
        AIMessage(content=answer)
    ]

    return {"answer": answer, "messages": new_messages, "error": None}


# -------------------------------------------------------
# AGENT NODE 7 — Agent Evaluate
# -------------------------------------------------------

def agent_evaluate_node(state) -> dict:
    answer = state.get("answer", "")
    chunks_used = state.get("chunks_used", 0)
    iteration = state.get("iteration_count", 0)

    refusal_phrases = [
        "i don't have enough information",
        "not mentioned", "cannot find",
        "no information found", "no relevant"
    ]

    is_refusal = any(p in answer.lower() for p in refusal_phrases)
    is_too_short = len(answer.strip()) < 50
    no_chunks = chunks_used == 0

    if (is_refusal or is_too_short or no_chunks) and iteration < state.get("max_iterations", 2):
        quality = "bad"
    else:
        quality = "good"

    logger.info(f"[agent_evaluate] quality={quality} iteration={iteration}")
    return {"answer_quality": quality, "iteration_count": iteration + 1}


# -------------------------------------------------------
# AGENT NODE 8 — Agent Reformulate
# -------------------------------------------------------

def agent_reformulate_node(state) -> dict:
    _, llm, _, parser = _get_services()

    original = state.get("original_question", state["question"])
    iteration = state.get("iteration_count", 1)

    reformulate_prompt = ChatPromptTemplate.from_template("""
Rewrite this career query as a keyword-dense search query.
Original: {question}
Attempt: {iteration}
Return ONLY the rewritten query.
""")

    chain = reformulate_prompt | llm | parser

    try:
        new_query = chain.invoke({
            "question": original,
            "iteration": iteration
        }).strip()
        logger.info(f"[agent_reformulate] → '{new_query[:50]}'")
        return {"reformulated_question": new_query, "question": new_query}
    except Exception as e:
        logger.error(f"[agent_reformulate] failed: {e}")
        return {"reformulated_question": original}