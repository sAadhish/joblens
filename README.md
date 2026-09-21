# 🔎 JobLens
### AI-Powered Job Market Intelligence & Career Assistant

> **Understand the job market. Identify skill gaps. Improve your resume. Find better opportunities.**

JobLens is an **AI-powered job market intelligence platform** designed to help tech professionals interact with job-market data and resumes using natural language, built using **FastAPI**, **LangGraph**, **LangChain**, and **Qdrant**, with a beautiful **Dockerized Frontend UI**.

🔗 **Live Demo**: _Coming soon — URL will be added after deployment_

---

## ✨ Features

- 🔍 **Semantic Job Search**: Query the job market naturally.
- 📄 **Resume Analysis & Comparison**: Identify missing skills by comparing your resume to job requirements.
- 🤖 **LangGraph Career Agent**: Multi-step AI reasoning that self-corrects bad retrieval automatically.
- 🧠 **Persistent Memory**: Conversational memory that remembers context.
- 📊 **API Dashboard**: A premium KPI dashboard to monitor vector chunks, health, and manage data.
- 🐳 **Fully Dockerized**: Effortlessly spin up the entire application (API, UI, Vector Store) in one command.

---

## 📸 Screenshots

### The KPI Dashboard
Monitor your API health, vector database status, and easily remove indexed job descriptions.
![Dashboard](joblens/assets/dashboard.png)

### The Career Assistant Chat
Interact with the LangGraph agent for personalized career advice based on indexed JDs and Resumes.
![Career Chat](joblens/assets/chat.png)

### Seamless Data Indexing
Index thousands of chunks into the Qdrant vector database via the UI.
![Indexing](joblens/assets/indexing.png)

---

## 🏗️ Architecture

### Deployed Architecture

```text
                ┌──────────────────┐
                │     Recruiter    │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │  JobLens Web UI  │
                │   (Vercel)       │
                └────────┬─────────┘
                         ↓ HTTPS
                ┌──────────────────┐
                │ FastAPI Backend  │
                │   (Render)       │
                └──────┬─────┬─────┘
                       ↓     ↓
                 ┌───────┐ ┌───────┐
                 │Qdrant │ │ Groq  │
                 │ Cloud │ │  LLM  │
                 └───────┘ └───────┘
```

### Technology Stack

| Layer              | Technology                                  |
|--------------------|---------------------------------------------|
| **Frontend**       | Vanilla JS/HTML/CSS with glassmorphism UI   |
| **API**            | FastAPI (async, high-performance)            |
| **Agent**          | LangGraph (multi-step reasoning, self-correction) |
| **RAG**            | LangChain + HuggingFace `bge-base-en-v1.5` |
| **Vector DB**      | Qdrant Cloud                                |
| **LLM**            | Groq API (fast inference)                   |
| **Observability**  | LangSmith tracing                           |
| **Hosting**        | Render (backend) + Vercel (frontend)        |

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- API Keys (Groq, Qdrant Cloud)

### 1. Clone the repository
```bash
git clone https://github.com/sAadhish/joblens.git
cd joblens/joblens
```

### 2. Configure Environment Variables
Copy the example environment file and fill in your API keys:
```bash
cp .env.example .env
```

Required variables:
| Variable             | Description                           | Required |
|----------------------|---------------------------------------|----------|
| `GROQ_API_KEY`       | Groq API key for LLM inference        | ✅        |
| `QDRANT_URL`         | Qdrant Cloud cluster URL              | ✅        |
| `QDRANT_API_KEY`     | Qdrant Cloud API key                  | ✅        |
| `QDRANT_COLLECTION`  | Qdrant collection name                | ✅        |
| `LANGSMITH_API_KEY`  | LangSmith API key (for tracing)       | Optional |
| `LANGSMITH_PROJECT`  | LangSmith project name                | Optional |
| `LANGSMITH_TRACING`  | Enable/disable LangSmith tracing      | Optional |
| `FRONTEND_URL`       | Deployed frontend URL (for CORS)      | Optional |

### 3. Run with Docker 🐳
```bash
docker compose up -d
```

### 4. Access the App
Once the container is up: 👉 **[http://localhost:8081/app/](http://localhost:8081/app/)**

To stop: `docker compose down`

---

## 🛠️ Local Development (without Docker)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

PYTHONPATH="$(pwd):$(pwd)/joblens_langchain" uvicorn api.main:app --host 127.0.0.1 --port 8080 --reload
```

Access the app at `http://127.0.0.1:8080/app/`

---

## 📖 API Documentation

Once running, interactive API docs are available at:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

### Endpoints

| Method   | Path                    | Description                      |
|----------|-------------------------|----------------------------------|
| `GET`    | `/`                     | API info and links               |
| `GET`    | `/health`               | Health check + Qdrant status     |
| `GET`    | `/companies`            | List indexed companies           |
| `GET`    | `/prompts`              | View deployed prompt versions    |
| `POST`   | `/chat`                 | Career chat (main endpoint)      |
| `POST`   | `/index/jd`             | Index a job description          |
| `POST`   | `/index/resume`         | Upload and index a resume PDF    |
| `DELETE` | `/index/jd/{company}`   | Remove a company's JD            |

---

## 🌐 Deployment

### Backend → Render (Free Tier)
The backend deploys as a Docker container on Render's free web service. The `render.yaml` Blueprint automates the setup.

### Frontend → Vercel (Hobby Tier)
The static frontend deploys to Vercel. Set `window.JOBLENS_API_URL` in `frontend/config.js` to your Render backend URL.

### ⚠️ Free-Tier Limitations
- **Cold starts**: Render free-tier services sleep after 15 minutes of inactivity. First request after sleep takes ~30-60 seconds. The UI displays a friendly "starting up" message during this time.
- **Memory**: Free tier has limited RAM. The HuggingFace embedding model loads on first request.
- **Rate limits**: Groq API has rate limits on the free tier. Heavy usage may hit these limits.

---

*Built with curiosity, iteration, and a lot of debugging. 🚀*