# 🔎 JobLens
### AI-Powered Job Market Intelligence & Career Assistant

> **Understand the job market. Identify skill gaps. Improve your resume. Find better opportunities.**

JobLens is an **AI-powered job market intelligence platform** built as part of a structured **100-day Generative AI engineering journey**.

The project started as a **hand-built RAG system** to understand the fundamentals from first principles, and was later rebuilt using **LangChain + LangGraph + MCP** to explore production-oriented AI application architecture.

It combines:

**RAG · Semantic Search · Reranking · Agents · Memory · Evaluation · Observability · MCP**

---

## ✨ What is JobLens?

JobLens helps you interact with job-market data using natural language.

You can ask questions like:

```text
"What skills are most common in ML Engineer jobs?"

"How does my resume compare with this job description?"

"What skills am I missing for an AI Engineer role?"

"Find companies hiring for GenAI positions."

"Which technologies appear most frequently in these job descriptions?"
```

Instead of simply generating an answer, JobLens retrieves relevant information from a job/resume knowledge base and uses an LLM to produce a grounded response.

### 🎯 Core Capabilities

| Capability | Description |
|---|---|
| 🔍 **Semantic Job Search** | Find relevant jobs using natural-language queries |
| 📄 **Resume Analysis** | Retrieve and analyze relevant resume information |
| 🧩 **Skill Gap Analysis** | Identify missing skills against job requirements |
| 🤖 **Career Agent** | Multi-step reasoning with LangGraph |
| 🧠 **Memory** | Persistent conversational state with checkpointers |
| 🔄 **Self-Correcting RAG** | Detect weak answers and retry retrieval |
| 📊 **Evaluation** | RAGAS + custom retrieval evaluation |
| 🔭 **Observability** | LangSmith tracing and monitoring |
| 🔌 **MCP Integration** | Use JobLens from Claude Desktop and other MCP clients |

---

# 🏗️ Architecture

JobLens is designed as a layered AI application.

```text
                         ┌─────────────────────────────┐
                         │        USER INTERFACES       │
                         │                             │
                         │  CLI       Claude Desktop   │
                         │  ↓              ↓           │
                         └──────────────┬──────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │       AI ORCHESTRATION      │
                         │                             │
                         │      LangGraph Agent        │
                         │                             │
                         │  ┌───────────────────────┐  │
                         │  │ classify_node         │  │
                         │  │ jd_retrieve_node      │  │
                         │  │ resume_retrieve_node  │  │
                         │  │ generate_node         │  │
                         │  │ evaluate_node         │  │
                         │  │ reformulate_node      │  │
                         │  └───────────────────────┘  │
                         └──────────────┬──────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │        RETRIEVAL LAYER      │
                         │                             │
                         │ Qdrant Cloud                │
                         │ HuggingFace Embeddings      │
                         │ LangChain RAG Services      │
                         │ Cross-Encoder Reranking     │
                         └──────────────┬──────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │       GENERATION LAYER      │
                         │                             │
                         │ Groq API                    │
                         │ Llama 3.3 70B               │
                         │ LangSmith Observability     │
                         └─────────────────────────────┘
```

### 🔌 MCP Architecture

JobLens can also expose its capabilities through **Model Context Protocol (MCP)**.

```text
                         ┌──────────────────────┐
                         │   Claude Desktop     │
                         └──────────┬───────────┘
                                    │
                                    │ MCP
                                    ▼
                         ┌──────────────────────┐
                         │    FastMCP Server    │
                         │                      │
                         │  search_jobs         │
                         │  answer_question     │
                         │  check_skill_gap     │
                         │                      │
                         │  Resources:          │
                         │  companies           │
                         │  resume              │
                         │  jd/{company}        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                              JobLens RAG
```

This allows JobLens to be consumed by MCP-compatible clients without building a separate custom integration for every application.

---

# 🧠 Two Implementations — One Project

One of the core goals of JobLens was to understand **what happens underneath AI frameworks**.

So the project contains two implementations of the same underlying system.

### 🛠️ Hand-Built RAG

Built using lower-level libraries to understand:

- Document ingestion
- Chunking
- Embeddings
- Vector search
- Retrieval
- Reranking
- Prompt construction
- Generation
- Evaluation

### ⚡ LangChain / LangGraph

The system was then refactored into a more modular architecture using:

- LangChain LCEL
- Service-oriented OOP
- Qdrant
- LangGraph
- Checkpointers
- RAGAS
- LangSmith
- FastMCP

| Feature | 🛠️ Hand-Built | ⚡ LangChain / LangGraph |
|---|---|---|
| RAG Pipeline | Raw libraries | LangChain LCEL |
| Vector DB | ChromaDB | Qdrant Cloud |
| Architecture | Functional | OOP Services |
| Reranking | ✅ Cross-Encoder | 🚧 Baseline |
| Hybrid Search | ✅ | 🚧 |
| Evaluation | Custom + RAGAS | RAGAS + LangSmith |
| Agents | — | LangGraph |
| Memory | — | Checkpointer |
| MCP | — | FastMCP |
| Observability | Custom | LangSmith |
| Production Focus | Learning | Production-oriented |

> **The goal wasn't to choose a framework blindly. It was to understand what the framework actually abstracts.**

---

# 📊 Evaluation

Retrieval quality matters more than simply getting an LLM to generate fluent answers.

JobLens therefore includes both **retrieval metrics** and **end-to-end RAG evaluation**.

### Retrieval Performance

| Metric | Hand-Built RAG | LangChain RAG |
|---|---:|---:|
| 🎯 Hit Rate | **100%** | — |
| 🥇 MRR | **0.84** | — |
| 📈 RAGAS Overall | **~78%** | **48%** |
| 🧪 Custom Evaluation | **85%** | **69%** |

### Why is the LangChain score lower?

The LangChain implementation currently uses a more basic retrieval pipeline.

The hand-built implementation includes:

```text
Query
  │
  ▼
Vector Search
  │
  ▼
Candidate Retrieval
  │
  ▼
Cross-Encoder Reranking
  │
  ▼
Relevant Context
  │
  ▼
LLM
```

The LangChain baseline currently lacks:

- Cross-encoder reranking
- Hybrid search

These are **retrieval architecture differences**, not limitations of LangChain itself.

### 🚀 Next Retrieval Improvements

```text
Dense Retrieval
      +
Sparse Retrieval
      ↓
Hybrid Search
      ↓
Cross-Encoder Reranking
      ↓
Context Compression
      ↓
LLM Generation
```

---

# 🔄 Self-Correcting RAG

Traditional RAG often follows:

```text
Question
   ↓
Retrieve
   ↓
Generate
   ↓
Answer
```

JobLens introduces an evaluation loop:

```text
                  ┌──────────────┐
                  │    Question  │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │  Classify    │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │   Retrieve   │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │   Generate   │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │   Evaluate   │
                  └──────┬───────┘
                         │
                 ┌───────┴────────┐
                 │                │
              Good?             Poor?
                 │                │
                 ↓                ↓
               Answer       Reformulate
                                  │
                                  └──────► Retrieve
```

The idea is simple:

> **If retrieval or generation produces a weak result, don't silently return it — try again.**

This makes the system more robust to poorly phrased or ambiguous queries.

---

# 🧩 Why These Technologies?

## Why build two implementations?

The hand-built implementation came first.

This made it possible to understand the internals of:

- Embedding generation
- Similarity search
- Retrieval pipelines
- Reranking
- Prompt construction
- Evaluation

Only after understanding those pieces was the system rebuilt with LangChain.

> **Learn the abstraction before relying on the abstraction.**

---

## Why Qdrant instead of ChromaDB?

**ChromaDB** is excellent for learning and local experimentation.

**Qdrant** was chosen for the production-oriented implementation because of:

- Cloud hosting
- Payload filtering
- Indexing
- Scalable vector search
- Metadata-aware retrieval

The project therefore uses:

```text
ChromaDB → Learning / local RAG

Qdrant → Production-oriented RAG
```

---

## Why LangGraph?

Instead of treating an agent as a black box, LangGraph makes the workflow explicit.

```text
State
 ↓
Node
 ↓
State
 ↓
Conditional Edge
 ↓
Node
 ↓
State
```

This gives JobLens:

- Explicit state management
- Conditional routing
- Loops
- Debuggable execution
- Memory/checkpointing
- Node-level observability

The agent is therefore easier to reason about and debug.

---

## Why MCP?

Instead of building a custom API for every AI client, JobLens exposes its capabilities through **Model Context Protocol**.

One server can potentially serve:

```text
Claude Desktop
      │
Cursor
      │
Cline
      │
Custom Agents
      │
Other MCP Clients
      │
      ▼
   JobLens MCP
```

This makes the system reusable beyond the CLI.

---

# 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| 🧠 LLM | Groq API · Llama 3.3 70B |
| 🔢 Embeddings | HuggingFace · BAAI/bge-base-en-v1.5 |
| 🗄️ Vector DB | Qdrant Cloud |
| 💾 Local Vector DB | ChromaDB |
| 🔗 Framework | LangChain LCEL |
| 🤖 Agents | LangGraph |
| 🧠 Memory | LangGraph Checkpointer |
| 🔌 Protocol | FastMCP |
| 📊 Evaluation | RAGAS + Custom Evaluator |
| 🔭 Observability | LangSmith |
| 🐍 Language | Python 3.11+ |
| 🐳 Deployment | Docker |

---

# 📁 Project Structure

```text
joblens/
│
├── joblens/                       # Hand-built RAG
│   ├── ingestion/
│   ├── retrieval/
│   ├── generation/
│   ├── evaluation/
│   └── main.py
│
├── joblens_langchain/             # LangChain implementation
│   ├── services/
│   ├── agents/
│   ├── retrieval/
│   ├── evaluation/
│   ├── career_assistant.py
│   └── main.py
│
├── mcp_server/                    # MCP integration
│   ├── server.py
│   └── DEMO.md
│
├── data/                          # Job / resume data
│
├── requirements.txt
├── .env.example
└── README.md
```

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/sAadhish/joblens.git
cd joblens
```

## 2. Hand-Built RAG

```bash
cd joblens

pip install -r requirements.txt

cp .env.example .env
```

Add your API keys and configuration to `.env`.

Then:

```bash
python main.py
```

---

## 3. LangChain / LangGraph Version

```bash
cd joblens_langchain

pip install -r requirements.txt

cp .env.example .env
```

Index the data:

```bash
python main.py
```

Start the career assistant:

```bash
python career_assistant.py
```

---

## 4. MCP Server

Start the MCP server:

```bash
python mcp_server/server.py
```

For Claude Desktop configuration and examples, see:

```text
mcp_server/DEMO.md
```

---

# 🧪 Example Workflow

A typical career-analysis query flows through the system like this:

```text
User
 │
 │ "What skills am I missing for an AI Engineer role?"
 ▼
Classifier
 │
 ▼
Job Retrieval ──────────► Qdrant
 │
 ▼
Resume Retrieval ───────► Qdrant
 │
 ▼
Reranking
 │
 ▼
Context Construction
 │
 ▼
Llama 3.3 70B
 │
 ▼
Evaluation
 │
 ├── Good ───────────────► Final Answer
 │
 └── Poor
       │
       ▼
   Reformulate
       │
       └──────────────► Retrieve Again
```

---

# 🗺️ 100-Day Engineering Journey

JobLens evolved incrementally rather than being built as one large application.

```text
Stage 1
│
├── LLM fundamentals
├── Embeddings
└── Vector databases
        │
        ▼
Stage 2
│
├── RAG
├── Retrieval evaluation
└── Hybrid search
        │
        ▼
Stage 3
│
├── LangChain
├── LCEL
├── Qdrant
└── RAGAS
        │
        ▼
Stage 4
│
├── LangGraph
├── Agents
├── Memory
└── MCP
        │
        ▼
Stage 5
│
└── Docker / Deployment
```

### Branches

| Branch | Focus |
|---|---|
| `stage-1-core-genai` | LLMs, embeddings, vector DB fundamentals |
| `stage-2-rag` | RAG, evaluation, hybrid search |
| `stage-3-langchain` | LangChain, OOP services, Qdrant, RAGAS |
| `stage-4-langgraph` | Agents, memory, MCP |
| `mcp` | MCP server + Claude Desktop integration |

---

# 🎯 Engineering Lessons

This project wasn't just about making an LLM application work.

It was about understanding the engineering decisions behind it.

### Key lessons

**1. Retrieval quality matters.**

A powerful LLM cannot compensate for poor context.

**2. Frameworks are abstractions, not magic.**

Understanding the underlying implementation makes debugging and architecture decisions much easier.

**3. Evaluation must be part of the system.**

A RAG pipeline should be measured, not judged by a few impressive examples.

**4. Agents need observability.**

Without state visibility and traces, debugging multi-step agent workflows becomes difficult.

**5. Failure recovery matters.**

A self-correcting RAG pipeline can be more reliable than a pipeline that blindly returns its first result.

**6. Standards improve interoperability.**

MCP makes it possible to expose JobLens capabilities to multiple AI clients without creating client-specific integrations.

---

# 🔮 Roadmap

- [x] Core LLM pipeline
- [x] Embedding pipeline
- [x] Vector search
- [x] RAG
- [x] Cross-encoder reranking
- [x] RAG evaluation
- [x] LangChain implementation
- [x] Qdrant integration
- [x] LangGraph agent
- [x] Memory / checkpointing
- [x] MCP server
- [x] Claude Desktop integration
- [x] LangSmith observability
- [ ] Hybrid retrieval in LangChain version
- [ ] Improve RAGAS score
- [ ] Advanced query rewriting
- [ ] Context compression
- [ ] Production deployment
- [ ] Dockerized deployment

---

# 💡 What Makes JobLens Different?

JobLens isn't just another chatbot built on top of an LLM.

It explores the complete lifecycle of an AI application:

```text
             ┌─────────────────────────┐
             │       RAW DATA          │
             └────────────┬────────────┘
                          ↓
             ┌─────────────────────────┐
             │       INGESTION         │
             └────────────┬────────────┘
                          ↓
             ┌─────────────────────────┐
             │       EMBEDDINGS        │
             └────────────┬────────────┘
                          ↓
             ┌─────────────────────────┐
             │        RETRIEVAL        │
             └────────────┬────────────┘
                          ↓
             ┌─────────────────────────┐
             │       RERANKING         │
             └────────────┬────────────┘
                          ↓
             ┌─────────────────────────┐
             │        GENERATION       │
             └────────────┬────────────┘
                          ↓
             ┌─────────────────────────┐
             │        EVALUATION       │
             └────────────┬────────────┘
                          ↓
             ┌─────────────────────────┐
             │    SELF-CORRECTION      │
             └────────────┬────────────┘
                          ↓
             ┌─────────────────────────┐
             │       OBSERVABILITY     │
             └─────────────────────────┘
```

The project therefore serves as both:

> **A career intelligence tool and a practical exploration of modern GenAI engineering.**

---

# ⭐ If You Find This Interesting

If you're interested in:

- RAG systems
- AI agents
- LangGraph
- LangChain
- MCP
- Vector databases
- LLM evaluation
- GenAI engineering

feel free to explore the repository and follow the evolution of JobLens across the different stages.

**Built with curiosity, iteration, and a lot of debugging. 🚀**
