import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import chat, index, health
from langsmith_setup import setup_langsmith
import logging
import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from langsmith import Client as LangSmithClient


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

setup_langsmith()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup logic before the API begins accepting requests."""

    logger.info(json.dumps({
        "event": "api_startup",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }))

    # Check LangSmith connection
    try:
        ls_client = LangSmithClient()
        logger.info("LangSmith connected — tracing active")
    except Exception as e:
        logger.warning(f"LangSmith not connected — tracing disabled: {e}")

    yield

    # Shutdown logic can go here later
    logger.info("JobLens API shutting down")

app=FastAPI(
    title="Joblens API",
    description="""
AI-powered job market intelligence for tech professionals in India.

## Features
- **Chat**: Multi-turn career conversations with memory
- **Index**: Add job descriptions and resumes
- **Search**: Query across indexed companies

## How it works
1. Index JDs using POST /index/jd
2. Start a conversation using POST /chat with a session_id
3. Continue the conversation with the same session_id
""",
version="1.0.0",
lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(health.router,tags=["System"])
app.include_router(chat.router,tags=["Chat"])
app.include_router(index.router,tags=["Indexing"])

@app.get("/",tags=["System"])
async def root():
    return{
        "name": "JobLens API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


