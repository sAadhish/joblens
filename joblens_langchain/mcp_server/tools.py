import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from services.llm_service import LLMService
from vectorstore.qdrant_service import QdrantService
from services.rag_service import RAGService
from services.career_service import CareerService
from config import Config
#from logger import logger
from graphs.career_agent_graph import career_agent
import hashlib

_career_service = None
def get_career_service() -> CareerService:
    global _career_service
    if _career_service is None:
        _career_service = CareerService()
    return _career_service

# Tools: search_joblens , ask_career_question , list_indexed_companies ,analyze_skill_gap 

# TOOL 1
def search_joblens(query: str, company: str = None) -> str:
    
    service = get_career_service()

    source_label = f"{company} JD" if company else None
    chunks = service.vector.retrieve(
        question=query,
        source_label=source_label,
        top_k=Config.RETRIEVAL_TOP_K
    )

    if not chunks:
        return f"No relevant content found for query: '{query}'"

    results = []
    for i, chunk in enumerate(chunks, 1):
        results.append(
            f"[Result {i} — {chunk.source_label}]\n{chunk.text}"
        )

    #logger.info(f"[MCP:search_joblens] query='{query}' company='{company}' → {len(chunks)} results")
    return "\n\n".join(results)

# TOOL 2
def ask_career_question(question: str, company: str = None,max_iterations: int = 2) -> str:

    thread_id =f"mcp_{hashlib.md5(question.encode()).hexdigest()[:8]}"

    config = {"configurable":{"thread_id":thread_id}}
    final_state = None
    for state in career_agent.stream(
        { 
            "question": question,
            "original_question": question,
            "reformulated_question": question,
            "iteration_count": 0,
            "max_iterations": max_iterations,
            "answer_quality": "",
            "answer": ""
        },
            config=config,
            stream_mode="values"
            ):

        final_state=state
    #  logger.info(f"[MCP:ask_career_question] agent used {final_state.get('iteration_count', 0)} iterations")
    return final_state["answer"]


# TOOL 3
def list_indexed_companies() -> str:
    """
    Lists all companies currently indexed in JobLens.

    Returns:
        Comma-separated list of company names available for querying.
    """
    service = get_career_service()

    # Scroll through Qdrant to find unique source labels
    from qdrant_client import QdrantClient
    client = QdrantClient(url=Config.QDRANT_URL, api_key=Config.QDRANT_API_KEY)

    results = client.scroll(
        collection_name=Config.QDRANT_COLLECTION,
        limit=100,
        with_payload=True
    )

    companies = set()
    for point in results[0]:
        label = point.payload.get("metadata", {}).get("source_label", "")
        if label.endswith(" JD"):
            companies.add(label.replace(" JD", ""))

    if not companies:
        return "No companies currently indexed in JobLens."

    #logger.info(f"[MCP:list_indexed_companies] found {len(companies)} companies")
    return f"Indexed companies: {', '.join(sorted(companies))}"


# TOOL 4
def analyze_skill_gap(candidate_skills: str, company: str) -> str:

    service = get_career_service()

    source_label = f"{company} JD"
    jd_chunks = service.vector.retrieve(
        question=f"required skills experience {company}",
        source_label=source_label,
        top_k=3
    )

    if not jd_chunks:
        return f"No JD found for {company}. Make sure it is indexed first."

    jd_text = "\n".join(c.text for c in jd_chunks)

    # Use LLM to analyze the gap


    llm = LLMService.get_model()
    prompt = ChatPromptTemplate.from_template("""
You are a career advisor. Compare the candidate's skills against the job requirements.

Candidate skills: {skills}

Job Description:
{jd}

Provide:
1. Matching skills (candidate has these)
2. Missing skills (JD requires these, candidate lacks)
3. Overall readiness (Low/Medium/High)
4. One specific action to improve readiness

Be concise and specific.
""")

    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({
        "skills": candidate_skills,
        "jd": jd_text
    })

   # logger.info(f"[MCP:analyze_skill_gap] company='{company}'")
    return result