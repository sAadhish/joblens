# 🔎 JobLens

### AI-Powered Job Market Intelligence & Career Assistant

> **Understand the job market. Identify skill gaps. Improve your resume. Make career decisions with evidence.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python\&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?logo=fastapi\&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20AI-orange)](https://langchain-ai.github.io/langgraph/)
[![LangChain](https://img.shields.io/badge/LangChain-LCEL-blue)](https://www.langchain.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Cloud-purple)](https://qdrant.tech)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-black)](https://modelcontextprotocol.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker\&logoColor=white)](https://docker.com)

---

## 🚀 What is JobLens?

**JobLens is an AI-powered job market intelligence platform that helps technology professionals understand job requirements, analyze skill gaps, and interact with their career data using natural language.**

Instead of treating a resume as a static document, JobLens turns **job descriptions, resumes, semantic retrieval, conversational memory, and agentic reasoning** into an interactive career intelligence system.

The system is grounded in real indexed job descriptions and resume data, rather than relying purely on the LLM's general knowledge.

### The core idea

```text
Job Descriptions + Resume
            ↓
      Semantic Retrieval
            ↓
      LangGraph Agent
            ↓
   Evaluate Retrieved Context
            ↓
     Self-Correct if Needed
            ↓
       LLM Generation
            ↓
    Career Intelligence
```

JobLens was intentionally built beyond a basic "chat with your resume" application.

It includes:

* Agentic RAG
* Self-correcting retrieval
* Persistent conversational memory
* Skill-gap analysis
* Qdrant Cloud vector search
* MCP integration
* RAG evaluation
* LangSmith observability
* REST APIs
* Dockerized deployment

---

# ✨ Key Features

| Feature                       | Description                                                                                                 |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------- |
| 🤖 **LangGraph Career Agent** | Multi-step agent that classifies questions, routes retrieval, evaluates results, and retries when necessary |
| 🔄 **Self-Correcting RAG**    | Automatically reformulates queries and retries retrieval when the initial context is insufficient           |
| 🧠 **Persistent Memory**      | Multi-turn conversations using LangGraph checkpointers and isolated session/thread IDs                      |
| 🔍 **Semantic Job Search**    | Search indexed job descriptions using vector similarity and metadata filtering                              |
| 📄 **Resume Intelligence**    | Upload and index a resume PDF, then ask questions about your background                                     |
| 📊 **Skill Gap Analysis**     | Compare candidate skills against indexed job requirements                                                   |
| 🔌 **MCP Integration**        | Access JobLens directly from Claude Desktop and other MCP-compatible clients                                |
| 📡 **REST API**               | Async FastAPI backend with OpenAPI documentation and file upload support                                    |
| 📈 **RAG Evaluation**         | Hit Rate, MRR, Precision@K, Faithfulness and RAGAS-based evaluation                                         |
| 🔭 **Observability**          | LangSmith tracing and evaluation for LLM and RAG workflows                                                  |
| 🐳 **Dockerized**             | Run the application stack with Docker Compose                                                               |

---

# 🖥️ Application

## 💬 Career Assistant

Ask natural-language questions about job descriptions, your resume, skills, and career requirements.

Example:

```text
User:
"What does the Sarvam AI role require?"

        ↓

User:
"Do I have the skills for that?
I know Python, SQL, FastAPI and Snowflake."

        ↓

JobLens:
Uses the same session memory to understand
the context of the previous question.
```

The conversational agent maintains context across turns using a session/thread ID.

### Career Assistant UI

<img width="1440" alt="Career Assistant Chat" src="https://github.com/user-attachments/assets/5097987c-3e9d-48f8-802a-29e531daac73" />

---

## 📊 KPI Dashboard

Monitor:

* API health
* Qdrant connectivity
* Indexed data
* Job descriptions
* Vector database status

<img width="1440" alt="KPI Dashboard" src="https://github.com/user-attachments/assets/42ba8729-21f8-4b08-9ac7-3d394b0c5909" />

---

## 📥 Data Indexing

Job descriptions and resumes can be indexed directly through the application.

<img width="1440" alt="Data Indexing" src="https://github.com/user-attachments/assets/7b361c55-789a-4639-985b-13522facf039" />

---

# 🏗️ Architecture

```text
                         USER INTERFACES
                              │
             ┌────────────────┼────────────────┐
             │                │                │
          Web UI             CLI        Claude Desktop
             │                                 │
             │ HTTP                            │ MCP
             ↓                                 ↓
      ┌──────────────┐                  ┌──────────────┐
      │   FastAPI    │                  │ MCP Server   │
      │    Backend   │                  │  FastMCP     │
      └──────┬───────┘                  └──────┬───────┘
             │                                 │
             └──────────────┬──────────────────┘
                            ↓
                 ┌─────────────────────┐
                 │  LangGraph Agent    │
                 │                     │
                 │ load history        │
                 │      ↓              │
                 │ classify            │
                 │      ↓              │
                 │ route               │
                 │      ↓              │
                 │ retrieve            │
                 │      ↓              │
                 │ evaluate            │
                 │      ↓              │
                 │ generate            │
                 │      ↑              │
                 │ reformulate/retry   │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │  Retrieval Layer    │
                 │                     │
                 │ Qdrant Cloud        │
                 │ BGE Embeddings      │
                 │ LangChain RAG       │
                 │ Reranking           │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Generation Layer    │
                 │                     │
                 │ Groq                │
                 │ Llama 3.3 70B       │
                 │ LangSmith           │
                 └─────────────────────┘
```

The deployed system uses a web frontend, FastAPI backend, Qdrant Cloud for vector retrieval, and Groq for LLM inference.

---

# 🧠 How the Career Agent Works

The core of JobLens is a **LangGraph StateGraph** rather than a simple linear RAG chain.

```text
                    ┌──────────────┐
                    │ User Query   │
                    └──────┬───────┘
                           ↓
                  ┌─────────────────┐
                  │ Load History    │
                  └────────┬────────┘
                           ↓
                  ┌─────────────────┐
                  │ Classify Query  │
                  └────────┬────────┘
                           ↓
                  ┌─────────────────┐
                  │ Route Request   │
                  └────────┬────────┘
                           ↓
                  ┌─────────────────┐
                  │ Retrieve Context│
                  └────────┬────────┘
                           ↓
                  ┌─────────────────┐
                  │ Evaluate Context│
                  └───────┬─┬───────┘
                          │ │
                   Good ──┘ └── Bad
                    ↓             ↓
             ┌────────────┐  ┌──────────────┐
             │ Generate   │  │ Reformulate  │
             │ Answer     │  │ Query        │
             └─────┬──────┘  └──────┬───────┘
                   │                 │
                   ↓                 └──────→ Retrieve
                Response
```

The retrieval loop can reformulate and retry when the retrieved context is considered insufficient, with a maximum retry limit.

---

# 🔍 RAG Pipeline

JobLens uses a retrieval pipeline built around semantic embeddings and vector search.

```text
Document
   ↓
Load
   ↓
Chunk
   ↓
Embedding
   ↓
BGE-base-en-v1.5
   ↓
Qdrant Cloud
   ↓
Metadata Filtering
   ↓
Vector Retrieval
   ↓
Cross-Encoder Reranking
   ↓
Relevant Context
   ↓
LLM
```

The system uses `BAAI/bge-base-en-v1.5` embeddings and Qdrant Cloud for production vector storage.

---

# 🔌 MCP Integration

JobLens exposes its capabilities through the **Model Context Protocol (MCP)**.

This allows the career intelligence system to be consumed by MCP-compatible clients such as Claude Desktop.

### MCP Tools

```text
search_jobs
    ↓
Semantic search across indexed job descriptions

answer_career_question
    ↓
Grounded career Q&A through the LangGraph agent

check_skill_gap
    ↓
Compare candidate skills against job requirements
```

### MCP Resources

```text
joblens://companies
    → Indexed companies

joblens://resume
    → Candidate resume

joblens://jd/{company}
    → Full job description
```

This makes JobLens more than a standalone application. Its capabilities can also be exposed as reusable AI tools and resources.

---

# 📊 Evaluation

A major focus of the project was **measuring RAG quality rather than assuming retrieval works because the demo looks good.**

JobLens includes both custom evaluation and RAGAS/LangSmith-based evaluation.

| Metric            | Hand-Built RAG | LangChain RAG |
| ----------------- | -------------: | ------------: |
| Hit Rate          |           100% |             — |
| MRR               |           0.84 |             — |
| Precision@K       |            72% |             — |
| RAGAS Overall     |           ~78% |           48% |
| Custom Evaluation |            85% |           69% |
| Faithfulness      |            85% |             — |

The project deliberately documents the quality difference between the two implementations rather than hiding it.

### Why this matters

The project demonstrates an important engineering lesson:

> **Using an AI framework does not automatically produce a high-quality RAG system.**

Retrieval strategy, reranking, query formulation, evaluation, and confidence handling still determine the quality of the final system.

---

# 🧪 Two Implementations, One System

JobLens was intentionally implemented twice.

### 1. Hand-Built RAG

```text
Raw Python
    ↓
Custom RAG Pipeline
    ↓
ChromaDB
    ↓
Custom Evaluation
```

### 2. LangChain + LangGraph

```text
LangChain
    ↓
LCEL
    ↓
Qdrant Cloud
    ↓
LangGraph
    ↓
Persistent Memory
    ↓
MCP
    ↓
RAGAS + LangSmith
```

| Area         | Hand-Built           | LangChain / LangGraph    |
| ------------ | -------------------- | ------------------------ |
| RAG          | Raw Python libraries | LangChain LCEL           |
| Vector DB    | ChromaDB             | Qdrant Cloud             |
| Architecture | Functional / modular | OOP service architecture |
| Agents       | —                    | LangGraph StateGraph     |
| Memory       | —                    | Checkpointer             |
| MCP          | —                    | FastMCP                  |
| Evaluation   | Custom               | RAGAS + LangSmith        |

The purpose was to understand the underlying mechanics first and then demonstrate framework-level implementation.

---

# 💡 Engineering Decisions

## Why LangGraph?

LangGraph provides explicit state and node-level control over the agent workflow.

This makes it easier to implement:

* Conditional routing
* Retry loops
* State inspection
* Persistent memory
* Debugging
* Controlled agent workflows

Rather than treating the agent as a black box, the workflow is represented as an explicit graph.

---

## Why Self-Correcting RAG?

A traditional RAG pipeline looks like:

```text
Query → Retrieve → Generate
```

JobLens extends this to:

```text
Query
 ↓
Retrieve
 ↓
Evaluate
 ↓
 ├── Good → Generate
 │
 └── Poor → Reformulate
              ↓
           Retrieve Again
```

This allows the system to respond to retrieval failures instead of blindly generating an answer from poor context.

---

## Why Qdrant?

ChromaDB is used in the hand-built implementation for local experimentation.

Qdrant Cloud is used in the production-oriented implementation because it provides:

* Cloud-hosted vector storage
* Metadata/payload filtering
* Scalable vector search
* Production-oriented infrastructure

---

## Why MCP?

Instead of creating a custom integration for every AI client, JobLens exposes tools and resources through MCP.

```text
                    JobLens MCP Server
                           │
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
       Claude Desktop    Cursor       Other
                                      MCP Clients
```

One MCP interface can therefore expose the same underlying career intelligence capabilities to multiple compatible clients.

---

# 🛠️ Technology Stack

| Layer                   | Technology                          |
| ----------------------- | ----------------------------------- |
| **Language**            | Python 3.11+                        |
| **API**                 | FastAPI                             |
| **LLM**                 | Groq / Llama 3.3 70B                |
| **Embeddings**          | HuggingFace `BAAI/bge-base-en-v1.5` |
| **RAG Framework**       | LangChain                           |
| **Agent Orchestration** | LangGraph                           |
| **Vector Database**     | Qdrant Cloud                        |
| **Local Vector DB**     | ChromaDB                            |
| **Reranking**           | Cross-Encoder                       |
| **MCP**                 | FastMCP                             |
| **Evaluation**          | RAGAS + Custom Evaluator            |
| **Observability**       | LangSmith                           |
| **Frontend**            | Vanilla HTML / CSS / JavaScript     |
| **Deployment**          | Docker + Docker Compose             |

---

# 📁 Project Structure

```text
joblens/
│
├── joblens/
│   ├── stage-1-core-genai/
│   │   └── embeddings, vector DB, prompting
│   │
│   ├── evaluation/
│   │   └── custom RAG evaluation
│   │
│   └── ...
│
└── joblens_langchain/
    │
    ├── api/
    │   ├── routes/
    │   │   ├── chat.py
    │   │   ├── index.py
    │   │   └── health.py
    │   │
    │   └── schemas.py
    │
    ├── graphs/
    │   ├── career_agent_graph.py
    │   ├── conversation_graph.py
    │   ├── rag_graph.py
    │   ├── nodes.py
    │   └── state.py
    │
    ├── mcp_server/
    │   ├── server.py
    │   ├── tools.py
    │   ├── resources.py
    │   └── DEMO.md
    │
    ├── services/
    │   ├── career_service.py
    │   ├── rag_service.py
    │   ├── vector_service.py
    │   ├── ingestion_service.py
    │   └── llm_service.py
    │
    ├── evaluation/
    │   ├── ragas_eval.py
    │   ├── langsmith_eval.py
    │   └── eval_dataset.py
    │
    ├── career_assistant.py
    └── docker-compose.yml
```

---

# 🚀 Quick Start

## Prerequisites

* Python 3.11+
* Docker & Docker Compose
* Groq API key
* Qdrant Cloud account/API key
* LangSmith account/API key for observability and evaluation

---

## 1. Clone the Repository

```bash
git clone https://github.com/sAadhish/joblens.git

cd joblens/joblens_langchain
```

---

## 2. Configure Environment

```bash
cp .env.example .env
```

Add the required credentials:

```env
# Groq
GROQ_API_KEY=your_groq_key

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key
QDRANT_COLLECTION=Joblens

# LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=joblens
```

---

## 3. Start with Docker

```bash
docker compose up -d
```

Open:

```text
http://localhost:8081/app/
```

Stop the application:

```bash
docker compose down
```

---

# 🧑‍💻 Development Setup

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
PYTHONPATH="$(pwd):$(pwd)/joblens_langchain" \
uvicorn api.main:app \
--host 127.0.0.1 \
--port 8080 \
--reload
```

Application:

```text
http://127.0.0.1:8080/app/
```

API documentation:

```text
http://127.0.0.1:8080/docs
```

---

# 📡 API

| Method   | Endpoint        | Purpose                         |
| -------- | --------------- | ------------------------------- |
| `POST`   | `/chat`         | Multi-turn career assistant     |
| `POST`   | `/index/jd`     | Index a job description         |
| `POST`   | `/index/resume` | Upload and index resume         |
| `GET`    | `/companies`    | List indexed companies          |
| `GET`    | `/health`       | API + Qdrant health check       |
| `DELETE` | `/session/{id}` | Clear conversation history      |
| `GET`    | `/docs`         | Swagger / OpenAPI documentation |

---

# 💬 API Example

### First conversation turn

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What does the Sarvam AI role require?",
    "session_id": "user_001"
  }'
```

### Follow-up question

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Do I have the skills for that? I know Python, SQL, FastAPI and Snowflake",
    "session_id": "user_001"
  }'
```

The same `session_id` allows the agent to maintain conversational context.

---

# 🌐 Deployment

The production-oriented architecture separates frontend and backend services:

```text
                    Internet
                       │
                       ↓
              ┌─────────────────┐
              │    Vercel       │
              │    Frontend     │
              └────────┬────────┘
                       │ HTTPS
                       ↓
              ┌─────────────────┐
              │     Render      │
              │  FastAPI API    │
              └───────┬─┬───────┘
                      │ │
             ┌────────┘ └─────────┐
             ↓                    ↓
       ┌───────────┐        ┌───────────┐
       │  Qdrant   │        │   Groq    │
       │   Cloud   │        │    LLM    │
       └───────────┘        └───────────┘
```

### Current deployment stack

* **Frontend:** Vercel
* **Backend:** Render
* **Vector Database:** Qdrant Cloud
* **LLM:** Groq
* **Containerization:** Docker

---

# ⚠️ Free-Tier Considerations

The deployed system is designed to operate using free/hobby-tier infrastructure.

Potential limitations include:

* Render cold starts
* Limited memory for embedding models
* Groq API rate limits
* Qdrant Cloud resource limits
* Initial model-loading latency

These constraints are useful for development and demonstration, but production workloads would require appropriate infrastructure sizing.

---

# 🌱 Development Journey

JobLens was developed incrementally rather than as a single application.

```text
Stage 1
Core GenAI
   ↓
Embeddings
   ↓
Vector Search
   ↓
Prompt Engineering
        │
        ↓
Stage 2
RAG
   ↓
Retrieval Evaluation
   ↓
Hybrid Search
   ↓
Reranking
        │
        ↓
Stage 3
LangChain
   ↓
LCEL
   ↓
Qdrant Cloud
   ↓
LangSmith
        │
        ↓
Stage 4
LangGraph
   ↓
Agentic Workflows
   ↓
Persistent Memory
   ↓
Self-Correcting RAG
        │
        ↓
Stage 5
MCP
   ↓
Claude Desktop
   ↓
Reusable AI Tools
        │
        ↓
Deployment
   ↓
FastAPI + Docker
   ↓
Cloud Infrastructure
```

The repository therefore represents an evolution from understanding individual GenAI components to building and deploying a complete AI application.

---

# 🌿 Branch Structure

```text
stage-1-core-genai
        │
        ├── LLM fundamentals
        ├── Embeddings
        ├── Vector databases
        └── Prompt engineering
                ↓
stage-2-rag
        │
        ├── RAG
        ├── Evaluation
        ├── Hybrid search
        └── Reranking
                ↓
stage-3-langchain
        │
        ├── LangChain
        ├── LCEL
        ├── Qdrant Cloud
        └── LangSmith
                ↓
stage-4-langgraph
        │
        ├── Agents
        ├── StateGraph
        ├── Memory
        └── Self-correcting RAG
                ↓
mcp
        │
        └── MCP + Claude Desktop
                ↓
main
        │
        └── Production-oriented application
```

---

# 🎯 What This Project Demonstrates

JobLens brings together several areas of modern AI engineering:

```text
                 ┌──────────────────┐
                 │   LLM Engineering│
                 └────────┬─────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
      RAG            AI Agents          MCP
        │                 │                 │
        ↓                 ↓                 ↓
   Retrieval         LangGraph        Tool Calling
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ↓
                    AI Application
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
     FastAPI          Evaluation       Observability
        │                 │                 │
        ↓                 ↓                 ↓
      Docker          RAGAS           LangSmith
                          │
                          ↓
                    Cloud Deployment
```

---

# 👨‍💻 About

Built by **Aadhish S**, transitioning from enterprise BI development into GenAI engineering.

JobLens represents a hands-on engineering journey covering:

* Generative AI
* RAG systems
* Vector databases
* LangChain
* LangGraph
* AI agents
* MCP
* Evaluation
* Observability
* FastAPI
* Docker
* Cloud deployment

The project intentionally documents the engineering process, including architectural decisions, experimentation, evaluation results, and the differences between framework-based and hand-built implementations.

### 🔗 Links

**GitHub:** https://github.com/sAadhish

**LinkedIn:** https://linkedin.com/in/aadhish-s

---

# ⭐ If You Find This Interesting

Feel free to explore the repository, experiment with the architecture, and build on top of it.

```text
Learn → Build → Evaluate → Debug → Improve → Deploy
```

That's the entire philosophy behind JobLens.

---

<p align="center">

### 🔎 JobLens

**From job descriptions to career intelligence.**

Built with Python • LangGraph • LangChain • Qdrant • FastAPI • MCP

🚀

</p>
