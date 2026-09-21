import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import chat, index, health
from langsmith_setup import setup_langsmith
import logging
import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from langsmith import Client as LangSmithClient

# Resolve the frontend directory (lives at ../../frontend relative to this file,
# but we use the absolute path from the joblens/frontend workspace).
FRONTEND_DIR = Path(os.getenv("FRONTEND_DIR", "/app/frontend"))

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

# CORS — use FRONTEND_URL for production, fallback to wildcard for local dev
_frontend_url = os.getenv("FRONTEND_URL", "")
_origins = [_frontend_url] if _frontend_url else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
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
        "health": "/health",
        "frontend": "/app/"
    }

# -------------------------------------------------------
# FRONTEND — serve the static UI at /app/
# -------------------------------------------------------

@app.get("/app", include_in_schema=False)
@app.get("/app/", include_in_schema=False)
async def serve_frontend():
    """Serve the JobLens frontend SPA."""
    return FileResponse(FRONTEND_DIR / "index.html")

# Mount static assets (JS, CSS) so the browser can load them
app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")
