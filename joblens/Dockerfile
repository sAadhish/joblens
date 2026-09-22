FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download the HuggingFace embedding model so it doesn't time out or hit rate limits at runtime on Render
RUN python -c "from langchain_huggingface import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')"

# Copy application code
COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/app:/app/joblens_langchain"

# Default port — Render overrides via $PORT env var
EXPOSE 8000

# Shell form allows $PORT expansion at runtime
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}