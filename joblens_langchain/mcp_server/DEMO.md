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
> "Read joblens://companies and tell me what's indexed"

### 2. Job Requirements
> "Use JobLens to search for what Sarvam AI requires"

### 3. Skill Gap Analysis
> "My skills are Python, SQL, Power BI. Use JobLens to check my gap for Freshworks"

### 4. Career Advice
> "I'm switching from BI to GenAI. Which company in JobLens is my best match?"

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