FROM python:3.11-slim

WORKDIR /app

LABEL maintainer="Adnan Khan <adnankhaan4488@gmail.com>"
LABEL description="TriageFlow Industrial Maintenance AI — Backend API"
LABEL version="1.0.0"

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the fastembed model during build so it's baked
# into the image — no download needed at container startup.
# This makes startup instant and removes the HuggingFace
# rate-limit problem entirely.
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')"

COPY . .

RUN mkdir -p data/manuals data/chroma_store

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "backend.api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1"]