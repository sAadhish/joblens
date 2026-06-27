from sentence_transformers import CrossEncoder
from logger import logger

_reranker_cache =None

def _get_reranker(model_name : str ="cross-encoder/ms-marco-MiniLM-L-6-v2"):
    global _reranker_cache
    if _reranker_cache is None:
        logger.info(f"Loading cross-encoder reranker: {model_name}")
        _reranker_cache=CrossEncoder(model_name)
    return _reranker_cache

def rerank_chunks(
        question: str,
        chunks : list[dict],
        top_k : int = 3
) -> list[dict]:
    if not chunks:
        return []
    
    model=_get_reranker()
    pairs = [[question,chunk["text"]] for chunk in chunks]
    scores = model.predict(pairs)

    for chunk,score in zip(chunks,scores):
        chunk["rerank_score"]=float(score)

    reranked = sorted(chunks,key=lambda c:c["rerank_score"],reverse=True)

    logger.info(f"Ranked {len(chunks)} chunks down to top {top_k}")

    return reranked[:top_k]
