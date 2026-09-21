FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/app:/app/joblens_langchain"

# Default port — Render overrides via $PORT env var
EXPOSE 8000

# Shell form allows $PORT expansion at runtime
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}