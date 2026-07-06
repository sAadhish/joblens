# ===================================
# CAREER Q&A
# Connects Stage 1 matching to Stage 2 RAG
# ===================================

from stage2_rag.rag import rag_query, compare_sources
from stage1_matching.profile_matcher import match_profile
from logger import logger


def ask_about_match(
    candidate_profile: str,
    question: str,
    match_rank: int = 1
) -> dict:
    matches = match_profile(candidate_profile,top_k=match_rank)

    if not matches or len(matches) < match_rank:
        logger.warning("No match found for career_qa request")
        return {"answer": "No matching job found for your profile.", "sources": []}
    
    target=matches[match_rank-1]
    company_label=f"{target['company']} JD"
    logger.info(f"Career Q&A: answering '{question}' grounded in {company_label}")

    result=rag_query(question=question,source_label=company_label)

    result["matched_company"] = target["company"]
    result["match_score"] = target["score"]
    return result
    

def compare_my_top_matches(
    candidate_profile: str,
    question: str,
    top_n: int = 2,
    min_similarity: float = 0.15
) -> dict:
    
    matches = match_profile(candidate_profile, top_k=top_n)
    if not matches:
        return {"answer": "No matches found.", "sources": []}

    # Build labels for every match found
    labels = [f"{m['company']} JD" for m in matches]

    return compare_sources(question, source_label=labels, include_resume=True,min_similarity=min_similarity)
