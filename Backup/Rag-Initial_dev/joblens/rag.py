
'''
INDEX (once per document)
  load_document(jd_or_resume) → chunk_document() → embed each chunk → store in ChromaDB

RETRIEVE (every question)
  user question → embed it → find top-k closest chunks in ChromaDB

GENERATE (every question)
  retrieved chunks + question → grounded prompt → LLM → answer
'''

import sys
import os
import hashlib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import embedding_model, rag_collection, groq_client
from logger import logger
from ingestion import load_document, chunk_document
from reranker import rerank_chunks

# STEP 1 — INDEX

def index_document(
        source :str,
        source_label: str,
        strategy: str= "paragraph",
        **chunk_kwargs
) ->int:
    
    try:
        text = load_document(source)
    except Exception as e:
        logger.error(f"Failed to load {source_label}: {e}")
        return 0

    chunks = chunk_document(text, strategy=strategy, **chunk_kwargs)

    if not chunks:
        logger.warning(f"No chunks produced for {source_label}")
        return 0

    indexed = 0
    for chunk in chunks:
        chunk_text = chunk["text"]
        embedding = embedding_model.encode([chunk_text]).tolist()

        doc_id = hashlib.md5(f"{source_label}_{chunk['index']}_{chunk_text}".encode()).hexdigest()

        metadata = {
            "source_label": source_label,
            "chunk_index": chunk["index"],
            "strategy": chunk["strategy"],
            "char_count": chunk["char_count"],
        }

        try:
            rag_collection.add(
                documents=[chunk_text],
                embeddings=embedding,
                metadatas=[metadata],
                ids=[doc_id]
            )
            indexed += 1
        except Exception as e:
            logger.warning(f"Failed to store chunk {chunk['index']} of {source_label}: {e}")
            continue

    logger.info(f"Indexed {indexed}/{len(chunks)} chunks for {source_label}")
    return indexed
    

# STEP 2 — RETRIEVE
def retrieve_chunks(
        question: str,
        top_k : int =3,
        source_label: str = None,
        min_similarity:float = 0.3
):
    query_embedding=embedding_model.encode([question]).tolist()
    where_filter =  ({"source_label":source_label}) if source_label else None

    results = rag_collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where =where_filter
    )

    if not results["documents"][0]:
        return [] 
    
    retrieved = []
    for doc , distance,meta in zip(
        results["documents"][0],
        results["distances"][0],
        results["metadatas"][0]
        ):

        similarity =1-distance

        if similarity >= min_similarity:
            retrieved.append({
                "text":doc,
                "score":round(similarity,3),
                "source_label":meta["source_label"],
                "chunk_index":meta["chunk_index"]
                
            })
    return retrieved


# STEP 3 — GENERATE
def build_context(chunks :list[dict])->str:
    if not chunks:
        return ""
    
    parts=[]
    for i,chunk in enumerate(chunks,1):
        parts.append(f"[Source {i}: {chunk['source_label']}]\n{chunk["text"]}")
    return "\n\n".join(parts)

def generate_answer(question :str ,context:str) ->str:
  response = groq_client.chat.completions.create(
      model="llama-3.3-70b-versatile",
      temperature=0,
      messages=[
          {
              "role":"system",
              "content":""" You are a career advisor for texh professionals in India.
              Answer the users questions with only the documents provided below.
              if the answer is not in the document , say excatly this :" i dont have enough information to answer this "
              do not use general knowledge. Donot hallucinate , dont guess . Only use whats provided
              Cite which source(s) you used in your answer , like [source 1]."""
          },
          {
              "role":"user",
              "content": f"DOCUMENTS:\n{context}\n\nQUESTION:\n{question}"
          }

      ]
  )
  return response.choices[0].message.content


# FULL PIPELINE 
#single entry for the whole rag pipe line
def rag_query(
    question: str,
    top_k: int = 3,
    source_label: str = None,
    min_similarity: float = 0.3
) -> dict:
    chunks = retrieve_chunks(question, 
                             top_k=top_k,
                             source_label=source_label,
                             min_similarity=min_similarity)
  
    if not chunks:
      logger.warning(f"No relevent chunks were found for question : {question}")
      return {
          "answers":"I dont have enough information to answer this",
          "sources":[],
          "chunks_used":0
      }
    
    context=build_context(chunks)
    answer=generate_answer(question,context)
    sources = list({c["source_label"] for c in chunks})

    logger.info(f"RAG query answered using {len(chunks)} chunks from {sources}")
    
    return {
        "answers": answer,
        "sources": sources,
        "chunks_used": len(chunks)
    }
