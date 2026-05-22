# JobLens 🔍
### AI-Powered Job Market Intelligence Platform

> Built as part of a structured 100-day GenAI engineering journey — from zero to production-ready AI systems.

---

## What is JobLens?

JobLens is a production-grade AI system that helps candidates make smarter job decisions using semantic search, RAG, and LLM-powered analysis.

**Not another resume analyzer.** JobLens combines vector search, metadata filtering, and AI reasoning to give you intelligence that keyword-based job platforms can't.

---

## Features

| Feature                                                        | Status | Tech Used |
|----------------------------------------------------------------|--------|-----------|
| JD Analyzer — extract structured data from any JD              | ✅ Live | Groq, Llama 3.3 70B |
| Skill Gap Analyzer — compare your profile vs JD                | ✅ Live | Structured JSON output |
| Semantic Job Matching — find best role by meaning              | ✅ Live | Sentence Transformers,   ChromaDB |
| Metadata Filtering — filter by location, experience, remote    | ✅ Live | ChromaDB |
| AI Skill Gap with Readiness Score                              | ✅ Live | RAG + LLM |
| Multi-document RAG system | 🔨 Building | LangChain, ChromaDB  |
| AI Career Agent | 🔜 Coming | LangChain Agents |
| Full REST API | 🔜 Coming | FastAPI |
| Production Deployment | 🔜 Coming | Docker |



---

## Architecture

```
User Profile / Resume
        ↓
Embedding Engine (Sentence Transformers)
        ↓
Vector Search (ChromaDB + Cosine Similarity)
        ↓
Metadata Filtering (role, location, experience, remote)
        ↓
Top Matching JDs Retrieved
        ↓
LLM Analysis (Groq / Llama 3.3 70B)
        ↓
Skill Gap Report + Readiness Score + Advice
```

---

## Tech Stack

```
LLM              Groq API (Llama 3.3 70B)
Embeddings       Sentence Transformers (all-MiniLM-L6-v2)
Vector DB        ChromaDB
Language         Python 3.11+
API (coming)     FastAPI
Deploy (coming)  Docker
```

---

## Project Structure

```
joblens/
├── stage-1-core-genai/       ← LLMs, Embeddings, Vector DBs
│   ├── day62_jd_analyzer/
│   ├── day63_structured_output/
│   ├── day64_embeddings/
│   ├── day65_vector_db/
│   ├── day66_metadata/
│   └── day67_similarity_search/
├── stage-2-rag/              ← RAG Systems (in progress)
├── stage-3-agents/           ← AI Agents (coming)
└── stage-4-production/       ← FastAPI + Docker (coming)
```

---

## 100-Day Journey

This project is built day by day as part of a structured GenAI engineering path:

| Stage | Days | Focus | Status |
|---|---|---|---|
| Stage 1 | 61–70 | Core GenAI — LLMs, Embeddings, Vector DBs | ✅ Complete |
| Stage 2 | 71–85 | RAG Systems | 🔨 In Progress |
| Stage 3 | 86–95 | AI Agents + Memory | 🔜 Coming |
| Stage 4 | 96–100 | Production + Scaling | 🔜 Coming |

---

## Key Engineering Decisions

**Why Groq over OpenAI?**
Groq offers free tier with Llama 3.3 70B — a genuinely powerful open model. For a learning project that will scale to production, avoiding vendor lock-in early is the right call.

**Why ChromaDB over Pinecone?**
ChromaDB runs locally with zero setup. The concepts — collections, embeddings, metadata filters, cosine similarity — transfer directly to Pinecone or Qdrant in production. Learn locally, scale externally.

**Why cosine similarity over L2 distance?**
For text embeddings, cosine similarity measures the angle between vectors — capturing semantic direction regardless of magnitude. L2 measures raw distance, which is less meaningful for high-dimensional text vectors.

**Why metadata filtering before semantic search?**
Pure semantic search on 10,000 JDs is noisy. Filtering by role type, experience, and location first reduces the search space to relevant candidates — then semantic ranking finds the best match within that space. Two-layer search beats one-layer search.

---

## Setup

```bash
git clone https://github.com/sAadhish/joblens
cd joblens
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

---

## About

Built by [Aadhish](https://linkedin.com/in/aadhish) — BI Developer transitioning into GenAI Engineering.

This repository documents real learning — not polished tutorials. Every decision, every bug, every fix is here.

GitHub: [github.com/sAadhish](https://github.com/sAadhish)
