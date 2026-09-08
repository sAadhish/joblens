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

# JobLens MCP Server — Demo Evidence

## What This Is
JobLens is callable from Claude Desktop via MCP (Model Context Protocol).
Claude can search JDs, answer career questions, and analyze skill gaps
using the JobLens RAG system — all from a conversation in Claude Desktop.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Add to `claude_desktop_config.json` (see README)
3. Restart Claude Desktop
4. JobLens tools appear in Claude's tool list

## Tools Available
| Tool | Description |
|------|-------------|
| `search_jobs` | Semantic search across indexed JDs |
| `answer_career_question` | Grounded Q&A via LangGraph agent |
| `check_skill_gap` | Compare your skills vs JD requirements |

## Resources Available
| Resource | Description |
|----------|-------------|
| `joblens://companies` | List of indexed companies |
| `joblens://resume` | Candidate's resume content |
| `joblens://jd/{company}` | Full JD for a specific company |

## Example Conversations That Work

### 1. List Available Companies
> "Read joblens://companies and tell me what's available"
> <img width="792" height="427" alt="Screenshot 2026-09-08 at 9 42 00 AM" src="https://github.com/user-attachments/assets/07f0c781-3aa4-4055-bb19-ebb454298843" />

### 2. Job Requirements
> "Use JobLens to search for what Python frameworks Sarvam AI requires"
> <img width="792" height="427" alt="Screenshot 2026-09-08 at 9 42 54 AM" src="https://github.com/user-attachments/assets/9b2f8e2f-a905-41ac-95e9-68320ca1ce15" />


### 3. Skill Gap Analysis
> "Ask JobLens: Does the Haptik AI Engineer role require RAG experience?"
> <img width="792" height="331" alt="Screenshot 2026-09-08 at 9 43 13 AM" src="https://github.com/user-attachments/assets/2469e5bf-bd9e-4f3d-9d2c-2b66c2389d86" />


### 4. Career Advice
> "I know Python, SQL, Power BI, Tableau, FastAPI, and Snowflake.
Use JobLens to check my skill gap for Freshworks."
<img width="792" height="661" alt="Screenshot 2026-09-08 at 9 43 51 AM" src="https://github.com/user-attachments/assets/78f809c7-ba2d-48f2-8cc0-01cd64b21940" />


### 5. Multi-tool conversation:
> "I'm a BI developer with 1 year experience looking to switch to GenAI.
My skills are: Qlik Sense, Power BI, SQL, Python, FastAPI, Snowflake, AWS.
Which company in JobLens is the best match for me right now?
Then tell me the top 3 skills I need to learn for that company."
> <img width="502" height="635" alt="Screenshot 2026-09-08 at 9 44 28 AM" src="https://github.com/user-attachments/assets/a5397fa1-83e1-42e5-b991-c61d62b36c25" />

## Architecture
```
Claude Desktop (MCP Client)
         ↓ MCP Protocol
JobLens MCP Server (FastMCP)
         ↓
    ┌────┴────┐
    ↓         ↓
LangGraph   Qdrant Cloud
  Agent      (Vector DB)
    ↓
  Groq API
  (Llama 3.3)
```


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
