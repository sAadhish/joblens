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
