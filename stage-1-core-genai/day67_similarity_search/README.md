# Stage 1 — Core GenAI Concepts

> Goal: Understand how LLMs actually work and build the foundation of JobLens

---

## What's Built Here

| Day | Topic | What Was Built | Key Learning |
|---|---|---|---|
| Day 62 | Prompt Engineering | JD Analyzer — extract structured info from any JD | System prompts, role-based prompting, few-shot |
| Day 63 | Structured Output | JSON JD Parser + Skill Gap Checker | Temperature=0 for reliable output, json.loads, try/catch |
| Day 64 | Embeddings | Resume Ranker using semantic similarity | Sentence vectors, cosine similarity, query phrasing impact |
| Day 65 | Vector Database | ChromaDB storage + semantic search | Persistent storage, cosine vs L2, confidence thresholds |
| Day 66 | Metadata Filtering | Location + experience aware job search | Two-layer search: filter then rank |
| Day 67 | Similarity Search | Real JD matching with 5 target companies | End-to-end pipeline, markdown JSON bug fix |

---

## Key Engineering Decisions Made

**Temperature = 0 for all structured output**
When parsing JDs or generating skill gap JSON, any variation breaks downstream code.
Deterministic output is not optional — it's a requirement.

**Hash-based IDs over sequential IDs**
`hashlib.md5(text)` as ChromaDB ID means duplicate documents are automatically
handled — same text always generates same ID. Sequential IDs break on re-runs.

**Cosine similarity over L2 distance**
Explicitly set `{"hnsw:space": "cosine"}` on every collection.
L2 distance on text embeddings produces scores that go negative — meaningless for ranking.

**Confidence threshold of 0.35**
Results below 0.35 are noise from the small embedding model.
Showing weak matches as "no confident result" is better UX than showing wrong results.


**Strip markdown before JSON parsing**
LLMs occasionally wrap JSON in ```json blocks even when told not to.
`re.sub(r"```json|```", "", raw).strip()` before json.loads() — always.

---

## Bugs Fixed (Real Learning)

1. `hsnw` typo → `hnsw` — caused L2 fallback, produced negative similarity scores
2. `{"$and", conditions}` → `{"$and": conditions}` — Python set vs dict
3. Markdown-wrapped JSON — LLM ignored "no markdown" instruction, added re.sub fix

---

## What's Next — Stage 2

Stage 2 builds a full RAG system on top of this foundation.
The vector search built here becomes the retrieval layer of the RAG pipeline.