# JobLens — AI Job Market Intelligence Platform

> Built across a structured 100-day GenAI engineering journey.
> Two implementations, one project: hand-built RAG and LangChain/LangGraph.

---

## Architecture Overview

┌─────────────────────────────────────────────────────────┐
│ USER INTERFACES │
│ CLI (career_assistant.py) │ Claude Desktop (MCP) │
└──────────────┬──────────────┴────────────┬──────────────┘
↓ ↓
┌──────────────────────────┐ ┌────────────────────────────┐
│ LangGraph Career Agent │ │ MCP Server (FastMCP) │
│ ├── classify_node │ │ ├── search_jobs tool │
│ ├── jd_retrieve_node │ │ ├── answer_question tool │
│ ├── resume_retrieve │ │ ├── check_skill_gap tool │
│ ├── generate_node │ │ ├── companies resource │
│ ├── evaluate_node │ │ ├── resume resource │
│ └── reformulate_node │ │ └── jd/{company} resource│
└──────────────┬────────────┘ └────────────┬───────────────┘
└──────────────┬─────────────┘
↓
┌─────────────────────────────────────────────────────────┐
│ RETRIEVAL LAYER │
│ Qdrant Cloud (Vector DB) │ HuggingFace Embeddings │
│ LangChain RAG Service │ Cross-encoder Reranking │
└─────────────────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────────────┐
│ GENERATION LAYER │
│ Groq API (Llama 3.3 70B) │ LangSmith Observability │
└─────────────────────────────────────────────────────────┘


## Two Implementations — One Project

| Feature | Hand-built (`joblens/`) | LangChain (`joblens_langchain/`) |
|---------|------------------------|----------------------------------|
| RAG Pipeline | Raw libraries | LangChain LCEL |
| Vector DB | ChromaDB (local) | Qdrant Cloud |
| Architecture | Functional | OOP (Services) |
| Evaluation | Custom + RAGAS | RAGAS + LangSmith |
| Agents | — | LangGraph |
| Memory | — | Checkpointer |
| MCP Server | — | FastMCP |
| Score (RAGAS) | ~78% (with reranking) | 48% (baseline RAG) |

## Key Engineering Decisions

**Why two implementations?**
Built hand-built first to understand internals deeply.
Refactored to LangChain after — can explain exactly what the framework abstracts and what it hides.

**Why Qdrant over ChromaDB in production?**
Purpose-built vector database with payload indexing, filtering at scale, and cloud hosting.
ChromaDB is excellent for learning — Qdrant is what production runs.

**Why LangGraph over LangChain AgentExecutor?**
Full state visibility, debuggable node-by-node, supports conditional routing and loops.
AgentExecutor is a black box — LangGraph is transparent.

**Why MCP over a custom API?**
MCP is a universal standard — one server, any compatible client.
Claude Desktop, Cursor, Cline, custom agents — all can call JobLens without custom integration code.

**Why self-correcting RAG?**
A system that detects its own failures and retries is more reliable than one that returns bad answers silently.
The evaluate → reformulate → retry loop improves answer quality without user intervention.

## Evaluation Results

| Metric | Hand-built RAG | LangChain RAG |
|--------|---------------|---------------|
| Hit Rate | 100% | — |
| MRR | 0.84 | — |
| RAGAS Overall | ~78% | 48% |
| Hand-built Eval | 85% | 69% |

The gap: LangChain version lacks cross-encoder reranking and hybrid search.
These are architectural choices, not framework limitations.

## Setup

```bash
git clone https://github.com/sAadhish/joblens
cd joblens

# Hand-built version
cd joblens
pip install -r requirements.txt
cp .env.example .env  # add your keys
python main.py

# LangChain version
cd joblens_langchain
pip install -r requirements.txt
cp .env.example .env  # add your keys
python main.py        # index data
python career_assistant.py  # run CLI

# MCP Server (for Claude Desktop)
python mcp_server/server.py
# See mcp_server/DEMO.md for Claude Desktop setup
```

## Tech Stack

LLM : Groq API (Llama 3.3 70B)
Embeddings : HuggingFace (BAAI/bge-base-en-v1.5)
Vector DB : Qdrant Cloud + ChromaDB
Orchestration: LangGraph (StateGraph + Checkpointer)
Framework : LangChain LCEL + OOP services
MCP : FastMCP (Claude Desktop integration)
Evaluation : RAGAS + custom evaluator + LangSmith
Observability: LangSmith tracing
Language : Python 3.11+
Deployment : Docker (Day 101)

## Branch Structure
stage-1-core-genai → LLMs, embeddings, vector DB fundamentals
stage-2-rag → RAG pipeline, evaluation, hybrid search
stage-3-langchain → LangChain OOP, Qdrant, RAGAS
stage-4-langgraph → LangGraph agents, memory, MCP server
mcp → MCP server with Claude Desktop integration
