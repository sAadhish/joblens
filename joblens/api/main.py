import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import chat, index, health
from langsmith_setup import setup_langsmith
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

setup_langsmith()

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
version="1.0.0"
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