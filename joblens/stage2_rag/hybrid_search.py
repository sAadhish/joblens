import re
from config import rag_collection ,  embedding_model
from logger import logger
from rank_bm25 import BM25Okapi
from sklearn.metrics.pairwise import cosine_similarity


def _tokenize(text : str) ->list[str]:
    return re.findall(r"\w+",text.lower())


def hybrid_search(
    question: str,
    source_label: str = None,
    top_k: int = 5,
    semantic_weight: float = 0.6
) -> list[dict]:
    

# -------------------------------------------------------
# STEP 1 — Pull all chunks from ChromaDB into memory
# -------------------------------------------------------

   where_filter = {"source_label": source_label} if source_label else None
    
   all_data = rag_collection.get(
        where=where_filter,
        include=["documents", "metadatas"]
    ) 
    
   if not all_data["documents"]:
      logger.warning[f"No document found for hybrrid search"]
      return []
   
   documents = all_data["documents"]    # list of chunk texts
   metadatas = all_data["metadatas"]    # list of metadata dicts


    # -------------------------------------------------------
    # STEP 2A — BM25 keyword scoring
    # -------------------------------------------------------
   
    
   tokenized_docs = [_tokenize(doc) for doc in documents]
   bm25 =BM25Okapi(tokenized_docs) #converted to bm25 index

   tokenized_query = _tokenize(question)
   bm25_score = bm25.get_scores(tokenized_query)

    # -------------------------------------------------------
    # STEP 2B — Normalize BM25 scores to 0-1 range
    # -------------------------------------------------------
    
   max_bm25 = max(bm25_score) if max(bm25_score) >0 else 1
   bm25_scores_norm =[s/max_bm25 for s in bm25_score]

    # -------------------------------------------------------
    # STEP 2C — Semantic scoring
    # -------------------------------------------------------

   query_embedding = embedding_model.encode([question])[0]
   doc_embeddings = embedding_model.encode(documents)

   semantic_score =cosine_similarity([query_embedding],doc_embeddings)[0]

    # -------------------------------------------------------
    # STEP 3 — Combine both scores
    # -------------------------------------------------------

   combined = []
   for i , doc in enumerate(documents):
      combined_score= (semantic_weight * semantic_score[i] + 
                        (1-semantic_weight) * bm25_scores_norm[i])
      combined.append({
         "text" : doc,
         "source_label": metadatas[i]["source_label"],
         "semantic_score":round(float(semantic_score[i]),3),
         "bm25_score": round(float(bm25_scores_norm[i]), 3),
         "combined_score": round(float(combined_score), 3)

      })

   combined.sort(key=lambda x:x["combined_score"], reverse=True)

   logger.info(f"Hybrid search ranked {len(combined)} chunks, returning top {top_k}")
   return combined[:top_k]