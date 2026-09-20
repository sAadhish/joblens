
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qdrant_client import QdrantClient
from config import Config
import logging

logger = logging.getLogger(__name__)

_qdrant_client = None


def _get_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY
        )
    return _qdrant_client


def get_companies_resource() -> str:
    """
    Returns list of all indexed companies.
    Reads directly from Qdrant — no LLM needed.
    """
    try:
        client = _get_client()
        results = client.scroll(
            collection_name=Config.QDRANT_COLLECTION,
            limit=100,
            with_payload=True
        )

        companies = {}
        for point in results[0]:
            label = point.payload.get("metadata", {}).get("source_label", "")
            if label.endswith(" JD"):
                company = label.replace(" JD", "")
                companies[company] = companies.get(company, 0) + 1

        if not companies:
            return "No companies indexed yet."

        lines = ["# JobLens — Indexed Companies\n"]
        for company, chunk_count in sorted(companies.items()):
            lines.append(f"- {company} ({chunk_count} chunks indexed)")

        logger.info(f"[Resource:companies] {len(companies)} companies")
        return "\n".join(lines)

    except Exception as e:
        logger.error(f"[Resource:companies] failed: {e}")
        return f"Error reading companies: {e}"


def get_resume_resource() -> str:
    """
    Returns the candidate's resume content from Qdrant.
    """
    try:
        client = _get_client()

        from qdrant_client.models import Filter, FieldCondition, MatchValue
        results = client.scroll(
            collection_name=Config.QDRANT_COLLECTION,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.source_label",
                        match=MatchValue(value="My Resume")
                    )
                ]
            ),
            limit=20,
            with_payload=True
        )

        if not results[0]:
            return "No resume indexed yet. Please index a resume first."

        chunks = []
        for point in results[0]:
            content = point.payload.get("page_content", "")
            if content:
                chunks.append(content)

        if not chunks:
            return "Resume found but no content could be extracted."

        header = "# Candidate Resume\n"
        logger.info(f"[Resource:resume] {len(chunks)} chunks")
        return header + "\n\n---\n\n".join(chunks)

    except Exception as e:
        logger.error(f"[Resource:resume] failed: {e}")
        return f"Error reading resume: {e}"


def get_jd_resource(company: str) -> str:
    """
    Returns full JD content for a specific company.

    Args:
        company: Company name (e.g. "Sarvam AI", "Freshworks")
    """
    try:
        if not company or not company.strip():
            return "Error: company name required"

        company = company.strip()
        source_label = f"{company} JD"

        client = _get_client()

        from qdrant_client.models import Filter, FieldCondition, MatchValue
        results = client.scroll(
            collection_name=Config.QDRANT_COLLECTION,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.source_label",
                        match=MatchValue(value=source_label)
                    )
                ]
            ),
            limit=20,
            with_payload=True
        )

        if not results[0]:
            return f"No JD found for '{company}'. Available companies: use joblens://companies to check."

        chunks = []
        for point in sorted(results[0], key=lambda p: p.payload.get("metadata", {}).get("chunk_index", 0)):
            content = point.payload.get("page_content", "")
            if content:
                chunks.append(content)

        header = f"# {company} — Job Description\n"
        logger.info(f"[Resource:jd] company='{company}' {len(chunks)} chunks")
        return header + "\n\n".join(chunks)

    except Exception as e:
        logger.error(f"[Resource:jd:{company}] failed: {e}")
        return f"Error reading JD for {company}: {e}"