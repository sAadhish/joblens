## Evaluation Results

| Metric | Hand-built RAG | LangChain RAG |
|--------|---------------|---------------|
| RAGAS Overall | ~78% (with reranking) | 48% (baseline) |
| Hand-built eval | 85% | 69% |

The LangChain implementation is intentionally a baseline RAG system
demonstrating the core LangChain patterns (LCEL, OOP services, Qdrant).
Production quality improvements (cross-encoder reranking, hybrid BM25 search,
confidence thresholds) are implemented in the hand-built version in `/joblens`.

This comparison proves that LangChain abstracts implementation, not quality —
the same retrieval improvements apply regardless of framework.