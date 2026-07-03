
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

# Build context
def build_context(chunks :list[dict])->str:
    if not chunks:
        return ""
    
    parts=[]
    for i,chunk in enumerate(chunks,1):
        parts.append(f"[Source {i}: {chunk['source_label']}]\n{chunk["text"]}")
    return "\n\n".join(parts)

#generate answer from llm
def generate_answer(question :str ,context:str) ->str:
  response = groq_client.chat.completions.create(
      model="llama-3.3-70b-versatile",
      temperature=0,
      messages=[
            {
                "role": "system",
                "content": """You are a career advisor for tech professionals in India.

Answer the user's question using ONLY the information in the documents provided below.

Rules:
1. If the documents fully answer the question, give a clear, direct answer.
2. If the documents only partially answer it, answer what you can and explicitly 
   state what information is missing — do not guess or fill gaps with general knowledge.
3. If multiple sources contain relevant pieces, synthesize them into one coherent 
   answer rather than listing them separately.
4. If the answer is not in the documents at all, say exactly: 
   "I don't have enough information to answer that."
5. Never use general training knowledge. Only use what's provided below.
6. Cite which source(s) you used, like [Source 1], at the end of relevant sentences."""
            },
            {
                "role": "user",
                "content": f"DOCUMENTS:\n{context}\n\nQUESTION:\n{question}"
            }
        ]
    
  )
  return response.choices[0].message.content


# FULL PIPELINE 
#single entry for the whole rag pipe line
def rag_query(
    question: str,
    retrieve_k: int =10,
    final_k: int = 3,
    source_label: str = None,
    min_similarity: float = 0.3,
    use_reranking:bool =True
) -> dict:
    
    # Stage 1 — Bi-encoder retrieval (wide net)
    chunks = retrieve_chunks(question, 
                             top_k=retrieve_k,
                             source_label=source_label,
                             min_similarity=min_similarity)
  
    if not chunks:
      logger.warning(f"No relevant chunks were found for question : {question}")
      return {
          "answers":"I dont have enough information to answer this",
          "sources":[],
          "chunks_used":0
      }
    
     # Stage 2 — Cross-encoder reranking (precision)
    if use_reranking:
        chunks = rerank_chunks(question, chunks, top_k=final_k)
    else:
        chunks=chunks[:final_k]


    context=build_context(chunks)
    answer=generate_answer(question,context)
    sources = list({c["source_label"] for c in chunks})

    logger.info(f"RAG query answered using {len(chunks)} chunks from {sources}")
    
    return {
        "answer": answer,
        "sources": sources,
        "chunks_used": len(chunks)
    }



##### Multi-Document Retrieval #####

#retrive from each label
def retrieve_multi_source(
        question : str,
        source_label: list[str],
        per_source_k: int = 2,
        min_similarity:float = 0.3
)-> dict[str, list[dict]]:
        results={}
        for label in source_label:
            chunks=retrieve_chunks(question=question,
                                   source_label=label,
                                   top_k=per_source_k,
                                   min_similarity=min_similarity)
            results[label] = chunks
            logger.info(f"Multi-source retrieval: {len(chunks)} chunks from {label}")

        return results


# contex for llm
def build_multi_source_context(grouped : dict[str,list[dict]]):
    sections=[]

    for label, chunks in grouped.items():
        if not chunks :
            sections.append(f"======={label}===\n(No relevant information found)")
            continue

        chunk_texts="\n".join(c["text"] for c in chunks)
        sections.append(f"=== {label} ===\n{chunk_texts}")

    return "\n\n".join(sections)

#generate answer from llm
def generate_comparison_answer(
        question : str,
        context : str,
        source_label : list[str]
) -> dict:
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": f"""You are a career advisor comparing multiple job opportunities 
for a candidate in India.

The documents below are organized into clearly labeled sections, one per source: 
{', '.join(source_label)}.

Rules:
1. Address EVERY source listed, even briefly — never skip one entirely.
2. If a source has no relevant information, explicitly say so for that source 
   rather than omitting it.
3. Use ONLY the information in the documents. Never use general knowledge.
4. Structure your answer clearly — one short section per source, then a final 
   recommendation if asked.
5. Cite sources by their section name."""
            },
            {
                "role": "user",
                "content": f"DOCUMENTS:\n{context}\n\nQUESTION:\n{question}"
            }
        ]
    )

    return response.choices[0].message.content
        

#single pipeline
def compare_sources(
        question :str ,
        source_label : list[str],
        min_similarity : float,
        per_source_k: int =2,
        include_resume: bool = True,
        resume_label: str = "My Resume",
        
) -> dict :
    
    if include_resume and resume_label not in source_label:
        source_label = source_label + [resume_label]
        
    grouped = retrieve_multi_source(question, source_label, per_source_k=per_source_k,min_similarity=min_similarity)

    total_chunk=sum(len(v) for v in grouped.values())
    if total_chunk == 0:
        return {
            "answers": "I don't have enough information to answer that.",
            "sources": [],
            "chunks_used": 0
        }
    
    context = build_multi_source_context(grouped)
    answer = generate_comparison_answer(question, context, source_label)

    return{
        "answers" : answer,
        "sources" : [label for label, chunks in grouped.items() if chunks],
        "chunks_used":total_chunk

    }
