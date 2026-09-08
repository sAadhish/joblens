import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.mcpserver import MCPServer as FastMCP
from mcp_server.tools import (
    search_joblens,
    ask_career_question,
    list_indexed_companies,
    analyze_skill_gap
)
from mcp_server.resources import (
    get_companies_resource,
    get_resume_resource,
    get_jd_resource
)
from langsmith_setup import setup_langsmith
import logging

logger = logging.getLogger(__name__)
setup_langsmith()

mcp = FastMCP(
    name="JobLens",
    instructions="""
JobLens is an AI-powered job market intelligence system for tech professionals in India.

AVAILABLE RESOURCES (read these first):
- joblens://companies     : list of all indexed companies
- joblens://resume        : candidate's resume and background
- joblens://jd/{company}  : full JD for a specific company

AVAILABLE TOOLS:
- search_jobs             : semantic search across JDs
- answer_career_question  : grounded Q&A using RAG + LangGraph agent
- list_companies          : list indexed companies
- check_skill_gap         : compare candidate skills vs JD requirements

BEST PRACTICE:
1. Read joblens://companies first to know what's available
2. Read joblens://jd/{company} before asking questions about that company
3. Use answer_career_question for complex multi-turn career advice
4. Use search_jobs for quick factual lookups
"""
)


# -------------------------------------------------------
# RESOURCES
# -------------------------------------------------------

@mcp.resource("joblens://companies")
def companies_resource() -> str:
    """
    List of all companies currently indexed in JobLens.
    Read this first before querying specific companies.
    """
    return get_companies_resource()


@mcp.resource("joblens://resume")
def resume_resource() -> str:
    """
    The candidate's resume and professional background.
    Read this when answering questions about the candidate's skills or experience.
    """
    return get_resume_resource()


@mcp.resource("joblens://jd/{company}")
def jd_resource(company: str) -> str:
    """
    Full job description for a specific company.
    Read this before answering detailed questions about a company's role.
    """
    return get_jd_resource(company)


# -------------------------------------------------------
# TOOLS — with input validation and error handling
# -------------------------------------------------------

@mcp.tool()
def search_jobs(query: str, company: str = "") -> str:
    """
    Search the JobLens knowledge base for relevant job information.
    Use this when the user asks about job requirements, skills needed,
    or any information about specific roles or companies.

    Args:
        query: What to search for (e.g. "Python backend requirements")
        company: Optional company name to restrict search (e.g. "Sarvam AI")
    """
    # Input validation
    if not query or not query.strip():
        return "Error: query cannot be empty"
    if len(query) > 500:
        return "Error: query too long (max 500 characters)"

    try:
        result = search_joblens(query.strip(), company.strip() if company else None)
        logger.info(f"[MCP:search_jobs] query='{query[:40]}' company='{company}'")
        return result
    except Exception as e:
        logger.error(f"[MCP:search_jobs] failed: {e}")
        return f"Search failed. Please try again. Error: {str(e)[:100]}"


@mcp.tool()
def answer_career_question(question: str, company: str = "") -> str:
    """
    Get a grounded answer to a career question from the JobLens RAG system.
    Use this for specific questions about roles, requirements, or career advice.
    The answer will be grounded in actual job descriptions.

    Args:
        question: The career question to answer
        company: Optional company to focus on
    """
    if not question or not question.strip():
        return "Error: question cannot be empty"
    if len(question) > 1000:
        return "Error: question too long (max 1000 characters)"

    try:
        result = ask_career_question(
            question.strip(),
            company.strip() if company else None
        )
        logger.info(f"[MCP:answer_career_question] '{question[:40]}'")
        return result
    except Exception as e:
        logger.error(f"[MCP:answer_career_question] failed: {e}")
        return f"Could not answer question. Please try again. Error: {str(e)[:100]}"


@mcp.tool()
def list_companies() -> str:
    """
    List all companies currently indexed in the JobLens system.
    Call this first to know which companies are available for querying.
    """
    try:
        result = list_indexed_companies()
        logger.info("[MCP:list_companies] called")
        return result
    except Exception as e:
        logger.error(f"[MCP:list_companies] failed: {e}")
        return "Could not retrieve company list. Please try again."


@mcp.tool()
def check_skill_gap(candidate_skills: str, company: str) -> str:
    """
    Analyze the skill gap between a candidate and a specific company's requirements.
    Use this when the user wants to know if they qualify for a role or what they need to learn.

    Args:
        candidate_skills: Comma-separated list of skills (e.g. "Python, SQL, Power BI")
        company: Company name to compare against (e.g. "Sarvam AI")
    """
    if not candidate_skills or not candidate_skills.strip():
        return "Error: candidate_skills cannot be empty"
    if not company or not company.strip():
        return "Error: company cannot be empty"

    try:
        result = analyze_skill_gap(
            candidate_skills.strip(),
            company.strip()
        )
        logger.info(f"[MCP:check_skill_gap] company='{company}'")
        return result
    except Exception as e:
        logger.error(f"[MCP:check_skill_gap] failed: {e}")
        return f"Skill gap analysis failed. Please try again. Error: {str(e)[:100]}"


# -------------------------------------------------------
# RUN
# -------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Starting JobLens MCP Server (Production)...")
    print("Resources: joblens://companies, joblens://resume, joblens://jd/{company}")
    print("Tools: search_jobs, answer_career_question, list_companies, check_skill_gap")
    mcp.run()