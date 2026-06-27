# ===================================
# TEST — Reranking + Better Prompts
# ===================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import rag_query, retrieve_chunks
from reranker import rerank_chunks
'''

# -------------------------------------------------------
# Test 1 — Compare retrieval order BEFORE vs AFTER reranking
# This is the most important test — it proves reranking does something
# -------------------------------------------------------

print("=" * 55)
print("TEST 1 — Before vs After Reranking")
print("=" * 55)

question = "What backend technologies does the role need?"

# Before reranking — raw bi-encoder order
raw_chunks = retrieve_chunks(question, top_k=5, min_similarity=0.2)

print("\nBEFORE reranking (bi-encoder order):")
for i, c in enumerate(raw_chunks):
    print(f"  {i+1}. [{c['score']}] {c['text'][:80]}")

# After reranking — cross-encoder order
reranked = rerank_chunks(question, raw_chunks.copy(), top_k=3)

print("\nAFTER reranking (cross-encoder order):")
for i, c in enumerate(reranked):
    print(f"  {i+1}. [rerank: {c['rerank_score']:.3f}] {c['text'][:80]}")




# -------------------------------------------------------
# Test 2 — Full pipeline with reranking on
# -------------------------------------------------------

print()
print("=" * 55)
print("TEST 2 — Full RAG with Reranking")
print("=" * 55)

result = rag_query(question, retrieve_k=10, final_k=3, use_reranking=True)
print(f"\nQ: {question}")
print(f"A: {result['answer']}")
print(f"   Sources: {result['sources']} | Chunks used: {result['chunks_used']}")


# -------------------------------------------------------
# Test 3 — Partial answer handling
# A question where only PART of the answer exists in your data
# -------------------------------------------------------

print()
print("=" * 55)
print("TEST 3 — Partial Answer Test")
print("=" * 55)

partial_question = "What does the role pay, and what tech skills are needed?"
result = rag_query(partial_question, retrieve_k=10, final_k=3)
print(f"\nQ: {partial_question}")
print(f"A: {result['answer']}")
print("\n(Check: does the answer explicitly say salary info is missing,")
print(" instead of just ignoring that part of the question?)")

'''
# -------------------------------------------------------
# Test 4 — With vs without reranking, side by side
# -------------------------------------------------------

print()
print("=" * 55)
print("TEST 4 — Reranking ON vs OFF Comparison")
print("=" * 55)

q = "What experience is required for this role?"

result_with = rag_query(q, use_reranking=True, min_similarity=0.15, retrieve_k=10)
result_without = rag_query(q, use_reranking=False, min_similarity=0.15, retrieve_k=10)

print(f"\nWith reranking:    {result_with['answer'][:150]}")
print(f"\nWithout reranking: {result_without['answer'][:150]}")

