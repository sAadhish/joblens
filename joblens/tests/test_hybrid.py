import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stage2_rag.hybrid_search import hybrid_search
from stage2_rag.rag import retrieve_chunks


# Pick a query with a SPECIFIC term — this is where BM25 wins
question = "Does the role require dbt?"

print("=" * 55)
print("SEMANTIC ONLY")
print("=" * 55)
semantic = retrieve_chunks(question, top_k=3, min_similarity=0.0)
for c in semantic:
    print(f"  [{c['score']}] {c['source_label']}: {c['text'][:80]}")

print()
print("=" * 55)
print("HYBRID (semantic + BM25)")
print("=" * 55)
hybrid = hybrid_search(question, top_k=3)
for c in hybrid:
    print(f"  combined={c['combined_score']} | "
          f"sem={c['semantic_score']} | "
          f"bm25={c['bm25_score']}")
    print(f"  {c['source_label']}: {c['text'][:80]}")
    print()