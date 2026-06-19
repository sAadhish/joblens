# JobLens 🔍
### AI-Powered Job Market Intelligence Platform

> Built as part of a structured 100-day GenAI engineering journey — from zero to production-ready AI systems.

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![LLM](https://img.shields.io/badge/LLM-Llama%203.3%2070B-green)](https://groq.com)
[![VectorDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange)](https://chromadb.com)
[![Status](https://img.shields.io/badge/Status-Stage%201%20Complete-brightgreen)]()

---

## What is JobLens?

JobLens is a production-grade AI system that helps candidates make smarter job decisions using semantic search, vector databases, and LLM-powered analysis.

**Not another resume analyzer.**

Most job platforms match keywords. JobLens matches **meaning** — using embeddings and vector similarity to find roles that align with your actual profile, even when the exact words don't match.

---

## The Problem It Solves

Traditional job search:
```
You search "data analyst" → platform finds "data analyst" keyword → done
```

JobLens:
```
Your full profile → converted to meaning (embeddings) 
→ compared against JD meanings → ranked by actual relevance
→ AI explains exactly what you're missing and how long to close the gap
```

---

## Features

| Feature | Status | What It Does |
|---|---|---|
| JD Analyzer | ✅ Live | Extracts structured data from any raw JD text |
| Skill Gap Analyzer | ✅ Live | Compares your profile vs JD, flags missing skills |
| Experience Gap Detection | ✅ Live | Flags experience mismatch, not just skill mismatch |
| Semantic Job Matching | ✅ Live | Finds best roles by meaning, not keywords |
| Metadata Filtering | ✅ Live | Filter by role type, location, experience, remote |
| Confidence Threshold | ✅ Live | Ignores weak matches below 0.35 similarity |
| Structured JSON Output | ✅ Live | All AI output parsed and usable by code |
| Error Handling | ✅ Live | Graceful degradation — one failure doesn't crash pipeline |
| File Logging | ✅ Live | Every operation logged with timestamp to file |
| Multi-document RAG | 🔨 Building | LangChain + ChromaDB retrieval system |
| AI Career Agent | 🔜 Coming | Agent that searches and recommends learning resources |
| REST API | 🔜 Coming | FastAPI — expose everything as callable endpoints |
| Production Deployment | 🔜 Coming | Docker + cloud deployment |

---

## System Architecture

```
                    ┌─────────────────────┐
                    │   Raw JD Text Input  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    JD Analyzer       │
                    │  (Groq / Llama 3.3)  │
                    │  Extracts structured │
                    │  JSON from JD text   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    JD Store          │
                    │  Sentence           │
                    │  Transformers        │
                    │  → Embeddings        │
                    │  → ChromaDB          │
                    └──────────┬──────────┘
                               │
              ┌────────────────▼────────────────┐
              │         Profile Matcher          │
              │  Candidate Profile → Embedding   │
              │  Cosine Similarity Search        │
              │  Metadata Filter (role/location) │
              │  Confidence Threshold (0.35)     │
              └────────────────┬────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Gap Analyzer      │
                    │  LLM compares        │
                    │  profile vs best JD  │
                    │  → Skills gap        │
                    │  → Experience gap    │
                    │  → Readiness score   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Final Report       │
                    │  Ranked matches +    │
                    │  Gap analysis +      │
                    │  Actionable advice   │
                    └─────────────────────┘
```

---

## Tech Stack

```
LLM API          Groq (Llama 3.3 70B) — fast inference, free tier
Embeddings       Sentence Transformers (all-MiniLM-L6-v2)
Vector DB        ChromaDB — local, cosine similarity
Language         Python 3.11+
Logging          Python logging module — file + terminal output
API (coming)     FastAPI
Deploy (coming)  Docker
```

---

## Project Structure

```
joblens/
├── main.py                          ← entry point
├── config.py                        ← shared setup (clients, models, DB)
├── requirements.txt
├── .env.example
├── .gitignore
│
├── joblens/                         ← core modules
│   ├── __init__.py
│   ├── analyzer.py                  ← JD analysis via LLM
│   ├── store.py                     ← embedding + ChromaDB storage
│   ├── matcher.py                   ← semantic profile matching
│   ├── gap.py                       ← skill gap analysis via LLM
│   ├── pipeline.py                  ← orchestrates all modules
│   └── logger.py                    ← centralized logging setup
│
├── stage-1-core-genai/              ← day-by-day learning progression
│   ├── README.md
│   ├── day62_jd_analyzer/
│   ├── day63_structured_output/
│   ├── day64_embeddings/
│   ├── day65_vector_db/
│   ├── day66_metadata/
│   ├── day67_similarity_search/
│   └── day68_unified_pipeline/
│
├── logs/                            ← auto-generated, gitignored
└── cache/                           ← auto-generated, gitignored
```

---

## Sample Output

```
=======================================================
  JOBLENS — AI Job Intelligence Platform
=======================================================

📥 Processing 5 job descriptions...

  ✓ Sarvam AI — Building low-latency APIs for ML models at scale
  ✓ Freshworks — Data Analyst for product analytics team
  ✓ Haptik — Building conversational AI using NLP and LLMs
  ✓ Zoho — Develop and integrate AI features across product suite
  ✓ Razorpay — Design and develop data pipelines and data warehouse

🔍 Finding best matches for your profile...

  Rank 1: Freshworks — Data Analyst
           Score: 0.756 | India | Remote: False | 2-4yrs
  Rank 2: Razorpay — Data Engineer
           Score: 0.626 | India | Remote: False | 2-5yrs
  Rank 3: Zoho — GenAI Developer
           Score: 0.536 | India | Remote: False | 1-3yrs

📊 Skill Gap Analysis — Freshworks

  Matching skills : ['SQL', 'Python', 'Tableau', 'Power BI']
  Missing skills  : ['statistical analysis', 'A/B testing']
  Experience gap  : candidate has 1 year, role needs 2-4 years
  Gap severity    : medium
  Ready in        : 8 weeks
  Top advice      : Focus on statistical analysis and A/B testing
                    to become a strong candidate for this role
=======================================================
```

---

## Key Engineering Decisions

**Why Groq over OpenAI?**
Groq offers free tier with Llama 3.3 70B — a genuinely capable open model. Avoiding vendor lock-in early is the right architectural call for a system that will scale.

**Why ChromaDB over Pinecone?**
ChromaDB runs locally with zero setup. The core concepts — collections, embeddings, metadata filters, cosine similarity — transfer directly to Pinecone or Qdrant in production. Right tool for the current stage.

**Why cosine similarity over L2 distance?**
For text embeddings, cosine measures semantic direction regardless of vector magnitude. L2 measures raw distance — less meaningful for high-dimensional text vectors. Explicitly set `{"hnsw:space": "cosine"}` on every collection.

**Why metadata filtering before semantic search?**
Pure semantic search on large datasets is noisy. Filtering by role type, experience, and location first reduces the search space to relevant candidates — semantic ranking then finds the best match within that space. Two-layer search consistently outperforms one-layer search.

**Why hash-based IDs over sequential IDs?**
`hashlib.md5(text)` as ChromaDB ID means duplicate documents are automatically handled — same text always generates the same ID. Sequential IDs break on re-runs with persistent storage.

**Why centralized logging over print statements?**
`print()` disappears after a run. Logging records every operation with timestamps to a file — essential for debugging production failures after the fact. When something breaks at 2 AM, the log file tells you exactly what happened.

**Why graceful degradation in the pipeline?**
If one JD fails to parse, the pipeline skips it and continues — 4 successful results beat 0 results. `continue` in exception handling is not laziness, it's intentional resilience design.

---

## Real Bugs Fixed During Development

These aren't hidden — they're the learning:

| Bug | Cause | Fix |
|---|---|---|
| Negative similarity scores | Typo: `hsnw` instead of `hnsw` — fell back to L2 distance | Fixed collection metadata key |
| JSON parsing crash | LLM wrapped JSON in markdown ` ```json ``` ` blocks despite instructions | `re.sub(r"```json\|```", "", raw)` before parsing |
| Python set instead of dict | `{"$and", conditions}` instead of `{"$and": conditions}` | Colon not comma |
| Inconsistent location values | LLM returned None, "", "not specified", "Not specified" for same concept | `clean_field()` normalizes all variations |
| Skills list in metadata | ChromaDB metadata doesn't support lists — silently fails | Moved skills to document text only |

---

## 100-Day Journey

| Stage | Days | Focus | Status |
|---|---|---|---|
| Stage 1 | 61–70 | Core GenAI — LLMs, Embeddings, Vector DBs, Pipelines | ✅ Complete |
| Stage 2 | 71–85 | RAG Systems — LangChain, chunking, retrieval | 🔨 In Progress |
| Stage 3 | 86–95 | AI Agents + Memory + Tool Calling | 🔜 Coming |
| Stage 4 | 96–100 | Production — FastAPI, Docker, Optimization | 🔜 Coming |

---

## Setup

```bash
git clone https://github.com/sAadhish/joblens
cd joblens
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
python main.py
```

---

## About

Built by [Aadhish](https://linkedin.com/in/aadhish) — BI Developer transitioning into GenAI Engineering.

This repository documents a real learning journey — not polished tutorials. Every decision, every bug, every fix is documented here because that's how real engineers learn.

- GitHub: [github.com/sAadhish](https://github.com/sAadhish)
- LinkedIn: [linkedin.com/in/aadhish](https://linkedin.com/in/aadhish)