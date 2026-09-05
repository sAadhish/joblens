import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.mcpserver import MCPServer as FastMCP
#from mcp.server.fastmcp import FastMCP
from mcp_server.tools import (
    search_joblens,
    ask_career_question,
    list_indexed_companies,
    analyze_skill_gap
)
from langsmith_setup import setup_langsmith
setup_langsmith()

mcp=FastMCP(
    name="Job Lens",
    instructions="""
JobLens is an AI-powered job market intelligence system for tech professionals in India.
It has indexed job descriptions from companies like Sarvam AI, Freshworks, Haptik, and more.
It can also analyze a candidate's resume against job requirements.

Use these tools to help users with career questions, job matching, and skill gap analysis.
Always cite sources when providing information from the JobLens knowledge base.
"""
)

# REGISTER TOOLS


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
    return search_joblens(query, company if company else None)


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
    return ask_career_question(question, company if company else None)


@mcp.tool()
def list_companies() -> str:
    """
    List all companies currently indexed in the JobLens system.
    Call this first to know which companies are available for querying.
    """
    return list_indexed_companies()


@mcp.tool()
def check_skill_gap(candidate_skills: str, company: str) -> str:
    """
    Analyze the skill gap between a candidate and a specific company's requirements.
    Use this when the user wants to know if they qualify for a role or what they need to learn.

    Args:
        candidate_skills: Comma-separated list of skills (e.g. "Python, SQL, Power BI")
        company: Company name to compare against (e.g. "Sarvam AI")
    """
    return analyze_skill_gap(candidate_skills, company)


# RUN THE SERVER

if __name__ == "__main__":
    print("Starting JobLens MCP Server...")
    print("Tools available:")
    print("  - search_jobs")
    print("  - answer_career_question")
    print("  - list_companies")
    print("  - check_skill_gap")
    print()
    print("Connect from Claude Desktop using the config below.")
    mcp.run()