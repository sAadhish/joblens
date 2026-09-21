# 🔎 JobLens
### AI-Powered Job Market Intelligence & Career Assistant

> Built across a structured 100-day GenAI engineering journey — from raw embeddings to a fully deployed, MCP-integrated AI system.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Cloud-purple.svg)](https://qdrant.tech)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)
[![MCP](https://img.shields.io/badge/MCP-Claude%20Desktop-black.svg)](https://modelcontextprotocol.io)

---

## What is JobLens?

JobLens is a production-grade AI system that helps tech professionals make smarter career decisions using semantic search, RAG, and LLM-powered analysis — grounded entirely in real job descriptions and resume data.

**Not another resume analyzer.** JobLens combines a self-correcting LangGraph agent, a multi-turn conversational interface, Qdrant Cloud vector search, and an MCP server that makes the entire system callable directly from Claude Desktop.

---

## Screenshots

### Career Assistant Chat
Interact with the LangGraph agent for personalized career advice grounded in indexed JDs and resumes.

<img width="1440" alt="Career Assistant Chat" src="https://github.com/user-attachments/assets/5097987c-3e9d-48f8-802a-29e531daac73" />

### KPI Dashboard
Monitor API health, vector database status, and manage indexed job descriptions.

<img width="1440" alt="KPI Dashboard" src="https://github.com/user-attachments/assets/42ba8729-21f8-4b08-9ac7-3d394b0c5909" />

### Data Indexing
Index job descriptions and resumes directly through the UI.

<img width="1440" alt="Data Indexing" src="https://github.com/user-attachments/assets/7b361c55-789a-4639-985b-13522facf039" />

---

## Features

| Feature | Description |
|---------|-------------|
| 🤖 **LangGraph Career Agent** | Self-correcting multi-step agent — classifies questions, routes to the right retrieval path, reformulates bad queries and retries automatically |
| 🧠 **Persistent Memory** | Conversation history across turns using LangGraph checkpointers — each session isolated by thread ID |
| 🔍 **Semantic Job Search** | Qdrant Cloud vector search with metadata filtering — search by role type, location, experience level |
| 📄 **Resume Analysis** | Index your resume, ask natural language questions about your own background |
| 📊 **Skill Gap Analysis** | Compare your skills against any indexed company's JD — get matching skills, missing skills, and a readiness score |
| 🔌 **MCP Integration** | Entire system callable from Claude Desktop via Model Context Protocol — tools + resources |
| 📡 **REST API** | FastAPI with async endpoints, OpenAPI docs, session management, file upload support |
| 🐳 **Fully Dockerized** | Single `docker compose up` runs the entire stack — API + frontend UI |
| 📈 **RAG Evaluation** | Production-grade eval pipeline: Hit Rate, MRR, Precision@K, Faithfulness via RAGAS + custom evaluator |
| 🔭 **LangSmith Observability** | Every LLM call traced, evaluated, and monitored out of the box |

---

## Quick Start (Docker)

```bash
git clone https://github.com/sAadhish/joblens.git
cd joblens/joblens_langchain

cp .env.example .env
# Add your GROQ_API_KEY, QDRANT_API_KEY, QDRANT_URL to .env

docker compose up -d
```

Open **[http://localhost:8081/app/](http://localhost:8081/app/)**

```bash
docker compose down   # to stop
```

---

## Manual Run (Development)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

PYTHONPATH="$(pwd):$(pwd)/joblens_langchain" \
  uvicorn api.main:app --host 127.0.0.1 --port 8080 --reload
```

Open **[http://127.0.0.1:8080/app/](http://127.0.0.1:8080/app/)**

---

## API Endpoints

```
POST   /chat                 → multi-turn career agent (session_id for memory)
POST   /index/jd             → index a job description from text
POST   /index/resume         → index a resume PDF (file upload)
GET    /companies            → list all indexed companies
GET    /health               → API + Qdrant health check
DELETE /session/{id}         → clear conversation history
GET    /docs                 → interactive OpenAPI documentation
```

### Example Chat (Multi-turn with Memory)

```bash
# Turn 1
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What does the Sarvam AI role require?", "session_id": "user_001"}'

# Turn 2 — agent remembers Turn 1
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Do I have the skills for that? I know Python, SQL, FastAPI, Snowflake", "session_id": "user_001"}'
```

---

## MCP Integration (Claude Desktop)

JobLens exposes a full MCP server — callable from Claude Desktop or any MCP-compatible client.

```json
{
  "mcpServers": {
    "joblens": {
      "command": "python",
      "args": ["/path/to/joblens_langchain/mcp_server/server.py"],
      "env": {
        "GROQ_API_KEY": "...",
        "QDRANT_URL": "...",
        "QDRANT_API_KEY": "..."
      }
    }
  }
}
```

**Available MCP Tools:**
- `search_jobs` — semantic search across indexed JDs
- `answer_career_question` — grounded Q&A via LangGraph agent
- `check_skill_gap` — compare skills vs JD requirements

**Available MCP Resources:**
- `joblens://companies` — list of indexed companies
- `joblens://resume` — candidate's resume content
- `joblens://jd/{company}` — full JD for any indexed company

See [`mcp_server/DEMO.md`](joblens_langchain/mcp_server/DEMO.md) for full Claude Desktop setup and example conversations.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      USER INTERFACES                          │
│   Web UI (Glassmorphism)  │  CLI  │  Claude Desktop (MCP)    │
└────────────┬──────────────┴───────┴────────────┬─────────────┘
             ↓                                   ↓
┌────────────────────────┐         ┌─────────────────────────┐
│     FastAPI (Async)    │         │    MCP Server (FastMCP) │
│  /chat  /index  /health│         │  Tools + Resources      │
└────────────┬───────────┘         └────────────┬────────────┘
             └────────────────┬─────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph Career Agent                      │
│  load_history → classify → route → retrieve → generate      │
│              ↑                          ↓                    │
│         reformulate ← evaluate ←───────┘                    │
│  (self-corrects on bad answers, max 2 retries)              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     RETRIEVAL LAYER                          │
│   Qdrant Cloud (Vector DB)  │  HuggingFace bge-base-en-v1.5 │
│   LangChain RAG Service     │  Cross-encoder Reranking       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    GENERATION LAYER                          │
│   Groq (Llama 3.3 70B)  │  LangSmith Observability         │
└─────────────────────────────────────────────────────────────┘
```

---

## Two Implementations — One Project

This project was built twice, intentionally:

| | Hand-built (`joblens/`) | LangChain (`joblens_langchain/`) |
|---|---|---|
| **RAG Pipeline** | Raw Python libraries | LangChain LCEL |
| **Vector DB** | ChromaDB (local) | Qdrant Cloud |
| **Architecture** | Functional / modular | OOP — Service classes |
| **Agents** | — | LangGraph StateGraph |
| **Memory** | — | Checkpointer (MemorySaver) |
| **MCP Server** | — | FastMCP |
| **Evaluation** | Custom evaluator | RAGAS + LangSmith |
| **RAGAS Score** | ~78% (with reranking) | 48% (baseline) |

**Why build it twice?**
The hand-built version exists to prove deep understanding — every component built from scratch. The LangChain version shows framework fluency. The RAGAS score gap (78% vs 48%) proves that LangChain doesn't give you quality for free — the same retrieval improvements (reranking, hybrid search) apply regardless of framework.

---

## Key Engineering Decisions

**Why LangGraph over LangChain AgentExecutor?**
Full state visibility at every node. Debuggable step by step. Supports conditional routing and retry loops. AgentExecutor is a black box — LangGraph is transparent. In production, transparency wins.

**Why self-correcting RAG?**
A system that detects its own failures and retries is more reliable than one that silently returns bad answers. The evaluate → reformulate → retrieve → generate loop improves answer quality without user intervention.

**Why Qdrant over ChromaDB in production?**
Purpose-built vector database with payload indexing, filtered search at scale, and cloud hosting. ChromaDB is excellent for learning and local development. Qdrant is what production runs on.

**Why MCP over a custom API for Claude Desktop?**
MCP is a universal standard — one server implementation, any compatible client. Claude Desktop, Cursor, Cline, and custom LangGraph agents can all call JobLens without custom integration code per client.

**Why two evaluation systems (custom + RAGAS)?**
Different tools for different purposes. The custom evaluator runs fast on every commit — binary pass/fail regression detection. RAGAS runs on significant pipeline changes — continuous scores for Faithfulness, Context Recall, Answer Relevancy. Both together give complete coverage.

---

## Evaluation Results

| Metric | Hand-built RAG | LangChain RAG |
|--------|---------------|---------------|
| Hit Rate | 100% | — |
| MRR | 0.84 | — |
| Precision@K | 72% | — |
| RAGAS Overall | ~78% | 48% |
| Custom Eval | 85% | 69% |
| Faithfulness | 85% | — |

The 48% vs 78% gap is documented and explained — the LangChain version is an intentional baseline to demonstrate that framework choice doesn't determine quality. Architectural decisions (reranking, hybrid search, confidence thresholds) do.

---

## Tech Stack

```
LLM              Groq API — Llama 3.3 70B (lightning-fast inference)
Embeddings       HuggingFace — BAAI/bge-base-en-v1.5
Vector DB        Qdrant Cloud (production) + ChromaDB (hand-built version)
Orchestration    LangGraph — StateGraph + Checkpointer
Framework        LangChain LCEL + OOP service architecture
MCP              FastMCP — Claude Desktop integration
Evaluation       RAGAS + custom evaluator (Hit Rate, MRR, Faithfulness)
Observability    LangSmith — tracing, evaluation, cost tracking
API              FastAPI — async, OpenAPI docs, file upload
Frontend         Vanilla JS/HTML/CSS — Glassmorphism UI
Deployment       Docker + Docker Compose
Language         Python 3.11+
```

---

## Branch Structure

```
stage-1-core-genai    →  LLMs, embeddings, vector DB, prompt engineering
stage-2-rag           →  RAG pipeline, evaluation, hybrid search, RAGAS
stage-3-langchain     →  LangChain OOP, Qdrant Cloud, LCEL, LangSmith
stage-4-langgraph     →  LangGraph agents, checkpointer memory, MCP server
mcp                   →  MCP server + Claude Desktop integration
main                  →  Production-ready: FastAPI + Docker + full system
```

Each branch represents a distinct architectural phase — not just code, but a progression in how AI systems are built and why.

---

## Project Structure

```
joblens/
├── joblens/                        ← Hand-built RAG (Stage 1-2)
│   ├── stage-1-core-genai/         ← Embeddings, vector DB, prompting
│   ├── evaluation/                 ← Custom evaluator: Hit Rate, MRR, Faithfulness
│   └── ...
└── joblens_langchain/              ← LangChain + LangGraph (Stage 3-4)
    ├── api/                        ← FastAPI endpoints
    │   ├── routes/
    │   │   ├── chat.py             ← /chat with session memory
    │   │   ├── index.py            ← /index/jd and /index/resume
    │   │   └── health.py           ← /health and /companies
    │   └── schemas.py              ← Pydantic request/response models
    ├── graphs/                     ← LangGraph
    │   ├── career_agent_graph.py   ← Full career agent
    │   ├── conversation_graph.py   ← Conversation with memory
    │   ├── rag_graph.py            ← Self-correcting RAG
    │   ├── nodes.py                ← All node functions
    │   └── state.py                ← State schemas
    ├── mcp_server/                 ← MCP integration
    │   ├── server.py               ← FastMCP server
    │   ├── tools.py                ← Tool implementations
    │   ├── resources.py            ← MCP resources
    │   └── DEMO.md                 ← Claude Desktop setup + examples
    ├── services/                   ← OOP service layer
    │   ├── career_service.py       ← Facade — coordinates all services
    │   ├── rag_service.py          ← RAG pipeline (LCEL)
    │   ├── vector_service.py       ← Qdrant operations
    │   ├── ingestion_service.py    ← Document loading + chunking
    │   └── llm_service.py          ← LLM singleton
    ├── evaluation/                 ← Evaluation pipeline
    │   ├── ragas_eval.py           ← RAGAS metrics
    │   ├── langsmith_eval.py       ← LangSmith experiments
    │   └── eval_dataset.py         ← Ground truth + hard negatives
    ├── career_assistant.py         ← CLI entry point
    └── docker-compose.yml          ← Full stack in one command
```

---

## Environment Variables

```env
# Required
GROQ_API_KEY=your_groq_key

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key
QDRANT_COLLECTION=Joblens

# LangSmith (optional but recommended)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=joblens
```

---

## About

Built by **Aadhish S** — BI Developer transitioning into GenAI Engineering.

This repository documents a real 100-day learning journey — not polished tutorials, but genuine engineering decisions, real bugs, documented fixes, and measurable improvements. Every architectural choice has a reason. Every evaluation score has a story.

**GitHub:** [github.com/sAadhish](https://github.com/sAadhish)
**LinkedIn:** [linkedin.com/in/aadhish-s](https://linkedin.com/in/aadhish-s)

---

*Built with curiosity, iteration, and a lot of debugging. 🚀*
