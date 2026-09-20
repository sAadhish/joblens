# Stage 1 — Core GenAI Concepts
### Days 61–70 | JobLens Foundation

> This stage builds the core foundation of JobLens — understanding how LLMs work internally, converting text to meaning using embeddings, storing and searching that meaning using vector databases, and connecting everything into a production-grade modular pipeline.

---

## What Was Built

By the end of Stage 1, JobLens can:
- Parse any job description and extract structured data using an LLM
- Convert JDs and candidate profiles into semantic vectors
- Store those vectors in ChromaDB with metadata for filtering
- Match a candidate profile against multiple JDs using cosine similarity
- Filter results by role type, location, experience, and remote preference
- Run an AI-powered skill gap analysis on the best match
- Handle failures gracefully with logging and error handling
- Run as a clean modular Python system — not a single script

---

## Day-by-Day Breakdown

### Day 62 — Prompt Engineering
**What was built:** JD Analyzer — extracts structured info from any raw JD text

**Key concepts:**
- System prompt vs user prompt — system prompt defines behavior, user prompt is the input
- Role-based prompting — giving the model a specific identity improves output quality
- Temperature = 0 for structured tasks — deterministic output is required when code processes the result

**Industry insight:** The system prompt is the product. Companies like Notion AI and Cursor differentiate themselves through prompt engineering, not model choice.

---

### Day 63 — Structured Output
**What was built:** JSON JD Parser + Skill Gap Checker

**Key concepts:**
- Getting reliable JSON from LLMs — ask, show example, enforce
- `json.loads()` for parsing AI output into usable Python objects
- Stripping markdown wrappers before parsing — LLMs ignore "no markdown" instructions regularly
- try/except around every JSON parse — LLM output will fail in production

**Production lesson learned:** LLMs occasionally wrap JSON in ```json blocks even when explicitly told not to. Always sanitize before parsing.

```python
cleaned = re.sub(r"```json|```", "", raw).strip()
parsed = json.loads(cleaned)
```

---

### Day 64 — Embeddings
**What was built:** Resume Ranker using semantic similarity

**Key concepts:**
- Embeddings convert entire sentences to 384 numbers (vectors) capturing meaning
- Cosine similarity measures how similar two vectors are — 1.0 = identical, 0.0 = unrelated
- Query phrasing changes retrieval scores significantly — same model, different results
- Small models (all-MiniLM-L6-v2) have quality limitations vs larger models

**Critical discovery:** "Built predictive models using Python" scored differently depending on whether the query was conversational or keyword-style. This is the semantic gap problem — solved in Stage 2 with hybrid search.

---

### Day 65 — Vector Databases
**What was built:** ChromaDB storage + semantic search with confidence thresholds

**Key concepts:**
- Vector DBs use ANN (Approximate Nearest Neighbor) search — O(log n) vs SQL's O(n)
- ChromaDB returns distance, not similarity — convert with `similarity = 1 - distance`
- Confidence threshold of 0.35 — results below this are noise, not matches
- Hash-based IDs — `hashlib.md5(text)` prevents duplicate storage errors

**Architecture decision:** Explicitly set `{"hnsw:space": "cosine"}` on every collection. Default L2 distance produces negative similarity scores for text — meaningless for ranking.

**Bug caught:** `hsnw` vs `hnsw` — one letter typo caused silent fallback to L2 distance, producing scores of -0.23. Always verify cosine is active.

---

### Day 66 — Metadata Filtering
**What was built:** Location, experience, and remote-aware job search

**Key concepts:**
- Metadata is exact-match filtering — like SQL WHERE clause
- Document text is semantic search — like meaning-based search
- Two-layer search: filter first (metadata), then rank (semantic)
- ChromaDB filter operators: `$gte`, `$lte`, `$in`, `$ne`, `$and`

**Why this matters:** Pure semantic search on all JDs returns noise. Filtering by role_type first means ML roles never appear in marketing searches — regardless of embedding quality.

**Metadata designed for JobLens:**
```
role_type        → filter by engineering/data/ai/product
experience_min   → filter by minimum years required
experience_max   → filter by maximum years required
location         → filter by city
remote_ok        → filter remote-friendly roles
company_type     → filter startup/product/enterprise
```

---

### Day 67 — Similarity Search With Real JDs
**What was built:** Real JD matching against 5 target companies + AI skill gap analysis

**Key concepts:**
- Real JDs are noisy — company culture text adds noise to embeddings
- Preprocessing JDs before embedding improves retrieval quality
- LLM returns inconsistent formats for missing fields — needs sanitization layer

**Production bugs fixed:**
1. LLM returned 4 variations for "not specified": `None`, `""`, `"not specified"`, `"Not specified in JD"` — `.get()` fallback doesn't catch existing-but-null values
2. Fixed with `clean_field()` function that normalizes all variations to a clean fallback

**Real output for candidate profile (Aadhish):**
```
Rank 1: Freshworks — Data Analyst     → 0.756
Rank 2: Razorpay — Data Engineer      → 0.626
Rank 3: Zoho — GenAI Developer        → 0.536
Rank 4: Haptik — AI Engineer          → 0.520
Rank 5: Sarvam AI — Backend Engineer  → 0.385
```

---

### Day 68 — Unified Modular Pipeline
**What was built:** All modules connected into one system with clean separation of concerns

**Architecture:**
```
main.py              → entry point only
joblens/
├── config.py        → shared dependencies (Groq, ChromaDB, embeddings)
├── analyzer.py      → analyze_jd() — LLM extraction
├── store.py         → store_jd() — embed + store in ChromaDB
├── matcher.py       → match_profile() — cosine search + filter
├── gap.py           → analyze_gap() — LLM skill gap report
├── pipeline.py      → run_joblens() — orchestrates all modules
└── logger.py        → centralized logging setup
```

**Key pattern — dependency centralization:**
All shared clients (Groq, ChromaDB, SentenceTransformer) live in `config.py`.
Every module imports only what it needs. Changing a model or API means editing one file.

**Key pattern — single responsibility:**
Each file does exactly one thing. `analyzer.py` knows nothing about storage.
`matcher.py` knows nothing about LLM calls. Failures are isolated.

---

### Day 69 — Error Handling + Logging
**What was built:** Production-grade error handling and file-based logging

**Key concepts:**
- Logging vs print: logging is permanent, has levels, saves to file, timestamps every line
- Log levels: DEBUG → INFO → WARNING → ERROR → CRITICAL
- Graceful degradation: one failed JD is skipped, pipeline continues with remaining JDs
- `continue` in loops — partial results beat total failure

**Log output example:**
```
2026-05-26 10:40:59 | INFO    | pipeline | Pipeline started — 5 JDs
2026-05-26 10:41:00 | INFO    | analyzer | JD analyzed successfully — role: Backend Engineer
2026-05-26 10:41:01 | INFO    | store    | JD stored — company: Sarvam AI | role: Backend Engineer
2026-05-26 10:41:03 | INFO    | pipeline | Processing complete — 5/5 JDs stored
2026-05-26 10:41:03 | INFO    | pipeline | Pipeline completed successfully
```

**Production rule:** Every LLM call is wrapped in try/except. Every module returns None on failure. Pipeline checks for None before proceeding. Never assume AI calls succeed.

---

### Day 70 — System Design Session
**What was reviewed:** Full architecture of Stage 1, scale analysis, interview preparation

**System layers:**
```
Input Layer       → Raw JD text + candidate profile
Processing Layer  → LLM extracts structured data (analyzer.py)
Storage Layer     → Embeddings + metadata stored in ChromaDB (store.py)
Retrieval Layer   → Cosine search + metadata filter (matcher.py)
Intelligence Layer→ LLM gap analysis on best match (gap.py)
Output Layer      → Ranked matches + skill gap report
```

**Scale analysis:**
- Speed bottleneck: sequential LLM calls — 100 JDs = ~80 seconds → fix: parallel processing (Stage 4)
- Cost bottleneck: re-analyzing unchanged JDs every run → fix: file-based caching
- Storage bottleneck: in-memory ChromaDB lost on restart → fix: PersistentClient

**What's missing for production:**
```
API layer          → FastAPI wrapper (Stage 4)
Unit tests         → pytest (Stage 4)
LLM evaluation     → measure match quality (Stage 4)
Real JD data       → scraping/importing (Stage 2-3)
```

---

## Engineering Decisions Made in Stage 1

| Decision | Choice | Why |
|---|---|---|
| LLM provider | Groq (Llama 3.3 70B) | Free tier, fast, no vendor lock-in |
| Embedding model | all-MiniLM-L6-v2 | Fast, local, no API cost. Upgrade to larger model in production |
| Vector DB | ChromaDB | Zero setup, local, concepts transfer to Pinecone/Qdrant |
| Distance metric | Cosine similarity | Captures semantic direction, not magnitude — standard for text |
| ID strategy | MD5 hash of text | Same text always maps to same ID — prevents duplicates |
| Temperature | 0 for all structured output | Deterministic output required when code parses the result |
| Error strategy | Graceful degradation | Partial results beat total failure |
| Logging | File + terminal | Permanent record for production debugging |

---

## Bugs Fixed in Stage 1 (Real Learning)

| Bug | Cause | Fix |
|---|---|---|
| Negative similarity scores | `hsnw` typo → L2 fallback instead of cosine | Fixed typo to `hnsw` |
| Filter crash | `{"$and", conditions}` — Python set not dict | Changed to `{"$and": conditions}` |
| JSON parse failure | LLM wrapped output in markdown code blocks | `re.sub(r"```json\|```", "", raw).strip()` |
| Missing fields showing None | LLM returns inconsistent "not specified" formats | `clean_field()` normalizes all variations |
| Wrong return type hint | `store_jd()` returned `str` but typed as `-> dict` | Fixed to `-> str` |

---

## Key Interview Answers From Stage 1

**"Why use a vector database instead of SQL?"**
SQL does exact keyword matching — it can't find semantic similarity. ChromaDB uses ANN search on embeddings, finding documents that match the meaning of a query even when exact words differ.

**"How does cosine similarity work?"**
It measures the angle between two vectors in high-dimensional space. Score of 1.0 means identical direction (same meaning), 0.0 means perpendicular (unrelated). We use it because it captures semantic meaning regardless of vector magnitude.

**"What breaks at scale?"**
Sequential LLM calls become slow (parallel processing fixes this), in-memory vector DB loses data on restart (PersistentClient or Pinecone fixes this), and re-analyzing unchanged JDs wastes API cost (caching fixes this).

**"How do you handle LLM failures in production?"**
Every LLM call is wrapped in try/except. Failures are logged with full error details. The pipeline uses graceful degradation — one failed component skips and continues, returning partial results rather than crashing entirely.

---

## Tech Stack

```
LLM API          Groq (Llama 3.3 70B)
Embeddings       Sentence Transformers (all-MiniLM-L6-v2)
Vector DB        ChromaDB (persistent)
Language         Python 3.11+
Environment      python-dotenv
Logging          Python logging module
```

---

## What Stage 2 Adds

Stage 1 retrieves documents. Stage 2 generates intelligent answers from them.

```
Stage 1   →  "Here are the 3 most relevant JDs for your profile"
Stage 2   →  "Here is what you need to study, here are the interview
              questions they will ask, here is your week-by-week prep plan"
```

The ChromaDB, embeddings, and metadata built in Stage 1 become the retrieval layer of the RAG system in Stage 2. Nothing is wasted — everything connects.

---

*Built by [Aadhish](https://linkedin.com/in/aadhish) as part of a 100-day GenAI engineering journey*
*GitHub: [github.com/sAadhish](https://github.com/sAadhish)*